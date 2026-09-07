# E1 — Custo da robustez

Fecha: `\sugestao` em [02_methodology.tex:177](../../paper/final/02_methodology.tex#L177)
e [03_results.tex:174](../../paper/final/03_results.tex#L174).
Este é **o resultado que justifica a palavra "robusta" no título**.

## Pergunta

Quanto material a mais custa exigir que a solução tolere um desvio de $\rho$ nas
variáveis de projeto?

## Protocolo

Para cada ponte (TB-240 e TB-450) e cada $\rho \in \{0{,}0;\ 2{,}5;\ 5{,}0;\ 10{,}0\}\%$:

1. Rodar o NSGA-II com `pop=500`, `n_gen=400`, `seed=1`.
2. $\rho = 0$ equivale ao caso determinístico — nesse caso usar `n_checagens=1`
   (não faz sentido pagar 10 avaliações idênticas).
3. Salvar população final (X, F, G) em CSV.

Custo estimado: 8 execuções. Com `n_checagens=10`, cada uma custa
$500 \times 400 \times 10 = 2\times10^6$ avaliações do modelo estrutural. **Medir o
tempo de uma geração antes de disparar tudo** — pode ser necessário reduzir
`n_checagens` ou `n_gen` (e nesse caso E4 justifica a redução).

## Saídas

**Figura 1 (por ponte):** quatro fronteiras sobrepostas no plano
(área $\times$ $\delta/\delta_{lim}$), uma cor por $\rho$. Espera-se deslocamento
monotônico da fronteira para dentro do domínio viável conforme $\rho$ cresce.

**Tabela 1:** para três níveis de $\delta/\delta_{lim}$ pareados (ex.: 0,6 / 0,8 /
0,95), a área de cada fronteira e o acréscimo percentual sobre $\rho = 0$.

| $\delta/\delta_{lim}$ | $A(\rho{=}0)$ | $A(2{,}5\%)$ | $\Delta\%$ | $A(5\%)$ | $\Delta\%$ | $A(10\%)$ | $\Delta\%$ |
|---|---|---|---|---|---|---|---|

## Cuidados

- Comparar fronteiras exige **pareamento por um dos objetivos**, não comparar
  extremos. Fixar $\delta/\delta_{lim}$ e ler a área é o mais legível.
- Se as fronteiras de $\rho = 0$ e $\rho = 5\%$ saírem praticamente coincidentes,
  isso é sintoma de que B1 não foi de fato corrigido — verificar antes de escrever
  qualquer coisa.
- Reportar o tempo de CPU de cada execução: revisor de SMO pergunta.
