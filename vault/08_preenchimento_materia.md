# Preenchimento do Artigo 1 (Matéria) — o que foi feito e o que falta

**Data:** 2026-09-07 (reprocessado com `a = 1,5 m`)
**Base de dados:** `simulacaoes_/lote_eixos_1p5/` (20 células, ρ = 5 %)
**Estado do PDF:** compila limpo em 36 páginas, sem *overfull*, sem referência cruzada
quebrada. Compilado localmente com MiKTeX + `latexmk`.

Este arquivo registra os números que entraram no `.tex`, para que o preenchimento
restante seja feito sem ter que reabrir as planilhas.

---

## 1. Conteúdo de cada arquivo entregue por célula

| Arquivo | O que é |
|---|---|
| `beam_data.xlsx` | dados de entrada usados na otimização |
| `design_variables_boxplot.png` | dispersão das variáveis na fronteira |
| `design_variables_statistics.xlsx` | tabela de estatísticas descritivas |
| `hypervolume_convergence.csv` / `.png` | convergência do hipervolume |
| `pareto_frontier.png` | fronteira eficiente |
| `pre_sizing_results_optimized.xlsx` | fronteira e valor de cada restrição |
| `sobol_total_indices.xlsx` / `.png` | índices de Sobol de efeito total |

### Convenções de leitura da planilha de resultados

- **`g_max` ignora `longarina_g_esp` e `tabuleiro_g_esp`.** O máximo se toma só sobre
  `longarina_g_m`, `longarina_g_v`, `longarina_g_f` e `tabuleiro_g_m`. As duas colunas
  de espaçamento são restrições geométricas de enquadramento, não expressam margem
  estrutural.
- A **coluna sem cabeçalho** depois de `of_volume_m3` (o pandas lê como `Unnamed: 6`) é
  a coluna "G": distância absoluta entre o volume daquela solução e o volume médio da
  fronteira.
- As **três últimas linhas** têm as variáveis de projeto vazias e trazem, em
  `of_volume_m3`, a média da fronteira, o menor volume e o maior volume. Remover com
  `dropna(subset=['d_cm'])` antes de qualquer estatística.
- As funções limite são normalizadas como `g = (S − R)/R`, logo o **grau de utilização
  é `(1 + g) × 100 %`**. Foi assim que a Figura `utilizacao_C13.png` foi gerada.

---

## 2. O que foi preenchido

| Seção | Conteúdo |
|---|---|
| Resumo | achados quantificados |
| `tab:parametros` | corrigidos `a` e `φ` para bater com `beam_data` — **ver §4** |
| §4.3.1 | `tab:solucoes_ref` com 7 soluções + análise da fronteira |
| §4.3.3 | utilização das 4 verificações + figura nova |
| §4.3.6 | `tab:hv` reestruturada: HV, *spacing* e geração de estabilização das **20 células** |
| §4.3.7 | `tab:sobol` com variável dominante + coluna nova de participação relativa |
| §4.3.8 | `tab:estatistica` com quartis + discussão |
| §4.4 | `tab:resultados_matriz` completa + coluna nova `g_max` + os 3 eixos de discussão |
| §4.5 | roteiro de uso dos ábacos + condições de validade |
| §5 | conclusões de plataforma, varredura e sensibilidade |

**Figuras:** as oito são geradas por `gerar_figuras_materia.py`, **em português e em
inglês** — PT em `figuras/`, EN em `figuras/en/` com os mesmos nomes de arquivo, de modo
que a versão em inglês só precise acrescentar `en/` ao `\graphicspath`. As quatro da
plataforma (fronteira, boxplot, hipervolume, Sobol) são reproduzidas pelas mesmas funções
de `madeiras.py` a partir dos dados do lote; as outras quatro (utilização e os três
ábacos) são montadas no próprio script, no padrão visual da plataforma.

O `.tex` referenciava `figuras/inicio.png` mas o arquivo era `Inicio.png`. Renomeado —
quebraria a compilação no Overleaf (Linux é *case-sensitive*).

**Correção de nome:** a figura da fronteira é `pareto_frontier_C13.png`, e não
`fronteira_C13.png` como está na tabela do `01_paper_materia.md`.

---

## 3. Achados principais (matriz com `a = 1,5 m`)

1. **Nem a flecha nem o cisalhamento governam qualquer célula.** As 20 são governadas por
   flexão: 12 pela longarina e 8 pelo tabuleiro. A propriedade determinante é resistência
   em toda a faixa de 3 a 6 m, não rigidez — a folga no estado limite de serviço é de
   pelo menos 62 % em todas as células (δ/lim máximo de 0,377, na C-20). A migração
   resistência → rigidez está fora da faixa estudada.
2. **No vão de 3 m, a saturação no diâmetro mínimo vale a partir de D40.** C-03, C-04 e
   C-05 convergem para d ≈ 30 cm, o limite inferior do domínio. Especificar acima de D40
   nesse vão deixa de trazer economia. A redução D20→D60 no vão de 3 m é de 23,5 %,
   contra 42 a 46 % nos vãos de 4 a 6 m.
3. **Nenhuma célula deu inviável**, nem a C-16 (6 m + D20), que converge com d = 59,5 cm.
4. Lei de potência `V ∝ L^n`: n = 1,84 (D20), 1,62 (D30 e D40), 1,49 (D50), 1,37 (D60),
   todos com R² > 0,978.
5. **O primeiro degrau de classe é o mais rentável.** D20→D30 rende 19 a 23 % nos vãos de
   4 m ou mais, cerca de metade de toda a economia entre D20 e D60; os degraus seguintes
   rendem 8 a 17 %, sem decaimento estritamente monotônico.
6. Sobol: só **duas** variáveis concentram a sensibilidade — diâmetro (91–96 % nas três
   verificações da longarina) e espaçamento entre longarinas (81 % na flexão do
   tabuleiro). São também as duas de maior dispersão na fronteira (CV de 41,2 % e 32,6 %),
   ou seja, as verdadeiras variáveis de decisão, uma por subsistema. As outras três
   admitem tolerância de execução folgada; `b_w ≈ 45 cm` (CV 6,6 %) pode ser fixado a
   priori.
7. Hipervolume estabiliza entre as gerações 25 e 102 (média 54). `N_gen = 150` confirmado
   a posteriori para todas as células, com folga de ao menos 48 gerações.
8. **Custo:** 30,7 s por célula (24,4 s de NSGA-II + 5,9 s de Sobol), 10,2 min o lote.

### Monotonicidade

A matriz é **integralmente monotônica**: o volume cresce com o vão dentro de cada classe e
decresce de D20 para D60 dentro de cada vão, sem uma única inversão. O empate D30/D40 no
vão de 4 m, que existia no lote antigo, desapareceu.

---

## 4. Auditoria dos dados de entrada — LER ANTES DE SUBMETER

Conferi as 24 colunas de `beam_data.xlsx` das 20 células. **O desenho experimental está
correto:** variam exatamente o vão e as cinco propriedades dependentes de classe
(longarina e tabuleiro sempre da mesma classe); as outras 18 colunas são constantes nas
20 células. As propriedades de classe batem com a `tab:classes_madeira`, inclusive
`f_mk = f_c0k / 0,77` (25,97 / 38,96 / 51,95 / 64,94 / 77,92 MPa).

Duas entradas divergiam do que o `.tex` afirmava, e uma delas era um erro de verdade.

### 4.1 Distância entre eixos — RESOLVIDO

O lote original usava `a = 2,0 m`, valor errado vindo do preset `VEICULOS_PADRAO`. A
matriz foi **reprocessada em 2026-09-07 com `a = 1,5 m`** e o artigo foi inteiramente
refeito sobre os números novos. Ver **D-13** em `04_decisoes.md`.

Auditoria do lote novo: as 20 células retornaram `status = ok`, 50 soluções cada, Sobol
executada, sem avisos nem erros. Os `beam_data` das saídas confirmam `a = 1,5` e todos os
demais parâmetros fixos; variam apenas o vão e as cinco propriedades de classe. O volume
mínimo subiu nas 20 células em relação ao lote antigo, com média de +10,9 %, que é a
direção esperada de um `a` menor.

### 4.2 Coeficiente de fluência `φ = 0,6` — confirmar, mas é de baixo risco

O `.tex` dizia 0,80; os dados dizem 0,60. Conferir na Tabela 20 da NBR 7190-1:2022 qual
é o valor para madeira natural em **classe de umidade 3**.

Impacto pequeno e localizado: `φ` entra só como `ψ₂(1+φ)δ_qk`, então mexe apenas no
objetivo `f₂`. Na C-13, `δ/lim` iria de 0,2705 para 0,2999 (+11 %). **Nenhuma restrição
muda** — nem mesmo `g3`, porque a verificação de flecha que governa é a de carga
variável contra `L/360`, que não depende de `φ`. Se 0,8 for o correto, dá para decidir
entre re-rodar ou registrar a diferença.

---

## 5. O que continua em vermelho

| Onde | O que falta | Depende de |
|---|---|---|
| Apêndice A | conferência manual passo a passo | fazer à mão |
| Apêndice B | anexar memorial exportado | exportar da plataforma |
| `title_authors.tex` | e-mails institucionais, ORCID, CEPs | os autores |

### §4.3.3, custo da robustez — FECHADO em 2026-09-08

Reotimizada só a C-13, para ρ ∈ {0 %, 2,5 %, 5 %, 10 %} (D-06). Scripts:
`gerar_casos_robustez.py` monta `robustez_casos.xlsx` (4 linhas, a partir do `beam_data`
já corrigido da C-13 em `lote_eixos_1p5/`, variando só "Percentual de robustez");
`rodar_lote_robustez.py` roda e grava em `simulacaoes_/custo_robustez_C13/`. Sobol
desligada (a seção não pede). `gerar_figuras_materia.py` ganhou `figura_custo_robustez()`.

**Tempos** (sequenciais, mesma máquina, sem Sobol): 57 s (ρ=0%), 82 s (ρ=2,5%),
107 s (ρ=5%), 157 s (ρ=10%). A maior parte do salto ρ=0→2,5% vem de `N_c` colapsar para 1
avaliação quando ρ=0 (madeiras.py, `_criar_multiplicadores_robustez`); o resto é
diferença entre execuções únicas, não isolada estatisticamente.

**Achado — o custo não é uniforme na fronteira:**

| Métrica | ρ=2,5% | ρ=5% | ρ=10% |
|---|---|---|---|
| Solução de menor volume (extremo econômico) | +0,4% | +2,8% | **+10,1%** |
| Média em 3 níveis pareados de flecha (soluções de compromisso) | +0,3% | +6,1% | +6,3% |

No extremo econômico o custo mais que triplica de ρ=5% para ρ=10%; em soluções de
compromisso, satura entre 5% e 10%. Interpretação: a robustez penaliza
desproporcionalmente as soluções mais coladas nas restrições ativas — exatamente as que
a otimização determinística produz — e é branda sobre soluções com folga própria.
Preenchidos: `tab:custo_robustez`, a discussão de §4.3.3, o bloco de conclusão
correspondente e uma frase no resumo.

⚠️ **Achado um typo de path** ao rodar pela primeira vez: o destino saiu em
`simulacoes_/...` (faltando um "a") em vez de `simulacaoes_/...`. Os dados em si estão
corretos, só precisaram ser movidos de pasta. Corrigido no script.

### Removido do escopo em 2026-09-06 (D-14)

As duas seções de Monte Carlo saíram do artigo: a comparação com amostragem aleatória
(era a §4.3.2, com `fig:mc_ref` e `fronteira_vs_mc_C13.png`) e a validação por simulação
independente (era a §4.3.5, com `tab:validacao_mc`), mais o bloco de conclusão sobre a
otimização frente à amostragem aleatória. O algoritmo já foi validado e funciona.
**Não reintroduzir.** As subseções seguintes foram renumeradas: o custo da robustez, que
era §4.3.4, passou a **§4.3.3**.

---

## 6. Como reproduzir os números

Os scripts de extração e de geração de figuras foram rodados a partir das planilhas,
sem re-executar otimização. O caminho é curto: ler cada
`pre_sizing_results_optimized.xlsx`, aplicar as convenções da §1, e a solução reportada
na `tab:resultados_matriz` é sempre a de **menor `of_volume_m3`** da célula.
