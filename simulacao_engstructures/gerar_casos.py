"""Monta a planilha de casos da campanha de semente única do Artigo 2 (Engineering Structures).

Mesma receita da campanha da Revista Matéria: uma execução do NSGA-II por caso, semente 1,
população 50, 300 gerações, robustez de 5% no diâmetro e os mesmos limites de busca. A
diferença é a faixa de vãos, de 3 a 10 m em passo de 1 m, e o bloco de espécies.

A planilha tem dois blocos:

    CLS  base de classes: 5 classes (D20 a D60) x 8 vãos = 40 casos.
         É a matriz vão x classe, como a da Matéria. As células de 3 a 6 m têm entradas
         idênticas às C-01 a C-20 da Matéria e devem reproduzir os mesmos volumes.
         Também é o cenário "cls" de todas as espécies: as propriedades da classe não
         dependem da espécie, então rodar "cls" por espécie repetiria o mesmo caso.

    E    bloco de espécies: 40 espécies x 8 vãos = 320 casos, cenário esp
         (propriedades medidas da espécie).

Comparação montada depois, no consolidar.py:
    esp x CLS  decisão de projeto real (espécie contra classe)

Só entram cenários que existem como decisão de projeto: projetar pela espécie ou pela
classe. Cenários híbridos (espécie com o E da classe, por exemplo) foram retirados.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\gerar_casos.py
    .venv\\Scripts\\python.exe simulacao_engstructures\\gerar_casos.py --forcar
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "paper" / "engstruct" / "scripts"))

import batch_pre_sizing as bps  # noqa: E402
from gerar_casos_engstruct import (  # noqa: E402
    BASE_ESPECIES,
    FATOR_CISALHAMENTO,
    montar_dados,
)

SAIDA_PADRAO = PASTA / "casos_engstruct_semente1.xlsx"

VAOS_M = [3, 4, 5, 6, 7, 8, 9, 10]

# ABNT NBR 7190-3:2022, florestas nativas. f_m,k = f_c0,k (NBR 7190-1:2022, item 6.3.4).
# Mesmos valores da Tabela de classes da Matéria. Conferidos contra a base de espécies.
CLASSES_NBR = {
    "D20": {"f_mk": 20.0, "f_vk": 4.0, "e_mpa": 10000.0, "densidade": 500.0},
    "D30": {"f_mk": 30.0, "f_vk": 5.0, "e_mpa": 12000.0, "densidade": 625.0},
    "D40": {"f_mk": 40.0, "f_vk": 6.0, "e_mpa": 14500.0, "densidade": 750.0},
    "D50": {"f_mk": 50.0, "f_vk": 7.0, "e_mpa": 16500.0, "densidade": 850.0},
    "D60": {"f_mk": 60.0, "f_vk": 8.0, "e_mpa": 19500.0, "densidade": 1000.0},
}

# Idêntico à Matéria (batch_pre_sizing_casos_materia.xlsx).
ALGORITMO = bps.ParametrosAlgoritmo(pop_size=50, n_gen=300, n_checagens=30, seed=1)
LIMITES = bps.LimitesBusca()  # d 20-100, bw 20-50, h 5-15, esp_long 30-200, esp_tab 2-5 cm


def id_classe(classe: str, l_m: int) -> str:
    return f"CLS_{classe}_L{l_m:02d}"


def conferir_classes(base: pd.DataFrame) -> None:
    """A base de espécies traz as propriedades da classe de cada espécie; têm de bater."""
    for _, esp in base.iterrows():
        ref = CLASSES_NBR[esp["classe_D"]]
        par = {
            "f_mk": esp["f_mk_classe_MPa"], "f_vk": esp["f_v0k_classe_MPa"],
            "e_mpa": esp["E_c0_classe_MPa"], "densidade": esp["rho_classe_kgm3"],
        }
        for k, v in par.items():
            if abs(float(v) - ref[k]) > 1e-9:
                raise ValueError(f"{esp['nome']}: {k} da classe {esp['classe_D']} = {v}, esperado {ref[k]}")


def propriedades_especie(esp: pd.Series, fator_cis: float) -> dict:
    """Propriedades medidas da espécie (cenário esp)."""
    return {
        "densidade": float(esp["rho_ap_kgm3"]),
        "f_mk": float(esp["f_c0_k_MPa"]),
        "f_vk": round(float(esp["f_v0_m_MPa"]) * fator_cis, 2),
        "e_mpa": float(esp["E_c0_m_MPa"]),
    }


def caso(t: dict, caso_id: str, l_m: int, prop: dict, sobol: bool) -> bps.CasoBatch:
    return bps.CasoBatch(
        id=caso_id,
        dados=montar_dados(t, l_m * 100, prop["densidade"], prop["f_mk"],
                           prop["f_vk"], round(prop["e_mpa"] / 1000.0, 3)),
        limites=LIMITES,
        algoritmo=ALGORITMO,
        sobol=bps.ConfigSobol(ativo=sobol),
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--fator-cisalhamento", type=float, default=FATOR_CISALHAMENTO)
    p.add_argument("--sobol-especies", action="store_true",
                   help="liga Sobol também no bloco de espécies (na base de classes já vem ligada, como na Matéria)")
    p.add_argument("--forcar", action="store_true", help="sobrescreve a planilha existente")
    args = p.parse_args()

    if args.saida.exists() and not args.forcar:
        print(f"{args.saida.name} já existe. Use --forcar para regerar.", file=sys.stderr)
        return 1

    base = pd.read_csv(BASE_ESPECIES)
    conferir_classes(base)
    t = bps.textos("pt")
    casos, refs = [], {}

    # Bloco CLS: matriz vão x classe
    for classe, prop in CLASSES_NBR.items():
        for l_m in VAOS_M:
            cid = id_classe(classe, l_m)
            casos.append(caso(t, cid, l_m, prop, sobol=True))
            refs[cid] = {"bloco": "classe", "especie_id": None, "especie": None, "classe": classe,
                         "cenario": "cls", "vao_m": l_m, "E_MPa": prop["e_mpa"], "id_classe": cid}

    # Bloco E: espécies
    for _, esp in base.iterrows():
        prop = propriedades_especie(esp, args.fator_cisalhamento)
        for l_m in VAOS_M:
            cid = f"E{int(esp['id']):02d}_L{l_m:02d}_esp"
            casos.append(caso(t, cid, l_m, prop, sobol=args.sobol_especies))
            refs[cid] = {"bloco": "especie", "especie_id": int(esp["id"]), "especie": esp["nome"],
                         "classe": esp["classe_D"], "cenario": "esp", "vao_m": l_m,
                         "E_MPa": prop["e_mpa"], "id_classe": id_classe(esp["classe_D"], l_m)}

    df = bps.montar_planilha_casos(casos)
    colunas_ref = ["bloco", "especie_id", "especie", "classe", "cenario", "vao_m", "E_MPa", "id_classe"]
    for pos, col in enumerate(colunas_ref, start=1):
        df.insert(pos, f"cfg_ref_{col}", [refs[i][col] for i in df["id"]])

    # Aba de conferência: a matriz vão x classe com os ids
    matriz = pd.DataFrame(
        {classe: [id_classe(classe, l) for l in VAOS_M] for classe in CLASSES_NBR},
        index=pd.Index([f"{l} m" for l in VAOS_M], name="Vão"),
    )
    # Aba de conferência: espécies, classe e desvios em relação à classe
    especies = pd.DataFrame({
        "id": base["id"], "especie": base["nome"], "nome_cientifico": base["nome_cientifico"],
        "classe": base["classe_D"],
        "delta_f_pct": (100 * (base["f_c0_k_MPa"] / base["f_mk_classe_MPa"] - 1)).round(1),
        "delta_E_pct": (100 * (base["E_c0_m_MPa"] / base["E_c0_classe_MPa"] - 1)).round(1),
        "delta_rho_pct": (100 * (base["rho_ap_kgm3"] / base["rho_classe_kgm3"] - 1)).round(1),
    })

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(args.saida) as w:
        df.to_excel(w, index=False, sheet_name="Casos")
        matriz.to_excel(w, sheet_name="Matriz_vao_classe")
        especies.to_excel(w, index=False, sheet_name="Especies")

    n_cls = len(CLASSES_NBR) * len(VAOS_M)
    n_esp = len(df) - n_cls
    print(f"{args.saida.name}: {len(df)} casos")
    print(f"  base de classes : {n_cls} ({len(CLASSES_NBR)} classes x {len(VAOS_M)} vãos)")
    print(f"  espécies        : {n_esp} ({len(base)} espécies x {len(VAOS_M)} vãos, cenário esp)")
    print(f"  vãos            : {', '.join(f'{v} m' for v in VAOS_M)}")
    print(f"  NSGA-II         : pop {ALGORITMO.pop_size}, {ALGORITMO.n_gen} gerações, semente {ALGORITMO.seed} (execução única)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
