"""Monta a planilha de casos do Artigo 2 (Engineering Structures).

A matriz é 40 espécies x 4 vãos x 2 bases de propriedades = 320 rodadas, conforme o
protocolo de comparação da Seção 3 daquele artigo:

  base "esp"  projeto pela espécie, com as propriedades medidas;
  base "cls"  projeto pela classe da NBR 7190-3 em que a espécie foi enquadrada.

As duas rodadas de um mesmo par espécie-vão usam configuração e semente idênticas, de
modo que a diferença de volume seja atribuível só às propriedades do material.

Uso:
    .venv\\Scripts\\python.exe gerar_casos_engstruct.py
    .venv\\Scripts\\python.exe gerar_casos_engstruct.py --fator-e 0.90   # ver C-02
"""

import argparse
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402

TABELA_ESPECIES = RAIZ / "paper" / "engstruct" / "tabelas" / "tab_especies.tex"

VAOS_M = [3.0, 5.0, 8.0, 10.0]

# Conversão média -> característico declarada no cabeçalho de tab_especies.tex.
FATOR_FLEXAO = 0.70
FATOR_CISALHAMENTO = 0.54

# Classes da NBR 7190-3, iguais às da tabela de classes do Artigo 1.
# (densidade kg/m³, f_mk MPa, f_v0k MPa, E GPa)
CLASSES = {
    "D20": (500, 25.97, 4, 10.0),
    "D30": (625, 38.96, 5, 12.0),
    "D40": (750, 51.95, 6, 14.5),
    "D50": (850, 64.94, 7, 16.5),
    "D60": (1000, 77.92, 8, 19.5),
}

# Parâmetros fixos. Por decisão do autor, são os mesmos do Artigo 1: a única coisa que
# muda entre os dois estudos é a faixa de vãos, para que a comparação entre eles seja
# direta. A tabela `tab:vaos` de 03_methodology.tex foi corrigida para bater com isto.
FIXOS = {
    "pista_cm": 450,
    "p_gk_kpa": 0.1,
    "p_rodak_kn": 40,
    "p_qk_kpa": 4,
    "a_m": 1.5,
    "classe_carregamento": "média duração",
    "classe_madeira": "madeira natural",
    "classe_umidade": 3,
    "gamma_g": 1.35,
    "gamma_q": 1.50,
    "gamma_wc": 1.80,
    "gamma_wf": 1.40,
    "psi2": 0.30,
    "phi": 0.60,
    "robustez_pct": 5,
}


def _num(txt: str) -> float:
    return float(txt.strip().replace(".", "").replace(",", "."))


def ler_especies(caminho: Path = TABELA_ESPECIES) -> list[dict]:
    """Extrai as 40 espécies de `tab_especies.tex`.

    A tabela traz valores médios; os característicos saem pelos fatores declarados no
    cabeçalho dela. `E_M0` é o módulo de elasticidade medido **na flexão**, que é o que o
    modelo pede em `e_modflex_long`.
    """
    especies = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not re.match(r"^\d{2}\s*&", linha):
            continue
        c = [x.strip() for x in linha.rstrip("\\").split("&")]
        especies.append(
            {
                "n": int(c[0]),
                "nome": c[1],
                "cientifico": re.sub(r"\\textit\{(.*?)\}", r"\1", c[2]),
                "densidade": _num(c[3]),
                "f_c0m": _num(c[4]),
                "f_c0k": _num(c[5]),
                "f_mm": _num(c[6]),
                "f_v0m": _num(c[7]),
                "e_mpa": _num(c[8]),
                "classe": c[9].strip(),
            }
        )
    if len(especies) != 40:
        raise ValueError(f"Esperava 40 especies em {caminho.name}, li {len(especies)}.")
    return especies


def montar_dados(t, l_cm, densidade, f_mk, f_vk, e_gpa) -> dict:
    """Monta o dicionário de entrada com as chaves e a ordem do `beam_data.xlsx`.

    Longarina e tabuleiro recebem as mesmas propriedades, como no Artigo 1.
    """
    return {
        t["entrada_comprimento"]: l_cm,
        t["pista"]: FIXOS["pista_cm"],
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


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    p.add_argument("--saida", default="engstruct_casos.xlsx")
    p.add_argument(
        "--sobol",
        action="store_true",
        help="liga a analise de Sobol (desligada por padrao: sao 320 rodadas)",
    )
    p.add_argument(
        "--fator-e",
        type=float,
        default=1.0,
        metavar="F",
        help="multiplica o E medido das especies, para a conversao flexao->compressao em "
        "aberto no item C-02 da revisao critica (padrao 1,0, sem conversao)",
    )
    args = p.parse_args()

    saida = Path(args.saida)
    if saida.exists():
        print(f"{saida.name} ja existe - apague antes se quiser regerar.", file=sys.stderr)
        return 1

    t = bps.textos("pt")
    especies = ler_especies()
    casos, referencias = [], {}

    for esp in especies:
        dens_c, fmk_c, fvk_c, e_c = CLASSES[esp["classe"]]
        for l_m in VAOS_M:
            propriedades = {
                "esp": (
                    esp["densidade"],
                    round(esp["f_mm"] * FATOR_FLEXAO, 2),
                    round(esp["f_v0m"] * FATOR_CISALHAMENTO, 2),
                    round(esp["e_mpa"] * args.fator_e / 1000.0, 3),
                ),
                "cls": (dens_c, fmk_c, fvk_c, e_c),
            }
            for base, (dens, fmk, fvk, e_gpa) in propriedades.items():
                caso_id = f"E{esp['n']:02d}_L{int(l_m):02d}_{base}"
                casos.append(
                    bps.CasoBatch(
                        id=caso_id,
                        dados=montar_dados(t, l_m * 100, dens, fmk, fvk, e_gpa),
                        sobol=bps.ConfigSobol(ativo=args.sobol),
                    )
                )
                referencias[caso_id] = (esp["nome"], esp["classe"], base, int(l_m))

    df = bps.montar_planilha_casos(casos)

    # Colunas de rastreabilidade, para achar a espécie sem abrir o .tex. Não entram no
    # cálculo porque `ler_planilha_casos` só trata como dados o que não começa com cfg_,
    # então elas precisam do prefixo.
    for pos, (nome, indice) in enumerate(
        [("cfg_ref_especie", 0), ("cfg_ref_classe", 1), ("cfg_ref_base", 2), ("cfg_ref_vao_m", 3)],
        start=1,
    ):
        df.insert(pos, nome, [referencias[i][indice] for i in df["id"]])

    df.to_excel(saida, index=False, sheet_name="Casos")

    print(
        f"{saida.name}: {len(df)} casos "
        f"({len(especies)} especies x {len(VAOS_M)} vaos x 2 bases)"
    )
    print("vaos       :", ", ".join(f"{v:.0f} m" for v in VAOS_M))
    print("Sobol      :", "ligada" if args.sobol else "desligada")
    print("fator do E :", args.fator_e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
