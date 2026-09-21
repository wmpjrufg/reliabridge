"""Ajusta a equação de pré-dimensionamento V(L, f_c0,k) = a * L^b * f_c0,k^c
ao banco de dados da varredura paramétrica (Seção 4.4/4.6, `tab:resultados_matriz`).

Regressão log-log (mínimos quadrados) sobre as vinte células da matriz:
    ln(V) = ln(a) + b*ln(L) + c*ln(f_c0,k)

f_c0,k é a propriedade de classe usada como regressor porque a Seção 4.4 mostra que a
flexão (para a qual f_m,k = f_c0,k, item 6.3.4 da NBR 7190-1) governa as vinte células —
não a rigidez.

Uso:
    .venv\\Scripts\\python.exe ajustar_equacao_pre_dimensionamento.py
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from batch_pre_sizing import LimitesBusca  # noqa: E402
from gerar_figuras_materia import (  # noqa: E402
    CLASSES,
    CM,
    COR,
    MARCADORES,
    ROTULOS,
    consolidar,
    estilo,
    salvar,
)

# Tabela `tab:classes_madeira` (04_methodology.tex): f_c0,k = f_m,k por classe, em MPa.
FC0K = {"D20": 20.0, "D30": 30.0, "D40": 40.0, "D50": 50.0, "D60": 60.0}


def ajustar(M: pd.DataFrame) -> dict:
    M = M.copy()
    M["fc0k"] = M["classe"].map(FC0K)

    X = np.column_stack([np.ones(len(M)), np.log(M["L"]), np.log(M["fc0k"])])
    y = np.log(M["V"])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    ln_a, b, c = coef
    a = float(np.exp(ln_a))
    b = float(b)
    c = float(c)

    M["V_pred"] = a * M["L"] ** b * M["fc0k"] ** c
    M["erro_rel_pct"] = (M["V_pred"] - M["V"]) / M["V"] * 100

    y_pred_log = X @ coef
    ss_res = float(np.sum((y - y_pred_log) ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot

    d_min = LimitesBusca().d[0]
    M["saturada_piso_d"] = M["d"] <= d_min + 0.5

    return {"a": a, "b": b, "c": c, "r2": r2, "d_min": d_min, "M": M}


def figura_paridade(Mr: pd.DataFrame, idioma: str) -> None:
    """Volume previsto pela equação ajustada contra o volume obtido na otimização."""
    r = ROTULOS[idioma]
    fig, ax = plt.subplots(figsize=(11 * CM, 10 * CM))
    lim = [0.0, float(max(Mr["V"].max(), Mr["V_pred"].max()) * 1.08)]
    ax.plot(lim, lim, linestyle="--", linewidth=1.0, color="gray")
    for k, c in enumerate(CLASSES):
        s = Mr[Mr.classe == c]
        ax.plot(s["V"], s["V_pred"], MARCADORES[k], markersize=6, linestyle="none",
                color=COR, alpha=0.35 + 0.65 * k / 4, label=c)
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal", adjustable="box")
    estilo(ax, r["v_obs"], r["v_pred"])
    ax.legend(fontsize=9, frameon=False, title=r["classe"], title_fontsize=9)
    fig.tight_layout()
    salvar(fig, "equacao_pre_dimensionamento.png", idioma)


def main() -> int:
    M = consolidar()
    r = ajustar(M)
    Mr = r["M"]

    print(f"V(L, f_c0,k) = {r['a']:.6e} * L^{r['b']:.4f} * f_c0,k^{r['c']:.4f}")
    print(f"R^2 (ajuste em log-log) = {r['r2']:.5f}")
    print(f"piso de diametro do dominio de busca: d_min = {r['d_min']:.1f} cm")
    print()

    erro_abs = Mr["erro_rel_pct"].abs()
    print(f"erro relativo (20 celulas): media |.|={erro_abs.mean():.2f}%  max |.|={erro_abs.max():.2f}%  "
          f"celula do max = {Mr.loc[erro_abs.idxmax(), 'cel']}")

    sem_sat = Mr[~Mr["saturada_piso_d"]]
    if len(sem_sat) < len(Mr):
        erro_sem_sat = sem_sat["erro_rel_pct"].abs()
        print(f"sem celulas saturadas no piso de d ({len(sem_sat)}/{len(Mr)} celulas): "
              f"media |.|={erro_sem_sat.mean():.2f}%  max |.|={erro_sem_sat.max():.2f}%")

    print()
    with pd.option_context("display.width", 160, "display.max_rows", 30):
        print(Mr[["cel", "L", "classe", "d", "V", "V_pred", "erro_rel_pct", "saturada_piso_d"]]
              .round({"V": 3, "V_pred": 3, "erro_rel_pct": 2, "d": 2}).to_string(index=False))

    Mr.to_excel(RAIZ / "tmp" / "equacao_pre_dimensionamento.xlsx", index=False)
    print("\ngravado em tmp/equacao_pre_dimensionamento.xlsx")

    for idioma in ("pt", "en"):
        figura_paridade(Mr, idioma)
    print("figura equacao_pre_dimensionamento.png gravada em pt e en")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
