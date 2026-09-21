# Engineering Structures — plano reformulado

**Decisão de 2026-09-20 (⚠️ base de dados revertida em 2026-09-21, ver seção final):** adotar como base experimental o artigo de Wolenski, Dias, Peixoto, Christoforo e Lahr (2020), DOI 10.1590/s1678-86212020000100373. A antiga tabela de 40 espécies não integra esta versão da investigação.
A base de dados voltou a ser a tabela do Fabrício (ver "Revisão de 2026-09-21" ao final deste arquivo) — **o protocolo descrito abaixo (comparação controlada R×C, multi-semente) permanece válido e é para ser mantido**, só a origem das 40 espécies mudou de volta.

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

## Revisão de 2026-09-21 — retorno à base do Fabrício, protocolo mantido

**Ponto de partida da sessão:** o Wanderlei colou no chat o conteúdo de `main.pdf` esperando que fosse o estado atual do artigo. **Não era** — esse PDF é uma versão antiga (pré-reformulação de 20/09, título "O enquadramento em classe de resistência não representa a rigidez das madeiras tropicais..."), provavelmente um arquivo local/baixado antes da reformulação. O `.tex` real já estava reformulado (título "Efeito da representação por classes de resistência...", base Wolenski). **Cuidado para sessões futuras:** sempre conferir `git log` e o `.tex`, nunca confiar num PDF colado no chat como se fosse o estado atual do repositório.

### Decisão 1 — a base de dados volta a ser o Fabrício, não o Wolenski

Achado o arquivo `artigo_fabricio.md` na raiz do repo: é o artigo de **Fabricio Moura Dias e Francisco Antonio Rocco Lahr (2004)**, *Estimativa de propriedades de resistência e rigidez da madeira através da densidade aparente*, Scientia Forestalis n.65, p.102-113. É quase certamente **a fonte original da antiga `tab_especies.tex`** — mesmas 40 espécies, mesma numeração/ordem, mesmos nomes científicos.

A troca para Wolenski (D-XX, 20/09) foi motivada pela suspeita de que a tabela antiga convertia $f_{c0,k}$ pela aproximação grosseira $f_k = 0{,}70 \times f_m$ em vez do característico de verdade. **Essa suspeita não procede**: o próprio Fabrício (2004), Tabela 3 do artigo-fonte, já publica $f_{c0,k}$ calculado pelo estimador de estatística de ordem da norma (não pela aproximação simplificada) — é a tabela antiga do manuscrito que reconvertia errado a partir da média, não a fonte.

Comparação das duas bases:

| | Fabrício (2004) | Wolenski et al. (2020) |
|---|---|---|
| Nº de espécies | 40 | 40 |
| Propriedades | $f_{c0}$, $f_{c0,k}$, $f_m$, $f_{v0}$, $\rho_{ap}$, $E_{M0}$ — completo para o modelo de ponte | só compressão e tração ($f_{c0}$, $f_{t0}$, $E_{c0}$, $E_{t0}$); falta flexão, cisalhamento, densidade |
| Angelim-pedra (caso extremo do artigo antigo) | presente | **ausente** da Tabela 1 |
| Inconsistências conhecidas | 2 espécies com $f_{c0,k}$ > $f_{c0}$ médio (ver abaixo — não é erro) | Tabela 7: mandioqueira/oiticica-amarela/quina-rosa como C60 com $f_{c0}$ < 60 MPa; piolho como C40 com $f_{c0}$ < 40 MPa — não esclarecido |

**Decisão do Wanderlei (2026-09-21): voltar para o Fabrício.** Reclassificação em D20–D60 (norma atual) já feita a partir do $f_{c0,k}$ real do Fabrício, não da aproximação. Planilha em `tmp/fabricio_classificacao_D.xlsx` (IS, nome, $f_{c0,k}$, $f_{c0}$ médio, $f_m$ médio, $E_{M0}$ médio, classe D). Distribuição: D20=3, D30=3, D40=11, D50=10, D60=13.

Duas espécies (Champanhe, $f_{c0,k}=96{,}2 > f_{c0,\text{médio}}=93$; Oiticica-amarela, $f_{c0,k}=73{,}5 > f_{c0,\text{médio}}=70$) foram checadas com o Wanderlei — **não são erro**: o estimador característico da norma só impõe um piso ($\geq \max(f_1, 0{,}70\bar{f})$), não um teto, então $f_{c0,k}$ pode superar a média amostral em lotes pequenos/assimétricos. Não sinalizar isso como anomalia daqui pra frente.

Pendência real, essa sim a resolver: identificar e contatar o Fabrício Moura Dias (e possivelmente o Rocco Lahr) sobre coautoria/permissão de reuso dos dados, exatamente como o `[PENDÊNCIA DE COAUTORIA]` do rascunho antigo já assinalava.

### Decisão 2 — o protocolo novo (controlado, multi-semente) é mantido

A reformulação de 20/09 não foi só trocar dado — trocou também o protocolo de comparação: de "duas otimizações independentes por espécie" para uma comparação controlada que isola só a rigidez (cenários R e C com geometria/carregamento fixos), com verificação analítica fechada ($\delta_C/\delta_R = E_{c0,s}/E_{c0,c_s}$ no regime elástico linear, `03_methodology.tex`) e redimensionamento com múltiplas sementes pareadas.

Isso é mantido porque é uma melhoria real de rigor, independente da base de dados: um revisor do Engineering Structures vai perguntar se um efeito medido é sinal ou ruído do NSGA-II entre execuções — exatamente a pergunta que acabou de derrubar o achado do "custo da robustez" no Artigo 1 (Matéria, ver `vault/CHANGELOG.md` 2026-09-21), que rodou uma execução única por condição. Não repetir esse erro aqui.

`03a_structural_model.tex` e `03b_optimization_protocol.tex` (formulação mecânica transferida da Matéria) também ficam, mas têm pendências de auditoria de código já registradas na seção "Transferência da Matéria" acima — conferir se a correção D-17 (envoltórias de momento/cortante, feita em `madeiras.py` para o Artigo 1) já resolve algumas delas, já que o código é compartilhado.

### Pergunta de enquadramento (respondida)

O Wanderlei perguntou se "quanto o dimensionamento muda entre classe e espécie, e como o volume de madeira muda" é pergunta suficiente para o Engineering Structures. Resposta: sim, **desde que respondida com o protocolo controlado**, não com a comparação ingênua de duas otimizações. Sem controle, é achado de caracterização de material (cabe em revista de madeira); com o efeito da rigidez isolado e a robustez estatística demonstrada (multi-semente), vira achado de projeto estrutural, que é o que a revista publica.

### Próximos passos, quando o Wanderlei retomar este artigo

1. Reconstruir `tabelas/tab_especies.tex`, `tab_dispersao.tex`, `tab_discordancia.tex` com a base do Fabrício (não a antiga aproximação 0,70×média, o $f_{c0,k}$ real) e gerar a Figura 1 ($E_{M0}$ vs $f_{c0,k}$, limites de classe sobrepostos, `figuras/E_vs_fc0.png`).
2. Atualizar `title_authors.tex` (fonte experimental), `abstract_keywords.tex`, `01_introduction.tex`, `02_materials.tex` para citar Fabrício em vez de Wolenski, preservando a estrutura/protocolo de `03_methodology.tex`.
3. Resolver as pendências de auditoria de código listadas na seção "Transferência da Matéria" (conferir contra a correção D-17 do Artigo 1 primeiro).
4. Rodar o piloto cronometrado (uma espécie, um vão) antes de comprometer a campanha completa — ainda não rodado.
5. Encaminhar a questão de coautoria do Fabrício/Rocco Lahr antes de submeter.
