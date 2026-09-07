# E3 — Validação Monte Carlo independente da robustez

Fecha: `\sugestao` em [03_results.tex:176](../../paper/final/03_results.tex#L176).

## Pergunta

A solução "robusta" realmente falha menos sob perturbação do que a determinística
de mesmo custo? Esta é a prova empírica direta — sem ela, a robustez é só uma
afirmação sobre o algoritmo.

## Protocolo

1. Da fronteira $\rho = 0$ (E1), escolher uma solução $\mathbf{x}_{det}$.
2. Da fronteira $\rho = 5\%$, escolher $\mathbf{x}_{rob}$ com **área equivalente**
   (dentro de ±1%). Se não existir par de mesma área, parear por
   $\delta/\delta_{lim}$ e reportar a diferença de área.
3. Para cada uma, gerar $10^4$ realizações $\tilde{\mathbf{x}} = \mathbf{x}(1 + \rho\xi)$,
   $\xi \sim U[-1,1]$, **com semente diferente da usada na otimização** — é o que
   torna a validação independente.
4. Avaliar as 6 restrições em cada realização e contar violações.

## Saída

**Tabela:** percentual de realizações que violam cada restrição.

| Restrição | $\mathbf{x}_{det}$ | $\mathbf{x}_{rob}$ |
|---|---|---|
| $g_1$ flexão longarina | | |
| $g_2$ cisalhamento longarina | | |
| $g_3$ flecha longarina | | |
| $g_4$ flexão tabuleiro | | |
| $g_5$ espaço longarinas | | |
| $g_6$ espaço tabuleiro | | |
| **Qualquer uma (sistema)** | | |

A linha "qualquer uma" é a mais importante — é a probabilidade de falha do sistema
sob tolerância de fabricação.

**Figura (opcional, forte):** histogramas sobrepostos de $g_3$ para as duas
soluções, com a linha $g = 0$ marcada. Mostra visualmente a margem que a robustez
compra.

## Cuidados

- Semente **diferente** da otimização. Validar com os mesmos números que treinaram
  é erro metodológico que revisor pega.
- Se a formulação usa média (`.mean()`), espera-se que $\mathbf{x}_{rob}$ ainda
  viole em torno de 40–50% das realizações em $g_3$ — o que é o argumento de E5
  (pior caso). Não maquiar: reportar e discutir é mais forte do que esconder.
- Reportar também a média e o desvio de $g$ em cada caso, não só a taxa de violação.
