"""Roda o lote do Artigo 2 (Engineering Structures).

Sao 40 especies x 4 vaos x 2 bases de propriedades = 320 rodadas do NSGA-II, o que leva
horas. A Sobol vem desligada na planilha justamente por isso.

Uso:
    .venv\Scripts\python.exe rodar_lote_engstruct.py                    # tudo
    .venv\Scripts\python.exe rodar_lote_engstruct.py --filtro _L03_     # so o vao de 3 m
    .venv\Scripts\python.exe rodar_lote_engstruct.py --filtro _esp      # so a base especie
    .venv\Scripts\python.exe rodar_lote_engstruct.py --apenas E01_L03_esp E01_L03_cls
    .venv\Scripts\python.exe rodar_lote_engstruct.py --retomar          # continua de onde parou

O proprio artigo prevê reduzir para os vaos de 3 e 10 m caso 320 rodadas inviabilizem o
lote. Para isso, rode duas vezes com --filtro _L03_ e --filtro _L10_.
"""

import sys

from rodar_lote import main

if __name__ == "__main__":
    raise SystemExit(
        main(
            planilha_padrao="engstruct_casos.xlsx",
            destino_padrao="simulacaoes_/lote_engstruct",
            descricao=__doc__,
        )
    )
