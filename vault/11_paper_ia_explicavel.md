# Artigo 3 — pré-dimensionamento explícito

**Pasta e estado canônico:** [paper/ia_explicavel/README.md](../paper/ia_explicavel/README.md). Desenho científico em [`01_proposta.md`](../paper/ia_explicavel/01_proposta.md).

Criado em 21/09/2026 a partir da sugestão do professor de ampliar vãos, cargas permanentes e trens-tipo.

## A pergunta de projeto, fechada em 22/09/2026

**Até onde a ponte de madeira roliça serve, e o que define esse limite.** A restrição que fecha a fronteira não é normativa, é o diâmetro comercial de tora disponível. No piloto, o diâmetro ótimo vai de 32,8 cm em `L = 3 m` com TB-240 a 82,0 cm em `L = 10 m` com TB-450, contra teto de busca de 100 cm.

Decompõe em três, qual verificação governa e onde troca, qual propriedade medida dimensiona, e quanto custa projetar para TB-450 em vez de TB-240 (no piloto, mais 36 % de madeira a 10 m).

O solucionador direto é **instrumento**, não contribuição. Ele é o que torna a grade de 24.300 casos computável em minutos, contra 142 horas de NSGA-II sem garantia de ótimo. A comparação entre os dois vira nota de método ou apêndice.

A campanha **não precisa de sementes**, porque o solucionador é determinístico e a grade de robustez já é determinística. Sementes sobram em dois lugares, a comparação com NSGA-II, onde viram medida da folga da metaheurística, e a regressão simbólica, onde viram teste de estabilidade da forma selecionada.

Pendência que virou condição do artigo, o **diâmetro comercial máximo de tora** (P-13). Sem ele a curva de fronteira não tem eixo vertical.

## O achado que reorganizou o artigo

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

Escrever `solver_direto.py` e conferir contra os oito casos do piloto, em volume e tempo. Depois decidir B-01 e rodar a grade.

## Em aberto ao fim da discussão de 22/09

- **Diâmetro comercial máximo de tora**, por espécie ou por região, e a fonte. Sem isso não há fronteira.
- **B-01**, se corrige agora, e o que isso faz com os resultados já publicados do artigo 1.
- Passo do vão na grade, 0,5 m ou 1,0 m, e se os seis níveis de `p_gk` se sustentam fisicamente.
- Revisão bibliográfica de metamodelo substituto de otimização estrutural e de fronteiras de aplicabilidade de tipologia.
