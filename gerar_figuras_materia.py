"""Gera as figuras do Artigo 1 a partir do lote, em português e em inglês.

As figuras em português vão para `paper/materia/figuras/` e as em inglês para
`paper/materia/figuras/en/`, com os mesmos nomes de arquivo. Assim a versão em inglês do
artigo só precisa acrescentar `en/` ao `\\graphicspath`, sem mexer em nenhum `\\includegraphics`.

Quatro figuras são reproduzidas pelas mesmas funções da plataforma, a partir dos dados
gravados no lote; as outras quatro (utilização e os três ábacos) são montadas aqui.

Uso:
    .venv\\Scripts\\python.exe gerar_figuras_materia.py
"""

import io
import sys
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402
from madeiras import (  # noqa: E402
    fronteira_pareto,
    plot_boxplot_variaveis_fronteira,
    plot_convergencia_hipervolume,
    plot_sobol_total_indices,
    historico_hipervolume,
)

LOTE = RAIZ / "simulacaoes_" / "lote_eixos_1p5"
ROBUSTEZ = RAIZ / "simulacaoes_" / "custo_robustez_C13"
FIG_PT = RAIZ / "paper" / "materia" / "figuras"
FIG_EN = FIG_PT / "en"

NIVEIS_RHO = [("rho000", 0.0), ("rho025", 2.5), ("rho050", 5.0), ("rho100", 10.0)]

CLASSES = ["D20", "D30", "D40", "D50", "D60"]
VAOS = [3.0, 4.0, 5.0, 6.0]
MARCADORES = ["o", "s", "^", "D", "v"]
COR = "#1f4e79"
COR2 = "#c00000"
PREENCHE = "#dbeafe"
CM = 1 / 2.54

# Rótulos que a plataforma não fornece: os das figuras montadas aqui.
ROTULOS = {
    "pt": {
        "utilizacao_x": "Grau de utilização (%)",
        "limite": "limite normativo",
        "verificacoes": ["Flexão da longarina", "Cisalhamento da longarina",
                         "Flecha da longarina", "Flexão do tabuleiro"],
        "vao": "Vão teórico $L$ (m)",
        "volume": "Volume total de madeira, $V_{total}$ (m$^3$)",
        "consumo": "Consumo de madeira (m$^3$/m$^2$ de tabuleiro)",
        "diametro": "Diâmetro da longarina, $d$ (cm)",
        "classe": "Classe",
    },
    "en": {
        "utilizacao_x": "Utilisation ratio (%)",
        "limite": "code limit",
        "verificacoes": ["Girder bending", "Girder shear",
                         "Girder deflection", "Deck bending"],
        "vao": "Design span $L$ (m)",
        "volume": "Total timber volume, $V_{total}$ (m$^3$)",
        "consumo": "Timber consumption (m$^3$/m$^2$ of deck)",
        "diametro": "Girder diameter, $d$ (cm)",
        "classe": "Class",
    },
}

GCOLS = ["longarina_g_m", "longarina_g_v", "longarina_g_f", "tabuleiro_g_m"]


def membro(celula: str, nome: str):
    z = zipfile.ZipFile(LOTE / f"simulacao_{celula}" / "pre_sizing_package.zip")
    return io.BytesIO(z.read(nome))


def salvar(fig, nome: str, idioma: str, dpi: int = 300) -> None:
    destino = (FIG_PT if idioma == "pt" else FIG_EN) / nome
    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=dpi, bbox_inches="tight")
    plt.close(fig)


def estilo(ax, lx, ly):
    ax.set_xlabel(lx, fontsize=10)
    ax.set_ylabel(ly, fontsize=10)
    ax.tick_params(axis="both", labelsize=10)
    ax.grid(True, linestyle="-", linewidth=0.5, color="gray", alpha=0.3)
    ax.set_axisbelow(True)


def consolidar() -> pd.DataFrame:
    """Solução de menor volume de cada célula, com o que as figuras precisam."""
    linhas = []
    for i in range(1, 21):
        df = pd.read_excel(membro(f"C_{i:02d}", "pre_sizing_results_optimized.xlsx"))
        b = df.loc[df["of_volume_m3"].idxmin()]
        L = VAOS[(i - 1) // 5]
        linhas.append({"cel": f"C-{i:02d}", "L": L, "classe": CLASSES[(i - 1) % 5],
                       "V": b.of_volume_m3, "d": b.d_cm, "Vm2": b.of_volume_m3 / (L * 4.5)})
    return pd.DataFrame(linhas)


def figuras_da_plataforma(idioma: str) -> None:
    """Reproduz as quatro figuras que a plataforma gera, com os rótulos do idioma."""
    t = bps.textos(idioma)
    cel = "C_13"

    df = pd.read_excel(membro(cel, "pre_sizing_results_optimized.xlsx"))
    salvar(
        fronteira_pareto(df["of_volume_m3"].tolist(), df["of_fator_flecha"].tolist(),
                         t["tag_x_fig"], t["tag_y_fig"]),
        "pareto_frontier_C13.png", idioma)

    cols = ["d_cm", "bw_cm", "h_cm", "esp_cm", "esp_tab_cm"]
    salvar(
        plot_boxplot_variaveis_fronteira(df, cols, t["fronteira_variaveis_labels"],
                                         t["fronteira_variaveis_y"]),
        "boxplot_variaveis_C13.png", idioma)

    hist = pd.read_csv(membro(cel, "hypervolume_convergence.csv"))
    salvar(
        plot_convergencia_hipervolume({t["convergencia_serie"]: hist},
                                      label_x=t["convergencia_x"], label_y=t["convergencia_y"]),
        "convergencia_hv.png", idioma)

    sobol = pd.read_excel(membro(cel, "sobol_total_indices.xlsx"))
    salvar(
        plot_sobol_total_indices(sobol, label_x=t["sobol_axis_constraints"],
                                 label_y=t["sobol_axis_variables"],
                                 x_labels=t["sobol_constraint_labels"],
                                 y_labels=t["sobol_variable_labels"]),
        "sobol_heatmap_C13.png", idioma)


def figura_utilizacao(idioma: str) -> None:
    r = ROTULOS[idioma]
    df = pd.read_excel(membro("C_13", "pre_sizing_results_optimized.xlsx"))
    b = df.loc[df["of_volume_m3"].idxmin()]
    valores = [(1 + b[c]) * 100 for c in GCOLS][::-1]
    rotulos = r["verificacoes"][::-1]

    fig, ax = plt.subplots(figsize=(16 * CM, 8 * CM))
    ax.barh(rotulos, valores, color=PREENCHE, edgecolor=COR, height=0.55)
    ax.axvline(100, color=COR2, linewidth=1.2, linestyle="--")
    ax.text(98, 3.45, r["limite"], color=COR2, fontsize=9, ha="right", va="center")
    for y, v in enumerate(valores):
        ax.text(v + 1.5, y, f"{v:.1f}%", va="center", fontsize=9, color="black")
    ax.set_xlim(0, 118)
    ax.set_xticks(range(0, 101, 20))
    ax.set_ylim(-0.6, 3.8)
    estilo(ax, r["utilizacao_x"], "")
    fig.tight_layout()
    salvar(fig, "utilizacao_C13.png", idioma)


def abacos(M: pd.DataFrame, idioma: str) -> None:
    r = ROTULOS[idioma]
    for coluna, chave, nome in [("V", "volume", "abaco_volume_vs_vao.png"),
                                ("Vm2", "consumo", "abaco_volume_por_m2.png"),
                                ("d", "diametro", "abaco_diametro_vs_vao.png")]:
        fig, ax = plt.subplots(figsize=(13 * CM, 10 * CM))
        for k, (c, m) in enumerate(zip(CLASSES, MARCADORES)):
            s = M[M.classe == c].sort_values("L")
            ax.plot(s.L, s[coluna], marker=m, markersize=5, linewidth=1.3, label=c,
                    color=COR, alpha=0.35 + 0.65 * k / 4)
        estilo(ax, r["vao"], r[chave])
        ax.set_xticks([3, 4, 5, 6])
        ax.legend(fontsize=9, frameon=False, title=r["classe"], title_fontsize=9)
        fig.tight_layout()
        salvar(fig, nome, idioma)


def _fmt_rho(rho: float, idioma: str) -> str:
    s = f"{int(rho)}" if rho == int(rho) else f"{rho:.1f}"
    if idioma == "pt":
        s = s.replace(".", ",")
    return rf"$\rho$ = {s}%"


def figura_custo_robustez(idioma: str) -> None:
    """Sobrepõe as quatro fronteiras da célula C-13 (ρ = 0/2,5/5/10 %), §4.3.3."""
    t = bps.textos(idioma)
    fig, ax = plt.subplots(figsize=(13 * CM, 10 * CM))
    for k, (nome, rho) in enumerate(NIVEIS_RHO):
        z = zipfile.ZipFile(ROBUSTEZ / f"simulacao_{nome}" / "pre_sizing_package.zip")
        df = pd.read_excel(io.BytesIO(z.read("pre_sizing_results_optimized.xlsx")))
        ax.plot(df["of_volume_m3"], df["of_fator_flecha"], MARCADORES[k], markersize=4,
                color=COR, alpha=0.35 + 0.65 * k / 3, label=_fmt_rho(rho, idioma))
    estilo(ax, t["tag_x_fig"], t["tag_y_fig"])
    ax.legend(fontsize=9, frameon=False)
    fig.tight_layout()
    salvar(fig, "custo_robustez_C13.png", idioma)


def main() -> int:
    M = consolidar()
    tem_robustez = ROBUSTEZ.exists()
    for idioma in ("pt", "en"):
        figuras_da_plataforma(idioma)
        figura_utilizacao(idioma)
        abacos(M, idioma)
        if tem_robustez:
            figura_custo_robustez(idioma)
        destino = FIG_PT if idioma == "pt" else FIG_EN
        n = 9 if tem_robustez else 8
        print(f"{idioma}: {n} figuras em {destino.relative_to(RAIZ)}")
    if not tem_robustez:
        print(f"aviso: {ROBUSTEZ.relative_to(RAIZ)} não existe — custo_robustez_C13.png não gerada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
