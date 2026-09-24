"""Reavalia o projeto obtido pela classe com as propriedades reais da espécie.

Para cada par espécie x vão, pega a geometria da melhor solução da base de classes
(aba Casos do consolidado.xlsx) e a avalia, sem reotimizar, com as propriedades medidas
da espécie (E, densidade, f_m,k, f_v0,k), pelo mesmo modelo da otimização:

    nominal  diâmetro nominal
    robusto  pior caso da grade de ±5% no diâmetro (o critério de aceitação da campanha)

Isso substitui a estimativa U_cls x E_cls/E_esp do consolidar.py, porque inclui a troca
de densidade (peso próprio) e de resistência. Como verificação, a mesma geometria também
é avaliada com as propriedades da classe e tem de reproduzir as utilizações gravadas.

Grava analise/reavaliacao_CtoR.xlsx.

Uso (na raiz do repositório, depois do consolidar.py):
    .venv\\Scripts\\python.exe simulacao_engstructures\\analise\\reavaliar_pares.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ANALISE = Path(__file__).resolve().parent
PASTA = ANALISE.parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402
from madeiras import _criar_projeto_otimo_pre_sizing, normalizar_dados_pre_sizing  # noqa: E402

GNOMES = ["g_flex_long", "g_cis_long", "g_flecha_long", "g_flex_tab", "g_esp_long", "g_esp_tab"]


def avaliar(caso: bps.CasoBatch, x: np.ndarray, t: dict, robusto: bool) -> tuple[np.ndarray, np.ndarray]:
    dados = normalizar_dados_pre_sizing(caso.dados, t)
    ds, bws, hs, nl, nt = caso.limites.como_listas()
    perc = float(dados[t["percentual_robustez"]]) if robusto else 0.0
    proj = _criar_projeto_otimo_pre_sizing(dados, ds, bws, hs, nl, nt, t, n_checagens=30, perc_robustez=perc)
    out: dict = {}
    proj._evaluate(x, out)
    return np.asarray(out["F"], float), np.asarray(out["G"], float)


def main() -> int:
    t = bps.textos("pt")
    casos = {c.id: c for c in bps.ler_planilha_casos(PASTA / "casos_engstruct.xlsx")}
    melhores = pd.read_excel(PASTA / "consolidado.xlsx", sheet_name="Casos").set_index("caso_base")
    pares = pd.read_excel(PASTA / "consolidado.xlsx", sheet_name="Pares")

    # 1) verificação: geometria da classe com as propriedades da classe reproduz o gravado
    dif = 0.0
    for base_id, m in melhores[melhores["bloco"] == "classe"].iterrows():
        x = m[["d_cm", "bw_cm", "h_cm", "esp_long_cm", "esp_tab_cm"]].to_numpy(float)
        _, G = avaliar(casos[f"{base_id}_s{int(m['semente_melhor'])}"], x, t, robusto=True)
        ref = np.array([m["U_longarina_m"], m["U_longarina_v"], m["U_longarina_f"], m["U_tabuleiro_m"]]) - 1
        dif = max(dif, float(np.abs(G[:4] - ref).max()))
    print(f"Verificação (classe com classe): maior diferença em g = {dif:.2e}")
    if dif > 1e-6:
        print("ATENÇÃO: a reavaliação não reproduz os resultados gravados.", file=sys.stderr)

    # 2) reavaliação: geometria da classe com as propriedades da espécie
    linhas = []
    for _, p in pares.iterrows():
        eid, l_m, cl = int(p["especie_id"]), int(p["vao_m"]), p["classe"]
        mc = melhores.loc[f"CLS_{cl}_L{l_m:02d}"]
        me = melhores.loc[f"E{eid:02d}_L{l_m:02d}_esp"]
        x = mc[["d_cm", "bw_cm", "h_cm", "esp_long_cm", "esp_tab_cm"]].to_numpy(float)
        caso_esp = casos[f"E{eid:02d}_L{l_m:02d}_esp_s1"]
        F_n, G_n = avaliar(caso_esp, x, t, robusto=False)
        F_r, G_r = avaliar(caso_esp, x, t, robusto=True)
        linha = {k: p[k] for k in ["especie_id", "especie", "classe", "vao_m", "delta_f_pct",
                                   "delta_E_pct", "delta_rho_pct", "V_esp", "V_cls", "dV_cls_pct",
                                   "dispersao_esp_pct", "dispersao_cls_pct", "gov_esp", "gov_cls"]}
        for nome, g in zip(GNOMES[:4], G_r[:4]):
            linha[f"U_{nome[2:]}_CtoR_rob"] = 1 + g
        for nome, g in zip(GNOMES[:4], G_n[:4]):
            linha[f"U_{nome[2:]}_CtoR_nom"] = 1 + g
        linha["U_flecha_cls"] = mc["U_longarina_f"]
        linha["U_flecha_esp"] = me["U_longarina_f"]
        linha["U_flecha_CtoR_est"] = p["U_flecha_CtoR_est"]
        linha["Umax_CtoR_rob"] = 1 + float(G_r[:4].max())
        linha["verif_violada_rob"] = ", ".join(n[2:] for n, g in zip(GNOMES[:4], G_r[:4]) if g > 0) or "-"
        linha["excede_rob"] = bool(G_r[:4].max() > 0)
        linha["excede_nom"] = bool(G_n[:4].max() > 0)
        linhas.append(linha)
    r = pd.DataFrame(linhas)
    saida = ANALISE / "reavaliacao_CtoR.xlsx"
    r.to_excel(saida, index=False)
    print(f"Pares: {len(r)}; projeto da classe viola algum estado limite com a espécie: "
          f"{int(r['excede_rob'].sum())} (robusto), {int(r['excede_nom'].sum())} (nominal)")
    print(r.groupby("vao_m")[["excede_rob", "excede_nom"]].sum().T.to_string())
    print(r["verif_violada_rob"].value_counts().to_string())
    print(f"\n{saida}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
