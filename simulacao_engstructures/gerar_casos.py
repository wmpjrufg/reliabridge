"""Monta a planilha de casos da campanha do Artigo 2 (Engineering Structures).

Mesma receita da campanha da Revista Matéria: NSGA-II com população 50, 300 gerações,
robustez de 5% no diâmetro e os mesmos limites de busca, exceto o teto do espaçamento entre
longarinas, ampliado de 200 para 250 cm. As outras diferenças são a faixa de vãos, de 3 a
10 m em passo de 1 m, o bloco de espécies e as sementes.

Sementes: cada caso é executado com N sementes (padrão 5). O consolidar.py fica com a
solução de menor volume entre as sementes de cada caso e reporta a dispersão entre elas.
Como todas as sementes buscam no mesmo domínio, o menor volume está sempre mais perto do
ótimo que qualquer execução isolada. Motivo: no teste com o teto de 250 cm, a execução
única de CLS_D40_L05 parou 2,2% acima do volume já conhecido (5,203 contra 5,090 m³), um
erro de otimização da mesma ordem dos efeitos que o artigo quer medir. Num teste com 8
sementes em 4 casos, ficar com o menor volume de 3 sementes deixou até 1,8% de distância do
melhor das 8; com 5 sementes, até 0,9% (em média, 0,1%). Por isso o padrão é 5.

A planilha tem dois blocos (ids com sufixo _s1, _s2, ... para a semente):

    CLS  base de classes: 5 classes (D20 a D60) x 8 vãos = 40 casos por semente.
         É a matriz vão x classe, como a da Matéria, e também o cenário "cls" de todas as
         espécies: as propriedades da classe não dependem da espécie, então rodar "cls"
         por espécie repetiria o mesmo caso. Sobol só na semente 1.

    E    bloco de espécies: 40 espécies x 8 vãos = 320 casos por semente, cenário esp
         (propriedades medidas da espécie).

Comparação montada depois, no consolidar.py:
    esp x CLS  decisão de projeto real (espécie contra classe)

Só entram cenários que existem como decisão de projeto: projetar pela espécie ou pela
classe. Cenários híbridos (espécie com o E da classe, por exemplo) foram retirados.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\gerar_casos.py --forcar
    .venv\\Scripts\\python.exe simulacao_engstructures\\gerar_casos.py --sementes 5 --forcar
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

SAIDA_PADRAO = PASTA / "casos_engstruct.xlsx"

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

# Idêntico à Matéria (batch_pre_sizing_casos_materia.xlsx), com a semente variando.
POP_SIZE, N_GEN, N_CHECAGENS = 50, 300, 30

# Limites de busca, em cm. Iguais aos da Matéria, exceto esp_long: na primeira rodada
# (teto de 200 cm) cinco soluções de espécie em 6 e 8 m encostaram no teto. O mesmo valor
# limita o espaçamento corrigido na restrição g5 (madeiras.restringir_espaco), então ampliar
# o teto amplia também o espaçamento admissível da ponte construída.
ESP_LONG_MAX_CM = 250.0
LIMITES = bps.LimitesBusca(esp_long=(30.0, ESP_LONG_MAX_CM))  # d 20-100, bw 20-50, h 5-15, esp_tab 2-5


def id_classe(classe: str, l_m: int) -> str:
    """Id base (sem semente) do caso de classe."""
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


def caso(t: dict, caso_id: str, l_m: int, prop: dict, semente: int, sobol: bool) -> bps.CasoBatch:
    return bps.CasoBatch(
        id=caso_id,
        dados=montar_dados(t, l_m * 100, prop["densidade"], prop["f_mk"],
                           prop["f_vk"], round(prop["e_mpa"] / 1000.0, 3)),
        limites=LIMITES,
        algoritmo=bps.ParametrosAlgoritmo(pop_size=POP_SIZE, n_gen=N_GEN,
                                          n_checagens=N_CHECAGENS, seed=semente),
        sobol=bps.ConfigSobol(ativo=sobol),
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--sementes", type=int, default=5, help="sementes por caso (padrão 5)")
    p.add_argument("--fator-cisalhamento", type=float, default=FATOR_CISALHAMENTO)
    p.add_argument("--sobol-especies", action="store_true",
                   help="liga Sobol também no bloco de espécies (semente 1)")
    p.add_argument("--forcar", action="store_true", help="sobrescreve a planilha existente")
    args = p.parse_args()

    if args.saida.exists() and not args.forcar:
        print(f"{args.saida.name} já existe. Use --forcar para regerar.", file=sys.stderr)
        return 1
    sementes = list(range(1, args.sementes + 1))

    base = pd.read_csv(BASE_ESPECIES)
    conferir_classes(base)
    t = bps.textos("pt")
    casos, refs = [], {}

    # Bloco CLS: matriz vão x classe
    for classe, prop in CLASSES_NBR.items():
        for l_m in VAOS_M:
            base_id = id_classe(classe, l_m)
            for s in sementes:
                cid = f"{base_id}_s{s}"
                casos.append(caso(t, cid, l_m, prop, s, sobol=(s == 1)))
                refs[cid] = {"caso_base": base_id, "semente": s, "bloco": "classe",
                             "especie_id": None, "especie": None, "classe": classe,
                             "cenario": "cls", "vao_m": l_m, "E_MPa": prop["e_mpa"],
                             "id_classe": base_id}

    # Bloco E: espécies
    for _, esp in base.iterrows():
        prop = propriedades_especie(esp, args.fator_cisalhamento)
        for l_m in VAOS_M:
            base_id = f"E{int(esp['id']):02d}_L{l_m:02d}_esp"
            for s in sementes:
                cid = f"{base_id}_s{s}"
                casos.append(caso(t, cid, l_m, prop, s, sobol=(args.sobol_especies and s == 1)))
                refs[cid] = {"caso_base": base_id, "semente": s, "bloco": "especie",
                             "especie_id": int(esp["id"]), "especie": esp["nome"],
                             "classe": esp["classe_D"], "cenario": "esp", "vao_m": l_m,
                             "E_MPa": prop["e_mpa"], "id_classe": id_classe(esp["classe_D"], l_m)}

    df = bps.montar_planilha_casos(casos)
    colunas_ref = ["caso_base", "semente", "bloco", "especie_id", "especie", "classe",
                   "cenario", "vao_m", "E_MPa", "id_classe"]
    for pos, col in enumerate(colunas_ref, start=1):
        df.insert(pos, f"cfg_ref_{col}", [refs[i][col] for i in df["id"]])

    # Aba de conferência: a matriz vão x classe com os ids base
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
    n_esp = len(base) * len(VAOS_M)
    print(f"{args.saida.name}: {len(df)} execuções ({n_cls + n_esp} casos x {len(sementes)} sementes)")
    print(f"  base de classes : {n_cls} casos ({len(CLASSES_NBR)} classes x {len(VAOS_M)} vãos)")
    print(f"  espécies        : {n_esp} casos ({len(base)} espécies x {len(VAOS_M)} vãos, cenário esp)")
    print(f"  vãos            : {', '.join(f'{v} m' for v in VAOS_M)}")
    print(f"  limites (cm)    : d {LIMITES.d}, bw {LIMITES.bw}, h {LIMITES.h}, "
          f"esp_long {LIMITES.esp_long}, esp_tab {LIMITES.esp_tab}")
    print(f"  NSGA-II         : pop {POP_SIZE}, {N_GEN} gerações, sementes {sementes[0]} a {sementes[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
