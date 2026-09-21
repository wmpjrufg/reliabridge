"""Dataset computacional do artigo 3. Não modifica o núcleo nem os artigos anteriores.

Uso na raiz: .venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py gerar
             .venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py piloto
Saídas JSONL: uma entrada por cenário e um registro por execução. Não são ensaios.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))


def read_config():
    return json.loads((BASE / "config.json").read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def cases(config):
    for span, load, width, vehicle, material in itertools.product(
        config["span_m"], config["dead_load_kpa"], config["width_m"], config["vehicles"], config["materials"]
    ):
        # IDs físicos: permanecem estáveis se a ordem da matriz mudar.
        cid = f"L{round(span*100):04d}_G{round(load*100):03d}_B{round(width*100):03d}_{vehicle}_{material}"
        yield {
            "case_id": cid, "span_m": span, "dead_load_kpa": load, "width_m": width,
            "vehicle": vehicle, "material_class": material,
            **config["vehicles"][vehicle], **config["materials"][material],
            "material_basis": "class_model", "status": "planned",
            "split": "test_span" if span in (4.5, 7.5, 9.5) else "validation_span" if span in (5.5, 8.5) else "train",
            "group_id": f"L{round(span*100):04d}",
            "crowd_moment_branch": "active" if span > 6 else "inactive",
            "publication_ready": False,
        }


def generate():
    config = read_config()
    rows = list(cases(config))
    assert len({r["case_id"] for r in rows}) == len(rows)
    path = BASE / "data/cenarios.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows), encoding="utf-8")
    manifest = {
        "dataset_version": config["dataset_version"], "created_utc": datetime.now(timezone.utc).isoformat(),
        "n_scenarios": len(rows), "n_simulated_in_this_file": 0,
        "counts_by_split": {s: sum(r["split"] == s for r in rows) for s in ("train", "validation_span", "test_span")},
        "config_sha256": digest(BASE / "config.json"), "scenarios_sha256": digest(path),
        "source_sha256": {str(p): digest(ROOT / p) for p in ("madeiras.py", "batch_pre_sizing.py", "pages/pre_sizing.py", "paper/materia/04_methodology.tex")},
        "note": "Entradas planejadas. Resultados ficam separados. A base antiga das 40 espécies NÃO foi usada.",
    }
    dump(BASE / "data/manifest.json", manifest)
    print(json.dumps(manifest["counts_by_split"]), f"total={len(rows)}", flush=True)


def build_problem(row, config):
    from batch_pre_sizing import textos
    from madeiras import _criar_projeto_otimo_pre_sizing
    t = textos("pt")
    fixed = config["fixed"]
    data = {
        t["entrada_comprimento"]: row["span_m"] * 100,
        t["pista"]: row["width_m"] * 100,
        f"{t['carga_permanente']} (kPa)": row["dead_load_kpa"],
        f"{t['carga_roda']} (kN)": row["wheel_load_kn"],
        f"{t['carga_multidao']} (kPa)": row["crowd_load_kpa"],
        f"{t['distancia_eixos']} (m)": row["axle_spacing_m"],
        t["classe_carregamento"]: fixed["load_duration"], t["classe_madeira"]: fixed["wood_type"],
        t["classe_umidade"]: fixed["moisture_class"],
        t["considerar_fluencia"]: fixed["phi"], t["percentual_robustez"]: fixed["robustness_pct"],
        f"{t['densidade_long']} (kg/m³)": row["density_kg_m3"],
        f"{t['densidade_tab']} (kg/m³)": row["density_kg_m3"],
        f"{t['f_mk']} (MPa)": row["fm_k_mpa"], f"{t['f_vk']} (MPa)": row["fv_k_mpa"],
        f"{t['e_modflex']} (GPa)": row["E_gpa"], f"{t['f_mk_tab']} (MPa)": row["fm_k_mpa"],
    }
    for key in ("gamma_g", "gamma_q", "gamma_wc", "gamma_wf", "psi2"):
        data[t[key]] = fixed[key]
    limits = [config["bounds_cm"][k] for k in ("d", "bw", "h", "esp_long", "esp_tab")]
    return _criar_projeto_otimo_pre_sizing(data, *limits, t,
        config["optimizer"]["robust_checks"], fixed["robustness_pct"])


def solve(row, config, seed):
    import numpy as np
    import pymoo
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.operators.sampling.rnd import FloatRandomSampling
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.mutation.pm import PM
    from pymoo.optimize import minimize
    start = time.perf_counter()
    result = {
        "case_id": row["case_id"], "inputs": row, "seed": seed,
        "config": config, "config_sha256": digest(BASE / "config.json"),
        "model_sha256": digest(ROOT / "madeiras.py"), "runner_sha256": digest(Path(__file__)),
        "python_version": platform.python_version(), "numpy_version": np.__version__, "pymoo_version": pymoo.__version__,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "publication_ready": False, "purpose": "exploratory_simulation",
    }
    try:
        problem = build_problem(row, config)
        opt = config["optimizer"]
        algorithm = NSGA2(pop_size=opt["population"], sampling=FloatRandomSampling(),
            crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20), eliminate_duplicates=True)
        res = minimize(problem, algorithm, ("n_gen", opt["generations"]), seed=seed, verbose=False)
        if res.X is None:
            result.update(status="no_feasible_found", frontier=[], selected=None)
        else:
            xs, fs, gs = map(np.atleast_2d, (res.X, res.F, res.G))
            front = []
            names = ("d_cm", "bw_cm", "h_cm", "esp_long_input_cm", "esp_tab_input_cm")
            for x, f, g in zip(xs, fs, gs):
                if not np.all(np.isfinite(np.concatenate([x, f, g]))):
                    raise ValueError("Resultado não finito")
                nominal = problem.calcular_objetivos_restricoes_otimizacao(*x)
                gn = np.asarray(nominal[1], dtype=float)
                loads = nominal[8]
                front.append({
                    **dict(zip(names, map(float, x))),
                    "volume_robust_mean_m3": float(f[0]), "deflection_ratio_robust_mean": float(f[1]),
                    "g_robust_mean": g.tolist(), "g_nominal": gn.tolist(),
                    "volume_nominal_m3": float(nominal[0][0]), "deflection_ratio_nominal": float(nominal[0][1]),
                    "n_beams": int(loads["num_longs"]), "n_deck_pieces": int(loads["num_tabs"]),
                    "esp_long_effective_cm": 100 * float(loads["esp_long_corr [m]"]),
                    "esp_tab_effective_cm": 100 * float(loads["esp_tab_corr [m]"]),
                    "governing_structural_nominal": int(np.argmax(gn[:4])) + 1,
                    "feasible_robust_mean": bool(np.max(g) <= 1e-8),
                    "feasible_nominal": bool(np.max(gn) <= 1e-8),
                    "near_bound": bool(np.any(np.minimum(x-problem.xl, problem.xu-x) / (problem.xu-problem.xl) < 0.005)),
                })
            candidates = [i for i, p in enumerate(front) if p["feasible_robust_mean"] and p["feasible_nominal"]]
            # Regra unívoca: extremo econômico entre candidatos também viáveis nominalmente.
            # Os dois objetivos no núcleo são minimizados; não inverter o sinal da flecha.
            best = min(candidates, key=lambda i: (front[i]["volume_robust_mean_m3"],
                front[i]["deflection_ratio_robust_mean"], tuple(xs[i]))) if candidates else None
            result.update(status="ok" if best is not None else "no_nominal_feasible_candidate",
                frontier=front, selected=front[best] if best is not None else None,
                selected_index=best, selection_rule="min_volume_among_mean_and_nominal_feasible")
    except Exception as exc:
        result.update(status="error", error=f"{type(exc).__name__}: {exc}", frontier=[], selected=None)
    result["elapsed_s"] = time.perf_counter() - start
    return result


def run(args):
    config = read_config()
    rows = list(cases(config))
    if args.action == "piloto":
        rows = [r for r in rows if r["material_class"] == "D40" and r["width_m"] == 4.5
            and r["span_m"] in (3, 10) and r["dead_load_kpa"] in (0.1, 5)]
    elif args.case_id:
        rows = [r for r in rows if r["case_id"] in args.case_id]
        if len(rows) != len(set(args.case_id)):
            raise ValueError("case-id não encontrado na configuração")
    else:
        raise ValueError("Para executar, indique --case-id ou use piloto. A matriz completa não roda implicitamente.")
    seed = args.seed if args.seed is not None else config["optimizer"]["seed"]
    target = BASE / "results" / ("piloto" if args.action == "piloto" else "casos")
    for row in rows:
        path = target / f"{row['case_id']}_s{seed}.json"
        if path.exists():
            old = json.loads(path.read_text(encoding="utf-8"))
            if old["config_sha256"] != digest(BASE / "config.json") or old["model_sha256"] != digest(ROOT / "madeiras.py") or old["runner_sha256"] != digest(Path(__file__)):
                raise ValueError(f"Resultado de outra versão em {path}. Preserve-o em outro diretório antes de reexecutar.")
            print(f"já existe: {row['case_id']}", flush=True)
            continue
        print(f"executando {row['case_id']} seed={seed}", flush=True)
        result = solve(row, config, seed)
        dump(path, result)
        print(f"{result['status']}: {result['elapsed_s']:.1f}s", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("action", choices=("gerar", "piloto", "executar"))
    p.add_argument("--case-id", action="append")
    p.add_argument("--seed", type=int)
    args = p.parse_args()
    generate() if args.action == "gerar" else run(args)


if __name__ == "__main__":
    main()
