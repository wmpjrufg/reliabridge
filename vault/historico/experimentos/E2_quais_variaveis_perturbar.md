# E2 — Quais variáveis perturbar

Não fecha uma `\sugestao` existente, mas resolve uma decisão de modelagem que
precisa estar justificada no paper (ver B1 em `../00_auditoria_codigo.md`).

## Pergunta

O paper afirma que o desvio de 5% é aplicado "a todas as variáveis de projeto". Isso
é fisicamente defensável?

O vetor é $\mathbf{x} = (d,\ b_w,\ h,\ n_{long},\ n_{tab})$:

| Variável | Perturbar? | Justificativa física |
|---|---|---|
| $d$ (diâmetro da longarina) | **Sim** | Madeira roliça tem variabilidade natural alta de diâmetro. É o caso mais forte do artigo. |
| $b_w,\ h$ (seção do tabuleiro) | **Sim** | Tolerância de serragem. |
| $n_{long},\ n_{tab}$ (espaçamentos) | **Discutível** | São decisões de montagem, com tolerância construtiva — não variabilidade do material. Um revisor pode questionar. |

Perturbar espaçamento também muda o número de peças (via `restringir_espaco`,
[madeiras.py:38](../../madeiras.py#L38)), o que faz $f_1$ saltar de forma discreta.
Isso introduz ruído descontínuo na função objetivo e pode atrapalhar a convergência
do NSGA-II — verificar se acontece.

## Protocolo

Rodar E1 com $\rho = 5\%$ em três configurações:

- **A** — perturbar todas as 5 variáveis (o que o paper afirma hoje)
- **B** — perturbar só $(d, b_w, h)$ — tolerância dimensional das peças
- **C** — perturbar só $d$ — variabilidade da madeira roliça isolada

## Saída

Fronteiras sobrepostas para A/B/C. Se ficarem próximas, adotar **B** e justificar
no texto como a hipótese fisicamente mais defensável (e mais fácil de sustentar
perante revisor). Se A for muito mais conservadora, vale reportar as duas e discutir.

Provável destino: um parágrafo curto na metodologia + uma figura no material
suplementar. Não precisa virar figura principal.

## Efeito no texto

A Eq. `eq:perturbacao` de [02_methodology.tex](../../paper/final/02_methodology.tex)
precisa ser reescrita para dizer explicitamente **quais** variáveis são perturbadas,
seja qual for a escolha.
