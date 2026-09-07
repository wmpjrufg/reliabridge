"""Roda o lote do custo da robustez (Artigo 1, §4.3.3): C-13 em quatro níveis de ρ.

Uso:
    .venv\\Scripts\\python.exe rodar_lote_robustez.py
    .venv\\Scripts\\python.exe rodar_lote_robustez.py --apenas rho000   # só um nível
    .venv\\Scripts\\python.exe rodar_lote_robustez.py --retomar         # continua de onde parou

Grava em `simulacaoes_/custo_robustez_C13/`, uma pasta `simulacao_rhoXXX` por nível de ρ
(XXX = ρ em décimos de por cento: rho000, rho025, rho050, rho100).
"""

from rodar_lote import main

if __name__ == "__main__":
    raise SystemExit(
        main(
            planilha_padrao="robustez_casos.xlsx",
            destino_padrao="simulacaoes_/custo_robustez_C13",
            descricao=__doc__,
        )
    )
