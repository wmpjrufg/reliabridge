"""Diagnóstico dos casos em que a solução encostou no limite do intervalo de busca.

Lê direto as pastas de resultados/ (não depende do consolidado.xlsx) e responde, para cada
caso sinalizado: qual variável bateu, em qual borda (mínimo ou máximo), em que vão e classe,
qual verificação governa, se o outro lado do par espécie x classe também bateu e se o limite
pressiona só a solução de menor volume ou a fronteira inteira.

Grava limites_diagnostico.xlsx com três abas:

    Detalhe     uma linha por (caso, variável no limite)
    Resumo      contagem por variável x borda x vão, e por variável x borda x classe
    Pares       pares espécie x classe em que só um dos lados encostou no limite
                (esses são os que podem enviesar o ΔV)

Uso (na raiz do repositório, depois de rodar a campanha):
    .venv\\Scripts\\python.exe simulacao_engstructures\\diagnosticar_limites.py
    .venv\\Scripts\\python.exe simulacao_engstructures\\diagnosticar_limites.py --tolerancia 1.0
"""

from __future__ import annotations

import argparse
import io
import sys
import zipfile
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
PLANILHA = PASTA / "casos_engstruct.xlsx"
RESULTADOS = PASTA / "resultados"
SAIDA = PASTA / "limites_diagnostico.xlsx"

# (nome, coluna no pre_sizing_results_optimized.xlsx, coluna cfg_ na planilha de casos)
VARIAVEIS = [
    ("d", "d_cm", "d"),
    ("bw", "bw_cm", "bw"),
    ("h", "h_cm", "h"),
    ("esp_long", "esp_cm", "esp_long"),
    ("esp_tab", "esp_tab_cm", "esp_tab"),
]

GCOLS = {
    "longarina_g_m": "Flexão long.",
    "longarina_g_v": "Cisalhamento long.",
    "longarina_g_f": "Flecha long.",
    "tabuleiro_g_m": "Flexão tab.",
}

# Leitura de cada borda. "construtivo" = limite com sentido físico/prático, é esperado que o
# ótimo encoste nele e o resultado é válido. "domínio" = o ótimo queria ir além de um limite
# escolhido só para delimitar a busca; o volume fica condicionado pelo intervalo.
LEITURA = {
    ("d", "mín"): "domínio: longarina queria ser mais fina que 20 cm",
    ("d", "máx"): "domínio: longarina queria ser mais grossa que 100 cm",
    ("bw", "mín"): "domínio: prancha queria ser mais estreita que 20 cm",
    ("bw", "máx"): "domínio: prancha queria ser mais larga que 50 cm",
    ("h", "mín"): "construtivo: tabuleiro sobra em resistência, prancha na espessura mínima",
    ("h", "máx"): "domínio: tabuleiro queria ser mais grosso que 15 cm",
    ("esp_long", "mín"): "construtivo: longarinas encostadas no espaçamento mínimo",
    ("esp_long", "máx"): "domínio: longarinas queriam ficar mais espaçadas que o teto do intervalo",
    ("esp_tab", "mín"): "construtivo: fresta mínima entre pranchas",
    ("esp_tab", "máx"): "construtivo: fresta máxima entre pranchas (menos pranchas, menos volume)",
}


def ler_fronteira(pasta: Path) -> tuple[pd.DataFrame | None, str]:
    """Lê a fronteira do caso. Tenta o xlsx solto e, se ele falhar, a cópia de dentro do zip.

    Devolve (fronteira, origem). Com fronteira None, origem traz o motivo da falha.
    """
    nome = "pre_sizing_results_optimized.xlsx"
    erros = []
    solto = pasta / nome
    if solto.exists():
        try:
            return pd.read_excel(solto), "xlsx"
        except Exception as exc:  # arquivo truncado, bloqueado ou corrompido
            erros.append(f"xlsx: {exc!r}")
    pacote = pasta / "pre_sizing_package.zip"
    if pacote.exists():
        try:
            with zipfile.ZipFile(pacote) as z:
                return pd.read_excel(io.BytesIO(z.read(nome))), "zip"
        except Exception as exc:
            erros.append(f"zip: {exc!r}")
    if not erros:
        return None, "sem resultado"
    return None, " | ".join(erros)


def limites_do_caso(linha: pd.Series) -> dict[str, tuple[float, float]]:
    return {nome: (float(linha[f"cfg_{cfg}_min"]), float(linha[f"cfg_{cfg}_max"]))
            for nome, _, cfg in VARIAVEIS}


def bordas(valor: float, lo: float, hi: float, tol: float) -> str | None:
    folga = tol / 100.0 * (hi - lo)
    if valor <= lo + folga:
        return "mín"
    if valor >= hi - folga:
        return "máx"
    return None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tolerancia", type=float, default=0.5,
                   help="distância à borda, em %% do intervalo, para contar como encostado (padrão 0,5)")
    args = p.parse_args()

    if not PLANILHA.exists():
        print(f"planilha ausente: {PLANILHA}", file=sys.stderr)
        return 1
    casos = pd.read_excel(PLANILHA, sheet_name="Casos")

    detalhe, por_caso, ilegiveis, do_zip = [], {}, [], []
    for _, linha in casos.iterrows():
        front, origem = ler_fronteira(RESULTADOS / f"simulacao_{linha['id']}")
        if front is None:
            if origem != "sem resultado":
                ilegiveis.append((linha["id"], origem))
            continue
        if origem == "zip":
            do_zip.append(linha["id"])
        front = front.dropna(subset=["d_cm"])
        if front.empty:
            continue
        lim = limites_do_caso(linha)
        s = front.loc[front["of_volume_m3"].idxmin()]
        gov = max(GCOLS, key=lambda k: float(s[k]))
        batidas = {}
        for nome, col, _ in VARIAVEIS:
            lo, hi = lim[nome]
            lado = bordas(float(s[col]), lo, hi, args.tolerancia)
            if lado is None:
                continue
            batidas[nome] = lado
            # fração da fronteira inteira encostada na mesma borda
            n_front = sum(bordas(float(v), lo, hi, args.tolerancia) == lado for v in front[col])
            detalhe.append({
                "id": linha["id"], "bloco": linha["cfg_ref_bloco"], "especie": linha["cfg_ref_especie"],
                "classe": linha["cfg_ref_classe"], "vao_m": linha["cfg_ref_vao_m"],
                "variavel": nome, "borda": lado, "valor_cm": round(float(s[col]), 3),
                "limite_cm": lo if lado == "mín" else hi,
                "fronteira_no_limite": f"{n_front}/{len(front)}",
                "V_m3": round(float(s["of_volume_m3"]), 4), "governante": GCOLS[gov],
                **{f"U_{k.replace('_g_', '_')}": round(1 + float(s[k]), 4) for k in GCOLS},
                "leitura": LEITURA[(nome, lado)],
            })
        por_caso[linha["id"]] = batidas

    if do_zip:
        print(f"{len(do_zip)} caso(s) com o xlsx solto ilegível, lidos da cópia do zip: {', '.join(do_zip)}")
    if ilegiveis:
        print(f"{len(ilegiveis)} caso(s) ilegíveis também no zip (ficaram fora do diagnóstico):")
        for cid, motivo in ilegiveis:
            print(f"  {cid}: {motivo}")
        print()
    if not por_caso:
        print("Nenhum resultado encontrado em", RESULTADOS)
        return 1
    det = pd.DataFrame(detalhe)
    print(f"{len(por_caso)} caso(s) lidos; {det['id'].nunique() if not det.empty else 0} com variável no limite "
          f"(tolerância de {args.tolerancia}% do intervalo)\n")
    if det.empty:
        return 0

    det["tipo"] = det["leitura"].str.split(":").str[0]
    res_vao = det.pivot_table(index=["variavel", "borda", "tipo"], columns="vao_m", values="id",
                              aggfunc="count", fill_value=0)
    res_cls = det.pivot_table(index=["variavel", "borda", "tipo"], columns="classe", values="id",
                              aggfunc="count", fill_value=0)

    # Pares espécie x classe com assimetria: só um dos lados no limite, ou em variáveis diferentes
    pares = []
    esp = casos[casos["cfg_ref_bloco"] == "especie"]
    for _, e in esp.iterrows():
        # o par é montado dentro da mesma semente: espécie _sN contra classe _sN
        id_cls = f"{e['cfg_ref_id_classe']}_s{int(e['cfg_ref_semente'])}"
        if e["id"] not in por_caso or id_cls not in por_caso:
            continue
        b_esp, b_cls = por_caso[e["id"]], por_caso[id_cls]
        if b_esp == b_cls:
            continue
        pares.append({
            "especie": e["cfg_ref_especie"], "classe": e["cfg_ref_classe"], "vao_m": e["cfg_ref_vao_m"],
            "semente": int(e["cfg_ref_semente"]),
            "id_esp": e["id"], "limite_esp": ", ".join(f"{k}={v}" for k, v in b_esp.items()) or "-",
            "id_cls": id_cls, "limite_cls": ", ".join(f"{k}={v}" for k, v in b_cls.items()) or "-",
            "so_construtivo": all(LEITURA[(k, v)].startswith("construtivo")
                                  for k, v in {**b_esp, **b_cls}.items()),
        })
    pares = pd.DataFrame(pares)

    with pd.ExcelWriter(SAIDA) as w:
        det.to_excel(w, index=False, sheet_name="Detalhe")
        res_vao.to_excel(w, sheet_name="Resumo", startrow=1)
        res_cls.to_excel(w, sheet_name="Resumo", startrow=len(res_vao) + 6)
        pares.to_excel(w, index=False, sheet_name="Pares")

    pd.set_option("display.width", 200)
    print("Por variável, borda e vão:")
    print(res_vao.to_string(), "\n")
    print("Por variável, borda e classe:")
    print(res_cls.to_string(), "\n")
    dominio = det[det["tipo"] == "domínio"]
    if dominio.empty:
        print("Todos os casos no limite estão em limites construtivos (esperado).")
    else:
        print(f"{dominio['id'].nunique()} caso(s) em limite de DOMÍNIO (volume condicionado pelo intervalo):")
        print(dominio[["id", "variavel", "borda", "valor_cm", "fronteira_no_limite", "governante"]].to_string(index=False))
    if not pares.empty:
        criticos = pares[~pares["so_construtivo"]]
        print(f"\n{len(pares)} par(es) espécie x classe com limites diferentes nos dois lados; "
              f"{len(criticos)} envolvem limite de domínio e podem enviesar o ΔV.")
    print(f"\n{SAIDA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
