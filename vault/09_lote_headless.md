# Lote headless de pré-dimensionamento

**Data:** 2026-09-07
**Arquivos:** `rodar_lote.py` (script), `batch_pre_sizing.py` (módulo),
`batch_pre_sizing_casos.xlsx` (entrada)

Substitui o processo de rodar a interface Streamlit 20 vezes à mão e baixar o zip a cada
vez. O script lê uma planilha com uma linha por simulação e grava os mesmos artefatos,
inclusive o `pre_sizing_package.zip` no formato original.

Funciona porque **`madeiras.py` não importa Streamlit** — a linha 15 é
`from scipy import stats as st`, scipy e não streamlit. Todo o cálculo já era puro. O que
estava preso à interface era só a cola, que agora vive em `batch_pre_sizing.py`.
`pages/pre_sizing.py` ficou intocado.

---

## Como usar

Pelo terminal, que é o caminho mais direto:

```
.venv\Scripts\python.exe rodar_lote.py                  # as 20 células
.venv\Scripts\python.exe rodar_lote.py --apenas C_13    # só uma
.venv\Scripts\python.exe rodar_lote.py --retomar        # continua de onde parou
.venv\Scripts\python.exe rodar_lote.py --verificar       # só confere o cálculo, não roda nada
```

**Tem de ser o Python do `.venv`** — o do sistema não tem UQpy, e o script recusa rodar
com uma mensagem clara em vez de falhar no meio.

A planilha `batch_pre_sizing_casos.xlsx` já vem com as 20 células e `a = 1,5 m`. A saída
vai para `simulacaoes_/lote_eixos_1p5/`.

**Nunca apontar o destino para `simulacaoes_/simulacao_C_XX/`** — ver a seção de riscos.
`salvar_caso` recusa gravar por cima, mas o cuidado é do operador.

### Planilha de entrada

Separação por prefixo: `id` e tudo que começa com `cfg_` é configuração; o resto das
colunas é entrada do modelo e vai inteiro para o `beam_data.xlsx`.

| Coluna | Papel |
|---|---|
| `cfg_d_min` … `cfg_esp_tab_max` | limites de busca, em cm. `esp_*` são **espaçamentos**, não contagens |
| `cfg_pop_size`, `cfg_n_gen`, `cfg_n_checagens` | parâmetros do NSGA-II |
| `cfg_sobol`, `cfg_sobol_n_samples` | liga/desliga a Sobol e o número base de amostras |
| `cfg_ativo` | `FALSE` pula a linha sem apagá-la |
| `cfg_subdiretorio` | nome da pasta de saída |

Para varrer robustez (§4.3.3 do artigo, ρ = 0 / 2,5 / 10 %), alterar a coluna
**"Percentual de robustez"**, que é entrada do modelo e não configuração — o
`chamando_nsga2` lê o valor de dentro do dicionário de dados.

---

## Limites de busca das 20 execuções publicadas

Não estão no `beam_data.xlsx` (na interface são widgets sem valor padrão), mas foram
**recuperados por inversão**: as colunas `longarina_g_esp` e `tabuleiro_g_esp` são função
apenas da geometria gravada e dos limites, então dá para resolver. Reproduzem os valores
gravados com erro de 3e-16.

| Variável | Limites (cm) |
|---|---|
| `d` | 30 – 150 |
| `bw` | 5 – 60 |
| `h` | 5 – 60 |
| `esp_long` | 30 – 200 |
| `esp_tab` | 2 – 5 |

`pop_size = 50`, `n_gen = 150`, `n_checagens = 30`, `ρ = 5 %`. São os padrões das
dataclasses do módulo. `bw_max` e `h_max` não aparecem em nenhuma restrição gravada e
foram determinados por impressão digital: rodando 6 gerações e comparando o número de
soluções não dominadas por geração contra o `hypervolume_convergence.csv` de referência,
só `bw_max = 60, h_max = 60` reproduz `[9, 19, 26, 25, 26, 30]`.

---

## Reprodutibilidade — ler antes de comparar resultados

**Mesma máquina, mesmas entradas: resultado idêntico.** Verificado, três execuções
seguidas dão o mesmo `vmin` até a nona casa. As sementes são fixas no código
(`minimize(seed=1)`, `SobolSensitivity(random_state=1)`, `default_rng(1)`).

**Entre máquinas diferentes: não.** O modelo mecânico difere no último bit do ponto
flutuante e o NSGA-II amplifica isso.

Medido contra as 20 simulações publicadas:

- O modelo reproduz os objetivos e as restrições gravados com diferença máxima de
  **1e-14** nas 20 células — precisão de máquina. O cálculo é o mesmo.
- Mas re-rodando a C-13 com as entradas originais, a trajetória bate **exatamente até a
  geração 6** e diverge a partir da 7. A fronteira final é equivalente, não idêntica:
  `vmin` 3,935 contra 3,991 publicado (1,4 %).

A causa é que as simulações originais foram rodadas em outra máquina. Uma diferença de
alguns ULP no ponto flutuante inverte uma comparação de dominância, e a busca segue por
outro caminho.

**Consequências práticas:**

1. Não exigir igualdade numérica ao comparar com as saídas antigas. A função
   `comparar_com_referencia` reporta `estrutura_igual` (mesmos membros, mesmas colunas,
   mesmo formato) e uma diferença numérica informativa — é `estrutura_igual` que se exige.
2. O teste de fidelidade que vale é **`rodar_lote.py --verificar`**, que reavalia as
   soluções já gravadas e confere se o cálculo mudou. Não há busca envolvida, então não
   depende do caminho do NSGA-II. Hoje a maior diferença nas 20 células é 2,5e-14.
3. **Reprocessar a matriz muda os números do artigo mesmo mantendo tudo igual.** Vale uma
   frase no texto sobre isso, já que a Revista Matéria pede reprodutibilidade: declarar
   as sementes e registrar que a fronteira é reprodutível na mesma máquina.

---

## Riscos registrados

**Os arquivos soltos em `simulacaoes_/simulacao_C_XX/` não são os artefatos originais.**
Em todas as 20 células o `pre_sizing_results_optimized.xlsx` solto difere do membro do
zip: são as colunas auxiliares (a coluna "G") e as 3 linhas de agregado adicionadas à mão
para o artigo. Em C-13 o `beam_data.xlsx` solto também foi re-salvo pelo Excel.

Portanto: **o zip é a única referência confiável**, e o lote nunca escreve nessas pastas.

As pastas soltas `simulacaoes_/simulacao_C_XX/` foram removidas do disco em 2026-09-07, ao
disparar o lote do `a = 1,5`. **Nada se perdeu:** os 200 arquivos das 20 simulações estão
no commit `b0ceb0ff`, nos caminhos antigos organizados por classe. Para recuperar uma:

```
git checkout b0ceb0ff -- simulacaoes_/simulacao_classe_D40/simulacao_C_13/
```

Conferido: a C-13 versionada está íntegra — o zip traz os 9 membros e `vmin = 3,991296`,
o valor publicado, e o `.xlsx` solto preserva as edições manuais (53×17, com a coluna G).

Outros pontos, todos com guarda no código:

- Interpretador errado: a Sobol só falharia depois do NSGA-II. O script checa
  `madeiras._UQPY_DISPONIVEL` antes de começar e recusa.
- Célula vazia em campo obrigatório desloca o schema do `beam_data.xlsx`.
  `ler_planilha_casos` rejeita.
- Lote longo caindo no meio: cada caso é gravado assim que termina e o `_lote_resumo.xlsx`
  é reescrito a cada iteração. `pular_existentes=True` retoma.

---

## Saída

```
simulacaoes_/lote_eixos_1p5/
  simulacao_C_01/ … simulacao_C_20/   # 10 arquivos cada, igual ao download da interface
  _lote_casos.xlsx                    # planilha efetivamente usada
  _lote_resumo.xlsx                   # status, indicadores e tempos por caso
  _lote_ambiente.md                   # interpretador, versões e data
```

O `_lote_resumo.xlsx` traz `t_nsga2_s` e `t_sobol_s` separados. A média de `t_total_s`
fecha o `\tofill` de tempo médio de processamento por célula que ainda está pendente na
Tabela de parâmetros do NSGA-II e na conclusão do artigo.

## Custo medido

Uma célula completa (C-13, `a = 1,5`, `pop 50 × 150 gerações × 30 checagens`, Sobol com
20 000 amostras): **147 s**, sendo 116 s de NSGA-II e 28 s de Sobol. O lote das 20 células
fica na ordem de **50 minutos**. Ao contrário do que se supunha, o NSGA-II domina o custo,
não a Sobol.

---

## Lote do Artigo 2 (Engineering Structures)

Mesma máquina, planilha e script próprios.

```
.venv\Scripts\python.exe gerar_casos_engstruct.py            # monta engstruct_casos.xlsx
.venv\Scripts\python.exe rodar_lote_engstruct.py             # as 320 rodadas
.venv\Scripts\python.exe rodar_lote_engstruct.py --filtro _L03_   # só um vão
.venv\Scripts\python.exe rodar_lote_engstruct.py --filtro _esp    # só uma base
```

`gerar_casos_engstruct.py` lê as 40 espécies direto de
`paper/engstruct/tabelas/tab_especies.tex`, então a planilha se regenera sozinha se a
tabela mudar. Saída em `simulacaoes_/lote_engstruct/`.

### A matriz

**40 espécies × 4 vãos (3, 5, 8, 10 m) × 2 bases = 320 rodadas.** Ids no formato
`E05_L10_esp`: espécie 05, vão 10 m, base espécie. `cls` é a base classe.

- base **`esp`**: propriedades medidas — densidade aparente, `f_mk = 0,70·f_m,m`,
  `f_v0k = 0,54·f_v0,m` (fatores declarados no cabeçalho de `tab_especies.tex`) e
  `E = E_M0` medido na flexão;
- base **`cls`**: valores tabelados da classe NBR em que a espécie foi enquadrada.

As colunas `cfg_ref_*` da planilha trazem espécie, classe, base e vão, para rastrear cada
linha sem abrir o `.tex`. Levam o prefixo `cfg_` justamente para não entrarem no cálculo.

### Parâmetros fixos — iguais aos do Artigo 1

**Por decisão do autor (2026-09-07), tudo é igual ao Artigo 1.** A única coisa que muda
entre os dois estudos é a faixa de vãos, para que a comparação entre eles seja direta; as
propriedades das espécies, que são experimentais, ficam preservadas como estão.

Pista 4,5 m, TB-240 (roda 40 kN, multidão 4 kPa), `p_gk` = 0,1 kPa, `a` = 1,5 m, classe de
umidade 3, carregamento de média duração, γ 1,35/1,50/1,40/1,80, ψ₂ = 0,30, φ = 0,60,
ρ = 5 %. Limites de busca e parâmetros do NSGA-II também iguais.

A `tab:vaos` de `engstruct/03_methodology.tex` trazia `p_gk` = 1 kPa, umidade 1 e
carregamento permanente; foi corrigida para bater com o que será rodado.

### Custo

Sem Sobol, ~23 s por rodada, o que põe as 320 em torno de **2 horas**. A Sobol vem
desligada na planilha por isso — o Artigo 2 não precisa dela, e ligá-la multiplicaria o
lote. Para ligar: `gerar_casos_engstruct.py --sobol`, ou editar a coluna `cfg_sobol`.

### Duas coisas a decidir antes de fechar o artigo

1. **C-02, o módulo de elasticidade.** A base `esp` usa `E_M0`, medido na flexão, e a base
   `cls` usa o `E_c0,med` tabelado, que é de compressão. É exatamente o offset apontado no
   item crítico C-02 de `05_revisao_critica.md`, e parte do "erro de enquadramento" pode
   ser esse offset. O gerador aceita `--fator-e F` para aplicar uma conversão e refazer a
   planilha, o que permite a análise de sensibilidade sugerida lá.
2. **Tabuleiro.** Recebe as mesmas propriedades da longarina, como no Artigo 1. Se o
   protocolo previr tabuleiro de outra espécie ou classe, o gerador precisa mudar.

### Sinal preliminar

Rodando três casos de teste: em `E05_L10_esp` (Angelim-pedra, vão de 10 m) a verificação
governante é a **flecha**, ao passo que nos vãos de 3 m é flexão. É exatamente a migração
que a tese do Artigo 2 prevê, e que o passo 4 da ordem de execução manda confirmar antes
de tudo. Não é resultado, é indício — mas indica que o artigo não vai cair no cenário
"a flecha nunca governa".
