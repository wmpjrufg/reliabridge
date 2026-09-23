# Artigo 3 — pré-dimensionamento explícito

**Pasta e estado canônico:** [paper/ia_explicavel/README.md](../paper/ia_explicavel/README.md). Desenho científico em [`01_proposta.md`](../paper/ia_explicavel/01_proposta.md).

Criado em 21/09/2026 a partir da sugestão do professor de ampliar vãos, cargas permanentes e trens-tipo.

## Refinamento de 22/09/2026 — o achado que reorganizou o artigo

A leitura do núcleo estabeleceu que o modelo estrutural é inteiramente algébrico e monótono nas variáveis de projeto. Duas consequências, ambas decisivas.

**A capacidade de carga não sustenta um artigo de IA.** Para geometria fixa, os esforços são lineares no multiplicador do carregamento móvel e as resistências não dependem dele. O multiplicador limite de cada verificação sai por inversão exata. Ajustar regressão simbólica a esse rótulo aprende uma função já conhecida em forma fechada, e um revisor de revista de estruturas aponta isso. O boneco de capacidade foi marcado como superado, com registro do que dele vira seção.

**O dimensionamento admite solução direta.** A única descontinuidade é a contagem inteira de peças em `restringir_espaco`. Fixadas `n_long` e `n_tab`, os espaçamentos corrigidos ficam determinados e as verificações viram um sistema monótono de três incógnitas. As contagens admissíveis são poucas, então a enumeração exaustiva resolve o problema. O marco zero do artigo é implementar isso e medir contra o NSGA-II.

O piloto já indica que o alvo atual não está convergido, com 15,2 % de folga de volume entre cenários. Treinar sobre ele ajustaria ruído do otimizador.

## Desfechos possíveis e alvo editorial

| Desfecho | Artigo | Revista |
|---|---|---|
| A — solução direta exata e rápida | Método direto, metaheurística desnecessária nesta classe de problema | Engineering Structures ou Advances in Engineering Software |
| B — exata, mas ramificada demais para comunicar | Mapa de regimes e equações compactas verificadas | Structures |
| C — a solução direta não fecha | Metamodelo explícito da otimização | Structures, ou EAAI |

Alvo padrão enquanto o marco zero não roda, **Structures**. O artigo 2 já vai para Engineering Structures, e dois manuscritos próximos da mesma equipe na mesma revista em sequência curta enfraquecem os dois.

## Mudança de material

A campanha passa a usar as propriedades medidas das 40 espécies de `paper/engstruct/dados/base_especies.csv`, com partição por espécie, no lugar das cinco classes colineares. As classes ficam como linha de comparação com o artigo 2.

## Bloqueadores

- **B-01** · `esp_long_corr`, espaçamento livre, é usado como largura tributária da longarina e como vão do tabuleiro. O valor entre eixos seria `esp_long_corr + d`. No artigo 2 o desvio se cancela na comparação pareada; no artigo 3 as dimensões absolutas vão publicadas como regra de projeto e ele não se cancela. É o bloqueador mais sério.
- **B-02** · Em `scripts/dataset.py`, `volume_robust_mean_m3` é idêntico a `volume_nominal_m3`, porque o núcleo avalia os objetivos no ponto nominal, e `g_robust_mean` é o pior caso sobre a grade de diâmetro. `02_dataset.md` descreve trinta perturbações aleatórias com média, o que o código não faz.
- **B-03** · Transições de envoltória em `L ≈ 3,34 m` e `L = 6 m` são trocas de expressão do modelo.
- **B-04** · Domínio das cargas em vão longo ainda em auditoria.

## Estado atual

- Proposta, aplicação, estratégia editorial e bloqueadores documentados.
- Matriz de 2.700 entradas JSONL por classe gerada, agora histórica.
- Piloto exploratório concluído, 8 de 8 execuções com solução viável, volumes reconstruídos. Resumo em `paper/ia_explicavel/results/PILOTO.md`.
- Nenhuma equação treinada, nenhuma alegação de desempenho.
- Solucionador direto ainda não implementado.

## Próximo marco

Implementar o solucionador direto e compará-lo ao NSGA-II nos oito casos do piloto, em volume, tempo e reprodutibilidade. Só depois redesenhar amostragem, partições e campanha.
