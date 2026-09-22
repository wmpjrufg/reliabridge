"""Consolida os resultados da campanha de semente única do Artigo 2 em uma planilha só.

Lê cada resultados/simulacao_<id>/pre_sizing_results_optimized.xlsx, extrai a solução de
menor volume da fronteira (a mesma leitura da Matéria) e grava consolidado.xlsx com:

    Casos             uma linha por caso: dimensões, volume, utilizações e verificação governante
    Matriz_volume     V_min da base de classes, vão x classe
    Matriz_governante verificação governante da base de classes, vão x classe
    Conferencia_Materia  CLS de 3 a 6 m contra os volumes publicados na Matéria
    Pares             por espécie e vão: esp x CLS (projetar pela espécie ou pela classe)

Na aba Pares, U_flecha_CtoR_est é a utilização de flecha do projeto da classe reavaliado com
o E da espécie, estimada por U_cls x E_cls / E_esp. A escala é exata para a rigidez com a
geometria fixa, mas ignora a troca de densidade (peso próprio); por isso o sufixo _est.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\consolidar.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
PLANILHA = PASTA / "casos_engstruct_semente1.xlsx"
RESULTADOS = PASTA / "resultados"
SAIDA = PASTA / "consolidado.xlsx"

GCOLS = {
    "longarina_g_m": "Flexão long.",
    "longarina_g_v": "Cisalhamento long.",
    "longarina_g_f": "Flecha long.",
    "tabuleiro_g_m": "Flexão tab.",
}

# Intervalos de busca (LimitesBusca padrão, iguais aos da Matéria), para sinalizar
# soluções encostadas no limite: nesses casos o volume é condicionado pelo intervalo.
LIMITES = [
    ("d", "d_cm", (20.0, 100.0)),
    ("bw", "bw_cm", (20.0, 50.0)),
    ("h", "h_cm", (5.0, 15.0)),
    ("esp_long", "esp_cm", (30.0, 200.0)),
    ("esp_tab", "esp_tab_cm", (2.0, 5.0)),
]

# Tabela de resultados consolidados da Matéria (solução de menor volume, m³).
MATERIA_V = {
    3: {"D20": 2.988, "D30": 2.464, "D40": 2.154, "D50": 1.903, "D60": 1.745},
    4: {"D20": 5.089, "D30": 4.076, "D40": 3.695, "D50": 3.163, "D60": 2.845},
    5: {"D20": 7.331, "D30": 6.001, "D40": 5.090, "D50": 4.562, "D60": 4.084},
    6: {"D20": 9.978, "D30": 7.907, "D40": 6.771, "D50": 6.015, "D60": 5.632},
}


def ler_solucao(pasta: Path) -> dict | None:
    arq = pasta / "pre_sizing_results_optimized.xlsx"
    if not arq.exists():
        return None
    df = pd.read_excel(arq).dropna(subset=["d_cm"])
    if df.empty:
        return None
    s = df.loc[df["of_volume_m3"].idxmin()]
    util = {f"U_{k.replace('_g_', '_')}": 1.0 + float(s[k]) for k in GCOLS}
    gov = max(GCOLS, key=lambda k: float(s[k]))
    return {
        "d_cm": s["d_cm"], "bw_cm": s["bw_cm"], "h_cm": s["h_cm"],
        "esp_long_cm": s["esp_cm"], "esp_tab_cm": s["esp_tab_cm"],
        "V_m3": float(s["of_volume_m3"]), "f2_flecha": float(s["of_fator_flecha"]),
        **util,
        "g_max": float(s[gov]), "governante": GCOLS[gov],
        "g_esp_long": float(s["longarina_g_esp"]), "g_esp_tab": float(s["tabuleiro_g_esp"]),
        "n_solucoes": len(df),
        "no_limite": ", ".join(
            nome for nome, col, (lo, hi) in LIMITES
            if s[col] <= lo + 0.005 * (hi - lo) or s[col] >= hi - 0.005 * (hi - lo)
        ),
    }


def main() -> int:
    if not PLANILHA.exists():
        print(f"planilha ausente: {PLANILHA}", file=sys.stderr)
        return 1
    ref = pd.read_excel(PLANILHA, sheet_name="Casos")
    ref = ref[[c for c in ref.columns if c == "id" or c.startswith("cfg_ref_")]]
    ref.columns = [c.removeprefix("cfg_ref_") for c in ref.columns]
    esp_info = pd.read_excel(PLANILHA, sheet_name="Especies")

    linhas = []
    for _, r in ref.iterrows():
        sol = ler_solucao(RESULTADOS / f"simulacao_{r['id']}")
        erro = (RESULTADOS / f"simulacao_{r['id']}" / "_erro.txt").exists()
        status = "ok" if sol else ("erro" if erro else "não rodado")
        linhas.append({**r.to_dict(), "status": status, **(sol or {})})
    casos = pd.DataFrame(linhas)
    print(casos["status"].value_counts().to_string())

    cls = casos[casos["bloco"] == "classe"]
    m_vol = cls.pivot(index="vao_m", columns="classe", values="V_m3")
    m_gov = cls.pivot(index="vao_m", columns="classe", values="governante")

    conf = []
    for l_m, por_classe in MATERIA_V.items():
        for classe, v_pub in por_classe.items():
            v = cls.loc[(cls["vao_m"] == l_m) & (cls["classe"] == classe), "V_m3"]
            v = float(v.iloc[0]) if len(v) and pd.notna(v.iloc[0]) else np.nan
            conf.append({"vao_m": l_m, "classe": classe, "V_materia": v_pub, "V_agora": v,
                         "dif_pct": 100 * (v / v_pub - 1) if pd.notna(v) else np.nan})
    conf = pd.DataFrame(conf)

    esp = casos[casos["bloco"] == "especie"]
    pares = []
    for (eid, l_m), g in esp.groupby(["especie_id", "vao_m"]):
        by = {row["cenario"]: row for _, row in g.iterrows()}
        e = by.get("esp")
        if e is None:
            continue
        c = cls[cls["id"] == e["id_classe"]]
        c = c.iloc[0] if len(c) else None
        info = esp_info[esp_info["id"] == eid].iloc[0]
        E_cls = float(c["E_MPa"]) if c is not None else np.nan
        linha = {
            "especie_id": eid, "especie": e["especie"], "classe": e["classe"], "vao_m": l_m,
            "delta_f_pct": info["delta_f_pct"], "delta_E_pct": info["delta_E_pct"],
            "delta_rho_pct": info["delta_rho_pct"],
            "V_esp": e.get("V_m3"), "V_cls": None if c is None else c.get("V_m3"),
            "gov_esp": e.get("governante"), "gov_cls": None if c is None else c.get("governante"),
            "U_flecha_esp": e.get("U_longarina_f"),
            "U_flecha_cls": None if c is None else c.get("U_longarina_f"),
        }
        linha["dV_cls_pct"] = 100 * (linha["V_cls"] / linha["V_esp"] - 1) if pd.notna(linha["V_cls"]) and pd.notna(linha["V_esp"]) else np.nan
        linha["U_flecha_CtoR_est"] = linha["U_flecha_cls"] * E_cls / float(e["E_MPa"]) if pd.notna(linha["U_flecha_cls"]) else np.nan
        linha["excede_ELS_est"] = bool(linha["U_flecha_CtoR_est"] > 1.0) if pd.notna(linha["U_flecha_CtoR_est"]) else None
        pares.append(linha)
    pares = pd.DataFrame(pares)

    with pd.ExcelWriter(SAIDA) as w:
        casos.to_excel(w, index=False, sheet_name="Casos")
        m_vol.to_excel(w, sheet_name="Matriz_volume")
        m_gov.to_excel(w, sheet_name="Matriz_governante")
        conf.to_excel(w, index=False, sheet_name="Conferencia_Materia")
        pares.to_excel(w, index=False, sheet_name="Pares")

    if conf["dif_pct"].notna().any():
        print(f"\nConferência com a Matéria (3 a 6 m): maior diferença {conf['dif_pct'].abs().max():.3f}%")
    lim = casos[casos["no_limite"].fillna("").astype(str) != ""]
    if not lim.empty:
        print(f"\nATENÇÃO: {len(lim)} caso(s) com variável no limite do intervalo de busca "
              "(coluna no_limite da aba Casos):")
        print(lim.groupby("no_limite")["id"].count().to_string())
    print(f"\n{SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
