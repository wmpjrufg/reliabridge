# Engineering Structures — plano reformulado

**Decisão de 2026-09-20:** adotar como base experimental o artigo de Wolenski, Dias, Peixoto, Christoforo e Lahr (2020), DOI 10.1590/s1678-86212020000100373. A antiga tabela de 40 espécies não integra esta versão da investigação.

**Título:** Efeito da representação por classes de resistência no desempenho e no consumo de material de pontes de madeira tropical.

**Pergunta:** quanto a substituição da rigidez experimental pela rigidez de classe altera a previsão de deslocamentos e o volume de madeira, e em quais condições o projeto por classe atende ao limite de serviço quando reavaliado com a rigidez experimental?

O trabalho não pressupõe inadequação das classes nem migração do estado limite governante. A otimização é instrumento de comparação. A versão de trabalho permanece em português; o título da referência experimental está em inglês, como solicitado.

## Base e limites

A fonte fornece 40 espécies, médias e DP/CV de compressão e tração, módulos E_c0 e E_t0, resistências características e classes históricas C20/C30/C40/C60. Não fornece as propriedades de flexão, cisalhamento e densidade por espécie exigidas pelo modelo de ponte. E_c0 não deve ser renomeado E_M0.

As tabelas antigas `tab_especies.tex`, `tab_dispersao.tex` e `tab_discordancia.tex` estão preservadas apenas como histórico e não são incluídas no manuscrito. Os percentuais 58%, 35%, as dispersões 70–74% e o exemplo angelim-pedra/goiabão foram retirados da argumentação. Não reutilizar os casos antigos nem executar `gerar_casos_engstruct.py` como se implementasse o novo protocolo: ele depende da antiga tabela e precisa de adaptação futura.

## Sequência de execução

1. Transcrever as Tabelas 1 e 3–7 do PDF para uma base auditável, com ID, nome científico, propriedade, unidade e origem. Conferir visualmente valores e estatísticas; preservar possíveis inconsistências da publicação.
2. Auditar a classificação histórica: conservar classe publicada e recalcular pelo maior limiar não superior a f_c0,k. Comparar separadamente com a classe obtida por 0,70 × f_c0,m. Não substituir o característico publicado pela conversão simplificada.
3. Definir o sistema de classes do estudo estrutural contemporâneo, conferindo a edição normativa e a aplicabilidade a madeira roliça. Não misturar os módulos históricos C com classes D. A tabela histórica do manuscrito serve à auditoria da fonte.
4. Definir e justificar alpha_E, resistências de flexão/cisalhamento e densidade. Marcar cada entrada como medida, estimada ou adotada. No experimento principal, somente a rigidez muda dentro de cada par.
5. Comparar uma mesma geometria e carregamento com rigidez R (experimental) e C (classe). Conferir a razão inversa entre deslocamento e módulo nas condições do modelo elástico aplicável.
6. Redimensionar com os mesmos critérios e múltiplas sementes pareadas. Extrair a solução viável de menor volume de cada cenário. Informar tolerâncias e dispersão numérica; a mesma semente não elimina erro de otimização.
7. Reavaliar a geometria do projeto C com rigidez R. Apresentar utilização de serviço e verificações complementares. Delta V negativo não implica, por si só, violação de limites.
8. Comparar os vãos propostos de 3, 5, 8 e 10 m, identificar restrições ativas e testar sensibilidade às hipóteses complementares. Não exigir transição entre estados limites.
9. Preencher resultados, resumo e conclusões somente com análises efetivamente realizadas. A extensão para variabilidade intraespécie é posterior e depende de hipóteses explícitas de distribuição e dependência.

## Figuras prioritárias

- Auditoria: classe publicada, recalculada e obtida pela conversão simplificada.
- Rigidez experimental versus classe, com erros por espécie e dispersão por classe.
- Flecha prevista C versus R sob geometria fixa.
- Delta V versus utilização C→R, por vão, com referência U=1.
- Restrições ativas e sensibilidade às hipóteses.

A comparação com EN 338 não faz parte do núcleo atual: requer dados e critérios próprios, indisponíveis apenas com esse PDF. A campanha antiga de 320 rodadas não descreve mais o custo computacional do protocolo com controles e repetições.

## Validação e apresentação

Conferir manualmente um caso, demonstrar viabilidade e convergência e disponibilizar scripts e dados derivados. Distinguir frequência de excedência no conjunto analisado de probabilidade de falha. A caracterização laboratorial não valida automaticamente peças de dimensões estruturais ou pontes construídas.

Antes da submissão: completar a literatura, concluir a verificação normativa, revisar autoria/contribuições, traduzir para inglês, adequar o formato e remover todos os marcadores de pendência.

## Transferência da Matéria — 2026-09-20

Incorporados sem resultados: enquadramento na literatura, propriedades geométricas, acomodação inteira de peças, volume, configuração TB-240, ações lineares, esforços e flechas de referência, resistência de cálculo, fluência, seis restrições, agregação robusta e operadores do NSGA-II. A formulação está em `03a_structural_model.tex` e `03b_optimization_protocol.tex`, incluídos pela metodologia.

Melhorias: distinguir espaçamento livre/eixos/largura tributária; chamar as expressões simétricas de respostas de uma configuração, não de envoltórias gerais; separar serviço quase permanente e variável; diferenciar volume nominal e objetivo médio; avaliar descendentes antes da seleção; propor dez sementes pareadas; preservar configuração discreta na verificação de uma solução construída. População 50, 150 gerações, 30 realizações e 5% são configurações iniciais do piloto, não parâmetros já validados para a nova base.

A auditoria de leitura do código identificou pendências antes das rodadas:

- `restringir_espaco` define espaçamento livre; o avaliador usa esse valor como largura tributária e vão de tabuleiro. Conferir equilíbrio de cargas, bordas e posição dos apoios.
- A expressão de cortante contém `e = L - 3*a - 2*d`, negativo para alguns vãos curtos. Conferir domínio e envoltória por posições reais das rodas.
- A flecha variável da rotina atual só inclui as rodas estáticas. Definir a composição completa de ELS, multidão e impacto segundo a combinação aplicável.
- A fronteira de CIV em L = 10 m difere entre a redação da Matéria e a rotina lida.
- A expressão de momento de roda no tabuleiro exige conferir contato e domínio; não pode produzir momento negativo por vão menor que o contato e seguir como verificação física.
- O artigo herda limites L/250 e L/360; verificar a justificativa normativa de cada combinação antes de tratá-los como conformidade final.

Nenhuma dessas rotinas foi alterada nesta transferência editorial. O código e a matriz de casos ainda devem ser adaptados e verificados antes da campanha.

Referências incorporadas da Matéria: Criado2024, Marti2013 e SimoesNegrao2005. Acrescentada Deb2002 como referência original do NSGA-II. Fontes conferidas: páginas do artigo em SciELO, ScienceDirect e ASCE e texto original do NSGA-II; a busca não substitui consulta às normas integrais.
