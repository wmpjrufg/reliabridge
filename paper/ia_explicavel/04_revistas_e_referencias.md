# Enquadramento editorial e leitura inicial

Consulta em 21/09/2026. As avaliações de adequação abaixo são recomendações, não garantias de aceite. Não foram usados fatores de impacto ou Qualis como critérios, nem foram verificados custos de publicação.

## Prioridade sugerida

| Revista | Adequação à proposta | O que precisa aparecer no artigo |
|---|---|---|
| **Structures** | Primeira opção: equações de projeto, otimização e caminho claro para uso em engenharia | Ganho demonstrado frente à expressão simples, avaliação fora do treinamento, verificação das geometrias e aplicação convincente |
| **Engineering Structures** | Alternativa mais ambiciosa se surgirem resultados mecânicos generalizáveis e validação consistente | Explicar regimes/interações e justificar a generalização; a IA precisa acrescentar conhecimento ao projeto |
| **Engineering Applications of Artificial Intelligence** | Opção condicional se a contribuição metodológica de IA se tornar central | Método com novidade própria, comparação rigorosa e dados/código reproduzíveis; aplicar pacote padrão e SHAP seria uma contribuição fraca |

Para **Structures**, a página oficial da Institution of Structural Engineers inclui projeto, mecânica, otimização e aplicações com caminho para adoção na prática. Isso sustenta a escolha de escopo: [Structures — IStructE](https://www.istructe.org/about-us/what-we-do/structures-journal/).

Para **Engineering Structures**, existem precedentes próximos de expressões empíricas e regressão simbólica em madeira, listados abaixo. Isso mostra afinidade temática, mas também significa que “usar regressão simbólica em madeira” não pode ser a única alegação de novidade. Página editorial para conferir na preparação da submissão: [Engineering Structures](https://www.sciencedirect.com/journal/engineering-structures).

Para **Engineering Applications of Artificial Intelligence**, verificar o escopo e as exigências vigentes quando o método estiver definido: [página da revista](https://www.sciencedirect.com/journal/engineering-applications-of-artificial-intelligence). Não é o alvo prioritário do desenho atual.

## Referências de partida

1. Cranmer, M. **Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl** (2023). Fundamenta a obtenção de modelos simbólicos interpretáveis. [Artigo e metadados](https://arxiv.org/abs/2305.01582). Regressão simbólica é candidata; não foi instalada nem executada nesta etapa.
2. **Two-dimensional estimation of service load limit in CLT plates** (Engineering Structures, 2025). Precedente de regressão simbólica para elementos de madeira, diferente da tipologia de pontes roliças. [Página do artigo](https://www.sciencedirect.com/science/article/abs/pii/S0141029625000926).
3. **Simple empirical equations to predict temperature rise and deformation history in structural members under standard fires** (Engineering Structures, 2025). Precedente de expressões explícitas e validação experimental, com sistemas de madeira entre os exemplos. [Página do artigo](https://www.sciencedirect.com/science/article/pii/S0141029625012726).
4. **Evaluating fire resistance of timber columns using explainable machine learning models**. Precedente de IA explicável em madeira, em outro fenômeno e elemento. [Página do artigo](https://www.sciencedirect.com/science/article/pii/S0141029623013251).

A consulta das páginas ScienceDirect encontrou restrições de acesso em alguns links; títulos e descrições disponíveis nos resultados da busca foram suficientes para indicar leituras, não para uma revisão sistemática ou uma análise integral dos métodos. Conferir texto completo e metadados antes de gerar as citações finais do manuscrito.

## Recorte da originalidade a demonstrar

O argumento promissor é combinar **domínio multidimensional de pontes roliças + equações explícitas + tratamento dos regimes/disposição inteira + avaliação do desempenho das geometrias previstas**. A busca inicial não prova ineditismo. Antes de escrever “primeiro estudo”, fazer uma revisão específica de pontes de madeira, dimensionamento preliminar, regressão simbólica e modelos substitutos de otimização, com busca e critérios documentados.
