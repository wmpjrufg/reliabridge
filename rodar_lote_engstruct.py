"""Roda o lote do Artigo 2 (Engineering Structures).

Sao 40 especies x 4 vaos (3, 5, 8 e 10 m) x 3 cenarios de propriedade x 5 sementes
pareadas = 2400 rodadas do NSGA-II. No piloto cronometrado cada rodada levou cerca de
20 s, o que coloca a campanha completa em torno de 13 h. A Sobol vem desligada na
planilha por isso.

Os tres cenarios por par especie-vao sao:

    esp   propriedades medidas da especie
    rig   medidas, com o E_c0 substituido pelo da classe  (so a rigidez muda)
    cls   propriedades da classe

    experimento principal   esp x rig
    experimento secundario  esp x cls

A planilha e gerada por `paper/engstruct/scripts/gerar_casos_engstruct.py`, que por sua
vez le a base auditavel produzida por `paper/engstruct/scripts/gerar_base_especies.py`.

Uso:
    .venv\\Scripts\\python.exe rodar_lote_engstruct.py                 # tudo
    .venv\\Scripts\\python.exe rodar_lote_engstruct.py --retomar       # continua de onde parou
    .venv\\Scripts\\python.exe rodar_lote_engstruct.py --filtro _L03_  # so o vao de 3 m
    .venv\\Scripts\\python.exe rodar_lote_engstruct.py --filtro _s1    # so a primeira semente
    .venv\\Scripts\\python.exe rodar_lote_engstruct.py --apenas E05_L10_esp_s3 E05_L10_rig_s3

Para um piloto antes de comprometer a campanha inteira, rodar com `--filtro _s1` fecha
uma semente completa (480 rodadas, cerca de 2,7 h) e ja permite conferir magnitudes.
Como o lote e serial e grava caso a caso, `--retomar` retoma sem repetir o que terminou.
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
