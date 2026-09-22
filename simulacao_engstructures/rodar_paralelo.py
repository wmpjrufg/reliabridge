"""Roda a campanha de semente única do Artigo 2 em paralelo, um caso por processo.

Cada caso continua sendo uma execução independente do NSGA-II com semente 1, então rodar
em paralelo não altera nenhum resultado em relação ao rodar.py: só divide os casos entre
os núcleos. Já pula os casos que têm pacote gravado, então pode ser interrompido e
relançado à vontade.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar_paralelo.py --filtro CLS_       # 1) base de classes
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar_paralelo.py                     # 2) tudo o que falta
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar_paralelo.py --processos 12

Por padrão usa (núcleos - 1) processos. Cada processo roda com uma thread de BLAS para
não disputar núcleo com os vizinhos.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
PLANILHA = PASTA / "casos_engstruct_semente1.xlsx"
DESTINO = PASTA / "resultados"


def _iniciar_processo() -> None:
    os.chdir(RAIZ)
    sys.path.insert(0, str(RAIZ))
    import matplotlib

    matplotlib.use("Agg")


def _rodar_um(caso) -> dict:
    """Roda e grava um caso. Devolve só a linha de resumo, para não trafegar figuras."""
    import batch_pre_sizing as bps

    art = bps.rodar_caso(caso, t=bps.textos("pt"), idioma="pt")
    bps.salvar_caso(art, caso.destino(DESTINO), sobrescrever=True)
    return bps.resumo_lote([art]).iloc[0].to_dict()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--processos", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    p.add_argument("--filtro", help="só os ids que contenham este texto (ex.: CLS_, _L10_, _esp)")
    p.add_argument("--planilha", type=Path, default=PLANILHA)
    args = p.parse_args()

    _iniciar_processo()
    import batch_pre_sizing as bps
    import madeiras
    import pandas as pd

    if not madeiras._UQPY_DISPONIVEL:
        print("ERRO: UQpy ausente. Rode com o Python do .venv.", file=sys.stderr)
        return 1

    casos = [c for c in bps.ler_planilha_casos(args.planilha) if c.ativo]
    if args.filtro:
        casos = [c for c in casos if args.filtro in c.id]
    pendentes = [c for c in casos if not (c.destino(DESTINO) / bps.NOME_ZIP).exists()]
    print(f"{len(casos)} caso(s) no filtro, {len(casos) - len(pendentes)} já gravado(s), "
          f"{len(pendentes)} para rodar com {args.processos} processo(s) -> {DESTINO}", flush=True)
    if not pendentes:
        return 0

    DESTINO.mkdir(parents=True, exist_ok=True)
    linhas, inicio = [], time.time()
    with ProcessPoolExecutor(max_workers=args.processos, initializer=_iniciar_processo) as pool:
        futuros = {pool.submit(_rodar_um, c): c.id for c in pendentes}
        for i, fut in enumerate(as_completed(futuros), start=1):
            cid = futuros[fut]
            try:
                linha = fut.result()
            except Exception as exc:  # falha de um caso não derruba o lote
                linha = {"id": cid, "status": "erro", "erro": repr(exc)}
            linhas.append(linha)
            decorrido = time.time() - inicio
            resta = decorrido / i * (len(pendentes) - i)
            print(f"[{i:>4}/{len(pendentes)}] {cid:<16} {str(linha.get('status')):<8} "
                  f"{linha.get('t_total_s', float('nan')):6.1f}s   faltam ~{resta/60:5.1f} min", flush=True)

    marca = time.strftime("%Y%m%d_%H%M%S")
    resumo = pd.DataFrame(linhas).sort_values("id")
    resumo.to_excel(DESTINO / f"_resumo_{marca}.xlsx", index=False)
    falhas = resumo[resumo["status"] != "ok"]
    print(f"\n{len(resumo) - len(falhas)} de {len(resumo)} ok em {(time.time() - inicio)/60:.1f} min")
    if not falhas.empty:
        print("com problema:", ", ".join(falhas["id"]))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
