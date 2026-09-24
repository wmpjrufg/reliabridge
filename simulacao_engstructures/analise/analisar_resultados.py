"""Análise da campanha do Artigo 2: figuras, tabelas e números do texto.

Lê consolidado.xlsx (consolidar.py) e analise/reavaliacao_CtoR.xlsx (reavaliar_pares.py) e grava:

    paper/engstruct/figuras/res_base_classes.png   volume e utilização de flecha da base de classes
    paper/engstruct/figuras/res_limiar_seguranca.png  critério de segurança do projeto pela classe
    paper/engstruct/figuras/res_leis_escala.png    ΔV observado contra as leis de escala
    paper/engstruct/figuras/res_mapa_decisao.png   mapa de decisão espécie x classe, por vão
    paper/engstruct/tabelas/tab_res_vao.tex         ΔV e reavaliação por vão
    paper/engstruct/tabelas/tab_res_regressao.tex   expoentes por regime
    analise/numeros_texto.txt                        todos os números citados no texto

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\analise\\analisar_resultados.py
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ANALISE = Path(__file__).resolve().parent
PASTA = ANALISE.parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))
PAPER = RAIZ / "paper" / "engstruct"
FIG = PAPER / "figuras"
TAB = PAPER / "tabelas"

from madeiras import restringir_espaco  # noqa: E402

# Paleta (validada com o validador do skill de dataviz)
CLS_COR = {"D20": "#86b6ef", "D30": "#5598e7", "D40": "#2a78d6", "D50": "#1c5cab", "D60": "#104281"}
AZUL, VERMELHO, LARANJA = "#2a78d6", "#e34948", "#eb6834"
TINTA, TINTA2, GRADE = "#0b0b0b", "#52514e", "#e3e2de"
LIMIAR_ATIVA = 0.99   # utilização a partir da qual a verificação é tratada como ativa
TAU = 5.0             # economia mínima (%) para que projetar pela espécie compense

plt.rcParams.update({
    "font.size": 8.5, "axes.titlesize": 9, "axes.labelsize": 8.5, "legend.fontsize": 7.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.edgecolor": TINTA2,
    "axes.labelcolor": TINTA, "xtick.color": TINTA2, "ytick.color": TINTA2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
    "grid.color": GRADE, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "savefig.dpi": 300, "savefig.bbox": "tight", "figure.facecolor": "white",
})


def pct(x, nd=1):
    """Número com vírgula decimal e sinal de menos tipográfico, para o LaTeX."""
    txt = f"{abs(x):.{nd}f}".replace(".", "{,}")
    return f"$-${txt}" if round(x, nd) < 0 else txt


def partes_volume(c: pd.DataFrame) -> pd.DataFrame:
    """Fração do volume nas longarinas, refazendo a acomodação inteira de peças."""
    lim = pd.read_excel(PASTA / "casos_engstruct.xlsx", sheet_name="Casos").drop_duplicates("cfg_ref_caso_base")
    lim = lim.set_index("cfg_ref_caso_base")
    out = []
    for _, s in c.iterrows():
        L = lim.loc[s["caso_base"]]
        _, nl, _ = restringir_espaco(s.esp_long_cm / 100, L.cfg_esp_long_min / 100, L.cfg_esp_long_max / 100, 4.5, s.d_cm / 100)
        _, nt, _ = restringir_espaco(s.esp_tab_cm / 100, L.cfg_esp_tab_min / 100, L.cfg_esp_tab_max / 100, s.vao_m, s.bw_cm / 100)
        v_l = nl * np.pi * (s.d_cm / 100) ** 2 / 4 * s.vao_m
        v_t = nt * (s.bw_cm / 100) * (s.h_cm / 100) * 4.5
        out.append({"n_long": nl, "n_tab": nt, "V_long": v_l, "V_tab": v_t, "share_long": v_l / (v_l + v_t)})
    return pd.concat([c.reset_index(drop=True), pd.DataFrame(out)], axis=1)


def ajuste(y, X):
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    n, k = X.shape
    s2 = (res ** 2).sum() / (n - k)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, 1.96 * se, r2, 100 * np.sqrt(s2)


def main() -> int:
    FIG.mkdir(parents=True, exist_ok=True)
    TAB.mkdir(parents=True, exist_ok=True)
    casos = pd.read_excel(PASTA / "consolidado.xlsx", sheet_name="Casos")
    conf = pd.read_excel(PASTA / "consolidado.xlsx", sheet_name="Conferencia_Materia")
    r = pd.read_excel(ANALISE / "reavaliacao_CtoR.xlsx")
    casos = partes_volume(casos)
    cidx = casos.set_index("caso_base")
    cls = casos[casos["bloco"] == "classe"]
    N = []  # números do texto

    # ---------------------------------------------------------------- ruído do otimizador
    d = casos["dispersao_pct"]
    N += [f"execuções: {5 * len(casos)}; casos: {len(casos)}",
          f"dispersão entre sementes: mediana {d.median():.2f}%, p90 {d.quantile(.9):.2f}%, máx {d.max():.2f}% ({casos.loc[d.idxmax(), 'caso_base']})",
          f"casos com verificação governante diferente entre sementes: {(~casos['governante_igual_nas_sementes'].astype(bool)).sum()} de {len(casos)}",
          f"semente de menor volume: {casos['semente_melhor'].value_counts().sort_index().to_dict()}",
          f"conferência Matéria (3-6 m): diferenças de {conf.dif_pct.min():.2f}% a {conf.dif_pct.max():.2f}%; mediana {conf.dif_pct.median():.2f}%",
          f"no_limite: {casos['no_limite'].fillna('').replace('', 'nenhum').value_counts().to_dict()}"]

    # ---------------------------------------------------------------- base de classes
    for cl, g in cls.groupby("classe"):
        b, a = np.polyfit(np.log(g.vao_m), np.log(g.V_m3), 1)
        N.append(f"lei de potência V ~ L^n, {cl}: n = {b:.3f}")
    ativa = cls[cls["U_longarina_f"] >= LIMIAR_ATIVA].groupby("classe")["vao_m"].min().to_dict()
    N.append(f"primeiro vão com flecha ativa (U>={LIMIAR_ATIVA}) por classe: {ativa}")
    N.append("U_flecha,cls em 10 m: " + str(cls[cls.vao_m == 10].set_index("classe")["U_longarina_f"].round(3).to_dict()))
    N.append("fração do volume nas longarinas (mediana por vão): " + str(casos.groupby("vao_m")["share_long"].median().round(2).to_dict()))

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
    for cl, g in cls.groupby("classe"):
        g = g.sort_values("vao_m")
        ax[0].plot(g.vao_m, g.V_m3, "-o", color=CLS_COR[cl], lw=1.6, ms=4, label=cl)
        ax[1].plot(g.vao_m, g.U_longarina_f, "-o", color=CLS_COR[cl], lw=1.6, ms=4, label=cl)
    ax[0].set(xlabel="Vão $L$ (m)", ylabel="Volume de madeira $V$ (m³)", title="(a) Volume do projeto pela classe")
    ax[1].axhline(1.0, color=TINTA2, lw=0.9, ls="--")
    ax[1].text(3.05, 1.015, "limite de serviço", color=TINTA2, fontsize=7, va="bottom")
    ax[1].set(xlabel="Vão $L$ (m)", ylabel="Utilização da flecha $U_{fin}$", title="(b) Utilização da flecha",
              ylim=(0, 1.1))
    ax[0].legend(title="Classe", frameon=False, loc="upper left")
    for a in ax:
        a.set_xticks(range(3, 11))
    fig.tight_layout()
    fig.savefig(FIG / "res_base_classes.png")
    plt.close(fig)

    # ---------------------------------------------------------------- ΔV por vão e reavaliação
    r["Uf_esp"] = [cidx.loc[f"E{int(e):02d}_L{int(l):02d}_esp", "U_longarina_f"] for e, l in zip(r.especie_id, r.vao_m)]
    r["s_l"] = [cidx.loc[f"CLS_{c}_L{int(l):02d}", "share_long"] for c, l in zip(r.classe, r.vao_m)]
    r["Erat"] = 1 + r.delta_E_pct / 100
    r["ruido"] = r.dispersao_esp_pct + r.dispersao_cls_pct
    viol = r["excede_rob"].astype(bool)
    N += [f"pares: {len(r)}; ΔV mediana {r.dV_cls_pct.median():.2f}%, média {r.dV_cls_pct.mean():.2f}%, de {r.dV_cls_pct.min():.2f}% a {r.dV_cls_pct.max():.2f}%",
          f"pares com ΔV<0: {(r.dV_cls_pct < 0).sum()}; dos quais violam ELS (robusto): {((r.dV_cls_pct < 0) & viol).sum()}",
          f"pares com |ΔV| acima do ruído: {(r.dV_cls_pct.abs() > r.ruido).sum()}",
          f"projeto da classe viola algum estado limite com a espécie: robusto {viol.sum()}, nominal {r.excede_nom.sum()}",
          f"verificações violadas: {r.verif_violada_rob.value_counts().to_dict()}",
          f"U_fin C->R (robusto) nos violados: mediana {r[viol].U_flecha_long_CtoR_rob.median():.3f}, máx {r[viol].U_flecha_long_CtoR_rob.max():.3f}",
          f"U de resistência C->R máximo: flex long {r.U_flex_long_CtoR_rob.max():.3f}, cis {r.U_cis_long_CtoR_rob.max():.3f}, flex tab {r.U_flex_tab_CtoR_rob.max():.3f}",
          f"espécies com E<E_cls: {(r[r.vao_m == 10].delta_E_pct < 0).sum()}"]
    seguros = r[~viol]
    N.append(f"pares seguros: {len(seguros)}; ΔV mediana {seguros.dV_cls_pct.median():.2f}%, de {seguros.dV_cls_pct.min():.2f}% a {seguros.dV_cls_pct.max():.2f}%")

    linhas = []
    for L, g in r.groupby("vao_m"):
        v = g[~g.excede_rob.astype(bool)]
        linhas.append((L, g.dV_cls_pct.median(), g.dV_cls_pct.quantile(.25), g.dV_cls_pct.quantile(.75),
                       g.dV_cls_pct.min(), g.dV_cls_pct.max(), int((g.dV_cls_pct < 0).sum()),
                       int(g.excede_rob.sum()), int(g.excede_nom.sum()),
                       int((v.dV_cls_pct > TAU).sum())))
    tex = [r"\begin{table}[!ht]", r"\centering",
           r"\caption{Diferença de volume $\Delta V=V_{cls}/V_{esp}-1$ entre o projeto pela classe e o projeto pela espécie, e reavaliação do projeto pela classe com as propriedades da espécie, por vão (40 pares por vão).}",
           r"\label{tab:res_vao}", r"\footnotesize", r"\setlength{\tabcolsep}{4pt}",
           r"\begin{tabular}{rrrrrrrr}", r"\toprule",
           r" & \multicolumn{3}{c}{$\Delta V$ (\%)} & & \multicolumn{2}{c}{Viola o ELS} & Espécie \\",
           r"\cmidrule(lr){2-4}\cmidrule(lr){6-7}",
           r"$L$ (m) & Mediana & $Q_1$ a $Q_3$ & Mín.\ a máx. & $\Delta V<0$ & Robusto & Nominal & economiza $>5\%$ \\", r"\midrule"]
    for L, med, q1, q3, mn, mx, neg, vr, vn, eco in linhas:
        tex.append(f"{L} & {pct(med)} & {pct(q1)} a {pct(q3)} & {pct(mn)} a {pct(mx)} & {neg} & {vr} & {vn} & {eco} \\\\")
    tex += [r"\midrule",
            f"Total & {pct(r.dV_cls_pct.median())} & {pct(r.dV_cls_pct.quantile(.25))} a {pct(r.dV_cls_pct.quantile(.75))} & "
            f"{pct(r.dV_cls_pct.min())} a {pct(r.dV_cls_pct.max())} & {(r.dV_cls_pct < 0).sum()} & {viol.sum()} & {r.excede_nom.sum()} & "
            f"{sum(l[-1] for l in linhas)} \\\\",
            r"\bottomrule", r"\end{tabular}", r"\begin{tablenotes}\footnotesize",
            r"\item ``Robusto'': alguma verificação excede o limite no pior caso da grade de $\pm5\%$ no diâmetro, que é o critério de aceitação da campanha. ``Nominal'': excede com o diâmetro nominal. ``Espécie economiza'': projeto pela classe seguro e $\Delta V>5\%$.",
            r"\end{tablenotes}", r"\end{table}"]
    (TAB / "tab_res_vao.tex").write_text("\n".join(tex).replace(r"\begin{tablenotes}", r"\begin{minipage}{0.95\linewidth}\vspace{2pt}").replace(r"\end{tablenotes}", r"\end{minipage}").replace(r"\item ", ""), encoding="utf-8")

    # ---------------------------------------------------------------- limiar de segurança
    pred_falha = r.Erat < r.U_flecha_cls
    acerto = int((pred_falha == viol).sum())
    y = np.log(r.U_flecha_long_CtoR_rob / r.U_flecha_cls)
    X = np.c_[-np.log(r.Erat), np.log(1 + r.delta_rho_pct / 100)]
    b, ic, r2, rmse = ajuste(y, X)
    N += [f"regra E_esp/E_cls >= U_fin,cls: acerta {acerto} de {len(r)}; falsos seguros {int((~pred_falha & viol).sum())}, falsos inseguros {int((pred_falha & ~viol).sum())}",
          f"ajuste U_CtoR/U_cls = (E_cls/E_esp)^a (rho_esp/rho_cls)^c: a={b[0]:.3f}±{ic[0]:.3f}, c={b[1]:.3f}±{ic[1]:.3f}, R2={r2:.4f}, rmse={rmse:.2f}%",
          "erros da regra: " + r[pred_falha != viol][["especie", "vao_m", "delta_E_pct", "delta_rho_pct", "U_flecha_cls", "U_flecha_long_CtoR_rob"]].round(3).to_string(index=False)]

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1))
    xx = np.linspace(0.2, 1.05, 10)
    ax[0].fill_between(xx, 0.5, xx, color=VERMELHO, alpha=0.07, lw=0)
    ax[0].plot(xx, xx, color=TINTA2, lw=1)
    ax[0].scatter(r.U_flecha_cls[~viol], r.Erat[~viol], s=14, facecolor="none", edgecolor=AZUL, lw=0.8, label="atende ao ELS")
    ax[0].scatter(r.U_flecha_cls[viol], r.Erat[viol], s=16, marker="x", color=VERMELHO, lw=0.9, label="viola o ELS")
    ax[0].set(xlabel="Utilização da flecha do projeto pela classe, $U_{fin,cls}$",
              ylabel="$E_{c0,m}^{exp}/E_{c0,m}^{NBR}$", xlim=(0.2, 1.05), ylim=(0.55, 1.52),
              title="(a) Critério de segurança")
    from matplotlib.patches import Patch
    hs, ls = ax[0].get_legend_handles_labels()
    hs.append(Patch(facecolor=VERMELHO, alpha=0.12, lw=0))
    ls.append("região $E_{esp}/E_{cls}<U_{fin,cls}$")
    ax[0].legend(hs, ls, frameon=False, loc="upper left")
    lim = (0.2, 1.65)
    ax[1].plot(lim, lim, color=TINTA2, lw=1)
    ax[1].axhline(1, color=TINTA2, lw=0.8, ls="--")
    est = r.U_flecha_cls / r.Erat
    ax[1].scatter(est[~viol], r.U_flecha_long_CtoR_rob[~viol], s=14, facecolor="none", edgecolor=AZUL, lw=0.8)
    ax[1].scatter(est[viol], r.U_flecha_long_CtoR_rob[viol], s=16, marker="x", color=VERMELHO, lw=0.9)
    ax[1].set(xlabel="$U_{fin,cls}\\,E_{cls}/E_{esp}$", ylabel="$U_{fin}^{C\\rightarrow R}$ (modelo completo)",
              xlim=lim, ylim=lim, title="(b) Previsão e reavaliação")
    fig.tight_layout()
    fig.savefig(FIG / "res_limiar_seguranca.png")
    plt.close(fig)

    # ---------------------------------------------------------------- leis de escala
    res_reg = (r.U_flecha_cls < LIMIAR_ATIVA) & (r.Uf_esp < LIMIAR_ATIVA)
    fle_reg = (r.U_flecha_cls >= LIMIAR_ATIVA) & (r.Uf_esp >= LIMIAR_ATIVA)
    mis_reg = ~(res_reg | fle_reg)
    yv = np.log(r.V_cls / r.V_esp)
    Xv = np.c_[np.log(1 + r.delta_f_pct / 100), np.log(r.Erat), np.log(1 + r.delta_rho_pct / 100)]
    reg_rows = []
    for nome, m in [("Resistência", res_reg), ("Flecha", fle_reg), ("Misto", mis_reg), ("Todos", pd.Series(True, index=r.index))]:
        b, ic, r2, rmse = ajuste(yv[m].to_numpy(), Xv[m.to_numpy()])
        reg_rows.append((nome, int(m.sum()), b, ic, r2, rmse))
        N.append(f"regressão {nome}: n={m.sum()} b_f={b[0]:.3f}±{ic[0]:.3f} b_E={b[1]:.3f}±{ic[1]:.3f} b_rho={b[2]:.3f}±{ic[2]:.3f} R2={r2:.3f} rmse={rmse:.2f}%")
    F = 1 + r.delta_f_pct / 100
    obs = r.V_cls / r.V_esp
    prev_res = F ** 0.5
    prev_fle = F ** (0.5 * (1 - r.s_l)) * r.Erat ** (0.5 * r.s_l)
    for nome, m, pv in [("resistência (1+Δf)^1/2", res_reg, prev_res), ("flecha (fração de volume)", fle_reg, prev_fle)]:
        e = 100 * (pv[m] / obs[m] - 1)
        N.append(f"previsão sem ajuste, {nome}: viés {e.mean():+.2f}%, rmse {np.sqrt((e ** 2).mean()):.2f}%, máx {e.abs().max():.2f}%")
    N.append(f"s_l nos pares do regime de flecha: mediana {r.s_l[fle_reg].median():.2f} ({r.s_l[fle_reg].min():.2f} a {r.s_l[fle_reg].max():.2f})")
    N.append("pares por regime e vão:\n" + pd.crosstab(r.vao_m, np.select([res_reg, fle_reg], ["resistência", "flecha"], "misto")).to_string())

    tex = [r"\begin{table}[!ht]", r"\centering",
           r"\caption{Expoentes do ajuste $\ln(V_{cls}/V_{esp})=b_f\ln(1+\Delta_f)+b_E\ln(1+\Delta_E)+b_\rho\ln(1+\Delta_\rho)$ por regime, com intervalos de confiança de 95\%.}",
           r"\label{tab:res_regressao}", r"\footnotesize",
           r"\begin{tabular}{lrrrrrr}", r"\toprule",
           r"Regime & $n$ & $b_f$ & $b_E$ & $b_\rho$ & $R^2$ & RMSE (\%) \\", r"\midrule"]
    for nome, n, b, ic, r2, rmse in reg_rows:
        tex.append(f"{nome} & {n} & " + " & ".join(f"{pct(v, 3)} $\\pm$ {pct(e, 3)}" for v, e in zip(b, ic)) + f" & {pct(r2, 3)} & {pct(rmse, 2)} \\\\")
    tex += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (TAB / "tab_res_regressao.tex").write_text("\n".join(tex), encoding="utf-8")

    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
    ff = np.linspace(0, 0.65, 50)
    m = res_reg
    ax[0].fill_between(100 * ff, 100 * ((1 + ff) ** 0.5 - 1), 100 * ((1 + ff) ** (2 / 3) - 1), color=TINTA2, alpha=0.10, lw=0)
    ax[0].plot(100 * ff, 100 * ((1 + ff) ** 0.5 - 1), color=TINTA, lw=1.2, label="$(1+\\Delta_f)^{1/2}-1$")
    ax[0].plot(100 * ff, 100 * ((1 + ff) ** (2 / 3) - 1), color=TINTA2, lw=1, ls="--", label="$(1+\\Delta_f)^{2/3}-1$")
    ax[0].scatter(r.delta_f_pct[m], r.dV_cls_pct[m], s=14, facecolor="none", edgecolor=AZUL, lw=0.8, label="pares")
    ax[0].set(xlabel="$\\Delta_f$ (%)", ylabel="$\\Delta V$ (%)", title=f"(a) Regime de resistência ($n={m.sum()}$)")
    ax[0].legend(frameon=False, loc="upper left")
    m = fle_reg
    lim = (-17, 17)
    ax[1].plot(lim, lim, color=TINTA2, lw=1)
    pos = m & (r.delta_E_pct >= 0)
    neg = m & (r.delta_E_pct < 0)
    ax[1].scatter(100 * (prev_fle[pos] - 1), r.dV_cls_pct[pos], s=14, facecolor="none", edgecolor=AZUL, lw=0.8, label="$\\Delta_E\\geq0$")
    ax[1].scatter(100 * (prev_fle[neg] - 1), r.dV_cls_pct[neg], s=16, marker="^", facecolor="none", edgecolor=LARANJA, lw=0.8, label="$\\Delta_E<0$")
    ax[1].set(xlabel="Previsão $(1+\\Delta_f)^{(1-s_\\ell)/2}(1+\\Delta_E)^{s_\\ell/2}-1$ (%)", ylabel="$\\Delta V$ observado (%)",
              xlim=lim, ylim=lim, title=f"(b) Regime de flecha ($n={m.sum()}$)")
    ax[1].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(FIG / "res_leis_escala.png")
    plt.close(fig)

    # ---------------------------------------------------------------- mapa de decisão
    cat = np.where(viol, "viola", np.where(r.dV_cls_pct > TAU, "economiza", "indiferente"))
    r["decisao"] = cat
    N.append("categorias por vão:\n" + pd.crosstab(r.vao_m, r.decisao).to_string())
    fig, axs = plt.subplots(2, 4, figsize=(7.2, 3.9), sharex=True, sharey=True)
    for a, L in zip(axs.flat, range(3, 11)):
        g = r[r.vao_m == L]
        for c, kw in [("indiferente", dict(s=13, facecolor="none", edgecolor="#9a9994", lw=0.7)),
                      ("economiza", dict(s=13, color=AZUL, lw=0)),
                      ("viola", dict(s=15, marker="x", color=VERMELHO, lw=0.9))]:
            h = g[g.decisao == c]
            a.scatter(h.delta_f_pct, h.delta_E_pct, label=c, **kw)
        a.axhline(0, color=TINTA2, lw=0.6)
        a.set_title(f"$L$ = {L} m", fontsize=8)
    for a in axs[1]:
        a.set_xlabel("$\\Delta_f$ (%)")
    for a in axs[:, 0]:
        a.set_ylabel("$\\Delta_E$ (%)")
    hs = [plt.Line2D([], [], ls="", marker="x", color=VERMELHO, label="classe viola o ELS"),
          plt.Line2D([], [], ls="", marker="o", color=AZUL, label=f"espécie economiza mais de {TAU:.0f}%"),
          plt.Line2D([], [], ls="", marker="o", mfc="none", mec="#9a9994", label=f"diferença de até {TAU:.0f}%")]
    fig.legend(handles=hs, loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.03))
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(FIG / "res_mapa_decisao.png")
    plt.close(fig)

    r.to_excel(ANALISE / "pares_analise.xlsx", index=False)
    (ANALISE / "numeros_texto.txt").write_text("\n".join(N), encoding="utf-8")
    print("\n".join(N))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
