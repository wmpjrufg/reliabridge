# Paper 1 — Revista Matéria — guia de preenchimento

**Mensagem do artigo:** apresentação da plataforma de dimensionamento paramétrico de pontes
de madeira para estradas vicinais, demonstrada por uma varredura de vãos × classes de
resistência que resulta em ábacos de anteprojeto.

Este texto é propositalmente extenso, pois servirá também de base para a dissertação.

## Configuração fixa (já escrita no texto, não alterar sem alinhar)

| Item | Valor |
|---|---|
| Trem tipo | TB-240 (roda 40 kN, multidão 4 kPa) |
| Largura da pista | 4,5 m (pista simples) |
| Vãos | 3,0 / 4,0 / 5,0 / 6,0 m |
| Classes | D20, D30, D40, D50, D60 |
| Células | 20 (C-01 a C-20, ver Tabela `tab:matriz`) |
| Célula de referência | **C-13** = L 5,0 m + D40 |
| Robustez | ρ = 5 % (e 0 / 2,5 / 5 / 10 % só na C-13) |

A faixa 3–6 m foi escolhida para manter toda a matriz na mesma fórmula de momento
(`eq:mqk30`). Se você estender para 7 m ou mais, a fórmula muda e as curvas dos ábacos
ganham uma quebra que precisa ser explicada no texto.

## Como o texto está marcado

- `\tofill{...}` — **vermelho, inline.** Um número ou frase curta a substituir.
- `fillblock` — **bloco vermelho.** Instrução do que escrever ali. Apague o bloco inteiro
  e escreva o parágrafo no lugar.

Ao terminar, `grep -rn "tofill\|fillblock" *.tex` deve retornar apenas as definições
em `preamble.tex`. Enquanto houver vermelho no PDF, o texto não está pronto.

## Ordem de execução

1. **Rodar a célula C-13 primeiro**, cronometrando. O tempo dessa única execução multiplicado
   por 23 (20 células + 3 níveis extras de ρ) é o custo total do lote. Descubra isso antes
   de começar, não depois.
2. **Definir `N_gen` e `N_c`** a partir da curva de hipervolume da C-13 e preencher a
   Tabela `tab:nsga2` em `02_optimization.tex`. Esses dois valores precisam ser os mesmos
   em todas as 20 células — decida uma vez.
3. **Análises da C-13** (§4.3): fronteira, utilização, custo da robustez, hipervolume,
   Sobol, boxplot. As duas análises de Monte Carlo saíram do escopo — ver D-14 em
   `vault/04_decisoes.md`. Não reintroduzir.
4. **Varredura das 20 células** (§4.4) → Tabela `tab:resultados_matriz`.
5. **Ábacos** (§4.5) a partir da tabela consolidada.
6. **Conferência manual** do Apêndice A. Faça isso de verdade: é a única validação
   ponta a ponta do modelo estrutural em todo o trabalho.
7. **Conclusões** (§5), que são cinco blocos vermelhos, um por achado.

## Figuras a gerar

Salvar em `figuras/` com **exatamente** estes nomes — o `.tex` já os referencia:

| Arquivo | Seção |
|---|---|
| `pareto_frontier_C13.png` | 4.3.1 |
| `utilizacao_C13.png` | 4.3.2 — barras horizontais, linha de referência em 100 % |
| `custo_robustez_C13.png` | 4.3.3 — 4 fronteiras sobrepostas |
| `convergencia_hv.png` | 4.3.4 |
| `sobol_heatmap_C13.png` | 4.3.5 |
| `boxplot_variaveis_C13.png` | 4.3.6 |
| `abaco_volume_vs_vao.png` | 4.5 — x = L, y = V, uma curva por classe |
| `abaco_volume_por_m2.png` | 4.5 |
| `abaco_diametro_vs_vao.png` | 4.5 |

As demais figuras (interface, fluxograma, caminhão) já estão na pasta.

## Armadilhas conhecidas

- **Célula inviável.** A rotina levanta `ValueError` quando não há solução viável — provável
  em D20 com vão de 6 m. Isso é **resultado**, não erro: registre "inviável" na linha da
  tabela e comente no texto. Não reduza a robustez para forçar uma solução.
- ~~**Validação de Monte Carlo circular.**~~ Não se aplica mais: as seções de Monte
  Carlo saíram do artigo (D-14).
- **Unidade do objetivo.** O código minimiza **volume em m³**. Todo o texto foi padronizado
  em volume. Se aparecer "área" ou "m²" em algum lugar, é resíduo da versão antiga.
- **Monotonicidade.** Na tabela consolidada, o volume deve crescer com o vão dentro de cada
  classe e cair de D20 para D60 em cada vão. Quebra de monotonicidade quase sempre significa
  que aquela célula não convergiu — aumente `N_gen` e rode só ela de novo.

## Antes de submeter

- [ ] Nenhum `\tofill` nem `fillblock` restante
- [ ] Nenhuma caixa "Missing figure" no PDF (o preâmbulo as desenha silenciosamente,
      então o documento compila mesmo faltando figura — confira visualmente)
- [ ] Nenhum `??` de referência cruzada
- [ ] Formato conferido contra as instruções aos autores da Revista Matéria
