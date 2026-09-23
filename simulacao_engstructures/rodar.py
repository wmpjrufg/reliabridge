"""Roda a campanha de semente única do Artigo 2 em série (um caso por vez).

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar.py --filtro CLS_      # 1) só a base de classes
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar.py --retomar          # 2) o resto, pulando o que já rodou
    .venv\\Scripts\\python.exe simulacao_engstructures\\rodar.py --apenas CLS_D40_L05

Grava uma pasta simulacao_<id> por caso em simulacao_engstructures/resultados/.
Em máquina com muitos núcleos, prefira rodar_paralelo.py.
"""

import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent))

from rodar_lote import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(
        main(
            planilha_padrao=str(PASTA / "casos_engstruct.xlsx"),
            destino_padrao=str(PASTA / "resultados"),
            descricao=__doc__,
        )
    )
