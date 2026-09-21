"""Audita entradas e reavalia os resultados do piloto no núcleo existente.

Conferência de integração, não validação independente das equações estruturais.
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np

from dataset import BASE, ROOT, build_problem, digest, dump, read_config


def main():
    config = read_config()
    rows = [json.loads(line) for line in (BASE / "data/cenarios.jsonl").read_text(encoding="utf-8").splitlines()]
    manifest = json.loads((BASE / "data/manifest.json").read_text(encoding="utf-8"))
    assert manifest["scenarios_sha256"] == digest(BASE / "data/cenarios.jsonl")
    assert manifest["config_sha256"] == digest(BASE / "config.json")
    for source, sha in manifest["source_sha256"].items():
        assert digest(ROOT / source) == sha, f"Fonte mudou: {source}"
    assert len(rows) == 2700 and len({r["case_id"] for r in rows}) == 2700
    groups = {}
    for row in rows:
        groups.setdefault(row["group_id"], set()).add(row["split"])
        assert row["status"] == "planned" and not row["publication_ready"]
    assert all(len(splits) == 1 for splits in groups.values())
    assert Counter(r["vehicle"] for r in rows) == {"TB240": 1350, "TB450": 1350}
    assert Counter(r["material_class"] for r in rows) == {c: 540 for c in config["materials"]}

    # Confere os limites contra os defaults atuais; não altera o núcleo.
    from batch_pre_sizing import LimitesBusca
    limits = LimitesBusca()
    for key, pair in config["bounds_cm"].items():
        assert tuple(pair) == getattr(limits, key)

    lookup = {r["case_id"]: r for r in rows}
    records = []
    pilot_results = []
    for path in sorted((BASE / "results/piloto").glob("*.json")):
        result = json.loads(path.read_text(encoding="utf-8"))
        pilot_results.append(result)
        assert result["model_sha256"] == digest(ROOT / "madeiras.py")
        assert result["config_sha256"] == digest(BASE / "config.json")
        assert result["runner_sha256"] == digest(BASE / "scripts/dataset.py")
        assert result["inputs"] == lookup[result["case_id"]]
        selected = result["selected"]
        record = {"case_id": result["case_id"], "status": result["status"], "elapsed_s": result["elapsed_s"]}
        if selected is not None:
            problem = build_problem(result["inputs"], result["config"])
            x = [selected[k] for k in ("d_cm", "bw_cm", "h_cm", "esp_long_input_cm", "esp_tab_input_cm")]
            nominal = problem.calcular_objetivos_restricoes_otimizacao(*x)
            np.testing.assert_allclose(nominal[1], selected["g_nominal"], atol=1e-10, rtol=1e-10)
            np.testing.assert_allclose(nominal[0][0], selected["volume_nominal_m3"], atol=1e-10)
            out = {}
            problem._evaluate(np.array(x), out)
            np.testing.assert_allclose(out["G"], selected["g_robust_mean"], atol=1e-10)
            np.testing.assert_allclose(out["F"][0], selected["volume_robust_mean_m3"], atol=1e-10)
            assert max(selected["g_nominal"]) <= 1e-8
            assert max(selected["g_robust_mean"]) <= 1e-8
            eligible = [p for p in result["frontier"] if p["feasible_nominal"] and p["feasible_robust_mean"]]
            assert selected["volume_robust_mean_m3"] == min(p["volume_robust_mean_m3"] for p in eligible)
            # Volume reconstruído independentemente das duas parcelas do registro.
            reconstructed = selected["n_beams"] * np.pi * (selected["d_cm"]/100)**2 / 4 * result["inputs"]["span_m"]
            reconstructed += selected["n_deck_pieces"] * selected["bw_cm"]/100 * selected["h_cm"]/100 * result["inputs"]["width_m"]
            np.testing.assert_allclose(reconstructed, selected["volume_nominal_m3"], atol=1e-10)
            record.update(d_cm=selected["d_cm"], volume_nominal_m3=selected["volume_nominal_m3"],
                g_nominal_max=max(selected["g_nominal"]), near_bound=selected["near_bound"])
        records.append(record)

    # Uma solução da carga maior pode revelar que a busca da carga menor perdeu
    # um candidato mais econômico. Reavaliar a geometria no problema de destino.
    improvements = []
    for low in pilot_results:
        for high in pilot_results:
            if low["selected"] is None or high["selected"] is None:
                continue
            a, b = low["inputs"], high["inputs"]
            if any(a[k] != b[k] for k in ("span_m", "width_m", "material_class", "vehicle")) or a["dead_load_kpa"] >= b["dead_load_kpa"]:
                continue
            p = build_problem(a, low["config"])
            x = np.array([high["selected"][k] for k in ("d_cm", "bw_cm", "h_cm", "esp_long_input_cm", "esp_tab_input_cm")])
            out = {}
            p._evaluate(x, out)
            nominal = p.calcular_objetivos_restricoes_otimizacao(*x)
            old_v = low["selected"]["volume_robust_mean_m3"]
            if max(out["G"]) <= 1e-8 and max(nominal[1]) <= 1e-8 and out["F"][0] < old_v - 1e-8:
                improvements.append({"target_case": low["case_id"], "candidate_from": high["case_id"],
                    "original_volume_robust_mean_m3": old_v, "candidate_volume_robust_mean_m3": float(out["F"][0]),
                    "reduction_pct": float(100 * (old_v-out["F"][0])/old_v),
                    "candidate_g_mean_max": float(max(out["G"])), "candidate_g_nominal_max": float(max(nominal[1]))})

    report = {"inputs_checked": len(rows), "pilot_runs_checked": len(records),
        "expected_pilot_runs": 8, "pilot_complete": len(records) == 8,
        "status_counts": dict(Counter(r["status"] for r in records)),
        "checks": ["hashes", "unique_ids", "split_groups", "balanced_vehicles_classes", "current_bounds",
            "nominal_re_evaluation", "robust_mean_re_evaluation", "minimum_volume_selection", "volume_reconstruction"],
        "records": records, "cross_load_feasible_improvements": improvements, "publication_ready": False}
    dump(BASE / "results/verificacao.json", report)
    lines = ["# Piloto exploratório — resultados e conferência", "",
        f"Entradas conferidas: **{len(rows)}**. Execuções do piloto: **{len(records)}/8**.", "",
        "Valores de soluções calculadas pelo modelo existente; não são resultados de uma equação de IA.", "",
        "| Cenário | Status | d (cm) | Volume nominal (m³) | Tempo (s) |",
        "|---|---|---:|---:|---:|"]
    for r in records:
        lines.append(f"| {r['case_id']} | {r['status']} | {r.get('d_cm', float('nan')):.2f} | {r.get('volume_nominal_m3', float('nan')):.3f} | {r['elapsed_s']:.1f} |")
    if records:
        median_s = float(np.median([r["elapsed_s"] for r in records]))
        lines += ["", f"Mediana observada: {median_s:.1f} s/caso. Projeção bruta para uma semente em 2.700 casos: {median_s*2700/3600:.1f} h.",
            "Essa projeção usa somente D40 e oito extremos; não inclui repetições, revisão do modelo ou casos difíceis."]
    if improvements:
        lines += ["", "## Diagnóstico de qualidade do alvo", "",
            "A transferência de geometrias entre cargas encontrou candidatos mais econômicos, também viáveis na média e nominalmente:", ""]
        for item in improvements:
            lines.append(f"- Em `{item['target_case']}`, a geometria de `{item['candidate_from']}` reduz o volume médio em **{item['reduction_pct']:.1f}%**.")
        lines += ["", "Isso demonstra que o extremo econômico selecionado no piloto não é uma referência convergida em todos os casos. Preservamos os resultados originais e registramos o diagnóstico. Antes de treinar, investigar sementes, gerações, retenção do melhor candidato econômico e eventualmente uma busca escalar de volume após o NSGA-II."]
    lines += ["", "Conferidos IDs, hashes, separação por vão, limites atuais, reavaliação das soluções e reconstrução do volume nominal.",
        "A reavaliação usa o mesmo núcleo e verifica a integração. A revisão física do modelo, as transições de carregamento, a convergência e a repetição de sementes permanecem pendentes.", ""]
    (BASE / "results/PILOTO.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "records"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
