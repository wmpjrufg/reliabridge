r"""Extrai TODOS os números citados em `paper/materia/05_results.tex` e
`06_conclusions.tex` a partir do lote reprocessado (`simulacaoes_/lote_eixos_1p5/` e
`simulacaoes_/custo_robustez_C13/`), para o preenchimento manual do `.tex`.

Não escreve no `.tex`. Apenas imprime um relatório e grava `tmp/preenchimento_materia.xlsx`
com uma aba por tabela, para conferência.

Uso:
    .venv\Scripts\python.exe extrair_preenchimento_materia.py
"""

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from madeiras import estatistica_descritiva_variaveis, geracao_estabilizacao_hipervolume  # noqa: E402

LOTE = RAIZ / "simulacaoes_" / "lote_eixos_1p5"
ROBUSTEZ = RAIZ / "simulacaoes_" / "custo_robustez_C13"

CLASSES = ["D20", "D30", "D40", "D50", "D60"]
VAOS = [3.0, 4.0, 5.0, 6.0]
FC0K = {"D20": 20.0, "D30": 30.0, "D40": 40.0, "D50": 50.0, "D60": 60.0}
NIVEIS_RHO = [("rho000", 0.0), ("rho025", 2.5), ("rho050", 5.0), ("rho100", 10.0)]

GCOLS = ["longarina_g_m", "longarina_g_v", "longarina_g_f", "tabuleiro_g_m"]
GLABEL = {
    "longarina_g_m": "Flexão long.",
    "longarina_g_v": "Cisalhamento long.",
    "longarina_g_f": "Flecha long.",
    "tabuleiro_g_m": "Flexão tab.",
}


def membro(pasta: Path, nome_arquivo: str) -> io.BytesIO:
    z = zipfile.ZipFile(pasta / "pre_sizing_package.zip")
    return io.BytesIO(z.read(nome_arquivo))


def ler_front(cel_dir: Path) -> pd.DataFrame:
    df = pd.read_excel(membro(cel_dir, "pre_sizing_results_optimized.xlsx"))
    return df.dropna(subset=["d_cm"]).reset_index(drop=True)


def loglog_fit(x: pd.Series, y: pd.Series) -> tuple[float, float, float]:
    """Ajusta y = a*x^b; devolve (a, b, R^2) em escala log-log."""
    lx, ly = np.log(x.to_numpy(float)), np.log(y.to_numpy(float))
    b, ln_a = np.polyfit(lx, ly, 1)
    a = np.exp(ln_a)
    pred = ln_a + b * lx
    ss_res = np.sum((ly - pred) ** 2)
    ss_tot = np.sum((ly - ly.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return float(a), float(b), float(r2)


def spacing_schott(F: np.ndarray) -> float:
    """Métrica de spacing de Schott (1995), objetivos normalizados por ideal/nadir do front final."""
    ideal, nadir = F.min(axis=0), F.max(axis=0)
    amp = np.where(nadir - ideal > 0, nadir - ideal, 1.0)
    Fn = (F - ideal) / amp
    n = len(Fn)
    d = np.empty(n)
    for i in range(n):
        dist = np.sum(np.abs(Fn - Fn[i]), axis=1)
        dist[i] = np.inf
        d[i] = dist.min()
    return float(np.sqrt(np.sum((d - d.mean()) ** 2) / (n - 1)))


def secao_matriz() -> pd.DataFrame:
    linhas = []
    for i in range(1, 21):
        cel_dir = LOTE / f"simulacao_C_{i:02d}"
        df = ler_front(cel_dir)
        b = df.loc[df["of_volume_m3"].idxmin()]
        gvals = {c: b[c] for c in GCOLS}
        gmax_nome = max(gvals, key=gvals.get)
        L = VAOS[(i - 1) // 5]
        classe = CLASSES[(i - 1) % 5]
        linhas.append({
            "cel": f"C-{i:02d}", "L": L, "classe": classe,
            "d": b.d_cm, "bw": b.bw_cm, "h": b.h_cm, "esp_long": b.esp_cm, "esp_tab": b.esp_tab_cm,
            "V": b.of_volume_m3, "delta_ratio": b.of_fator_flecha,
            "g_max": gvals[gmax_nome], "verificacao": GLABEL[gmax_nome],
            "Vm2": b.of_volume_m3 / (L * 4.5),
        })
    return pd.DataFrame(linhas)


def secao_efeito_vao_classe(M: pd.DataFrame) -> None:
    print("\n=== Efeito do vão: V = a*L^n por classe ===")
    for c in CLASSES:
        s = M[M.classe == c].sort_values("L")
        a, n, r2 = loglog_fit(s.L, s.V)
        print(f"  {c}: n={n:.3f}  R2={r2:.4f}  (a={a:.4f})")
    print("  multiplicador 3,0->6,0 m por classe:")
    for c in CLASSES:
        s = M[M.classe == c].sort_values("L")
        v3 = s[s.L == 3.0].V.iloc[0]
        v6 = s[s.L == 6.0].V.iloc[0]
        print(f"    {c}: {v6/v3:.2f}x")

    print("\n=== Efeito da classe: reducao D20->D60 por vao ===")
    for L in VAOS:
        s = M[M.L == L].set_index("classe")
        red = (s.loc["D20", "V"] - s.loc["D60", "V"]) / s.loc["D20", "V"] * 100
        deg1 = (s.loc["D20", "V"] - s.loc["D30", "V"]) / s.loc["D20", "V"] * 100
        print(f"  L={L}: D20->D60 = -{red:.1f}%   D20->D30 = -{deg1:.1f}%")

    print("\n=== Monotonicidade ===")
    ok = True
    for c in CLASSES:
        s = M[M.classe == c].sort_values("L").V.to_numpy()
        if not np.all(np.diff(s) > 0):
            ok = False
            print(f"  QUEBRA em {c} (V nao cresce com L): {s}")
    for L in VAOS:
        s = M[M.L == L].sort_values("classe").V.to_numpy()
        if not np.all(np.diff(s) < 0):
            ok = False
            print(f"  QUEBRA em L={L} (V nao decresce com classe): {s}")
    print("  matriz integralmente monotonica" if ok else "  ATENCAO: monotonicidade quebrada, ver acima")

    print("\n=== Consumo m3/m2 (abacos) ===")
    print(f"  min={M.Vm2.min():.3f}  (cel {M.loc[M.Vm2.idxmin(),'cel']})  "
          f"max={M.Vm2.max():.3f}  (cel {M.loc[M.Vm2.idxmax(),'cel']})")

    print("\n=== Diametro minimo do dominio de busca (saturacao) ===")
    from batch_pre_sizing import LimitesBusca
    d_min = LimitesBusca().d[0]
    sat = M[M.d <= d_min + 0.5]
    print(f"  d_min do dominio = {d_min}")
    print(sat[["cel", "L", "classe", "d", "g_max", "verificacao"]].to_string(index=False) if not sat.empty
          else "  nenhuma celula saturada no piso de d")


def secao_c13_fronteira() -> pd.DataFrame:
    df = ler_front(LOTE / "simulacao_C_13")
    df = df.sort_values("of_volume_m3").reset_index(drop=True)
    n = len(df)
    idx = np.round(np.linspace(0, n - 1, 7)).astype(int)
    amostra = df.iloc[idx].copy()
    for c in GCOLS:
        pass
    amostra["g_max"] = amostra[GCOLS].max(axis=1)

    print("\n=== C-13: 7 solucoes representativas da fronteira ===")
    cols = ["d_cm", "bw_cm", "h_cm", "esp_cm", "esp_tab_cm", "of_volume_m3", "of_fator_flecha", "g_max"]
    print(amostra[cols].round(4).to_string(index=False))

    print("\n=== C-13: extremos da fronteira ===")
    vmin_row = df.loc[df.of_volume_m3.idxmin()]
    vmax_row = df.loc[df.of_volume_m3.idxmax()]
    print(f"  min V = {vmin_row.of_volume_m3:.3f} m3, delta_ratio = {vmin_row.of_fator_flecha:.4f} "
          f"({vmin_row.of_fator_flecha*100:.1f}% do limite)")
    print(f"  max V = {vmax_row.of_volume_m3:.3f} m3, delta_ratio = {vmax_row.of_fator_flecha:.4f} "
          f"({vmax_row.of_fator_flecha*100:.2f}% do limite)")
    print(f"  V multiplica por {vmax_row.of_volume_m3/vmin_row.of_volume_m3:.2f}x, "
          f"delta_ratio cai {vmin_row.of_fator_flecha/vmax_row.of_fator_flecha:.1f}x")

    print("\n=== C-13: leis de potencia ao longo da fronteira (50 pontos) ===")
    _, b1, r1 = loglog_fit(df.d_cm, df.of_volume_m3)
    print(f"  V ~ d^{b1:.2f}  R2={r1:.4f}")
    _, b2, r2v = loglog_fit(df.d_cm, df.of_fator_flecha)
    print(f"  delta_ratio ~ d^{b2:.2f}  R2={r2v:.4f}")
    _, b3, r3 = loglog_fit(df.of_volume_m3, df.of_fator_flecha)
    print(f"  delta_ratio ~ V^{b3:.2f}  R2={r3:.4f}")

    print("\n=== C-13: verificacao ativa ao longo da fronteira ===")
    dominante = df[GCOLS].idxmax(axis=1).value_counts()
    print(dominante.to_string())
    print(f"  no extremo de menor volume: {dict(df.loc[df.of_volume_m3.idxmin(), GCOLS].round(4))}")

    return df


def secao_utilizacao(df_c13: pd.DataFrame) -> None:
    b = df_c13.loc[df_c13.of_volume_m3.idxmin()]
    print("\n=== C-13: grau de utilizacao na solucao de menor volume ===")
    for c in GCOLS:
        print(f"  {GLABEL[c]:<20} g={b[c]:.4f}  utilizacao={(1+b[c])*100:.1f}%")


def secao_robustez() -> pd.DataFrame:
    fronts = {}
    for nome, rho in NIVEIS_RHO:
        fronts[rho] = ler_front(ROBUSTEZ / f"simulacao_{nome}")

    print("\n=== Robustez: extremo economico por rho ===")
    vmins = {}
    for rho, df in fronts.items():
        vmin = df.of_volume_m3.min()
        vmins[rho] = vmin
        print(f"  rho={rho}%: Vmin={vmin:.3f} m3")
    base = vmins[0.0]
    for rho in (2.5, 5.0, 10.0):
        print(f"    delta vs rho=0: {(vmins[rho]-base)/base*100:+.1f}%")

    print("\n=== Robustez: niveis pareados de flecha ===")
    faixa_min = max(df.of_fator_flecha.min() for df in fronts.values())
    faixa_max = min(df.of_fator_flecha.max() for df in fronts.values())
    alvos = np.linspace(faixa_min, faixa_max, 5)[1:4]
    print(f"  faixa comum de delta_ratio: [{faixa_min:.4f}, {faixa_max:.4f}]; alvos: {alvos.round(4)}")
    tabela = []
    for alvo in alvos:
        linha = {"delta_ratio_alvo": alvo}
        for rho, df in fronts.items():
            idx = (df.of_fator_flecha - alvo).abs().idxmin()
            linha[f"V(rho={rho})"] = df.loc[idx, "of_volume_m3"]
            linha[f"delta_real(rho={rho})"] = df.loc[idx, "of_fator_flecha"]
        tabela.append(linha)
    tab = pd.DataFrame(tabela)
    for rho in (2.5, 5.0, 10.0):
        tab[f"delta%(rho={rho})"] = (tab[f"V(rho={rho})"] - tab["V(rho=0.0)"]) / tab["V(rho=0.0)"] * 100
    print(tab.round(4).to_string(index=False))
    print("  media dos 3 niveis:")
    for rho in (2.5, 5.0, 10.0):
        print(f"    rho={rho}%: delta medio = {tab[f'delta%(rho={rho})'].mean():+.1f}%")

    print("\n=== Robustez: tempos de execucao ===")
    resumo_path = ROBUSTEZ / "_lote_resumo.xlsx"
    if resumo_path.exists():
        resumo = pd.read_excel(resumo_path)
        print(resumo[["id", "t_total_s"]].to_string(index=False))
    else:
        print("  _lote_resumo.xlsx nao encontrado")

    return tab


def secao_hv() -> pd.DataFrame:
    linhas = []
    for i in range(1, 21):
        cel_dir = LOTE / f"simulacao_C_{i:02d}"
        hist = pd.read_csv(membro(cel_dir, "hypervolume_convergence.csv"))
        hv_final = float(hist["hipervolume"].iloc[-1])
        gen_estab = geracao_estabilizacao_hipervolume(hist)
        front = ler_front(cel_dir)
        F = front[["of_volume_m3", "of_fator_flecha"]].to_numpy(float)
        spacing = spacing_schott(F)
        L = VAOS[(i - 1) // 5]
        classe = CLASSES[(i - 1) % 5]
        linhas.append({"cel": f"C-{i:02d}", "L": L, "classe": classe,
                       "HV": hv_final, "spacing": spacing, "geracao_estab": gen_estab})
    tab = pd.DataFrame(linhas)
    print("\n=== Hipervolume, spacing, geracao de estabilizacao ===")
    print(tab.round(4).to_string(index=False))
    print(f"\n  geracao_estab: min={tab.geracao_estab.min()} max={tab.geracao_estab.max()} "
          f"media={tab.geracao_estab.mean():.1f}  celula mais lenta={tab.loc[tab.geracao_estab.idxmax(),'cel']}")
    print(f"  HV: min={tab.HV.min():.3f} max={tab.HV.max():.3f}  "
          f"(% do maximo teorico 1,21: {tab.HV.min()/1.21*100:.0f}% a {tab.HV.max()/1.21*100:.0f}%)")
    print(f"  spacing: min={tab.spacing.min():.4f} max={tab.spacing.max():.4f} media={tab.spacing.mean():.4f}")
    return tab


def secao_sobol() -> pd.DataFrame:
    sobol = pd.read_excel(membro(LOTE / "simulacao_C_13", "sobol_total_indices.xlsx"))
    sobol = sobol.set_index("variavel")
    print("\n=== Sobol C-13: variavel dominante por restricao ===")
    linhas = []
    for col in sobol.columns:
        vals = sobol[col]
        trunc = vals.clip(lower=0)
        soma = trunc.sum()
        dominante = vals.idxmax()
        participacao = trunc[dominante] / soma * 100 if soma > 0 else float("nan")
        linhas.append({"restricao": col, "variavel": dominante, "S_Ti": vals[dominante],
                       "participacao_pct": participacao})
        print(f"  {col:<28} dominante={dominante:<12} S_Ti={vals[dominante]:.3f}  "
              f"participacao={participacao:.1f}%")
    print("\n  tabela completa de S_Ti:")
    print(sobol.round(3).to_string())
    return pd.DataFrame(linhas)


def secao_estatistica() -> pd.DataFrame:
    df = ler_front(LOTE / "simulacao_C_13")
    cols = ["d_cm", "bw_cm", "h_cm", "esp_cm", "esp_tab_cm"]
    labels = ["$d$ (cm)", "$b_w$ (cm)", "$h$ (cm)", "$esp_{long}$ (cm)", "$esp_{tab}$ (cm)"]
    tab = estatistica_descritiva_variaveis(df, cols, labels)
    print("\n=== Estatistica descritiva C-13 ===")
    print(tab.to_string(index=False))
    return tab


def main() -> int:
    if not LOTE.exists():
        print(f"ERRO: {LOTE} nao existe. Rode rodar_lote.py primeiro.", file=sys.stderr)
        return 1

    M = secao_matriz()
    print("=== Tabela consolidada (tab:resultados_matriz) ===")
    print(M.round(4).to_string(index=False))

    secao_efeito_vao_classe(M)
    df_c13 = secao_c13_fronteira()
    secao_utilizacao(df_c13)

    tem_robustez = ROBUSTEZ.exists()
    tab_rob = secao_robustez() if tem_robustez else None

    tab_hv = secao_hv()
    tab_sobol = secao_sobol()
    tab_est = secao_estatistica()

    destino = RAIZ / "tmp" / "preenchimento_materia.xlsx"
    with pd.ExcelWriter(destino) as xl:
        M.to_excel(xl, sheet_name="matriz", index=False)
        df_c13.to_excel(xl, sheet_name="c13_fronteira", index=False)
        tab_hv.to_excel(xl, sheet_name="hv", index=False)
        tab_sobol.to_excel(xl, sheet_name="sobol", index=False)
        tab_est.to_excel(xl, sheet_name="estatistica", index=False)
        if tab_rob is not None:
            tab_rob.to_excel(xl, sheet_name="robustez", index=False)
    print(f"\ngravado em {destino.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
