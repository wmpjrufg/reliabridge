"""Análise exploratória dos agrupamentos resistência--rigidez de Dias e Lahr (2004).

Os valores de f_c0,k e as classes D são lidos da planilha de conferência. Os valores
de E_c0,m foram transcritos da Tabela 5 do artigo-fonte. A análise é exploratória e
não propõe substituir a classificação normativa.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "tmp" / "fabricio_classificacao_D.xlsx"
FIG_PT = ROOT / "paper" / "engstruct" / "figuras"
FIG_EN = FIG_PT / "en"

CLASSES = ["D20", "D30", "D40", "D50", "D60"]
MARCADORES = ["o", "s", "^", "D", "v"]
CORES = ["#f2f2f2", "#d0d0d0", "#a6a6a6", "#737373", "#333333"]
COR_PRINCIPAL = "#000000"
CM = 1 / 2.54

EC0_MEDIO_MPA = np.array(
    [
        15940, 12587, 21263, 16695, 11990, 24081, 15375, 13813, 14185, 14613,
        17936, 11105, 13029, 9601, 8358, 10252, 23002, 14012, 14125, 18238,
        17718, 18717, 14027, 16214, 17398, 17443, 22967, 13536, 21900, 19274,
        14719, 17718, 21881, 13404, 8783, 14411, 20917, 19901, 18574, 10178,
    ],
    dtype=float,
)

ROTULOS = {
    "pt": {
        "x": r"Resistência característica, $f_{c0,k}$ (MPa)",
        "y": r"Módulo de elasticidade médio, $E_{c0,m}$ (MPa)",
        "classe": "Classe",
        "grupos": "Número de grupos, $k$",
        "silhueta": "Coeficiente de silhueta",
    },
    "en": {
        "x": r"Characteristic strength, $f_{c0,k}$ (MPa)",
        "y": r"Mean modulus of elasticity, $E_{c0,m}$ (MPa)",
        "classe": "Class",
        "grupos": "Number of clusters, $k$",
        "silhueta": "Silhouette coefficient",
    },
}


def configurar_estilo() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "mathtext.fontset": "stix",
            "axes.linewidth": 0.8,
            "figure.dpi": 120,
            "savefig.dpi": 300,
        }
    )


def estilizar_eixo(ax: plt.Axes, xlabel: str, ylabel: str) -> None:
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(axis="both", labelsize=8)
    ax.grid(True, linestyle="-", linewidth=0.45, color="gray", alpha=0.25)
    ax.set_axisbelow(True)


def gerar_figuras(
    data: pd.DataFrame,
    silhouettes_kmeans: list[float],
    idioma: str,
) -> None:
    rotulos = ROTULOS[idioma]
    configurar_estilo()
    destino = FIG_PT if idioma == "pt" else FIG_EN
    destino.mkdir(parents=True, exist_ok=True)

    fig, ax0 = plt.subplots(figsize=(8.6 * CM, 8.0 * CM))

    for classe, marcador, cor in zip(CLASSES, MARCADORES, CORES):
        grupo = data[data["Classe D (NBR 7190-3)"] == classe]
        ax0.scatter(
            grupo["fc0,k (MPa)"],
            grupo["E_c0,m (MPa)"],
            s=34,
            marker=marcador,
            facecolor=cor,
            edgecolor=COR_PRINCIPAL,
            linewidth=0.7,
            alpha=0.9,
            label=classe,
            zorder=3,
        )

    ax0.set_xlim(20, 100)
    ax0.set_ylim(7000, 28000)
    ax0.set_yticks([10000, 15000, 20000, 25000])
    estilizar_eixo(ax0, rotulos["x"], rotulos["y"])
    ax0.legend(
        fontsize=7.2,
        frameon=False,
        title=rotulos["classe"],
        title_fontsize=7.5,
        ncol=3,
        loc="upper left",
        handletextpad=0.45,
        columnspacing=0.8,
    )
    fig.tight_layout()
    fig.savefig(destino / "dispersao_resistencia_rigidez.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    fig, ax1 = plt.subplots(figsize=(8.6 * CM, 8.0 * CM))
    ks = np.arange(2, 9)
    ax1.plot(
        ks,
        silhouettes_kmeans,
        color=COR_PRINCIPAL,
        marker="o",
        markersize=4.5,
        linewidth=1.4,
    )
    ax1.scatter([2, 5], [silhouettes_kmeans[0], silhouettes_kmeans[3]],
                s=48, facecolor="white", edgecolor=COR_PRINCIPAL,
                linewidth=1.2, zorder=4)
    ax1.annotate(
        f"{silhouettes_kmeans[0]:.3f}".replace(".", "," if idioma == "pt" else "."),
        (2, silhouettes_kmeans[0]),
        xytext=(5, 7),
        textcoords="offset points",
        fontsize=7.5,
        color=COR_PRINCIPAL,
    )
    ax1.annotate(
        f"{silhouettes_kmeans[3]:.3f}".replace(".", "," if idioma == "pt" else "."),
        (5, silhouettes_kmeans[3]),
        xytext=(5, 7),
        textcoords="offset points",
        fontsize=7.5,
        color=COR_PRINCIPAL,
    )
    ax1.set_xticks(ks)
    ax1.set_ylim(0.40, 0.51)
    estilizar_eixo(ax1, rotulos["grupos"], rotulos["silhueta"])
    fig.tight_layout()
    fig.savefig(destino / "silhueta_kmeans.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    data = pd.read_excel(SOURCE)
    if len(data) != len(EC0_MEDIO_MPA):
        raise ValueError("A planilha e a transcrição de E_c0,m têm tamanhos distintos.")

    data["E_c0,m (MPa)"] = EC0_MEDIO_MPA
    features = data[["fc0,k (MPa)", "E_c0,m (MPa)"]].to_numpy()
    scaler = StandardScaler()
    standardized = scaler.fit_transform(features)

    print("Distribuição normativa")
    summary = data.groupby("Classe D (NBR 7190-3)")["IS"].agg(
        n="count", ids=lambda values: ", ".join(f"{value:02d}" for value in values)
    )
    print(summary.to_string())

    print("\nDiagnóstico do número de grupos")
    print("k  silhouette_kmeans  ARI_kmeans")
    silhouettes_kmeans = []
    for k in range(2, 9):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=100).fit(standardized)
        silhouette_kmeans = silhouette_score(standardized, kmeans.labels_)
        silhouettes_kmeans.append(silhouette_kmeans)
        print(
            f"{k}  {silhouette_kmeans:.3f}"
            f"            {adjusted_rand_score(data['Classe D (NBR 7190-3)'], kmeans.labels_):.3f}"
        )

    for k in (2, 5):
        selected = KMeans(n_clusters=k, random_state=42, n_init=100).fit(standardized)
        raw_centers = scaler.inverse_transform(selected.cluster_centers_)
        order = np.argsort(raw_centers[:, 0])
        ordered_label = {old: new + 1 for new, old in enumerate(order)}
        group_column = f"grupo_k{k}"
        data[group_column] = [ordered_label[label] for label in selected.labels_]
        centers = pd.DataFrame(
            raw_centers[order],
            columns=["f_c0,k (MPa)", "E_c0,m (MPa)"],
            index=pd.Index(range(1, k + 1), name=group_column),
        )

        print(f"\nCentros da solução com {k} grupos")
        print(centers.round(1).to_string())
        print(f"\nMembros da solução com {k} grupos")
        members = data.groupby(group_column).agg(
            n=("IS", "count"),
            ids=("IS", lambda values: ", ".join(f"{value:02d}" for value in values)),
            classes=(
                "Classe D (NBR 7190-3)",
                lambda values: ", ".join(
                    f"{label}:{count}"
                    for label, count in values.value_counts().sort_index().items()
                ),
            ),
        )
        print(members.to_string())

    for idioma in ("pt", "en"):
        gerar_figuras(data, silhouettes_kmeans, idioma)
    print(f"\nFiguras salvas em {FIG_PT.relative_to(ROOT)} e {FIG_EN.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
