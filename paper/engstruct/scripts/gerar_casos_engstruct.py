"""Monta a planilha de casos da campanha do Artigo 2 (Engineering Structures).

Protocolo fechado com o autor em 2026-09-22:

1. O modulo comparado e o E_c0 nos dois lados. O cenario da especie usa o E_c0
   medido; o cenario da classe usa o E_c0,med tabelado pela ABNT NBR 7190-3:2022.
   Evita o fator de conversao alpha_E entre modulo de compressao e de flexao. O
   E_M0 medido, tambem disponivel na fonte, fica para analise de sensibilidade.
2. Dois experimentos por par especie-vao:
     principal (controlado)  troca somente a rigidez;
     secundario (pratico)    troca o conjunto completo de propriedades.
3. Vaos de 3, 5, 8 e 10 m. Robustez fixa em 5%.

Isso gera tres cenarios por par especie-vao, porque o membro "especie" e comum
aos dois experimentos:

    esp   propriedades medidas da especie             (R dos dois experimentos)
    rig   medidas, com o E_c0 substituido pelo da classe  (C do experimento principal)
    cls   propriedades da classe                      (C do experimento secundario)

    principal   esp x rig   isola a rigidez
    secundario  esp x cls   conjunto completo

Cada cenario e repetido com sementes pareadas, porque uma execucao unica por
condicao nao distingue efeito de material de ruido do NSGA-II entre execucoes.
As tres rodadas de um mesmo par especie-vao-semente compartilham configuracao e
semente, de modo que a diferenca observada venha das propriedades.

Resistencia caracteristica a flexao: f_m,k = f_c0,k nos dois cenarios, seguindo o
item 6.3.4 da ABNT NBR 7190-1:2022, ja adotado no Artigo 1. A especie entra com o
f_c0,k publicado por Dias e Rocco Lahr (2004), calculado pelo estimador de
estatistica de ordem da norma, e nao pela aproximacao 0,70 x media.

Uso:
    .venv\\Scripts\\python.exe paper\\engstruct\\scripts\\gerar_casos_engstruct.py
    .venv\\Scripts\\python.exe paper\\engstruct\\scripts\\gerar_casos_engstruct.py --sementes 10
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402

BASE_ESPECIES = RAIZ / "paper" / "engstruct" / "dados" / "base_especies.csv"

VAOS_M = [3.0, 5.0, 8.0, 10.0]

# Fator caracteristico do cisalhamento a partir da media publicada. A fonte so
# traz f_V0 medio. O valor 0,70 e o piso do estimador da ABNT NBR 7190-1:2022.
# [PENDENCIA] confirmar contra o texto integral da norma antes da submissao; a
# campanha do Artigo 1 mostrou o cisalhamento longe do limite (utilizacao maxima
# de 60%), entao este fator nao deve decidir nenhum dimensionamento.
FATOR_CISALHAMENTO = 0.70

# Parametros fixos, identicos aos do Artigo 1 exceto a faixa de vaos.
FIXOS = {
    "pista_cm": 450,
    "p_gk_kpa": 0.1,
    "p_rodak_kn": 40,
    "p_qk_kpa": 4,
    "a_m": 1.5,
    "classe_carregamento": "curta duração",
    "classe_madeira": "madeira natural",
    "classe_umidade": 3,
    "gamma_g": 1.30,
    "gamma_q": 1.50,
    "gamma_wc": 1.80,
    "gamma_wf": 1.40,
    "psi2": 0.30,
    "phi": 0.80,
    "robustez_pct": 5,
}


def montar_dados(t: dict, l_cm: float, densidade: float, f_mk: float,
                 f_vk: float, e_gpa: float) -> dict:
    """Monta o dicionario de entrada com as chaves e a ordem do `beam_data.xlsx`.

    Longarina e tabuleiro recebem as mesmas propriedades, como no Artigo 1.
    """
    return {
        t["entrada_comprimento"]: l_cm,
        t["pista"]: FIXOS["pista_cm"],
        # `t["tipo_secao_longarina"]` e a lista de opcoes do widget, nao um rotulo.
        # O cabecalho gravado no `beam_data.xlsx` e a representacao dessa lista,
        # literalmente "['Circular']". Reproduzido aqui para casar com o schema.
        f"{t['tipo_secao_longarina']}": "Circular",
        t["tipo_secao_tabuleiro"]: "Retangular",
        f"{t['carga_permanente']} (kPa)": FIXOS["p_gk_kpa"],
        f"{t['carga_roda']} (kN)": FIXOS["p_rodak_kn"],
        f"{t['carga_multidao']} (kPa)": FIXOS["p_qk_kpa"],
        f"{t['distancia_eixos']} (m)": FIXOS["a_m"],
        t["classe_carregamento"]: FIXOS["classe_carregamento"],
        t["classe_madeira"]: FIXOS["classe_madeira"],
        t["classe_umidade"]: FIXOS["classe_umidade"],
        t["gamma_g"]: FIXOS["gamma_g"],
        t["gamma_q"]: FIXOS["gamma_q"],
        t["gamma_wc"]: FIXOS["gamma_wc"],
        t["gamma_wf"]: FIXOS["gamma_wf"],
        t["psi2"]: FIXOS["psi2"],
        t["considerar_fluencia"]: FIXOS["phi"],
        t["percentual_robustez"]: FIXOS["robustez_pct"],
        f"{t['densidade_long']} (kg/m³)": densidade,
        f"{t['f_mk']} (MPa)": f_mk,
        f"{t['f_vk']} (MPa)": f_vk,
        f"{t['e_modflex']} (GPa)": e_gpa,
        f"{t['densidade_tab']} (kg/m³)": densidade,
        f"{t['f_mk_tab']} (MPa)": f_mk,
    }


def propriedades_por_cenario(esp: pd.Series, fator_cis: float) -> dict[str, dict]:
    """Devolve (densidade, f_mk, f_vk, E em GPa) de cada um dos tres cenarios."""
    f_vk_especie = round(esp["f_v0_m_MPa"] * fator_cis, 2)
    medidas = {
        "densidade": float(esp["rho_ap_kgm3"]),
        "f_mk": float(esp["f_c0_k_MPa"]),
        "f_vk": f_vk_especie,
        "e_gpa": round(float(esp["E_c0_m_MPa"]) / 1000.0, 3),
    }
    return {
        "esp": medidas,
        "rig": {**medidas, "e_gpa": round(float(esp["E_c0_classe_MPa"]) / 1000.0, 3)},
        "cls": {
            "densidade": float(esp["rho_classe_kgm3"]),
            "f_mk": float(esp["f_mk_classe_MPa"]),
            "f_vk": float(esp["f_v0k_classe_MPa"]),
            "e_gpa": round(float(esp["E_c0_classe_MPa"]) / 1000.0, 3),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--saida", default="engstruct_casos.xlsx")
    p.add_argument("--sementes", type=int, default=5,
                   help="sementes pareadas por cenario (padrao 5)")
    p.add_argument("--pop-size", type=int, default=50)
    p.add_argument("--n-gen", type=int, default=300)
    p.add_argument("--fator-cisalhamento", type=float, default=FATOR_CISALHAMENTO,
                   help="f_v0,k = fator x f_V0 medio da especie (padrao 0,70)")
    p.add_argument("--sobol", action="store_true",
                   help="liga a analise de Sobol (desligada por padrao: sao centenas de rodadas)")
    p.add_argument("--forcar", action="store_true", help="sobrescreve a planilha existente")
    args = p.parse_args()

    saida = Path(args.saida)
    if not saida.is_absolute():
        saida = RAIZ / saida
    if saida.exists() and not args.forcar:
        print(f"{saida.name} ja existe. Use --forcar para regerar.", file=sys.stderr)
        return 1
    if not BASE_ESPECIES.exists():
        print(f"base nao encontrada: {BASE_ESPECIES}\n"
              "Rode antes: paper/engstruct/scripts/gerar_base_especies.py", file=sys.stderr)
        return 1

    base = pd.read_csv(BASE_ESPECIES)
    t = bps.textos("pt")
    casos, referencias = [], {}

    for _, esp in base.iterrows():
        cenarios = propriedades_por_cenario(esp, args.fator_cisalhamento)
        for l_m in VAOS_M:
            for cenario, prop in cenarios.items():
                for semente in range(1, args.sementes + 1):
                    caso_id = f"E{int(esp['id']):02d}_L{int(l_m):02d}_{cenario}_s{semente}"
                    casos.append(
                        bps.CasoBatch(
                            id=caso_id,
                            dados=montar_dados(
                                t, l_m * 100, prop["densidade"], prop["f_mk"],
                                prop["f_vk"], prop["e_gpa"],
                            ),
                            algoritmo=bps.ParametrosAlgoritmo(
                                pop_size=args.pop_size,
                                n_gen=args.n_gen,
                                n_checagens=5,
                                seed=semente,
                            ),
                            sobol=bps.ConfigSobol(ativo=args.sobol),
                        )
                    )
                    referencias[caso_id] = {
                        "cfg_ref_especie_id": int(esp["id"]),
                        "cfg_ref_especie": esp["nome"],
                        "cfg_ref_classe": esp["classe_D"],
                        "cfg_ref_cenario": cenario,
                        "cfg_ref_vao_m": int(l_m),
                        "cfg_ref_semente": semente,
                        "cfg_ref_E_MPa": round(prop["e_gpa"] * 1000, 1),
                    }

    df = bps.montar_planilha_casos(casos)
    for pos, coluna in enumerate(
        ["cfg_ref_especie_id", "cfg_ref_especie", "cfg_ref_classe", "cfg_ref_cenario",
         "cfg_ref_vao_m", "cfg_ref_semente", "cfg_ref_E_MPa"], start=1
    ):
        df.insert(pos, coluna, [referencias[i][coluna] for i in df["id"]])

    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(saida, index=False, sheet_name="Casos")

    n_esp = len(base)
    print(f"{saida.relative_to(RAIZ)}: {len(df)} casos")
    print(f"  {n_esp} especies x {len(VAOS_M)} vaos x 3 cenarios x {args.sementes} sementes")
    print(f"  vaos     : {', '.join(f'{v:.0f} m' for v in VAOS_M)}")
    print(f"  robustez : {FIXOS['robustez_pct']}%")
    print(f"  NSGA-II  : pop {args.pop_size}, {args.n_gen} geracoes, sementes 1 a {args.sementes}")
    print(f"  Sobol    : {'ligada' if args.sobol else 'desligada'}")
    print("\n  pares de comparacao montados a partir desses cenarios:")
    print(f"    principal  esp x rig : {n_esp * len(VAOS_M) * args.sementes} pares (so a rigidez muda)")
    print(f"    secundario esp x cls : {n_esp * len(VAOS_M) * args.sementes} pares (conjunto completo)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
