# Artigo 2 — Engineering Structures

**Pasta:** `paper/engstruct/`. **Idioma de trabalho:** português.

**Título:** Efeito da representação por classes de resistência no desempenho e no consumo de material de pontes de madeira tropical.

**Base experimental:** Dias e Rocco Lahr (2004), *Estimativa de propriedades de resistência e rigidez da madeira através da densidade aparente*, Scientia Forestalis n.65, p.102-113. Transcrição em `artigo_fabricio.md`.

## Pergunta e contribuição

O enquadramento em classe é indexado pela resistência característica à compressão; a rigidez acompanha por associação, sem entrar no critério. Quando a correlação entre resistência e rigidez é fraca dentro da classe, o módulo atribuído se afasta do medido e o desvio passa para toda verificação que dependa de rigidez. A pergunta é quanto isso altera o consumo de madeira e o atendimento ao limite de serviço, e sob quais condições o projeto pela classe excede o limite quando reavaliado com a rigidez real.

Não pressupor inadequação das classes nem migração do estado limite governante. Delta V negativo não prova insegurança. A otimização é instrumento de comparação, não a contribuição.

## Autoria (definida em 2026-09-22)

Wanderlei M. Pereira Junior (correspondente), André Luís Christoforo, Matheus Henrique Morato de Moraes, Wellington Andrade da Silva. Saíram Enzo Moura Rezende, Maria José Pereira Dantas e Fran Sergio Lobato. Pendência: coautoria ou permissão de reuso com Fabrício Moura Dias e Rocco Lahr.

## Decisões de protocolo — 2026-09-22

**Módulo comparado: E_c0 nos dois lados.** A fonte publica dois módulos por espécie, E_c0 (compressão, Tabela 5) e E_M0 (flexão, Tabela 5). A NBR 7190-3 só tabela E_c0,med por classe. Comparar E_c0 medido contra E_c0 da classe mantém a mesma propriedade nos dois membros e dispensa o fator alpha_E, que um revisor cobraria. O E_M0 fica como análise de sensibilidade. Na base, a razão E_M0/E_c0 tem média 0,97 e varia de 0,73 a 1,13.

**Dois experimentos, três cenários.** O membro "espécie" é comum aos dois experimentos, então são três cenários por par espécie-vão, não quatro:

| cenário | E_c0 | densidade | f_mk | f_v0k |
|---|---|---|---|---|
| `esp` | medido | medida | medida | medida |
| `rig` | da classe | medida | medida | medida |
| `cls` | da classe | da classe | da classe | da classe |

Principal (controlado) `esp × rig`, isola a rigidez. Secundário (prático) `esp × cls`, conjunto completo.

**Vãos 3, 5, 8 e 10 m.** Faixa inteira abaixo de 10 m, então o CIV é constante e nenhuma mudança de expressão de carregamento atravessa a comparação.

**Robustez fixa em 5%.** Sem varredura de rho: o objeto é a representação do material, e fixar rho garante que essa hipótese seja idêntica nos dois membros de cada par.

**f_m,k = f_c0,k nos dois lados** (item 6.3.4 da NBR 7190-1:2022, mesma convenção do Artigo 1). A espécie entra com o f_c0,k publicado, não com 0,70 × média. Só o f_v0,k da espécie usa fator sobre a média, porque a fonte não publica o característico de cisalhamento; como é comum a `esp` e `rig`, não interfere no experimento principal.

## Estado em 2026-09-22

Manuscrito compila limpo, 24 páginas, sem referências indefinidas. Estrutura: introdução, base experimental, projeto da ponte, metodologia, resultados (esqueleto), conclusões, apêndices.

Feito nesta sessão:

- `01_introduction.tex` reescrita no ângulo próprio do artigo (assimetria entre o critério de enquadramento e a rigidez), distinta da introdução da Matéria.
- `03_bridge_design.tex` novo, seção de projeto de ponte transferida da Matéria sem anatomia nem catálogo de tipologias, já com as envoltórias corrigidas de momento e cortante.
- `04_methodology.tex` novo, com os três cenários, rho fixo em 5% e sementes pareadas.
- `appendices.tex` ganhou a tabela de propriedades normativas das classes D20–D60 abaixo da tabela de ensaios.
- Removidos `03_methodology.tex`, `03a_structural_model.tex` e `03b_optimization_protocol.tex`, superados (recuperáveis no git).
- Citações do Wolenski trocadas por DiasLahr2004 em resultados, conclusões, declarações e resumo.

## Correção importante: o texto antigo divergia do código

`03b_optimization_protocol.tex` descrevia a robustez como perturbação **aleatória uniforme nas cinco variáveis** agregada por **média**, com N_c = 30. O código (`madeiras.py:_evaluate`, `_criar_multiplicadores_robustez`) faz outra coisa:

- objetivos avaliados no ponto **nominal**, não em média;
- restrições no **pior caso** (`np.max`) sobre a grade;
- grade **determinística** de 5 níveis {-rho, -rho/2, 0, +rho/2, +rho} aplicada **só ao diâmetro**.

A metodologia nova está escrita conforme o código. Ver também o Artigo 1, que descreve corretamente.

## Semente do NSGA-II — parametrizada em 2026-09-22

A semente estava fixa em `seed=1` dentro de `madeiras.py`, o que impedia o protocolo multi-semente. Foi parametrizada ao longo da pilha, com padrão 1: `chamando_nsga2(seed=...)`, `ParametrosAlgoritmo.seed`, coluna `cfg_seed` da planilha. As planilhas da Matéria continuam lendo semente 1, então os resultados anteriores são reproduzidos sem alteração. Verificado: mesma semente reproduz, semente diferente muda o resultado.

## Campanha

`engstruct_casos.xlsx`: 40 espécies × 4 vãos × 3 cenários × 5 sementes = **2400 rodadas**, Sobol desligada, pop 50, 300 gerações, N_c = 5, rho = 5%.

Cadeia reprodutível, resolvendo a dívida técnica das tabelas sem script:

1. `paper/engstruct/scripts/gerar_base_especies.py` lê `artigo_fabricio.md` e grava `paper/engstruct/dados/base_especies.csv` mais os metadados de origem de cada coluna. Reproduz a distribuição D20=3, D30=3, D40=11, D50=10, D60=13 e os números do `02_materials.tex` (faixa −38,3% a +45,9% na D50, 23 espécies com E abaixo da classe).
2. `paper/engstruct/scripts/gerar_casos_engstruct.py` monta a planilha a partir dessa base.
3. `rodar_lote_engstruct.py` executa, serial, com `--retomar`.

Piloto cronometrado: ~20 s por rodada, ~13 h a campanha completa. Uma semente inteira (`--filtro _s1`, 480 rodadas) fecha em ~2,7 h e já dá ordem de grandeza.

Resultado do piloto, Angelim-pedra (D40) em L = 10 m, semente 3: volume mínimo 16,150 m³ em `esp`, 15,253 m³ em `rig` (−5,56%) e 15,578 m³ em `cls` (−3,54%). O efeito controlado é **maior** que o prático, isto é, densidade e resistência compensam parte do efeito da rigidez. Três pontos não são resultado; serve só para confirmar que a campanha produz sinal mensurável.

## Pendências antes de rodar a campanha completa

- Confirmar o fator característico do cisalhamento a partir da média (usado 0,70; o gerador antigo usava 0,54, provavelmente herdado da NBR 7190:1997). Baixo impacto: no Artigo 1 o cisalhamento ficou em utilização máxima de 60%.
- Conferir a largura tributária: `restringir_espaco` devolve espaçamento livre e o avaliador o usa como largura tributária e como vão do tabuleiro. Pendência herdada da transferência da Matéria, ainda não resolvida.
- Rodar o piloto de uma semente antes de comprometer as 13 h.
- `references.bib` tem três teses não citadas (ADOLFS2011, Moraes2023, MIOTTO2009). Não aparecem na bibliografia porque o biblatex só imprime o que é citado, mas convém remover para não voltarem por engano — a regra do projeto é citar só artigo.
