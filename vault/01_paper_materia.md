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

Texto redigido de ponta a ponta com os resultados pendentes marcados em vermelho.
**Nenhuma das 20 células foi rodada ainda** — ou, se foi, o resultado não está no `.tex`.

Estrutura: `00_nomenclature`, `01_introduction`, `02_optimization`, `03_methodology`,
`04_results`, `05_conclusions`, `appendices`, `declarations`.

## Ordem de execução pendente

1. **Rodar a célula C-13 primeiro, cronometrando.** Esse tempo × 23 (20 células + 3
   níveis extras de ρ) é o custo total do lote. Descobrir isso antes, não depois.
2. **Definir `N_gen` e `N_c`** pela curva de hipervolume da C-13 e preencher a Tabela
   `tab:nsga2` em `02_optimization.tex`. Os dois valores têm de ser os mesmos nas 20
   células — decidir uma vez.
3. **Análises da C-13** (§4.3): fronteira, Monte Carlo no espaço de projeto, utilização,
   custo da robustez, validação independente, hipervolume, Sobol, boxplot.
4. **Varredura das 20 células** (§4.4) → Tabela `tab:resultados_matriz`.
5. **Ábacos** (§4.5) a partir da tabela consolidada.
6. **Conferência manual** do Apêndice A. Fazer de verdade: é a única validação ponta a
   ponta do modelo estrutural em todo o trabalho.
7. **Conclusões** (§5) — cinco blocos vermelhos, um por achado.

## Figuras a gerar

Salvar em `figuras/` com **exatamente** estes nomes (o `.tex` já os referencia):

| Arquivo | Seção |
|---|---|
| `fronteira_C13.png` | 4.3.1 |
| `fronteira_vs_mc_C13.png` | 4.3.2 |
| `utilizacao_C13.png` | 4.3.3 — barras horizontais, linha de referência em 100 % |
| `custo_robustez_C13.png` | 4.3.4 — 4 fronteiras sobrepostas |
| `convergencia_hv.png` | 4.3.6 |
| `sobol_heatmap_C13.png` | 4.3.7 |
| `boxplot_variaveis_C13.png` | 4.3.8 |
| `abaco_volume_vs_vao.png` | 4.5 — x = L, y = V, uma curva por classe |
| `abaco_volume_por_m2.png` | 4.5 |
| `abaco_diametro_vs_vao.png` | 4.5 |

As demais (interface, fluxograma, caminhão) já estão na pasta.

## Armadilhas conhecidas

- **Célula inviável.** A rotina levanta `ValueError` quando não há solução viável —
  provável em D20 com vão de 6 m. Isso é **resultado**, não erro: registrar "inviável"
  na linha da tabela e comentar no texto. **Não reduzir a robustez para forçar solução.**
- **Validação de Monte Carlo circular.** A semente das perturbações da §4.3.5 tem de ser
  diferente da usada na otimização. Reaproveitar os mesmos multiplicadores faz a
  validação validar a si mesma, e o resultado não vale nada.
- **Monotonicidade.** Na tabela consolidada o volume deve crescer com o vão dentro de
  cada classe e cair de D20 para D60 em cada vão. Quebra de monotonicidade quase sempre
  significa que a célula não convergiu — aumentar `N_gen` e rodar só ela de novo.

## Antes de submeter

- [ ] Nenhum `\tofill` nem `fillblock` restante
- [ ] Nenhuma caixa "Missing figure" no PDF (o preâmbulo as desenha silenciosamente,
      então o documento compila mesmo faltando figura — conferir visualmente)
- [ ] Nenhum `??` de referência cruzada
- [ ] Formato conferido contra as instruções aos autores da Revista Matéria
