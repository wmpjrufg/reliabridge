# _vault — área de trabalho do paper ReliaBridge

Espaço de rascunho, auditoria e planejamento para transformar o repositório em um
artigo submissível a *Structures* (Elsevier) ou *Structural and Multidisciplinary
Optimization* (Springer).

> **Este diretório é ignorado pelo git** (`.gitignore:93`). É o lugar certo para
> PDFs de referência (que não podem ser redistribuídos), rascunhos, resultados
> intermediários e anotações. Nada aqui vaza para o repositório público.

## Organização

| Pasta / arquivo | Conteúdo |
|---|---|
| `00_auditoria_codigo.md` | Estado real do código vs. o que o paper afirma. **Ler primeiro.** |
| `01_roadmap.md` | Plano priorizado: o que fazer, em que ordem, e qual figura/tabela cada item gera |
| `02_revistas_alvo.md` | Structures vs. SMO — escopo, o que cada uma exige, posicionamento |
| `refs/` | PDFs das referências base + `entradas.bib` (ver `refs/README.md` para o índice) |
| `notas/` | Fichamento de leitura, um arquivo por trabalho (`notas/_template_leitura.md` para novos) |
| `experimentos/` | Especificação de cada experimento numérico que vira figura/tabela |

## Estado do paper

O rascunho vive em [paper/final/](../paper/final/) e já tem estrutura completa
(introdução, metodologia, resultados, conclusões, bibliografia). As caixas
`\sugestao{...}` no LaTeX marcam os pontos onde falta resultado — elas estão
consolidadas e priorizadas em `01_roadmap.md`.

## Fluxo de trabalho sugerido

1. Corrigir os bloqueadores de `00_auditoria_codigo.md` (sem isso, os números do
   paper não sustentam revisão).
2. Rodar os experimentos de `experimentos/` na ordem do `01_roadmap.md`.
3. Substituir cada `\sugestao{...}` pelo resultado correspondente.
4. Escolher a revista com base em `02_revistas_alvo.md` e adaptar formato/idioma.
