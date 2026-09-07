# Auditoria do código vs. o que o paper afirma

Data original: 2026-07-25 · Commit base: `f0170362`
**Atualização 2026-07-25 (mesmo dia, sessão seguinte):** B1 e B2 foram corrigidos
pelo usuário — ver nota no topo de cada item abaixo. B3 (sinal de $f_2$) segue
aberto.

Levantamento do que o código realmente faz, comparado ao que
[paper/final/02_methodology.tex](../paper/final/02_methodology.tex) descreve.
Ordenado por gravidade.

---

## ✅ B1 — RESOLVIDO. A otimização robusta não estava implementada

> **Corrigido.** `_criar_multiplicadores_robustez` ([madeiras.py:1578](../madeiras.py#L1578))
> gera `n_checagens` multiplicadores $1+\rho\xi$ com `rng.default_rng(1)` fixo
> (*common random numbers*), aplicados às 5 variáveis em `_evaluate`
> ([madeiras.py:1704](../madeiras.py#L1704)). O texto abaixo é mantido como
> histórico do problema original.

**Onde:** [madeiras.py:1553-1573](../madeiras.py#L1553-L1573)

```python
dados = []
for _ in range(self.n_checagens):
    f, g, *_ = self.calcular_objetivos_restricoes_otimizacao(d, bw, h, esp_long, esp_tab)
    ...
df = pd.DataFrame(dados)
f = df[['f1', 'f2']].mean().tolist()
```

O laço chama a mesma função determinística `n_checagens` vezes com **exatamente os
mesmos argumentos** `(d, bw, h, esp_long, esp_tab)`. Não há nenhuma perturbação
aplicada. `self.perc_robustez` é armazenado em
[madeiras.py:1432](../madeiras.py#L1432) e **nunca mais é lido em lugar nenhum do
repositório** (verificado por busca global em `*.py`).

Consequência: a média de 10 valores idênticos é o próprio valor. O bloco é um
*no-op* matemático que custa 10× o número de avaliações do modelo estrutural.
**A "fronteira robusta" produzida até hoje é numericamente idêntica à fronteira
determinística.**

O paper, em contraste, descreve a Eq. `eq:perturbacao` com
$\tilde{x}_i^{(c)} = x_i(1 + \rho\,\xi_i^{(c)})$, $\rho = 0{,}05$,
$\xi \sim U[-1,1]$ — que não existe no código.

**Correção:** perturbar o vetor de projeto dentro do laço, antes de avaliar:

```python
rho = self.perc_robustez / 100.0
rng = np.random.default_rng(...)          # semente controlada, ver nota abaixo
x_nom = np.array([d, bw, h, esp_long, esp_tab])
for _ in range(self.n_checagens):
    xi = rng.uniform(-1.0, 1.0, size=x_nom.size)
    x_pert = x_nom * (1.0 + rho * xi)
    f, g, *_ = self.calcular_objetivos_restricoes_otimizacao(*x_pert)
```

**Decisões que precisam ser tomadas junto com a correção** (e justificadas no paper):

- **Semente.** Semente fixa por indivíduo torna a avaliação determinística e o
  NSGA-II bem-comportado, mas enviesa (todos veem o mesmo padrão de perturbação).
  Semente livre introduz ruído na função objetivo, o que degrada a convergência do
  NSGA-II. Recomendação: usar amostragem por *Latin Hypercube* de $N_c$ pontos
  fixa e comum a todos os indivíduos (*common random numbers*) — reduz variância
  entre indivíduos e é defensável perante revisor.
- **Quais variáveis perturbar.** Perturbar `n_long`/`n_tab` (espaçamentos) é
  discutível: são decisões de montagem, não tolerâncias de fabricação. O caso
  fisicamente forte é perturbar o **diâmetro da madeira roliça** ($d$), que tem
  variabilidade natural alta, e as dimensões serradas do tabuleiro ($b_w$, $h$).
  Ver E2 no roadmap.
- **Agregação.** Média (atual, na Eq. `eq:gmed`) vs. pior caso
  $\bar{g}_j = \max_c g_j$. A média deixa passar soluções que violam em metade das
  realizações. O `\sugestao` de [02_methodology.tex:179](../paper/final/02_methodology.tex#L179)
  já pede essa comparação — é um resultado barato e de alto valor.

---

## ✅ B2 — RESOLVIDO. Colunas trocadas no DataFrame de saída do NSGA-II

> **Corrigido.** `chamando_nsga2` ([madeiras.py:1926](../madeiras.py#L1926)) agora
> rotula `d/bw/h/esp/esp tab` na ordem correta de `X_nsga`, e todas as 6
> restrições ($g_1$–$g_6$) aparecem no retorno. O texto abaixo é mantido como
> histórico do problema original.

**Onde:** [madeiras.py:1653-1666](../madeiras.py#L1653-L1666)

A ordem das variáveis de projeto definida em `xl`/`xu`
([madeiras.py:1433-1434](../madeiras.py#L1433-L1434)) e lida em `_evaluate` é:

```
x[0]=d   x[1]=bw   x[2]=h   x[3]=n_long   x[4]=n_tab
```

Mas o DataFrame de retorno rotula:

```python
"d [cm]":   X_nsga[:, 0],   # ok
"esp [cm]": X_nsga[:, 1],   # ← na verdade é bw
"bw [cm]":  X_nsga[:, 2],   # ← na verdade é h
"h [cm]":   X_nsga[:, 3],   # ← na verdade é n_long
                            # ← n_tab (X[:,4]) é descartado
```

Toda tabela de soluções extraída da fronteira está com três colunas com rótulo
errado e uma variável de projeto ausente. Qualquer resultado do paper que liste
geometrias ótimas precisa ser refeito depois da correção.

Adicionalmente, o problema declara `n_ieq_constr=6` mas só 4 restrições
($g_1$–$g_4$) são reportadas; $g_5$ e $g_6$ (preenchimento de espaço) ficam de fora
do DataFrame. Não é erro de cálculo, mas impede auditar viabilidade das soluções.

---

## 🟠 B3 — Sinal de $f_2$: os objetivos não são antagônicos como o texto afirma

**Onde:** [madeiras.py:1545](../madeiras.py#L1545), `f2 = -res_f_total["of [-]"]`,
com `of [-] = delta_sd_1 / lim_1` ([madeiras.py:692](../madeiras.py#L692)).

Como o pymoo minimiza, `f2 = -δ_tot/δ_lim` significa **maximizar a utilização do
limite de flecha**. Ou seja: o algoritmo é premiado por chegar mais perto do
estado limite de serviço.

Isso contradiz o texto do próprio paper. O abstract
([abstract_keywords.tex:2](../paper/final/abstract_keywords.tex#L2)) e a
metodologia ([02_methodology.tex:66](../paper/final/02_methodology.tex#L66)) dizem
"maximizar o desempenho estrutural em serviço" — o que corresponde a **minimizar**
$\delta/\delta_{lim}$, não maximizar.

Pior: com o sinal atual, os dois objetivos são em boa parte **alinhados**, não
conflitantes. Reduzir o diâmetro da longarina reduz a área *e* aumenta
$\delta/\delta_{lim}$ — melhora ambos. O trade-off que sobra vem por um canal
indireto (reduzir o tabuleiro reduz a área mas também alivia a carga na longarina,
reduzindo a flecha), o que é um mecanismo acidental e difícil de defender perante
um revisor de SMO.

**Duas saídas, ambas defensáveis — escolher uma:**

1. **Correção mínima:** `f2 = +δ_tot/δ_lim` (minimizar utilização). Passa a ser
   genuinamente antagônico com a área e coerente com o texto. Custo: refazer todas
   as fronteiras.
2. **Correção forte (recomendada, ver R3 no roadmap):** substituir $f_2$ pelo
   **índice de confiabilidade $\beta$** (maximizar), transformando o problema em
   custo × confiabilidade. Isso conecta o `confia_mad.py` (hoje órfão) ao NSGA-II,
   é exatamente o que o `\sugestao` de
   [02_methodology.tex:179](../paper/final/02_methodology.tex#L179) pede, e
   posiciona o artigo bem melhor em SMO.

---

## 🟠 B4 — O módulo de confiabilidade está desconectado e parcialmente comentado

**Onde:** [confia_mad.py](../confia_mad.py)

- As linhas 1–71 (`smooth_max`, `obj_confia`) estão **inteiramente comentadas**.
  Tanto `chamando_form` ([linha 116](../confia_mad.py#L116)) quanto
  `chamando_sampling` ([linha 245](../confia_mad.py#L245)) instanciam
  `PythonModel(model_script='madeiras.py', model_object_name='obj_confia', ...)`.
  **`obj_confia` não existe em `madeiras.py`** (busca confirmada — o único símbolo
  relacionado lá é `beta_from_pf`, na linha 93). Ou seja: FORM e Monte Carlo estão
  quebrados hoje. A função existe apenas comentada em `confia_mad.py`, e mesmo essa
  versão chama uma classe `ProjetoEstrutural` que também não existe mais após a
  refatoração do commit `128fa076`.
- `import numpy as np` aparece na **linha 126**, depois de já ser usado nas linhas
  74–109. O arquivo só funciona se importado num contexto onde `np` já esteja no
  namespace — sinal de que nunca foi executado como módulo isolado.
- `beta_from_pf` é usado em `chamando_sampling` mas não está importado.
- Os COVs estão todos *hardcoded* em 0.10 (0.20 para as GEV). Para o paper, esses
  valores precisam de referência bibliográfica (JCSS Probabilistic Model Code,
  ou literatura de madeira roliça brasileira).

Nada disso aparece no paper hoje. É código morto que, se ressuscitado, vira o
resultado mais forte do artigo (ver R3).

---

## 🟡 B5 — Bloco `__main__` obsoleto

**Onde:** [madeiras.py:1668+](../madeiras.py#L1668)

Usa `esp_min=`/`esp_max=` e a variável `esps`, que não existem mais após a
refatoração para 5 variáveis. Lê `beam_data_02.xlsx`, que não está no repositório
(só existe `beam_data_01.xlsx`). Quebra se executado. Baixa prioridade, mas é a
primeira coisa que um revisor que baixa o código tenta rodar.

---

## 🟡 B6 — Ausência de testes e de reprodutibilidade

Não há nenhum teste no repositório. Para *Structures*/SMO, cada vez mais se exige
código reprodutível com DOI (Zenodo). O mínimo defensável:

- Teste de regressão do dimensionamento contra o exemplo manual da Seção 2.7 do
  paper (validação passo a passo já escrita — basta transformar em assert).
- Script único que regenera **todas** as figuras do paper a partir do zero, com
  semente fixa.
- `requirements.txt` com versões fixadas (hoje tem, mas conferir se está pinado).

---

## Resumo do impacto no paper

| Item | O paper afirma | O código faz | Ação |
|---|---|---|---|
| B1 | Perturbação de 5% em todas as variáveis | Nenhuma perturbação | Implementar + refazer **todos** os resultados |
| B2 | Tabela de geometrias ótimas | 3 colunas com rótulo errado | Corrigir + refazer tabelas |
| B3 | Objetivos antagônicos, "maximizar desempenho" | Maximiza a utilização da flecha | Decidir entre correção mínima e $\beta$ |
| B4 | (não menciona) | FORM/MC órfãos e quebrados | Reativar → vira o resultado central |
| B5 | — | `__main__` quebrado | Limpar |
| B6 | Plataforma de acesso livre | Sem testes, sem script de reprodução | Adicionar antes da submissão |

**Nenhum número do paper atual deve ser considerado final até B1–B3 serem
corrigidos.**
