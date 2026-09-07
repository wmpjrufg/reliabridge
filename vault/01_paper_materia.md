# Artigo 1 — Revista Matéria

**Pasta:** `paper/materia/`
**Idioma:** português
**Título:** *Projeto inteligente e otimização robusta multiobjetivo de pontes de madeira:
uma abordagem paramétrica e automatizada*

## Mensagem do artigo

Apresentação da plataforma de dimensionamento paramétrico de pontes de madeira para
estradas vicinais, demonstrada por uma varredura de vãos × classes de resistência que
resulta em **ábacos de anteprojeto**.

O texto é propositalmente extenso porque serve também de base para a dissertação.

> **2026-09-08:** confirmado que este artigo fica na Revista Matéria — **não vai ser
> elevado a um periódico internacional de nível Structures**, e não haverá seção de
> validação contra ponte executada, por não haver exemplo real disponível. Ver **D-15**
> em `04_decisoes.md`. Não relitigar essa pergunta.

## Autoria (atual)

1. Wanderlei M. Pereira Junior — UFCAT (correspondente)
2. Priscilla Silva Teotônio — UFCAT
3. Pedro Henrique Gomes Duarte — UFCAT
4. Wellington A. da Silva — UFCAT
5. André Luís Christoforo — UFSCar
6. Matheus Henrique Morato de Moraes — UFG
7. João Paulo M. Lopes — UFCAT

> **2026-08-12:** Enzo Moura Rezende, Maria José Pereira Dantas e Fran Sergio Lobato
> foram **removidos** deste artigo. Os três estão no artigo do Engineering Structures.
> Ver `04_decisoes.md`.
> Atenção: `pages/home.py` ainda credita os três na equipe da plataforma — por decisão
> explícita, créditos da plataforma ≠ autoria do artigo. Não "corrigir" sem perguntar.

## Configuração fixa (já escrita no texto — não alterar sem alinhar)

| Item | Valor |
|---|---|
| Trem tipo | TB-240 (roda 40 kN, multidão 4 kPa) |
| Largura da pista | 4,5 m (pista simples) |
| Vãos | 3,0 / 4,0 / 5,0 / 6,0 m |
| Classes | D20, D30, D40, D50, D60 |
| Células | 20 (C-01 a C-20, Tabela `tab:matriz`) |
| Célula de referência | **C-13** = L 5,0 m + D40 |
| Robustez | ρ = 5 % (e 0 / 2,5 / 5 / 10 % só na C-13) |

A faixa 3–6 m foi escolhida para manter toda a matriz na **mesma fórmula de momento**
(`eq:mqk30`). Estender para 7 m ou mais muda a fórmula e cria uma quebra nas curvas
dos ábacos que precisa ser explicada no texto.

## Estado atual

**2026-09-06:** as 20 células foram rodadas (ρ = 5 %) e os resultados estão em
`simulacaoes_/`. O `.tex` foi preenchido com tudo que esses dados sustentam e compila
limpo em 37 páginas. **O detalhamento completo — números, achados, auditoria dos dados
de entrada e o que continua pendente — está em
[`08_preenchimento_materia.md`](08_preenchimento_materia.md).**

**2026-09-07:** a matriz foi reprocessada com `a = 1,5 m` (lote em
`simulacaoes_/lote_eixos_1p5/`) e o artigo inteiramente refeito sobre os números novos:
resumo, §4, §5 e todas as tabelas e figuras. O PDF compila limpo em 36 páginas. As figuras
foram geradas em **português e inglês** — as em inglês estão em `figuras/en/`, com os
mesmos nomes de arquivo, para a versão que será submetida em inglês.

**2026-09-08:** custo da robustez fechado (§4.3.3) e Apêndice A escrito e validado
(D-16; Apêndice B removido). **O corpo do artigo está pronto.** Único vermelho restante:
`title_authors.tex` (e-mail/ORCID/CEP, só os autores preenchem) e as definições em
`preamble.tex`. PDF compila limpo em 43 páginas, sem overfull, sem warning.

**Antes de submeter de verdade, ainda falta:** os dados de `title_authors.tex`;
`declarations.tex` — contribuição CRediT (financiamento já preenchido: CAPES
88881.914003/2023-01); conferir φ=0,60 contra a Tabela 20 da NBR 7190-1 (baixo risco);
e o checklist de formato contra as instruções aos autores da Revista Matéria, que ainda
não foi verificado contra o site da revista.

Falta ainda conferir o coeficiente de fluência `φ = 0,60` na Tabela 20 da NBR 7190-1 (o
texto original dizia 0,80).

Estrutura: `00_nomenclature`, `01_introduction`, `02_optimization`, `03_methodology`,
`04_results`, `05_conclusions`, `appendices`, `declarations`.

## Ordem de execução pendente

1. ~~Rodar a célula C-13 primeiro, cronometrando~~ ✅ — 30,7 s por célula, 10,2 min o
   lote. Já está na `tab:nsga2` e na §5.
2. ~~Definir `N_gen` e `N_c`~~ — feito: `N_gen = 150`, `N_pop = 50`, `N_c = 30`,
   confirmados a posteriori pelo hipervolume em todas as 20 células.
3. ~~Análises da C-13~~ ✅ — fronteira, utilização, hipervolume, Sobol, boxplot e
   **custo da robustez** (§4.3.3, ρ = 0/2,5/5/10 %, script em
   `gerar_casos_robustez.py` + `rodar_lote_robustez.py`, resultados em
   `simulacaoes_/custo_robustez_C13/`). As duas análises de Monte Carlo saíram do
   escopo — ver **D-14**.
4. ~~Varredura das 20 células~~ ✅ → `tab:resultados_matriz` completa.
5. ~~Ábacos~~ ✅ — as três figuras estão geradas.
6. ~~Conferência manual~~ ✅ — Apêndice A escrito e validado (script independente,
   1e-7 de diferença contra a avaliação nominal). Apêndice B removido (D-16).
7. ~~Conclusões~~ ✅ — os cinco blocos preenchidos.

## Figuras a gerar

Salvar em `figuras/` com **exatamente** estes nomes (o `.tex` já os referencia):

| Arquivo | Seção | Estado |
|---|---|---|
| `pareto_frontier_C13.png` | 4.3.1 | ✅ (o nome é este, não `fronteira_C13.png`) |
| `utilizacao_C13.png` | 4.3.2 — barras horizontais, linha em 100 % | ✅ |
| `custo_robustez_C13.png` | 4.3.3 — 4 fronteiras sobrepostas | ✅ |
| `convergencia_hv.png` | 4.3.4 | ✅ |
| `sobol_heatmap_C13.png` | 4.3.5 | ✅ |
| `boxplot_variaveis_C13.png` | 4.3.6 | ✅ |
| `abaco_volume_vs_vao.png` | 4.5 — x = L, y = V, uma curva por classe | ✅ |
| `abaco_volume_por_m2.png` | 4.5 | ✅ |
| `abaco_diametro_vs_vao.png` | 4.5 | ✅ |

As demais (interface, fluxograma, caminhão) já estão na pasta. O `.tex` referencia
`inicio.png` em minúsculo — o arquivo foi renomeado de `Inicio.png` para não quebrar no
Overleaf.

As nove figuras de resultado são geradas por `gerar_figuras_materia.py`, **em português
e em inglês**: PT em `figuras/`, EN em `figuras/en/` com os mesmos nomes. Para a versão em
inglês, basta acrescentar `en/` ao `\graphicspath`.

## Armadilhas conhecidas

- ~~**Célula inviável.**~~ Não se materializou: as 20 células convergiram para soluções
  viáveis, inclusive a C-16 (6 m + D20). A ressalva original continua valendo se a
  matriz for re-rodada com outros parâmetros — registrar "inviável" na linha e comentar,
  **sem reduzir a robustez para forçar solução**.
- ~~**Validação de Monte Carlo circular.**~~ Deixou de valer para este artigo: as duas
  seções de Monte Carlo saíram do escopo (**D-14**). A ressalva sobre a semente continua
  registrada em D-11 caso a validação seja retomada em algum desdobramento.
- **Monotonicidade.** Na tabela consolidada o volume deve crescer com o vão dentro de
  cada classe e cair de D20 para D60 em cada vão. Quebra de monotonicidade quase sempre
  significa que a célula não convergiu — aumentar `N_gen` e rodar só ela de novo.
  *Situação em 2026-09-07:* a matriz reprocessada é **integralmente monotônica**; o
  empate D30/D40 no vão de 4 m, que existia no lote antigo, desapareceu.

## Antes de submeter

- [ ] Nenhum `\tofill` nem `fillblock` restante
- [ ] Nenhuma caixa "Missing figure" no PDF (o preâmbulo as desenha silenciosamente,
      então o documento compila mesmo faltando figura — conferir visualmente)
- [ ] Nenhum `??` de referência cruzada
- [ ] Formato conferido contra as instruções aos autores da Revista Matéria
