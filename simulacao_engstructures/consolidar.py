"""Consolida os resultados da campanha do Artigo 2 em uma planilha só.

Para cada execução (caso x semente), lê resultados/simulacao_<id>/pre_sizing_results_optimized.xlsx
e extrai a solução de menor volume da fronteira (a mesma leitura da Matéria). Depois, para
cada caso, fica com a semente de menor volume e mede a dispersão entre as sementes.

Grava consolidado.xlsx com:

    Execucoes            uma linha por execução (caso x semente)
    Casos                uma linha por caso: a melhor semente, com V_min, V_max, dispersão
    Matriz_volume        V do melhor resultado da base de classes, vão x classe
    Matriz_governante    verificação governante da base de classes, vão x classe
    Matriz_dispersao     dispersão entre sementes da base de classes, vão x classe (%)
    Conferencia_Materia  CLS de 3 a 6 m contra os volumes publicados na Matéria
    Pares                por espécie e vão: projeto pela espécie x projeto pela classe

Dispersão = 100 x (V_max / V_min - 1) entre as sementes do caso. Na aba Pares, a coluna
dV_acima_ruido diz se |ΔV| supera a dispersão somada dos dois lados do par.

U_flecha_CtoR_est é a utilização de flecha do projeto da classe reavaliado com o E da
espécie, estimada por U_cls x E_cls / E_esp. A escala é exata para a rigidez com a geometria
fixa, mas ignora a troca de densidade (peso próprio); por isso o sufixo _est.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\consolidar.py
"""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
PLANILHA = PASTA / "casos_engstruct.xlsx"
RESULTADOS = PASTA / "resultados"
SAIDA = PASTA / "consolidado.xlsx"

GCOLS = {
    "longarina_g_m": "Flexão long.",
    "longarina_g_v": "Cisalhamento long.",
    "longarina_g_f": "Flecha long.",
    "tabuleiro_g_m": "Flexão tab.",
}

# Variáveis de projeto: (nome, coluna na fronteira, prefixo cfg_ na planilha de casos).
# Os intervalos de busca são lidos da própria planilha, execução a execução.
LIMITES = [
    ("d", "d_cm", "d"),
    ("bw", "bw_cm", "bw"),
    ("h", "h_cm", "h"),
    ("esp_long", "esp_cm", "esp_long"),
    ("esp_tab", "esp_tab_cm", "esp_tab"),
]

# Tabela de resultados consolidados da Matéria (solução de menor volume, m³, teto de
# esp_long 200 cm, semente 1).
MATERIA_V = {
    3: {"D20": 2.988, "D30": 2.464, "D40": 2.154, "D50": 1.903, "D60": 1.745},
    4: {"D20": 5.089, "D30": 4.076, "D40": 3.695, "D50": 3.163, "D60": 2.845},
    5: {"D20": 7.331, "D30": 6.001, "D40": 5.090, "D50": 4.562, "D60": 4.084},
    6: {"D20": 9.978, "D30": 7.907, "D40": 6.771, "D50": 6.015, "D60": 5.632},
}

ILEGIVEIS: list[tuple[str, str]] = []


def ler_fronteira(pasta: Path) -> pd.DataFrame | None:
    """Lê a fronteira: o xlsx solto e, se ele falhar, a cópia de dentro do zip."""
    nome = "pre_sizing_results_optimized.xlsx"
    erros = []
    if (pasta / nome).exists():
        try:
            return pd.read_excel(pasta / nome)
        except Exception as exc:
            erros.append(f"xlsx: {exc!r}")
    if (pasta / "pre_sizing_package.zip").exists():
        try:
            with zipfile.ZipFile(pasta / "pre_sizing_package.zip") as z:
                return pd.read_excel(io.BytesIO(z.read(nome)))
        except Exception as exc:
            erros.append(f"zip: {exc!r}")
    if erros:
        ILEGIVEIS.append((pasta.name, " | ".join(erros)))
    return None


def ler_solucao(pasta: Path, limites: dict[str, tuple[float, float]]) -> dict | None:
    df = ler_fronteira(pasta)
    if df is None:
        return None
    df = df.dropna(subset=["d_cm"])
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
            f"{nome}={'mín' if s[col] <= lo + 0.005 * (hi - lo) else 'máx'}"
            for nome, col, _ in LIMITES
            for lo, hi in [limites[nome]]
            if s[col] <= lo + 0.005 * (hi - lo) or s[col] >= hi - 0.005 * (hi - lo)
        ),
    }


def melhor_por_caso(execucoes: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por caso: a semente de menor volume, mais a dispersão entre sementes."""
    linhas = []
    for base_id, g in execucoes.groupby("caso_base", sort=False):
        ok = g[g["status"] == "ok"]
        if ok.empty:
            linha = g.iloc[0].to_dict()
            linha.update({"status": g["status"].iloc[0], "n_sementes_ok": 0})
            linhas.append(linha)
            continue
        best = ok.loc[ok["V_m3"].idxmin()].to_dict()
        v = ok["V_m3"]
        best.update({
            "semente_melhor": int(best["semente"]),
            "n_sementes": len(g), "n_sementes_ok": len(ok),
            "V_min_sementes": float(v.min()), "V_max_sementes": float(v.max()),
            "V_media_sementes": float(v.mean()),
            "dispersao_pct": 100.0 * (float(v.max()) / float(v.min()) - 1.0),
            "governante_igual_nas_sementes": ok["governante"].nunique() == 1,
        })
        linhas.append(best)
    out = pd.DataFrame(linhas)
    return out.drop(columns=["id", "semente"], errors="ignore")


def main() -> int:
    if not PLANILHA.exists():
        print(f"planilha ausente: {PLANILHA}", file=sys.stderr)
        return 1
    bruto = pd.read_excel(PLANILHA, sheet_name="Casos")
    limites_exec = {
        linha["id"]: {nome: (float(linha[f"cfg_{cfg}_min"]), float(linha[f"cfg_{cfg}_max"]))
                      for nome, _, cfg in LIMITES}
        for _, linha in bruto.iterrows()
    }
    ref = bruto[[c for c in bruto.columns if c == "id" or c.startswith("cfg_ref_")]]
    ref.columns = [c.removeprefix("cfg_ref_") for c in ref.columns]
    esp_info = pd.read_excel(PLANILHA, sheet_name="Especies")

    linhas = []
    for _, r in ref.iterrows():
        pasta = RESULTADOS / f"simulacao_{r['id']}"
        sol = ler_solucao(pasta, limites_exec[r["id"]])
        status = "ok" if sol else ("erro" if (pasta / "_erro.txt").exists() else "não rodado")
        linhas.append({**r.to_dict(), "status": status, **(sol or {})})
    execucoes = pd.DataFrame(linhas)
    print("Execuções:")
    print(execucoes["status"].value_counts().to_string())

    casos = melhor_por_caso(execucoes)
    ok = casos[casos["n_sementes_ok"] > 0]
    incompletos = casos[(casos["n_sementes_ok"] > 0) & (casos["n_sementes_ok"] < casos["n_sementes"])]
    print(f"\nCasos com resultado: {len(ok)} de {len(casos)}"
          + (f" ({len(incompletos)} com sementes faltando)" if len(incompletos) else ""))

    cls = ok[ok["bloco"] == "classe"]
    m_vol = cls.pivot(index="vao_m", columns="classe", values="V_m3")
    m_gov = cls.pivot(index="vao_m", columns="classe", values="governante")
    m_disp = cls.pivot(index="vao_m", columns="classe", values="dispersao_pct")

    conf = []
    for l_m, por_classe in MATERIA_V.items():
        for classe, v_pub in por_classe.items():
            v = cls.loc[(cls["vao_m"] == l_m) & (cls["classe"] == classe), "V_m3"]
            v = float(v.iloc[0]) if len(v) and pd.notna(v.iloc[0]) else np.nan
            conf.append({"vao_m": l_m, "classe": classe, "V_materia": v_pub, "V_agora": v,
                         "dif_pct": 100 * (v / v_pub - 1) if pd.notna(v) else np.nan})
    conf = pd.DataFrame(conf)

    pares = []
    for _, e in ok[ok["bloco"] == "especie"].iterrows():
        c = cls[cls["caso_base"] == e["id_classe"]]
        c = c.iloc[0] if len(c) else None
        info = esp_info[esp_info["id"] == e["especie_id"]].iloc[0]
        V_esp = e["V_m3"]
        V_cls = np.nan if c is None else c["V_m3"]
        disp_esp = e["dispersao_pct"]
        disp_cls = np.nan if c is None else c["dispersao_pct"]
        dV = 100 * (V_cls / V_esp - 1) if pd.notna(V_cls) else np.nan
        U_cls = np.nan if c is None else c["U_longarina_f"]
        U_CtoR = U_cls * float(c["E_MPa"]) / float(e["E_MPa"]) if c is not None else np.nan
        pares.append({
            "especie_id": e["especie_id"], "especie": e["especie"], "classe": e["classe"],
            "vao_m": e["vao_m"],
            "delta_f_pct": info["delta_f_pct"], "delta_E_pct": info["delta_E_pct"],
            "delta_rho_pct": info["delta_rho_pct"],
            "V_esp": V_esp, "V_cls": V_cls, "dV_cls_pct": dV,
            "dispersao_esp_pct": disp_esp, "dispersao_cls_pct": disp_cls,
            "dV_acima_ruido": bool(abs(dV) > disp_esp + disp_cls) if pd.notna(dV) and pd.notna(disp_cls) else None,
            "gov_esp": e["governante"], "gov_cls": None if c is None else c["governante"],
            "U_flecha_esp": e["U_longarina_f"], "U_flecha_cls": U_cls,
            "U_flecha_CtoR_est": U_CtoR,
            "excede_ELS_est": bool(U_CtoR > 1.0) if pd.notna(U_CtoR) else None,
        })
    pares = pd.DataFrame(pares)

    with pd.ExcelWriter(SAIDA) as w:
        casos.to_excel(w, index=False, sheet_name="Casos")
        execucoes.to_excel(w, index=False, sheet_name="Execucoes")
        m_vol.to_excel(w, sheet_name="Matriz_volume")
        m_gov.to_excel(w, sheet_name="Matriz_governante")
        m_disp.round(2).to_excel(w, sheet_name="Matriz_dispersao")
        conf.to_excel(w, index=False, sheet_name="Conferencia_Materia")
        pares.to_excel(w, index=False, sheet_name="Pares")

    if not ok.empty:
        d = ok["dispersao_pct"]
        print(f"\nDispersão entre sementes (V_max/V_min - 1): mediana {d.median():.2f}%, "
              f"p90 {d.quantile(0.9):.2f}%, máxima {d.max():.2f}% ({ok.loc[d.idxmax(), 'caso_base']})")
        mudou = ok[~ok["governante_igual_nas_sementes"].astype(bool)]
        if len(mudou):
            print(f"{len(mudou)} caso(s) com verificação governante diferente entre sementes")
    if conf["dif_pct"].notna().any():
        print(f"Conferência com a Matéria (3 a 6 m): maior diferença {conf['dif_pct'].abs().max():.3f}% "
              "(a Matéria usou teto de 200 cm e uma semente; diferenças de 1 a 2% são esperadas)")
    if not pares.empty and pares["dV_acima_ruido"].notna().any():
        n = int(pares["dV_acima_ruido"].fillna(False).sum())
        print(f"Pares com |ΔV| acima da dispersão entre sementes: {n} de {pares['dV_acima_ruido'].notna().sum()}")
    lim = ok[ok["no_limite"].fillna("").astype(str) != ""]
    if not lim.empty:
        print(f"\nATENÇÃO: {len(lim)} caso(s) com variável no limite do intervalo de busca "
              "(coluna no_limite da aba Casos):")
        print(lim.groupby("no_limite")["caso_base"].count().to_string())
        print("Detalhe por vão, classe e par: simulacao_engstructures\\diagnosticar_limites.py")
    if ILEGIVEIS:
        print(f"\nATENÇÃO: {len(ILEGIVEIS)} resultado(s) ilegível(is), marcados como 'erro' ou 'não rodado':")
        for nome, motivo in ILEGIVEIS:
            print(f"  {nome}: {motivo}")
    print(f"\n{SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
