"""Monta a planilha de casos do custo da robustez (Artigo 1, §4.3.3).

Conforme D-06: só a célula de referência C-13 é reotimizada, para cinco níveis de
desvio, ρ ∈ {0 %, 5 %, 10 %, 15 %, 20 %} (grade em passo uniforme de 5 pontos
percentuais, estendida até 20 % para efeito de teste), mantendo todos os demais
parâmetros do algoritmo (configuração atual: pop 50, 300 gerações). Os limites de
busca são os padrões atuais de `batch_pre_sizing.LimitesBusca`. O caso ρ = 0 % é o
determinístico: `_criar_multiplicadores_robustez` (madeiras.py) já colapsa para uma
única avaliação quando `rho <= 0`, então basta zerar o percentual — nenhum outro
parâmetro muda. Para ρ > 0, a perturbação é uma grade determinística de 5 pontos
aplicada só ao diâmetro `d` (ver docstring de `_criar_multiplicadores_robustez`).

Uso:
    .venv\\Scripts\\python.exe gerar_casos_robustez_materia.py

Para atualizar somente os limites das planilhas existentes:
    .venv\\Scripts\\python.exe atualizar_limites_casos.py
"""

import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402

# A C-13 da entrada principal permite gerar o estudo antes de executar o NSGA-II.
REFERENCIA = RAIZ / "batch_pre_sizing_casos_materia.xlsx"

NIVEIS_RHO = [0.0, 5.0, 10.0, 15.0, 20.0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--saida", type=Path, default=RAIZ / "robustez_casos_materia.xlsx")
    parser.add_argument("--referencia", type=Path, default=REFERENCIA,
                        help="planilha principal contendo o caso C_13")
    args = parser.parse_args()
    saida = args.saida
    if saida.exists():
        print(f"{saida.name} já existe — apague antes se quiser regerar.", file=sys.stderr)
        return 1

    if not args.referencia.exists():
        print(f"ERRO: não achei a planilha principal {args.referencia}.",
              file=sys.stderr)
        return 1

    t = bps.textos("pt")
    chave_rho = t["percentual_robustez"]
    casos_base = bps.ler_planilha_casos(args.referencia)
    referencia = next((caso for caso in casos_base if caso.id == "C_13"), None)
    if referencia is None:
        print(f"ERRO: caso C_13 ausente em {args.referencia}.", file=sys.stderr)
        return 1
    dados_base = referencia.dados

    casos = []
    for rho in NIVEIS_RHO:
        dados = dict(dados_base)
        dados[chave_rho] = rho
        # Codifica o nível na id como décimos de %, sem ponto decimal: 2,5% -> rho025.
        caso_id = f"rho{round(rho * 10):03d}"
        casos.append(
            bps.CasoBatch(
                id=caso_id,
                dados=dados,
                limites=referencia.limites,
                algoritmo=referencia.algoritmo,
                sobol=bps.ConfigSobol(ativo=False),  # a seção não pede Sobol por nível de ρ
            )
        )

    df = bps.montar_planilha_casos(casos)
    df.to_excel(saida, index=False, sheet_name="Casos")

    print(f"{saida.name}: {len(df)} casos (celula C-13, rho = {NIVEIS_RHO} %)")
    print("fonte dos dados de entrada:", args.referencia)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
