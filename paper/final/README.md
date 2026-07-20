# Artigo: Projeto inteligente e otimização robusta de pontes de madeira

Artigo científico completo, redigido em português, seguindo o modelo LaTeX fornecido
(`paper/modelo`) e inspirado na abordagem, no rigor e no estilo do paper de referência
(de Moraes e Buttignol, *Structural Concrete*, 2025). O texto tem como principal
referência de qualidade e organização o material da Priscila.

## Como compilar

O projeto usa `biblatex` com `backend=biber`. Em Overleaf, basta abrir e compilar
com `pdfLaTeX`. Localmente:

```bash
pdflatex main
biber main
pdflatex main
pdflatex main
```

## Estrutura dos arquivos

| Arquivo | Conteúdo |
|---|---|
| `main.tex` | Arquivo principal que agrega todas as seções |
| `preamble.tex` | Preâmbulo do modelo, adaptado (babel português, `xcolor`, comando `\sugestao`) |
| `title_authors.tex` | Título e autores (preencher afiliações) |
| `abstract_keywords.tex` | Resumo e palavras-chave |
| `00_nomenclature.tex` | Nomenclatura |
| `01_introduction.tex` | Introdução (projeto clássico -> inteligente, robustez) |
| `02_methodology.tex` | Metodologia: sistema estrutural, formulação multiobjetivo, NSGA-II (com algoritmo), robustez (desvio de 5%), dimensionamento NBR 7190 e demonstração de cálculo |
| `03_results.tex` | Resultados: plataforma, Pontes 01/02, fronteiras, comparação Monte Carlo, efeito da robustez |
| `04_conclusions.tex` | Conclusões |
| `declarations.tex` | Declarações (dados, conflito, financiamento, contribuição) |
| `appendices.tex` | Apêndice (relatório de verificação) |
| `references.bib` | Referências (BibTeX) |
| `figuras/` | Figuras reutilizadas do material da Priscila |

## Conteúdo técnico obrigatório atendido

1. **Dimensionamento passo a passo** (Seção 2.6 e demonstração em 2.7): propriedades
   geométricas, ações permanentes e trem tipo, esforços, combinações, resistências e
   verificações, com exemplo numérico completo da longarina e do tabuleiro.
2. **Algoritmo de otimização** (Seção 2.3): NSGA-II com lógica, dominância, distância
   de aglomeração, pseudocódigo (Algoritmo 1) e tabela de parâmetros (pop=500,
   gerações=400, SBX 0,9/15, PM 20).
3. **Robustez** (Seção 2.5): todas as variáveis de projeto avaliadas sob desvio de
   5% (Eq. de perturbação), agregação por média de N_c checagens, e discussão do
   efeito sobre a fronteira eficiente.

## Sugestões de alto impacto (destaques em vermelho)

Ao longo do texto há caixas vermelhas geradas pelo comando `\sugestao{...}`, indicando
resultados adicionais que elevariam o artigo ao nível de periódico JCR elevado
(ex.: estudo de sensibilidade do parâmetro de robustez, hipervolume/convergência,
validação por Monte Carlo independente, índices de Sobol, estudo de caso real).
Cada caixa descreve o que precisa ser calculado, plotado ou analisado.

> Observação: os valores numéricos e figuras das Pontes 01 e 02 foram tomados como
> base a partir dos resultados da Priscila. As caixas em vermelho apontam os
> resultados a produzir/atualizar para a submissão final.
