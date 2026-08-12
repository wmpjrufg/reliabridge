# Próximos passos — fila de trabalho

Ordem pensada para **desbloquear o máximo com o mínimo de computação**. Os três
primeiros itens não exigem rodar otimização nenhuma e destravam quase tudo.

Legenda: ⬜ pendente · 🟦 em andamento · ✅ concluído

---

## Bloco 0 — Bloqueadores (fazer antes de qualquer rodada)

- ⬜ **P-01 · Localizar e citar o artigo-fonte das 40 espécies.** Tudo depende disso, e
  a coautoria também. Falar com o André Luís Christoforo. Perguntar de uma vez se a
  fonte reporta **desvio-padrão por espécie** — se reportar, destrava a linha de
  confiabilidade inteira (`07_linha_ciencia_de_dados.md`).
- ⬜ **P-02 · Validar a conversão média → característico** contra a fonte. Se ela já
  reportar característicos, usar os originais. *(Ver `03_dados_40_especies.md`.)*
- ⬜ **P-03 · Escrever `scripts/gera_tabelas_especies.py` e commitar** junto com a
  planilha de origem. Sem isso, P-02 vira trabalho manual em 40 linhas. *(C-08)*
- ⬜ **P-04 · Resolver E_M0 × E_c0,med.** É o furo mais provável de derrubar o artigo.
  *(C-02 em `05_revisao_critica.md`.)*

## Bloco 1 — Barato e de alto retorno (sem otimização)

- ⬜ **P-05 · Figura `E_vs_fc0.png`.** Dispersão de E_M0 contra f_c0,k, linhas verticais
  nos limites de classe, segmentos horizontais no E tabelado, angelim-pedra e goiabão
  anotados. Conta metade da história sozinha.
- ⬜ **P-06 · Reenquadrar as 40 espécies na EN 338** e preencher `tab:comparacao_normas`.
  Uma planilha. É o que torna o artigo relevante fora do Brasil. Conferir os valores
  contra a EN 338:2016 Tabela 2 — não de memória, não de fonte secundária.
- ⬜ **P-07 · Acrescentar CoV intraclasse e "fração acima de meio passo"** às tabelas de
  dispersão. *(C-03)*
- ⬜ **P-08 · Ajustar os 35 % → reportar 14 (35 %) e 12 (30 %).** *(C-04)*
- ⬜ **P-09 · Corrigir a frase do cisalhamento na introdução.** *(C-06)*
- ⬜ **P-10 · Entradas de norma no `.bib` e `\parencite` na primeira menção.** *(C-09)*

## Bloco 2 — Decide o formato do artigo

- ⬜ **P-11 · Cronometrar UMA rodada do NSGA-II** antes de planejar qualquer lote.
  Multiplicar por 320 (ou 480, com a variante C) e decidir com o número na mão.
- ⬜ **P-12 · Preencher `tab:governante` — a migração do critério governante.**
  **Não assumir o desfecho.** Três caminhos possíveis, todos já escritos no bloco
  vermelho da §4.1 de `04_results.tex`:
  - flecha passa a governar com o vão → artigo segue como está;
  - flecha governa sempre → reescrever em torno da magnitude, não da variação;
  - flecha nunca governa → resultado negativo, reescrever introdução e resumo.
- ⬜ **P-13 · Definir limite superior de diâmetro** por disponibilidade comercial de
  tora, antes de rodar os vãos de 8 e 10 m. *(C-07)*
- ⬜ **P-14 · Verificar a transição da fórmula de momento em L = 6 m.** Uma mudança de
  inclinação entre 5 e 8 m não pode ser confundida com efeito do material.

## Bloco 3 — O lote

- ⬜ **P-15 · Adotar o protocolo de três variantes (A / B / C).** *(C-01)*
- ⬜ **P-16 · Rodar com k = 5 sementes** e reportar ΔV como média ± desvio, ou reportar
  hipervolume por rodada. *(C-05)*
- ⬜ **P-17 · Varredura completa** → `tab:custo_enquadramento`.
- ⬜ **P-18 · Figura `continuo_vs_degraus.png`** — a figura central, um painel por vão.
- ⬜ **P-19 · Caso detalhado** (§4.4) e **limitações** (§4.5).
- ⬜ **P-20 · Conclusões 4, 5 e 6** e a implicação prática.

## Bloco 4 — Artigo 1 (paralelo, independente do Bloco 0)

Fila completa em [`01_paper_materia.md`](01_paper_materia.md). Resumo:

- ⬜ **P-21 · Rodar a C-13 cronometrando** → custo do lote de 23 execuções.
- ⬜ **P-22 · Fixar `N_gen` e `N_c`** pela curva de hipervolume da C-13.
- ⬜ **P-23 · Oito análises da C-13** (§4.3).
- ⬜ **P-24 · Varredura das 20 células** → `tab:resultados_matriz`.
- ⬜ **P-25 · Três ábacos** (§4.5).
- ⬜ **P-26 · Conferência manual do Apêndice A.** Fazer de verdade — única validação
  ponta a ponta do modelo estrutural em todo o trabalho.

## Bloco 5 — Antes de submeter o Artigo 2

- ⬜ **P-27 · Retraduzir para o inglês** e reverter `babel` para `[english]`. *(D-09)*
- ⬜ **P-28 · Converter para `elsarticle`** com citações numéricas.
- ⬜ **P-29 · Varrer `\tofill` e `fillblock`** — só devem restar as definições no
  `preamble.tex`.

---

## Notas de sequenciamento

- Blocos 0 e 1 **não exigem computação** e resolvem 6 dos 9 itens da revisão crítica.
  Se o tempo for curto, é aqui que ele rende mais.
- P-11 antes de qualquer planejamento de lote. O número de rodadas (320, ou 480 com a
  variante C) só é decidível com o tempo por rodada medido.
- P-12 é a bifurcação: até ele existir, não vale reescrever introdução nem resumo.
