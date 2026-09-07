"""Roda as simulações de pré-dimensionamento em lote, sem interface.

Uso:
    .venv\Scripts\python.exe rodar_lote.py                  # roda tudo
    .venv\Scripts\python.exe rodar_lote.py --apenas C_13    # roda uma célula
    .venv\Scripts\python.exe rodar_lote.py --retomar        # continua de onde parou
    .venv\Scripts\python.exe rodar_lote.py --verificar       # só confere o cálculo, não roda nada

Lê `batch_pre_sizing_casos.xlsx` e grava uma pasta por célula em
`simulacaoes_/lote_eixos_1p5/`, com os mesmos artefatos que a interface baixa.
"""

import argparse
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402


def verificar() -> int:
    """Reavalia as soluções já gravadas e confere se o cálculo mudou.

    Não envolve busca, então não depende do caminho do NSGA-II: é o teste que de fato
    afere fidelidade. Diferença na ordem de 1e-14 é precisão de máquina.
    """
    pacotes = sorted(Path("simulacaoes_").glob("simulacao_C_*/pre_sizing_package.zip"))
    if not pacotes:
        print("Nenhum pacote de referência encontrado em simulacaoes_/.")
        return 1

    pior = 0.0
    for pacote in pacotes:
        r = bps.verificar_modelo(pacote)
        pior = max(pior, r["dif_max_F"], r["dif_max_G"])
        nome = pacote.parent.name.removeprefix("simulacao_")
        print(
            f"{nome:<6} n={r['n_solucoes']:<3} dF={r['dif_max_F']:.2e} dG={r['dif_max_G']:.2e}"
            f"  {'ok' if r['dentro_precisao_maquina'] else 'DIVERGE'}"
        )

    veredito = "(precisão de máquina)" if pior < 1e-9 else "(DIVERGE)"
    print(f"\nmaior diferença: {pior:.2e} {veredito}")
    return 0 if pior < 1e-9 else 1


def main(
    argv=None,
    *,
    planilha_padrao: str = "batch_pre_sizing_casos.xlsx",
    destino_padrao: str = "simulacaoes_/lote_eixos_1p5",
    descricao: str = __doc__,
) -> int:
    p = argparse.ArgumentParser(description=descricao, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--planilha", default=planilha_padrao)
    p.add_argument("--destino", default=destino_padrao)
    p.add_argument("--apenas", nargs="+", metavar="ID", help="roda só estes ids (ex.: C_01 C_13)")
    p.add_argument(
        "--filtro",
        metavar="TEXTO",
        help="roda só os ids que contenham este texto (ex.: _L10_ para um vão, _esp para uma base)",
    )
    p.add_argument("--retomar", action="store_true", help="pula células que já têm pacote gravado")
    p.add_argument(
        "--verificar",
        action="store_true",
        help="confere se o cálculo ainda reproduz as simulações já gravadas e sai",
    )
    args = p.parse_args(argv)

    import madeiras

    if not madeiras._UQPY_DISPONIVEL:
        print("ERRO: UQpy ausente. Rode com o Python do .venv:", file=sys.stderr)
        print(r"  .venv\Scripts\python.exe rodar_lote.py", file=sys.stderr)
        return 1

    if args.verificar:
        return verificar()

    casos = bps.ler_planilha_casos(args.planilha)
    if args.apenas:
        pedidos = set(args.apenas)
        desconhecidos = pedidos - {c.id for c in casos}
        if desconhecidos:
            print(f"ERRO: ids inexistentes na planilha: {sorted(desconhecidos)}", file=sys.stderr)
            return 1
        casos = [c for c in casos if c.id in pedidos]

    if args.filtro:
        casos = [c for c in casos if args.filtro in c.id]
        if not casos:
            print(f"ERRO: nenhum id contem {args.filtro!r}.", file=sys.stderr)
            return 1

    destino = Path(args.destino)
    ativos = [c for c in casos if c.ativo]
    print(f"{len(ativos)} célula(s) para rodar -> {destino}")
    print("cerca de 2,5 min por célula\n", flush=True)

    def progresso(i, n, art):
        aviso = f"  ! {art.avisos[0]}" if art.avisos else ""
        erro = f"  ERRO: {art.erro}" if art.erro else ""
        print(
            f"[{i:>2}/{n}] {art.id:<6} {art.status:<10} "
            f"{art.tempos.get('total', float('nan')):7.1f}s{aviso}{erro}",
            flush=True,
        )

    artefatos, resumo = bps.rodar_lote(
        casos, destino, callback=progresso, pular_existentes=args.retomar
    )

    if resumo.empty:
        print("\nNada rodou.")
        return 0

    import pandas as pd

    resumo.to_excel(destino / "_lote_resumo.xlsx", index=False)
    bps.montar_planilha_casos(casos).to_excel(destino / "_lote_casos.xlsx", index=False)
    (destino / "_lote_ambiente.md").write_text(
        f"python     : {sys.executable}\n"
        f"pandas     : {pd.__version__}\n"
        f"data       : {pd.Timestamp.now():%Y-%m-%d %H:%M}\n",
        encoding="utf-8",
    )

    ok = resumo[resumo.status == "ok"]
    print(f"\n{len(ok)} de {len(resumo)} célula(s) ok")
    if not ok.empty:
        print(f"tempo médio por célula : {ok.t_total_s.mean()/60:.2f} min")
        print(f"  NSGA-II              : {ok.t_nsga2_s.mean()/60:.2f} min")
        if ok.t_sobol_s.notna().any():
            print(f"  Sobol                : {ok.t_sobol_s.mean()/60:.2f} min")
    print(f"tempo total do lote    : {resumo.t_total_s.sum()/60:.2f} min")
    print(f"\nresultados em {destino}")

    falhas = resumo[resumo.status != "ok"]
    if not falhas.empty:
        print(f"\ncélulas com problema: {list(falhas.id)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
