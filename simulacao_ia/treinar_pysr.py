"""Ajusta equações explícitas sobre o dataset do Artigo 3 e mede o erro fora do treino.

Duas famílias, sempre nesta ordem.

**Lei de potência multidimensional**, por mínimos quadrados em escala logarítmica. É a
referência que a regressão simbólica precisa bater, roda em segundos e não depende de
instalação nenhuma. Se ela bastar, o artigo conclui isso, e concluir isso é um resultado.

**Regressão simbólica** via PySR, se estiver instalado. Estocástica, então roda com k
sementes e o relatório diz quantas vezes a forma selecionada se repetiu. Publicar a
expressão de uma execução única é furo que revisor cobra.

As três partições respondem perguntas diferentes e não são intercambiáveis.

    split_aleatorio   exploratório e otimista. As 540 linhas de uma espécie compartilham
                      as mesmas propriedades, então toda linha de teste tem quase-gêmea no
                      treino. Serve para calibrar operadores e complexidade, não para o
                      artigo.
    split_especie     a equação serve para madeira que ela nunca viu?
    split_vao         a equação interpola em vão?

As linhas de classe ficam fora de todas, marcadas `referencia`. Elas produzem a leitura
oficial da fronteira e não podem estar no treino.

Métricas em unidades físicas, porque R² alto sobre um alvo bem-comportado não diz nada. O
que decide o uso é o erro relativo mediano, o percentil 95, o máximo e, sobretudo, a
**frequência de subestimativa**, que no pré-dimensionamento é o sentido desfavorável.

Instalar o PySR, se for usar:
    .venv\\Scripts\\python.exe -m pip install pysr
    .venv\\Scripts\\python.exe -c "import pysr; pysr.install()"
O PySR baixa um Julia próprio na primeira execução, o que leva alguns minutos.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_ia\\treinar_pysr.py
    .venv\\Scripts\\python.exe simulacao_ia\\treinar_pysr.py --alvo volume_m3
    .venv\\Scripts\\python.exe simulacao_ia\\treinar_pysr.py --particao split_especie --pysr
    .venv\\Scripts\\python.exe simulacao_ia\\treinar_pysr.py --pysr --sementes 3 --amostra 3000
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
DATASET_PADRAO = PASTA / "dataset_ia.parquet"
SAIDA = PASTA / "equacoes"

# Entradas disponíveis no momento da previsão. Nada calculado pelo modelo entra aqui: o
# estado limite governante é saída, nunca entrada.
#
# `p_roda_kn` representa o veículo. A carga de multidão NÃO entra: ela é função do mesmo
# veículo e, com dois perfis, dar as duas ao ajuste permite combinações que não se
# sustentam fora desses dois pontos.
ENTRADAS = ["vao_m", "largura_m", "p_gk_kpa", "p_roda_kn", "E_mpa", "f_mk_mpa",
            "densidade_kgm3"]

# Alvos contínuos. `n_long` e `n_tab` são inteiros e não entram aqui; a disposição sai da
# regra geométrica construtiva a partir de `d` e da largura de pista.
ALVOS = ["d_cm", "volume_m3", "h_cm", "bw_cm"]

PARTICOES = ["split_aleatorio", "split_especie", "split_vao"]


# ---------------------------------------------------------------------------------------
# Referência: lei de potência multidimensional
# ---------------------------------------------------------------------------------------

def ajustar_potencia(X: pd.DataFrame, y: np.ndarray) -> tuple[np.ndarray, str]:
    """Mínimos quadrados em log. Devolve os coeficientes e a expressão legível.

    O deslocamento de 1 em `p_gk` evita o log de zero e preserva a interpretação, porque a
    carga permanente adicional pode ser nula e as demais entradas são estritamente
    positivas.
    """
    A = np.column_stack([np.ones(len(X))] + [np.log(deslocar(X[c].to_numpy(), c))
                                             for c in X.columns])
    coef, *_ = np.linalg.lstsq(A, np.log(y), rcond=None)
    termos = " ".join(f"({c}{sufixo(c)})^{e:+.4f}" for c, e in zip(X.columns, coef[1:]))
    return coef, f"{np.exp(coef[0]):.6g} * {termos}"


def deslocar(v: np.ndarray, coluna: str) -> np.ndarray:
    return v + 1.0 if coluna == "p_gk_kpa" else v


def sufixo(coluna: str) -> str:
    return "+1" if coluna == "p_gk_kpa" else ""


def prever_potencia(coef: np.ndarray, X: pd.DataFrame) -> np.ndarray:
    A = np.column_stack([np.ones(len(X))] + [np.log(deslocar(X[c].to_numpy(), c))
                                             for c in X.columns])
    return np.exp(A @ coef)


# ---------------------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------------------

def metricas(y: np.ndarray, previsto: np.ndarray) -> dict:
    """Erro em unidades físicas mais a frequência de subestimativa."""
    erro = previsto - y
    rel = 100 * erro / y
    return {
        "n": len(y),
        "MAE": float(np.mean(np.abs(erro))),
        "rel_mediano_%": float(np.median(np.abs(rel))),
        "rel_p95_%": float(np.percentile(np.abs(rel), 95)),
        "rel_max_%": float(np.max(np.abs(rel))),
        "vies_%": float(np.mean(rel)),
        "subestima_%": float(100 * np.mean(erro < 0)),
        "R2": float(1 - np.sum(erro ** 2) / np.sum((y - y.mean()) ** 2)),
    }


def imprimir(titulo: str, m: dict) -> None:
    print(f"  {titulo:22s} n={m['n']:6d}  MAE={m['MAE']:9.4f}  "
          f"mediana={m['rel_mediano_%']:6.2f}%  p95={m['rel_p95_%']:7.2f}%  "
          f"máx={m['rel_max_%']:8.2f}%  viés={m['vies_%']:+6.2f}%  "
          f"subest={m['subestima_%']:5.1f}%  R²={m['R2']:.5f}")


# ---------------------------------------------------------------------------------------
# Regressão simbólica
# ---------------------------------------------------------------------------------------

def ajustar_pysr(X: pd.DataFrame, y: np.ndarray, semente: int, iteracoes: int,
                 complexidade: int):
    from pysr import PySRRegressor

    modelo = PySRRegressor(
        niterations=iteracoes,
        maxsize=complexidade,
        binary_operators=["+", "-", "*", "/"],
        unary_operators=["square", "sqrt", "log", "exp"],
        # Divisão e raiz sobre argumento não positivo geram singularidade fora do domínio
        # amostrado. A restrição corta expressões que só funcionam por sorte.
        constraints={"/": (-1, 4), "sqrt": 6, "log": 6, "exp": 4},
        nested_constraints={"exp": {"exp": 0, "log": 0}, "log": {"log": 0, "exp": 0}},
        elementwise_loss="loss(pred, target) = (pred - target)^2",
        model_selection="best",
        progress=False,
        random_state=semente,
        deterministic=True,
        parallelism="serial",
        verbosity=0,
    )
    modelo.fit(X.to_numpy(), y, variable_names=list(X.columns))
    return modelo


# ---------------------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", type=Path, default=DATASET_PADRAO)
    p.add_argument("--alvo", default="d_cm", choices=ALVOS)
    p.add_argument("--particao", default="todas",
                   choices=["todas"] + PARTICOES)
    p.add_argument("--amostra", type=int, default=3000,
                   help="linhas estratificadas usadas na busca simbólica (padrão 3000)")
    p.add_argument("--pysr", action="store_true", help="roda também a regressão simbólica")
    p.add_argument("--sementes", type=int, default=3, help="sementes do PySR (padrão 3)")
    p.add_argument("--iteracoes", type=int, default=40)
    p.add_argument("--complexidade", type=int, default=20)
    p.add_argument("--semente-amostra", type=int, default=1)
    args = p.parse_args()

    if not args.dataset.exists():
        print(f"dataset ausente: {args.dataset}\nRode antes: simulacao_ia/consolidar.py",
              file=sys.stderr)
        return 1

    df = pd.read_parquet(args.dataset)
    df = df[df["status"] == "ok"].dropna(subset=ENTRADAS + [args.alvo])
    print(f"{len(df)} linhas com solução, alvo = {args.alvo}\n")

    particoes = PARTICOES if args.particao == "todas" else [args.particao]
    SAIDA.mkdir(parents=True, exist_ok=True)
    resumo = []

    for particao in particoes:
        treino = df[df[particao] == "treino"]
        teste = df[df[particao] == "teste"]
        referencia = df[df[particao] == "referencia"]
        if treino.empty or teste.empty:
            print(f"{particao}: partição vazia, pulando")
            continue

        print(f"── {particao} · treino {len(treino)} · teste {len(teste)} · "
              f"referência {len(referencia)}")

        y_tr = treino[args.alvo].to_numpy()
        coef, expressao = ajustar_potencia(treino[ENTRADAS], y_tr)
        m_tr = metricas(y_tr, prever_potencia(coef, treino[ENTRADAS]))
        m_te = metricas(teste[args.alvo].to_numpy(), prever_potencia(coef, teste[ENTRADAS]))
        imprimir("potência · treino", m_tr)
        imprimir("potência · teste", m_te)
        print(f"    {args.alvo} = {expressao}")
        resumo.append({"particao": particao, "modelo": "potencia", "conjunto": "treino", **m_tr})
        resumo.append({"particao": particao, "modelo": "potencia", "conjunto": "teste", **m_te})

        if not referencia.empty:
            m_ref = metricas(referencia[args.alvo].to_numpy(),
                             prever_potencia(coef, referencia[ENTRADAS]))
            imprimir("potência · classes", m_ref)
            resumo.append({"particao": particao, "modelo": "potencia",
                           "conjunto": "referencia", **m_ref})

        if args.pysr:
            amostra = treino.sample(min(args.amostra, len(treino)),
                                    random_state=args.semente_amostra)
            formas = {}
            for semente in range(1, args.sementes + 1):
                t0 = time.perf_counter()
                try:
                    modelo = ajustar_pysr(amostra[ENTRADAS], amostra[args.alvo].to_numpy(),
                                          semente, args.iteracoes, args.complexidade)
                except ImportError:
                    print("    PySR não instalado. Veja as instruções no topo do arquivo.")
                    break
                except Exception as exc:
                    print(f"    semente {semente}: {type(exc).__name__}: {exc}")
                    continue
                expr = str(modelo.sympy())
                formas[expr] = formas.get(expr, 0) + 1
                m = metricas(teste[args.alvo].to_numpy(),
                             modelo.predict(teste[ENTRADAS].to_numpy()))
                imprimir(f"pysr s{semente} · teste", m)
                print(f"    {args.alvo} = {expr}   [{time.perf_counter() - t0:.0f}s]")
                resumo.append({"particao": particao, "modelo": f"pysr_s{semente}",
                               "conjunto": "teste", "expressao": expr, **m})
                modelo.equations_.to_csv(
                    SAIDA / f"pysr_{args.alvo}_{particao}_s{semente}.csv", index=False)
            if formas:
                repetida = max(formas.values())
                print(f"    formas distintas: {len(formas)} em {sum(formas.values())} "
                      f"execuções; a mais frequente saiu {repetida}x")
        print()

    if resumo:
        destino = SAIDA / f"resumo_{args.alvo}.csv"
        pd.DataFrame(resumo).to_csv(destino, index=False)
        print(f"{destino}")

    print("\nLeitura. O split_aleatorio é otimista por construção e não vai para o artigo.")
    print("O que decide o uso é a subestimativa no split_especie e no split_vao, porque no")
    print("pré-dimensionamento prever menos que o necessário é o sentido desfavorável.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
