"""Análise exploratória dos agrupamentos resistência--rigidez de Dias e Lahr (2004).

Os valores de f_c0,k e as classes D são lidos da planilha de conferência. Os valores
de E_c0,m foram transcritos da Tabela 5 do artigo-fonte. A análise é exploratória e
não propõe substituir a classificação normativa.
"""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "tmp" / "fabricio_classificacao_D.xlsx"

EC0_MEDIO_MPA = np.array(
    [
        15940, 12587, 21263, 16695, 11990, 24081, 15375, 13813, 14185, 14613,
        17936, 11105, 13029, 9601, 8358, 10252, 23002, 14012, 14125, 18238,
        17718, 18717, 14027, 16214, 17398, 17443, 22967, 13536, 21900, 19274,
        14719, 17718, 21881, 13404, 8783, 14411, 20917, 19901, 18574, 10178,
    ],
    dtype=float,
)


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
    print("k  silhouette_kmeans  silhouette_ward  ARI_kmeans  ARI_ward")
    for k in range(2, 9):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=100).fit(standardized)
        ward = AgglomerativeClustering(n_clusters=k, linkage="ward").fit_predict(
            standardized
        )
        print(
            f"{k}  {silhouette_score(standardized, kmeans.labels_):.3f}"
            f"              {silhouette_score(standardized, ward):.3f}"
            f"            {adjusted_rand_score(data['Classe D (NBR 7190-3)'], kmeans.labels_):.3f}"
            f"       {adjusted_rand_score(data['Classe D (NBR 7190-3)'], ward):.3f}"
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


if __name__ == "__main__":
    main()
