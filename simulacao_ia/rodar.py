"""Resolve a grade do Artigo 3 com o solucionador direto, em paralelo, com retomada.

Grava um parquet por bloco em `resultados/`. Um bloco já gravado não é recalculado, então
a execução pode ser interrompida e retomada sem perder trabalho. Ao final, `consolidar.py`
junta os blocos no dataset do PySR.

O solucionador é determinístico, então não há semente, repetição nem dispersão a reportar.
Dois processos que resolvam o mesmo caso produzem o mesmo número.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_ia\\rodar.py
    .venv\\Scripts\\python.exe simulacao_ia\\rodar.py --processos 8
    .venv\\Scripts\\python.exe simulacao_ia\\rodar.py --limite 500 --processos 4
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(PASTA))

CASOS_PADRAO = PASTA / "casos_ia.xlsx"
RESULTADOS = PASTA / "resultados"
TAMANHO_BLOCO = 250


def resolver_bloco(args: tuple[Path, int, int, float]) -> tuple[int, int, float]:
    """Resolve um intervalo de casos e grava o parquet do bloco.

    A importação acontece dentro da função porque cada processo carrega o núcleo uma vez;
    `madeiras` puxa dependências pesadas e não sobrevive ao pickle.
    """
    caminho, inicio, fim, passo_bw = args
    import batch_pre_sizing as bps
    from solver_direto import resolver_caso

    t = bps.textos("pt")
    casos = bps.ler_planilha_casos(caminho)[inicio:fim]
    t0 = time.perf_counter()
    linhas = [resolver_caso(c, t, passo_bw=passo_bw) for c in casos]
    destino = RESULTADOS / f"bloco_{inicio:06d}_{fim:06d}.parquet"
    pd.DataFrame(linhas).to_parquet(destino, index=False)
    return inicio, len(linhas), time.perf_counter() - t0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", type=Path, default=CASOS_PADRAO)
    p.add_argument("--processos", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    p.add_argument("--bloco", type=int, default=TAMANHO_BLOCO)
    p.add_argument("--limite", type=int, default=0, help="resolve só os N primeiros casos")
    p.add_argument("--passo-bw", type=float, default=2.5)
    p.add_argument("--refazer", action="store_true", help="ignora os blocos já gravados")
    args = p.parse_args()

    if not args.casos.exists():
        print(f"planilha ausente: {args.casos}\nRode antes: simulacao_ia/gerar_casos.py",
              file=sys.stderr)
        return 1

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    total = len(pd.read_excel(args.casos, sheet_name="Casos"))
    if args.limite:
        total = min(total, args.limite)

    blocos = []
    for inicio in range(0, total, args.bloco):
        fim = min(inicio + args.bloco, total)
        destino = RESULTADOS / f"bloco_{inicio:06d}_{fim:06d}.parquet"
        if destino.exists() and not args.refazer:
            continue
        blocos.append((args.casos, inicio, fim, args.passo_bw))

    feitos = total - sum(fim - inicio for _, inicio, fim, _ in blocos)
    print(f"{total} casos, blocos de {args.bloco}, {args.processos} processo(s)")
    print(f"  já gravados : {feitos}")
    print(f"  a resolver  : {total - feitos} em {len(blocos)} bloco(s)\n")
    if not blocos:
        print("Nada a fazer. Use --refazer para recalcular.")
        return 0

    t0 = time.perf_counter()
    concluidos, casos_feitos = 0, 0
    with ProcessPoolExecutor(max_workers=args.processos) as executor:
        futuros = {executor.submit(resolver_bloco, b): b for b in blocos}
        for futuro in as_completed(futuros):
            inicio, n, dt = futuro.result()
            concluidos += 1
            casos_feitos += n
            decorrido = time.perf_counter() - t0
            ritmo = casos_feitos / decorrido
            restantes = (total - feitos - casos_feitos) / ritmo if ritmo > 0 else 0
            print(f"[{concluidos:4d}/{len(blocos)}] bloco {inicio:6d} · {n} casos em "
                  f"{dt:6.1f}s · {ritmo:5.1f} casos/s · faltam ~{restantes / 60:.0f} min")

    print(f"\n{casos_feitos} casos em {(time.perf_counter() - t0) / 60:.1f} min")
    print(f"{RESULTADOS}")
    print("\nPróximo: simulacao_ia/consolidar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
