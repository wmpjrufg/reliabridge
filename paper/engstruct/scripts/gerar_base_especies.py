"""Extrai a base experimental das 40 especies de Dias e Rocco Lahr (2004).

Fonte: `artigo_fabricio.md` na raiz do repositorio, transcricao do artigo
Scientia Forestalis n.65, p.102-113. As tabelas lidas sao:

    Tabela 1  nome vulgar e nome cientifico
    Tabela 3  f_c0,k publicado (estimador de estatistica de ordem da norma)
    Tabela 4  densidade aparente, f_c0 medio, f_V0 medio
    Tabela 5  f_M medio, E_c0 medio, E_M0 medio

Saida: `paper/engstruct/dados/base_especies.csv`, uma linha por especie, com a
origem de cada coluna registrada em `base_especies_metadados.csv`.

O enquadramento em classe usa o f_c0,k publicado, nao a aproximacao 0,70 x media:
o proprio artigo-fonte ja aplica o estimador da norma. Duas especies apresentam
f_c0,k acima da media amostral (Champanhe e Oiticica-amarela); isso nao e erro,
porque o estimador impoe piso e nao teto.

Uso:
    .venv\\Scripts\\python.exe paper\\engstruct\\scripts\\gerar_base_especies.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[3]
FONTE = RAIZ / "artigo_fabricio.md"
SAIDA_DIR = RAIZ / "paper" / "engstruct" / "dados"

# Classes de folhosas da ABNT NBR 7190-3:2022.
# f_m,k = f_c0,k segue o item 6.3.4 da ABNT NBR 7190-1:2022, mesma convencao
# adotada no Artigo 1 (Materia) e implementada em `madeiras.py`.
CLASSES_D = {
    "D20": {"f_c0k": 20.0, "f_mk": 20.0, "f_v0k": 4.0, "E_c0med": 10000.0, "rho": 500.0},
    "D30": {"f_c0k": 30.0, "f_mk": 30.0, "f_v0k": 5.0, "E_c0med": 12000.0, "rho": 625.0},
    "D40": {"f_c0k": 40.0, "f_mk": 40.0, "f_v0k": 6.0, "E_c0med": 14500.0, "rho": 750.0},
    "D50": {"f_c0k": 50.0, "f_mk": 50.0, "f_v0k": 7.0, "E_c0med": 16500.0, "rho": 850.0},
    "D60": {"f_c0k": 60.0, "f_mk": 60.0, "f_v0k": 8.0, "E_c0med": 19500.0, "rho": 1000.0},
}


def _num(txt: str) -> float | None:
    """Converte '14\\,947', '1.103' ou '4,5' em float. Retorna None para '*'."""
    txt = txt.strip().replace("\\,", "").replace(" ", "").replace(" ", "")
    if txt in {"", "*", "-", "--"}:
        return None
    # Milhar com ponto so aparece em numeros >= 4 digitos sem virdula decimal.
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    return float(txt)


def _linhas_tabela(texto: str, marcador: str) -> list[list[str]]:
    """Devolve as celulas das linhas de dados da tabela markdown apos `marcador`."""
    inicio = texto.index(marcador)
    fim = texto.find("**Tabela", inicio + len(marcador))
    bloco = texto[inicio : fim if fim != -1 else len(texto)]

    linhas = []
    for linha in bloco.splitlines():
        linha = linha.strip()
        if not linha.startswith("|"):
            continue
        celulas = [c.strip() for c in linha.strip("|").split("|")]
        # Descarta cabecalho e separador (':---:' etc.). A transcricao do PDF traz
        # ruido de OCR na coluna de numero (a especie 32 aparece como ",32" na
        # Tabela 4), entao a identificacao tolera pontuacao em volta do digito.
        if not re.fullmatch(r"[^\w]*\d{1,2}[^\w]*", celulas[0]):
            continue
        celulas[0] = re.sub(r"\D", "", celulas[0])
        linhas.append(celulas)
    return linhas


def classificar(f_c0k: float) -> str:
    """Maior classe D cujo f_c0,k nao supera o caracteristico da especie."""
    elegiveis = [c for c, v in CLASSES_D.items() if v["f_c0k"] <= f_c0k]
    if not elegiveis:
        raise ValueError(f"f_c0,k = {f_c0k} MPa fica abaixo da classe D20.")
    return max(elegiveis, key=lambda c: CLASSES_D[c]["f_c0k"])


def main() -> int:
    if not FONTE.exists():
        print(f"fonte nao encontrada: {FONTE}", file=sys.stderr)
        return 1
    texto = FONTE.read_text(encoding="utf-8")

    # Tabela 1: numero, nome vulgar, nome cientifico.
    nomes: dict[int, tuple[str, str]] = {}
    for c in _linhas_tabela(texto, "**Tabela 1**"):
        n = int(c[0])
        cientifico = re.sub(r"\*(.*?)\*", r"\1", c[2]).strip()
        nomes[n] = (c[1].strip(), cientifico)

    # Tabela 3: layout de duas metades lado a lado (n, f_c0k, CR, n, f_c0k, CR).
    caracteristicos: dict[int, float] = {}
    classes_historicas: dict[int, str] = {}
    for c in _linhas_tabela(texto, "**Tabela 3**"):
        for base in (0, 3):
            if len(c) < base + 3 or not re.match(r"^\d{1,2}$", c[base]):
                continue
            n = int(c[base])
            caracteristicos[n] = _num(c[base + 1])
            classes_historicas[n] = c[base + 2].strip()

    # Tabela 4: densidade aparente, f_c0 medio e f_V0 medio.
    fisicas: dict[int, dict] = {}
    for c in _linhas_tabela(texto, "**Tabela 4**"):
        fisicas[int(c[0])] = {
            "rho_ap_kgm3": _num(c[1]),
            "f_c0_m_MPa": _num(c[4]),
            "f_v0_m_MPa": _num(c[7]),
        }

    # Tabela 5: f_M medio, E_c0 medio e E_M0 medio.
    mecanicas: dict[int, dict] = {}
    for c in _linhas_tabela(texto, "**Tabela 5**"):
        mecanicas[int(c[0])] = {
            "f_M_m_MPa": _num(c[1]),
            "E_c0_m_MPa": _num(c[2]),
            "E_M0_m_MPa": _num(c[4]),
        }

    for rotulo, d in [
        ("Tabela 1", nomes),
        ("Tabela 3", caracteristicos),
        ("Tabela 4", fisicas),
        ("Tabela 5", mecanicas),
    ]:
        if len(d) != 40:
            print(f"{rotulo}: li {len(d)} especies, esperava 40.", file=sys.stderr)
            return 1

    registros = []
    for n in range(1, 41):
        f_c0k = caracteristicos[n]
        classe = classificar(f_c0k)
        registros.append(
            {
                "id": n,
                "nome": nomes[n][0],
                "nome_cientifico": nomes[n][1],
                "rho_ap_kgm3": fisicas[n]["rho_ap_kgm3"],
                "f_c0_m_MPa": fisicas[n]["f_c0_m_MPa"],
                "f_c0_k_MPa": f_c0k,
                "f_M_m_MPa": mecanicas[n]["f_M_m_MPa"],
                "f_v0_m_MPa": fisicas[n]["f_v0_m_MPa"],
                "E_c0_m_MPa": mecanicas[n]["E_c0_m_MPa"],
                "E_M0_m_MPa": mecanicas[n]["E_M0_m_MPa"],
                "classe_D": classe,
                "classe_historica_C": classes_historicas[n],
                "E_c0_classe_MPa": CLASSES_D[classe]["E_c0med"],
                "rho_classe_kgm3": CLASSES_D[classe]["rho"],
                "f_mk_classe_MPa": CLASSES_D[classe]["f_mk"],
                "f_v0k_classe_MPa": CLASSES_D[classe]["f_v0k"],
            }
        )

    df = pd.DataFrame(registros).sort_values("id").reset_index(drop=True)
    df["razao_E_M0_E_c0"] = (df["E_M0_m_MPa"] / df["E_c0_m_MPa"]).round(4)
    df["desvio_E_vs_classe_pct"] = (
        (df["E_c0_m_MPa"] / df["E_c0_classe_MPa"] - 1) * 100
    ).round(2)

    SAIDA_DIR.mkdir(parents=True, exist_ok=True)
    destino = SAIDA_DIR / "base_especies.csv"
    df.to_csv(destino, index=False, encoding="utf-8")

    metadados = pd.DataFrame(
        [
            ("id", "Tabela 1", "medida", "numero da especie na fonte"),
            ("nome", "Tabela 1", "medida", "nome vulgar"),
            ("nome_cientifico", "Tabela 1", "medida", "nome cientifico"),
            ("rho_ap_kgm3", "Tabela 4", "medida", "densidade aparente a 12% de umidade"),
            ("f_c0_m_MPa", "Tabela 4", "medida", "compressao paralela, valor medio"),
            ("f_c0_k_MPa", "Tabela 3", "medida", "compressao paralela, caracteristico publicado"),
            ("f_M_m_MPa", "Tabela 5", "medida", "flexao, valor medio"),
            ("f_v0_m_MPa", "Tabela 4", "medida", "cisalhamento, valor medio"),
            ("E_c0_m_MPa", "Tabela 5", "medida", "modulo na compressao paralela, medio"),
            ("E_M0_m_MPa", "Tabela 5", "medida", "modulo na flexao estatica, medio"),
            ("classe_D", "derivada", "calculada", "maior classe D com f_c0,k <= caracteristico"),
            ("classe_historica_C", "Tabela 3", "medida", "classe C da NBR 7190:1997 publicada"),
            ("E_c0_classe_MPa", "NBR 7190-3:2022", "normativa", "E_c0,med da classe"),
            ("rho_classe_kgm3", "NBR 7190-3:2022", "normativa", "densidade da classe"),
            ("f_mk_classe_MPa", "NBR 7190-1:2022", "normativa", "f_m,k = f_c0,k, item 6.3.4"),
            ("f_v0k_classe_MPa", "NBR 7190-3:2022", "normativa", "f_v0,k da classe"),
            ("razao_E_M0_E_c0", "derivada", "calculada", "razao entre os dois modulos medidos"),
            ("desvio_E_vs_classe_pct", "derivada", "calculada", "E_c0 medido contra E_c0 da classe"),
        ],
        columns=["coluna", "origem", "natureza", "descricao"],
    )
    metadados.to_csv(SAIDA_DIR / "base_especies_metadados.csv", index=False, encoding="utf-8")

    print(f"{destino.relative_to(RAIZ)}: {len(df)} especies")
    print("\ndistribuicao por classe D:")
    for classe, n in df["classe_D"].value_counts().sort_index().items():
        print(f"  {classe}: {n:2d}")
    print(f"\nrazao E_M0/E_c0: media {df['razao_E_M0_E_c0'].mean():.3f}, "
          f"faixa {df['razao_E_M0_E_c0'].min():.3f} a {df['razao_E_M0_E_c0'].max():.3f}")
    print(f"desvio do E medido contra a classe: "
          f"{df['desvio_E_vs_classe_pct'].min():+.1f}% a "
          f"{df['desvio_E_vs_classe_pct'].max():+.1f}%")
    anomalas = df[df["f_c0_k_MPa"] > df["f_c0_m_MPa"]]
    if len(anomalas):
        print("\nf_c0,k acima da media amostral (esperado, o estimador so impoe piso):")
        for _, r in anomalas.iterrows():
            print(f"  {r['nome']}: {r['f_c0_k_MPa']} > {r['f_c0_m_MPa']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
