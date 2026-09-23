# Enquadramento editorial e leitura inicial

**Refinado em 22/09/2026.** As avaliações são recomendações, não garantias de aceite. Não foram usados fator de impacto nem Qualis como critério, nem verificados custos de publicação.

## A escolha depende do marco zero

O alvo editorial não se decide agora, porque a contribuição ainda não existe. Ela depende de qual dos três desfechos do solucionador direto, descritos em [`01_proposta.md`](01_proposta.md), se confirmar.

| Desfecho do marco zero | Revista indicada | Argumento de venda |
|---|---|---|
| A — solução direta exata e rápida, metaheurística desnecessária | **Engineering Structures** ou **Advances in Engineering Software** | Resultado metodológico com alcance além da madeira roliça, mais as equações de projeto como entrega prática |
| B — solução direta exata, mas ramificada demais para comunicar | **Structures** | Regra de projeto verificada, com mapa de regimes e domínio declarado |
| C — a solução direta não fecha, o metamodelo é necessário | **Structures**, com **Engineering Applications of Artificial Intelligence** como alternativa | Metamodelo explícito de otimização, com verificação estrutural das previsões |

## Recomendação enquanto isso

Escrever para **Structures** como alvo padrão. É a revista da Institution of Structural Engineers que acolhe projeto, mecânica, otimização e aplicações com caminho para a prática, o que é exatamente o formato de regra de anteprojeto com domínio e erro conhecidos. Página oficial para conferir o escopo, [Structures — IStructE](https://www.istructe.org/about-us/what-we-do/structures-journal/).

Há uma razão adicional. O artigo 2 está indo para **Engineering Structures**, e enviar dois manuscritos próximos, da mesma equipe e sobre a mesma ponte, à mesma revista em sequência curta enfraquece os dois. Reservar Engineering Structures para o caso em que o achado do marco zero for forte o bastante para carregar o artigo sozinho, [página da revista](https://www.sciencedirect.com/journal/engineering-structures).

Para **Engineering Applications of Artificial Intelligence**, conferir escopo e exigências quando o método estiver definido, [página da revista](https://www.sciencedirect.com/journal/engineering-applications-of-artificial-intelligence). Aplicar um pacote padrão de regressão simbólica e gráficos SHAP seria contribuição fraca ali.

Descartados por ora. **Journal of Bridge Engineering** pede validação experimental ou ponte instrumentada, que este trabalho não tem. **Construction and Building Materials** e revistas de material só entram se o eixo virar a indexação das espécies. **Results in Engineering** e similares aceitam rápido e custam prestígio, então ficam como último recurso.

## O que precisa aparecer no manuscrito, em qualquer revista

Ganho demonstrado frente à expressão simples do artigo 1 e frente à inversão analítica. Avaliação fora do treinamento com partição por espécie. Reanálise completa das geometrias previstas, com taxa de violação relatada. Tempo comparado. Domínio de validade explícito.

O que não sustenta novidade sozinho, base maior, gráficos SHAP, R² alto, ou usar regressão simbólica em madeira, que já tem precedente publicado.

## Referências de partida

1. Cranmer, M. **Interpretable Machine Learning for Science with PySR and SymbolicRegression.jl** (2023). Fundamenta a obtenção de modelos simbólicos interpretáveis, [artigo e metadados](https://arxiv.org/abs/2305.01582). A biblioteca ainda não foi instalada nem executada.
2. **Two-dimensional estimation of service load limit in CLT plates** (Engineering Structures, 2025). Precedente de regressão simbólica em elemento de madeira, tipologia diferente, [página do artigo](https://www.sciencedirect.com/science/article/abs/pii/S0141029625000926).
3. **Simple empirical equations to predict temperature rise and deformation history in structural members under standard fires** (Engineering Structures, 2025). Precedente de expressões explícitas com validação experimental, [página do artigo](https://www.sciencedirect.com/science/article/pii/S0141029625012726).
4. **Evaluating fire resistance of timber columns using explainable machine learning models**. Precedente de IA explicável em madeira, outro fenômeno e outro elemento, [página do artigo](https://www.sciencedirect.com/science/article/pii/S0141029623013251).
5. Dias, F. M.; Rocco Lahr, F. A. **Estimativa de propriedades de resistência e rigidez da madeira através da densidade aparente**. Scientia Forestalis, n. 65, p. 102-113, 2004. Base das 40 espécies, já auditada em `paper/engstruct/dados/`.

Falta uma leitura que o artigo 3 exige e que os quatro primeiros itens não cobrem. Literatura de metamodelo substituto de otimização estrutural, e literatura que compare metaheurística com solução direta em problemas de projeto de pequena dimensão. Sem ela não dá para posicionar o desfecho A.

A consulta das páginas ScienceDirect encontrou restrição de acesso em alguns links. Títulos e descrições bastaram para indicar leitura, não para revisão sistemática. Conferir o texto integral antes de gerar as citações finais.

## Recorte da originalidade a demonstrar

A combinação promissora reúne domínio multidimensional de pontes roliças, propriedades contínuas de espécies reais, solução direta do dimensionamento e verificação estrutural das geometrias previstas. A busca inicial não prova ineditismo. Antes de escrever "primeiro estudo", fazer revisão específica de pontes de madeira, dimensionamento preliminar, regressão simbólica e metamodelos de otimização, com busca e critérios documentados.
