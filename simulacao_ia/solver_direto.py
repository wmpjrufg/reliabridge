"""Solução exata do pré-dimensionamento, sem metaheurística e sem semente.

O modelo estrutural é algébrico e monótono nas variáveis de projeto, e a única
descontinuidade é a contagem inteira de peças em `madeiras.restringir_espaco`. Isso
permite resolver o problema por construção em vez de por busca.

Três observações sustentam o algoritmo.

1. `restringir_espaco` escolhe o número de peças entre o piso e o teto de
   `n_cont = (comp + esp) / (peca + esp)`. Se o espaçamento de entrada for exatamente o
   espaçamento corrigido de uma contagem `n`, então `n_cont = n` e a contagem fica
   determinada. Enumerar contagens equivale a enumerar geometrias construtivas.

2. Com `n_long` fixo, aumentar o diâmetro aumenta a seção **e** reduz a largura
   tributária, porque o vão livre entre longarinas encolhe. As três verificações da
   longarina e a do tabuleiro melhoram juntas, então a viabilidade é monótona em `d` e
   admite bisseção.

3. O tabuleiro de menor volume é o de maior fresta admissível, porque menos peças
   significam menos madeira e menos peso próprio. A contagem mínima sai de
   `esp_tab_corr <= esp_tab_max`, não precisa ser varrida.

Resta enumerar `n_long` e varrer `bw`, que é grosseiro porque a largura da prancha quase
se cancela na verificação do tabuleiro (carga e módulo resistente crescem juntos com
`bw`). Para cada combinação, `d` e `h` saem por bisseção alternada até o ponto fixo.

A viabilidade usada na bisseção é a **mesma** do NSGA-II, pior caso sobre a grade
determinística de tolerância no diâmetro (`ProjetoOtimo._evaluate`). A solução devolvida é
reavaliada por esse caminho antes de ser gravada, então o que sai daqui é comparável com o
que sai da otimização, sem reinterpretação.

Nenhuma física é reimplementada. Tudo passa por
`ProjetoOtimo.calcular_objetivos_restricoes_otimizacao`, de modo que qualquer correção no
núcleo, a de largura tributária inclusive, propaga sozinha.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_ia\\solver_direto.py --limite 20
    .venv\\Scripts\\python.exe simulacao_ia\\solver_direto.py --comparar-nsga 6
"""

from __future__ import annotations

import argparse
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))

import batch_pre_sizing as bps  # noqa: E402
from madeiras import _criar_projeto_otimo_pre_sizing  # noqa: E402

CASOS_PADRAO = PASTA / "casos_ia.xlsx"

# Ordem das restrições devolvidas pelo núcleo.
NOMES_G = ["flexao_long", "cisalhamento_long", "flecha_long", "flexao_tab",
           "disposicao_long", "disposicao_tab"]
# Só as quatro estruturais entram na escolha do governante; as duas últimas são geométricas.
N_ESTRUTURAIS = 4

TOL = 1e-9


@dataclass
class Solucao:
    """Geometria de menor volume encontrada, já reavaliada pelo caminho do NSGA-II."""

    status: str = "sem_solucao"
    d_cm: float = math.nan
    bw_cm: float = math.nan
    h_cm: float = math.nan
    esp_long_cm: float = math.nan
    esp_tab_cm: float = math.nan
    esp_long_corr_cm: float = math.nan
    esp_tab_corr_cm: float = math.nan
    n_long: int = 0
    n_tab: int = 0
    volume_m3: float = math.nan
    flecha_ratio: float = math.nan
    governante: str = ""
    g: list[float] = field(default_factory=list)
    d_no_teto: bool = False
    avaliacoes: int = 0
    tempo_s: float = math.nan


def espacamento_corrigido(comp: float, n: int, peca: float) -> float:
    """Fresta uniforme que resulta de dispor `n` peças de largura `peca` em `comp`."""
    return (comp - n * peca) / (n - 1)


def faixa_diametro(comp: float, n: int, esp_min: float, esp_max: float) -> tuple[float, float]:
    """Diâmetros que mantêm a fresta de `n` longarinas dentro dos limites, em cm."""
    return ((comp - esp_max * (n - 1)) / n, (comp - esp_min * (n - 1)) / n)


def contagem_minima_tabuleiro(comp: float, bw: float, esp_max: float) -> int:
    """Menor número de pranchas cuja fresta ainda cabe no limite superior.

    Menos peças significam menos volume e menos peso próprio, então esta é a contagem que
    interessa. A folga de 1e-9 evita que o piso caia uma peça abaixo por erro de ponto
    flutuante quando a divisão dá um inteiro exato.
    """
    return max(2, math.ceil((comp + esp_max) / (bw + esp_max) - 1e-9))


class Avaliador:
    """Envelope sobre o núcleo, com a mesma definição de viabilidade do NSGA-II."""

    def __init__(self, projeto):
        self.projeto = projeto
        self.n = 0

    def restricoes(self, d: float, bw: float, h: float, esp_long: float,
                   esp_tab: float) -> np.ndarray:
        """Pior caso das seis restrições sobre a grade de tolerância no diâmetro."""
        x = np.array([d, bw, h, esp_long, esp_tab], dtype=float)
        pior = None
        for multiplicador in self.projeto.multiplicadores_robustez:
            self.n += 1
            _, g, *_ = self.projeto.calcular_objetivos_restricoes_otimizacao(*(x * multiplicador))
            g = np.asarray(g, dtype=float)
            pior = g if pior is None else np.maximum(pior, g)
        return pior

    def viavel_estrutural(self, d: float, bw: float, h: float, esp_long: float,
                          esp_tab: float) -> bool:
        """Só as quatro verificações estruturais; a disposição é garantida por construção."""
        g = self.restricoes(d, bw, h, esp_long, esp_tab)
        return bool(np.all(np.isfinite(g)) and np.max(g[:N_ESTRUTURAIS]) <= TOL)


def menor_viavel(lo: float, hi: float, viavel, passos: int = 40, refino: int = 30) -> float | None:
    """Menor valor em [lo, hi] que satisfaz `viavel`, por bisseção.

    A viabilidade é monótona no intervalo, mas `restringir_espaco` introduz degraus, então
    o topo é conferido antes e o resultado é empurrado para cima até passar de fato. Assim
    um degrau nunca devolve um ponto inviável.
    """
    if lo > hi:
        return None
    if not viavel(hi):
        return None
    if viavel(lo):
        return lo
    a, b = lo, hi
    for _ in range(passos):
        meio = 0.5 * (a + b)
        if viavel(meio):
            b = meio
        else:
            a = meio
        if b - a < 1e-4:
            break
    passo = max((hi - lo) * 1e-4, 1e-4)
    for _ in range(refino):
        if viavel(b):
            return b
        b = min(b + passo, hi)
    return hi if viavel(hi) else None


def resolver(projeto, *, passo_bw: float = 5.0, passo_h: float = 1.0,
             refino: int = 3) -> Solucao:
    """Geometria admissível de menor volume, por enumeração das disposições inteiras.

    Para cada disposição, a espessura da prancha é varrida do teto para baixo e o
    diâmetro mínimo compatível sai por bisseção. Minimizar `d` e `h` em alternância seria
    errado: reduzir o diâmetro alarga o vão do tabuleiro e pode exigir uma prancha mais
    grossa do que o teto permite, o que descartaria disposições viáveis. Varrer `h` da
    folga para a restrição preserva a monotonicidade e, de quebra, trata a espessura como
    a dimensão comercial discreta que ela é.
    """
    inicio = time.perf_counter()
    av = Avaliador(projeto)

    pista = float(projeto.bw_pista)
    vao = float(projeto.l)
    esp_min_long, esp_max_long = float(projeto.n_min_long), float(projeto.n_max_long)
    esp_min_tab, esp_max_tab = float(projeto.n_min_tab), float(projeto.n_max_tab)

    n_long_max = int(pista // (projeto.d_min + esp_min_long)) + 1

    melhor, melhor_volume = None, math.inf
    vistos: dict[tuple[int, int], tuple[float, float, float]] = {}

    def combinacao(n_long: int, bw: float, n_tab: int, hs) -> None:
        """Melhor geometria de uma disposição, varrendo `h` e resolvendo `d` por bisseção."""
        nonlocal melhor, melhor_volume
        d_lo, d_hi = faixa_diametro(pista, n_long, esp_min_long, esp_max_long)
        d_lo, d_hi = max(d_lo, projeto.d_min), min(d_hi, projeto.d_max)
        if d_lo > d_hi:
            return
        esp_tab_corr = espacamento_corrigido(vao, n_tab, bw)
        if not (esp_min_tab - TOL <= esp_tab_corr <= esp_max_tab + TOL):
            return

        piores, volume_anterior = 0, math.inf
        for h in hs:
            def viavel_d(valor, h=h):
                esp_long = espacamento_corrigido(pista, n_long, valor)
                return av.viavel_estrutural(valor, bw, h, esp_long, esp_tab_corr)

            d = menor_viavel(d_lo, d_hi, viavel_d)
            if d is None:
                return  # prancha mais fina só torna a condição mais severa
            esp_long = espacamento_corrigido(pista, n_long, d)
            saida: dict = {}
            projeto._evaluate(
                np.array([d, bw, h, esp_long, esp_tab_corr], dtype=float), saida)
            g = np.asarray(saida["G"], dtype=float)
            volume = float(saida["F"][0])
            if not np.all(np.isfinite(g)) or np.max(g) > TOL:
                continue

            anterior = vistos.get((n_long, n_tab))
            if anterior is None or volume < anterior[0]:
                vistos[(n_long, n_tab)] = (volume, float(bw), float(h))

            if volume < melhor_volume:
                _, _, *resto = projeto.calcular_objetivos_restricoes_otimizacao(
                    d, bw, h, esp_long, esp_tab_corr)
                cargas = resto[-1]
                melhor_volume = volume
                melhor = Solucao(
                    status="ok", d_cm=d, bw_cm=float(bw), h_cm=float(h),
                    esp_long_cm=esp_long, esp_tab_cm=esp_tab_corr,
                    esp_long_corr_cm=100 * float(cargas["esp_long_corr [m]"]),
                    esp_tab_corr_cm=100 * float(cargas["esp_tab_corr [m]"]),
                    n_long=int(cargas["num_longs"]), n_tab=int(cargas["num_tabs"]),
                    volume_m3=volume, flecha_ratio=float(saida["F"][1]),
                    governante=NOMES_G[int(np.argmax(g[:N_ESTRUTURAIS]))],
                    g=[float(v) for v in g],
                    d_no_teto=bool(d >= projeto.d_max - 1e-6),
                )

            # O volume troca madeira da prancha por madeira da longarina, então tem um
            # mínimo no interior da varredura. Duas pioras seguidas encerram.
            piores = piores + 1 if volume > volume_anterior else 0
            volume_anterior = volume
            if piores >= 2:
                return

    # Passada grossa, para localizar as disposições promissoras.
    hs_grossa = np.arange(projeto.h_max, projeto.h_min - 1e-9, -passo_h)
    for n_long in range(2, n_long_max + 1):
        for bw in np.arange(projeto.bw_min, projeto.bw_max + 1e-9, passo_bw):
            n_tab_min = contagem_minima_tabuleiro(vao, bw, esp_max_tab)
            for n_tab in (n_tab_min, n_tab_min + 1):
                combinacao(n_long, bw, n_tab, hs_grossa)

    # Refino local. A passada grossa erra por discretizar `bw` e `h`, que o otimizador
    # trata como contínuos, então as melhores disposições são revisitadas em malha fina.
    # Sem isto o resultado fica alguns por cento acima do ótimo, e um solucionador que
    # perde para a metaheurística não serve de referência exata.
    for (n_long, n_tab), (_, bw_bom, _) in sorted(vistos.items(), key=lambda kv: kv[1][0])[:refino]:
        hs_fina = np.arange(projeto.h_max, projeto.h_min - 1e-9, -passo_h / 8)
        for bw in np.arange(max(projeto.bw_min, bw_bom - passo_bw),
                            min(projeto.bw_max, bw_bom + passo_bw) + 1e-9, passo_bw / 8):
            n_tab_local = contagem_minima_tabuleiro(vao, bw, esp_max_tab)
            for n in {n_tab, n_tab_local, n_tab_local + 1}:
                combinacao(n_long, bw, n, hs_fina)

    if melhor is None:
        return Solucao(status="sem_solucao", avaliacoes=av.n,
                       tempo_s=time.perf_counter() - inicio)
    melhor.avaliacoes = av.n
    melhor.tempo_s = time.perf_counter() - inicio
    return melhor


def projeto_do_caso(caso: bps.CasoBatch, t: dict):
    """Instancia o problema do núcleo a partir de uma linha da planilha de casos."""
    ds, bws, hs, n_long, n_tab = caso.limites.como_listas()
    dados = bps.normalizar_dados_pre_sizing(caso.dados, t)
    return _criar_projeto_otimo_pre_sizing(
        dados, ds, bws, hs, n_long, n_tab, t,
        n_checagens=caso.algoritmo.n_checagens,
        perc_robustez=float(dados[t["percentual_robustez"]]),
    )


def resolver_caso(caso: bps.CasoBatch, t: dict, **kwargs) -> dict:
    try:
        solucao = resolver(projeto_do_caso(caso, t), **kwargs)
    except Exception as exc:
        solucao = Solucao(status=f"erro: {type(exc).__name__}: {exc}")
    linha = {"id": caso.id, **{k: v for k, v in vars(solucao).items() if k != "g"}}
    linha.update({f"g_{nome}": valor for nome, valor in zip(NOMES_G, solucao.g or [math.nan] * 6)})
    return linha


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", type=Path, default=CASOS_PADRAO)
    p.add_argument("--limite", type=int, default=0, help="resolve só os N primeiros casos")
    p.add_argument("--passo-bw", type=float, default=2.5, help="passo da varredura de bw, em cm")
    p.add_argument("--comparar-nsga", type=int, default=0, metavar="N",
                   help="roda também o NSGA-II em N casos sorteados e compara os volumes")
    p.add_argument("--semente-amostra", type=int, default=1)
    p.add_argument("--saida", type=Path, default=None)
    args = p.parse_args()

    if not args.casos.exists():
        print(f"planilha ausente: {args.casos}\nRode antes: simulacao_ia/gerar_casos.py",
              file=sys.stderr)
        return 1

    t = bps.textos("pt")
    casos = bps.ler_planilha_casos(args.casos)
    if args.limite:
        casos = casos[: args.limite]

    inicio = time.perf_counter()
    linhas = [resolver_caso(c, t, passo_bw=args.passo_bw) for c in casos]
    df = pd.DataFrame(linhas)
    total = time.perf_counter() - inicio

    ok = df[df["status"] == "ok"]
    print(f"{len(df)} caso(s) em {total:.1f} s ({total / max(len(df), 1):.2f} s/caso)")
    print(f"  ok           : {len(ok)}")
    print(f"  sem solução  : {int((df['status'] == 'sem_solucao').sum())}")
    print(f"  erro         : {int(df['status'].str.startswith('erro').sum())}")
    if not ok.empty:
        print(f"  avaliações   : {ok['avaliacoes'].median():.0f} por caso (mediana)")
        print(f"  d no teto    : {int(ok['d_no_teto'].sum())}")
        print("\n  governante:")
        for nome, n in ok["governante"].value_counts().items():
            print(f"    {nome:20s} {n}")

    if args.saida:
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(args.saida, index=False)
        print(f"\n{args.saida}")

    if args.comparar_nsga:
        comparar(casos, df, args.comparar_nsga, args.semente_amostra, t)
    return 0


def comparar(casos, df: pd.DataFrame, n: int, semente: int, t: dict) -> None:
    """Roda o NSGA-II nos mesmos casos e mede a folga da metaheurística.

    Não é validação do modelo físico, que é o mesmo dos dois lados. Mede só quanto a busca
    estocástica deixa na mesa em relação ao ótimo construído.
    """
    from madeiras import chamando_nsga2

    rng = np.random.default_rng(semente)
    indices = rng.choice(len(casos), size=min(n, len(casos)), replace=False)
    print(f"\nComparação com NSGA-II em {len(indices)} caso(s)")
    print(f"{'id':38s} {'direto':>9s} {'nsga':>9s} {'folga':>8s} {'t_nsga':>8s}")

    folgas = []
    for i in indices:
        caso = casos[i]
        linha = df[df["id"] == caso.id].iloc[0]
        if linha["status"] != "ok":
            continue
        ds, bws, hs, nl, nt = caso.limites.como_listas()
        dados = bps.normalizar_dados_pre_sizing(caso.dados, t)
        t0 = time.perf_counter()
        try:
            # `salvar_historico=True` é obrigatório: sem ele `chamando_nsga2` entrega
            # `callback=None` ao pymoo, que tenta chamá-lo e quebra. Bug do núcleo,
            # contornado aqui em vez de alterado.
            front, _ = chamando_nsga2(caso.dados, ds, bws, hs, nl, nt, t,
                                      salvar_historico=True,
                                      pop_size=caso.algoritmo.pop_size,
                                      n_gen=caso.algoritmo.n_gen,
                                      n_checagens=caso.algoritmo.n_checagens,
                                      seed=caso.algoritmo.seed, verbose=False)
        except Exception as exc:
            print(f"{caso.id:38s} {'':>9s} erro: {type(exc).__name__}: {exc}")
            continue
        dt = time.perf_counter() - t0
        # `chamando_nsga2` devolve a fronteira já em DataFrame. As soluções que ela
        # entrega passaram pelas restrições do próprio otimizador, então basta o volume.
        if front is None or len(front) == 0 or "of_volume_m3" not in front.columns:
            print(f"{caso.id:38s} {linha['volume_m3']:9.4f} {'sem sol':>9s}")
            continue
        v_nsga = float(front["of_volume_m3"].min())
        folga = 100 * (v_nsga / linha["volume_m3"] - 1)
        folgas.append(folga)
        print(f"{caso.id:38s} {linha['volume_m3']:9.4f} {v_nsga:9.4f} "
              f"{folga:+7.2f}% {dt:7.1f}s")

    if folgas:
        f = np.array(folgas)
        print(f"\nfolga do NSGA-II: mediana {np.median(f):+.2f}%, "
              f"máxima {f.max():+.2f}%, mínima {f.min():+.2f}%")
        print("Folga positiva significa volume maior que o ótimo construído.")
        if f.min() < -0.05:
            print("ATENÇÃO: folga negativa. O NSGA-II achou solução melhor que o solver, "
                  "então o solver não é exato. Investigar antes de rodar a grade.")


if __name__ == "__main__":
    raise SystemExit(main())
