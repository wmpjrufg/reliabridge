"""Monta a planilha de casos do custo da robustez (Artigo 1, §4.3.3).

Conforme D-06: só a célula de referência C-13 é reotimizada, para quatro níveis de
desvio, ρ ∈ {0 %, 2,5 %, 5 %, 10 %}, mantendo todos os demais parâmetros do algoritmo
(Tabela `tab:nsga2`: pop 50, 150 gerações, N_c = 30). O caso ρ = 0 % é o determinístico:
`_criar_multiplicadores_robustez` (madeiras.py) já colapsa para uma única avaliação
quando `rho <= 0`, então basta zerar o percentual — nenhum outro parâmetro muda.

Uso:
    .venv\\Scripts\\python.exe gerar_casos_robustez.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402

# Fonte dos dados de entrada: a C-13 já reprocessada com a = 1,5 m (D-13).
REFERENCIA = RAIZ / "simulacaoes_" / "lote_eixos_1p5" / "simulacao_C_13" / "pre_sizing_package.zip"

NIVEIS_RHO = [0.0, 2.5, 5.0, 10.0]


def main() -> int:
    saida = RAIZ / "robustez_casos.xlsx"
    if saida.exists():
        print(f"{saida.name} já existe — apague antes se quiser regerar.", file=sys.stderr)
        return 1

    if not REFERENCIA.exists():
        print(f"ERRO: não achei {REFERENCIA}. Rode antes o lote principal (rodar_lote.py).",
              file=sys.stderr)
        return 1

    t = bps.textos("pt")
    chave_rho = t["percentual_robustez"]
    dados_base = bps.ler_beam_data(REFERENCIA)

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
                sobol=bps.ConfigSobol(ativo=False),  # a seção não pede Sobol por nível de ρ
            )
        )

    df = bps.montar_planilha_casos(casos)
    df.to_excel(saida, index=False, sheet_name="Casos")

    print(f"{saida.name}: {len(df)} casos (celula C-13, rho = {NIVEIS_RHO} %)")
    print("fonte dos dados de entrada:", REFERENCIA.relative_to(RAIZ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
