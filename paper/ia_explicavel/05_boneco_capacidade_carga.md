# Boneco do artigo 3 — capacidade de carga

> **Superado em 22/09/2026.** Este boneco tratava a capacidade de geometrias fixas como pergunta central de um artigo de IA. O modelo estrutural é algébrico e os esforços são lineares no multiplicador do carregamento móvel, de modo que o multiplicador limite sai por **inversão exata**, sem ajuste e sem erro. Regressão simbólica sobre esse rótulo aprenderia uma função já conhecida em forma fechada. O recorte atual está em [`01_proposta.md`](01_proposta.md).
>
> **O que sobrevive e vira seção do artigo de pré-dimensionamento.** A convenção do multiplicador da seção 2.3, a definição separada de `lambda_ELS`, `lambda_ELU` e `lambda_lim` da seção 2.4, o mapa de estados limites governantes da seção 5.1 e o exemplo de aplicação da seção 6. Tudo obtido por inversão, sem campanha de dados própria.
>
> **O que não sobrevive.** A base de capacidade da seção 3, a regressão simbólica de `lambda` da seção 4.2 e as métricas de superestimação da seção 4.4, que só fariam sentido contra um rótulo aproximado. O termo *capacidade* também precisa de cuidado na redação, porque `lambda` mede atendimento às verificações do modelo, não ruptura.

**Versão de planejamento — 21/09/2026.** Recorte adotado para este roteiro após a discussão com o usuário: capacidade de carga de geometrias fixas como pergunta central; pré-dimensionamento como aplicação secundária. Não há dataset de capacidade calculado nem equações ajustadas nesta etapa.

## Título de trabalho

**Equações explicáveis para estimativa da capacidade de carga e identificação dos estados limites governantes em pontes de madeira roliça**

Inglês: *Explainable equations for load-capacity estimation and governing limit-state identification in roundwood bridges*.

Se a campanha sustentar apenas limites de serviço, restringir o título e as conclusões a esse domínio. “Capacidade” significa atendimento às verificações incluídas no modelo; não é previsão experimental de colapso nem capacidade integral de uma ponte inspecionada.

## Mensagem central pretendida

Para uma ponte com geometria e material definidos, estimar o multiplicador do carregamento móvel que leva ao primeiro limite de serviço ou de resistência, e explicar como o limite governante muda no espaço de projeto. Demonstrar quando uma expressão compacta reproduz essa avaliação com erro aceitável e em quais regiões a superestimação exige correção ou cálculo completo.

A hipótese não é que a IA necessariamente supere as expressões mecânicas. Se as verificações puderem ser invertidas diretamente, essa solução analítica será uma referência forte e poderá tornar a regressão simbólica dispensável. A contribuição precisa ser avaliada frente a essa referência, incluindo simplicidade e capacidade de representar mudanças de regime.

## Resumo provisório — texto de proposta, sem resultados inventados

A avaliação preliminar da capacidade de carga de pontes de madeira roliça exige considerar a interação entre geometria, propriedades do material e carregamento, bem como a competição entre estados limites de serviço e de resistência. Este estudo propõe desenvolver equações explícitas por regressão simbólica para estimar a capacidade de configurações de pontes com vãos de 3 a 10 m, sob perfis de carregamento associados aos trens-tipo TB-240 e TB-450. Um conjunto de dados computacional será gerado a partir de geometrias construtivamente admissíveis, variando dimensões e disposição das peças, largura da pista, classe da madeira e carga permanente adicional. Para cada configuração, serão determinados separadamente os multiplicadores de carga móvel correspondentes aos limites de serviço e de resistência, mantendo fixas a geometria e as ações permanentes. As expressões serão comparadas com referências mecânicas e modelos estatísticos, utilizando validação agrupada e cenários não empregados no ajuste. A avaliação abrangerá precisão, complexidade, superestimação da capacidade e reprodução dos critérios governantes. A aplicação pretendida é apoiar a comparação de alternativas e o pré-dimensionamento, com domínio de validade declarado e conferência pelo modelo estrutural completo.

**Palavras-chave:** pontes de madeira roliça; capacidade de carga; regressão simbólica; estados limites; modelos interpretáveis; pré-dimensionamento.

Na versão para submissão, substituir o futuro por descrição do método executado e acrescentar tamanho final da base, erros de teste, taxa de superestimação e achado mecânico efetivamente observado. Este resumo não é um resumo final de resultados.

## Sumário e conteúdo esperado

### 1. Introdução

**1.1 Contexto e necessidade prática.** Apresentar pontes vicinais de madeira roliça e a decisão de comparar configurações por capacidade. Distinguir avaliação de uma configuração idealizada e avaliação de ponte existente com condição conhecida.

**1.2 Estado da arte e lacuna.** Relacionar métodos de capacidade, equações simplificadas e regressão simbólica em estruturas de madeira. Usar o precedente de CLT como referência metodológica, sem tratá-lo como validação de pontes. Fazer revisão específica antes de alegar ineditismo.

**1.3 Objetivo e contribuição.** Declarar as saídas: capacidade limitada por serviço, capacidade limitada por resistência e critério governante. A novidade pretendida combina domínio multidimensional, equações compactas e avaliação de superestimações; não se resume a aplicar uma biblioteca de IA.

**Entrega da seção:** pergunta testável e três contribuições claras, sem prometer qual estado limite dominará.

### 2. Modelo estrutural e definição da capacidade

**2.1 Tipologia e hipóteses.** Definir apoios, longarinas circulares, peças do tabuleiro, contagem inteira, dimensões, propriedades e modelo de distribuição de cargas. Indicar quais verificações não estão cobertas. Citar o artigo da plataforma sem reproduzir sua interface.

**2.2 Ações e combinações.** Manter peso próprio e p_gk fixos durante cada avaliação de capacidade. Definir as posições críticas e a regra de aplicação do veículo e da multidão. Resolver as pendências do domínio ampliado, incluindo exclusão da multidão, envoltórias e distribuição transversal, antes de congelar a base.

**2.3 Multiplicador de carga.** Convenção proposta para a campanha inicial: escalar conjuntamente as cargas características móveis do perfil de referência, preservando sua geometria:

```text
P_roda(lambda) = lambda * P_roda,ref
p_multidao(lambda) = lambda * p_multidao,ref
G(lambda) = G fixo
```

Aplicar os coeficientes de cada combinação e a regra de amplificação dinâmica de forma documentada e consistente. Essa convenção define um perfil proporcional de pesquisa; não é um procedimento normativo de classificação de qualquer caminhão. Se outra convenção for estudada, tratá-la como cenário distinto. Não multiplicar as ações permanentes por lambda.

**2.4 Limites separados e governante.** Para geometrias válidas, atendidas as ações permanentes e confirmada a monotonicidade no domínio:

```text
lambda_ELS = maior multiplicador que atende às verificações de serviço incluídas
lambda_ELU = maior multiplicador que atende às verificações de resistência incluídas
lambda_lim = min(lambda_ELS, lambda_ELU)
```

Guardar também cada verificação governante específica, empates e a combinação determinante. lambda=1 corresponde ao perfil de referência. lambda_lim menor que 1 indica insuficiência em pelo menos uma verificação do modelo sob esse perfil; não converter lambda diretamente em tonelagem irrestrita de tráfego.

**2.5 Verificação do cálculo.** Conferências independentes de casos selecionados e transições de expressão; identificar o que valida implementação e o que valida comportamento físico. A reavaliação pelo mesmo núcleo não é validação independente.

**Entrega da seção:** esquema estrutural, convenção inequívoca de carga e tabela de verificações/unidades. Não chamar limite de resistência de carga real de ruptura.

### 3. Planejamento e geração do dataset

**3.1 Domínio e amostragem.** Manter como ponto de partida L=3–10 m, perfis TB-240/TB-450, classes D20–D60, largura e p_gk propostos. Acrescentar diâmetro, seção do tabuleiro e disposição de peças. Preferir amostragem estratificada com cobertura dos limites e das transições, calibrada por piloto e curva de aprendizado; não fixar um número arbitrário de “milhares de pontes”.

**3.2 Admissibilidade geométrica.** Gerar contagens/disposições construtivas compatíveis, registrar espaçamentos efetivos e eliminar duplicatas físicas produzidas pelo arredondamento. Separar geometria impossível, estrutura insuficiente sob permanentes e configuração válida. Os limites comerciais atuais são referência, não justificativa para sortear combinações incoerentes.

**3.3 Cálculo dos rótulos.** Para cada geometria fixa, obter os limites por inversão das expressões quando possível ou por busca escalar com intervalo que contenha a transição. Confirmar monotonicidade e definir tolerâncias, teto de busca e tratamento de falhas. Validar a busca contra a inversão analítica em casos em que esta exista. Não redimensionar a ponte enquanto aumenta a carga.

Se a estrutura falhar com lambda=0, registrar esse estado separadamente. Se não atingir o limite até o teto computacional, guardar um limite inferior/censura; não registrar o teto como capacidade exata. Geometrias inválidas e falhas numéricas não recebem capacidade zero por conveniência.

**3.4 Organização e partições.** Uma configuração física é a unidade de agrupamento. Manter seus dois perfis de veículo, variantes de p_gk e eventuais perturbações no mesmo grupo. Definir grupos/famílias de modo a evitar que pequenas variantes da mesma geometria apareçam em treino e teste. Separar um teste de interpolação e outro de generalização controlada em vão ou classe. Ajustes de pré-processamento e seleção de equação usam apenas treinamento/validação.

**3.5 Rastreabilidade.** Guardar entradas, geometria efetiva, origem das propriedades, edições normativas adotadas, versão do núcleo, critério/combinação determinante, tolerância da busca e status. Reportar cobertura e casos excluídos. A base de classes não permite atribuir efeitos independentes a rigidez, densidade e resistência, que variam conjuntamente.

**Entrega da seção:** tabela do domínio, fluxograma de geração e distribuição dos estados limites. Os 2.700 registros anteriores são cenários de otimização sem geometrias fixas e NÃO constituem este novo dataset de capacidade.

### 4. Desenvolvimento das equações explicáveis

**4.1 Referências de comparação.** Usar inversão mecânica das verificações disponíveis, regressão simples e um modelo flexível de referência. Comparar não apenas R², mas custo, complexidade e extrapolação. Uma expressão mecânica exata sob as mesmas hipóteses pode ser preferível à IA.

**4.2 Regressão simbólica.** Definir entradas disponíveis antes do cálculo, escalas/razões adimensionais, operadores, restrições de complexidade e seleção pela validação. Desenvolver expressões separadas para lambda_ELS e lambda_ELU ou para verificações individuais, conforme os resultados. O mínimo fornece a capacidade global considerada.

**4.3 Consistência e interpretação.** Investigar sinais, limites, singularidades e sensibilidade. Relacionar termos à mecânica sem atribuir causalidade a variáveis colineares. O estado limite calculado é saída; não usá-lo como entrada de uma previsão que pretende descobrir esse próprio regime.

**4.4 Validação e erro desfavorável.** Reportar MAE/RMSE, erro relativo quando a capacidade de referência não for próxima de zero, percentil 95, máximo e frequência/magnitude de superestimação. Para capacidade, superestimar é o sentido desfavorável. Para capacidades nulas ou muito pequenas, usar métricas absolutas e relatório separado. Definir eventual correção conservadora no conjunto de calibração/validação, mantendo o teste intacto.

**Entrega da seção:** protocolo reproduzível de escolha da equação e tratamento explícito das previsões excessivas.

### 5. Resultados

**5.1 Cobertura, qualidade e regimes.** Quantos casos válidos foram calculados, onde houve falhas/censura e quais critérios governam cada região. Não assumir que o vão longo será sempre governado pela flecha.

**5.2 Desempenho fora do treinamento.** Comparação entre referências e equações simbólicas, com erros estratificados por vão, veículo, classe e dimensões. Reportar dispersão da seleção/ajuste e curva de aprendizado.

**5.3 Expressões finais.** Apresentar coeficientes, unidades/escalas, domínio e complexidade. Explicar transições e relação com a mecânica. Mostrar se a mesma expressão funciona para ambos os veículos ou se exige termos específicos.

**5.4 Superestimações e limites de uso.** Mapear regiões desfavoráveis, avaliar a correção proposta e reavaliar no modelo estrutural a carga prevista. Verificar simultaneamente todas as restrições incluídas, não apenas acertar o rótulo do governante.

**Entrega da seção:** equações utilizáveis, erros de teste e achados físicos reais. Nenhum número do piloto de otimização anterior deve aparecer como resultado desta campanha de capacidade.

### 6. Aplicação em avaliação preliminar e pré-dimensionamento

**6.1 Comparação de configurações.** Propor uma travessia hipotética com L=7,5 m, B=4,0 m e classe D40. Escolher configurações válidas com diferentes diâmetros e disposições; comparar os dois perfis móveis e níveis de p_gk. Reservar essas configurações fora do ajuste.

**6.2 Leitura dos resultados.** Apresentar lambda_ELS, lambda_ELU, lambda_lim e critério governante. Explicar qual alteração geométrica melhora a capacidade, quanto custa em volume e se a mudança desloca o governante.

**6.3 Aplicação inversa.** Demonstrar a seleção de uma alternativa que atenda lambda_lim >= 1 para o perfil escolhido, seguida de reanálise completa. Essa triagem ilustra pré-dimensionamento; não precisa de uma segunda campanha de otimização global ou de promessa de ótimo econômico.

**Entrega da seção:** exemplo numérico rastreável, comparação equação/modelo e tabela de alternativas. Não apresentar caso hipotético como ponte real avaliada.

### 7. Discussão e limitações

Explicar o que as expressões acrescentam às referências mecânicas, quando vale usar a forma compacta e onde ela perde validade. Discutir dependência da tipologia, hipóteses de apoio/distribuição, propriedades vinculadas às classes, fórmulas de carga, discretização e dados simulados. Tratar conexões, degradação, apoios/fundações e outros mecanismos não modelados conforme o escopo efetivo.

Separar precisão perante o simulador de validação por ensaio/ponte real. TB-240 e TB-450 representam dois perfis de referência, não a diversidade de veículos reais. A robustez geométrica média de 5% usada no estudo anterior não será automaticamente a definição de capacidade: a campanha inicial proposta usa geometria nominal fixa. Qualquer extensão de variabilidade exige objetivo e agregação próprios, explicitamente definidos.

**Entrega da seção:** afirmações proporcionais às evidências e distinção clara entre capacidade calculada, margem calibrada e confiabilidade probabilística.

### 8. Conclusões

Responder diretamente: qual foi o erro das equações em teste; quais regimes/interações apareceram; em quais condições a superestimação foi controlada; como a expressão apoiou a comparação/pré-dimensão; quais limites impedem uso fora do domínio. Usar somente resultados apresentados. Se a regressão simples ou a inversão analítica vencer, concluir isso de forma explícita.

**Entrega da seção:** quatro a seis conclusões quantitativas e delimitadas, escritas apenas após os resultados.

## Figuras e tabelas planejadas

| Item | Conteúdo e finalidade |
|---|---|
| Figura 1 | Esquema estrutural, dimensões e convenção de carregamento |
| Figura 2 | Fluxo geometria → busca de capacidade → dataset → equações → reanálise |
| Figura 3 | Cobertura da base e mapas de estados limites governantes |
| Figura 4 | Erro versus complexidade das expressões candidatas |
| Figura 5 | Paridade em teste para serviço e resistência, destacando superestimações |
| Figura 6 | Capacidade versus geometria no exemplo de aplicação, com troca de governante |
| Tabela 1 | Domínio, unidades, origem e hipóteses de cada variável |
| Tabela 2 | Verificações, combinações, tolerâncias e critérios de rotulagem |
| Tabela 3 | Desempenho dos modelos e magnitude de superestimação no teste |
| Tabela 4 | Expressões finais, domínio e limites de uso |
| Tabela 5 | Configurações do exemplo, capacidade, governante e volume |

## Material suplementar

Dataset com dicionário, manifesto de fontes/versões e grupos de partição; gerador e cálculo de capacidade; exemplos de verificação independente; protocolo/expressões de treinamento e seleção; resultados detalhados por configuração. Manter no corpo as hipóteses necessárias à compreensão, sem esconder as limitações no suplemento.

## Ordem prática de execução e redação

1. Fechar as definições da seção 2 e auditar o domínio mecânico; escrever seções 1–2 como rascunho com referências verificadas.
2. Implementar o rotulador de capacidade e validar em geometrias fixas, incluindo falha sob permanentes e censura.
3. Fazer piloto de amostragem, dimensionar a campanha e congelar grupos/partições; completar seção 3.
4. Comparar referências e ajustar equações; completar seção 4.
5. Preencher resultados e aplicação, depois discussão/conclusões.
6. Reescrever título/resumo ao redor do achado real e só então fechar o alvo editorial.

O novo executor de capacidade ainda precisa ser implementado. Os scripts existentes continuam sendo do piloto de otimização e não foram alterados para produzir rótulos fictícios de capacidade.
