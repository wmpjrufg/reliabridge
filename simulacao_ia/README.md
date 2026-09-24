# Campanha do Artigo 3 — pré-dimensionamento explícito

Casos e resultados do artigo da fronteira da tipologia. O plano está em
[`paper/ia_explicavel/01_proposta.md`](../paper/ia_explicavel/01_proposta.md); esta pasta é
só a execução.

**Pergunta.** Até onde a ponte de madeira roliça serve, e o que define esse limite. A
restrição que fecha a fronteira não é normativa, é o diâmetro comercial de tora.

## A grade

| Eixo | Valores | n |
|---|---|---:|
| Vão | 3 a 10 m, passo 0,5 | 15 |
| Veículo | TB-240, TB-450 | 2 |
| Largura de pista | 3,5 / 4,0 / 4,5 m | 3 |
| `p_gk` | 0,1 / 0,5 / 1 / 2 / 3 / 5 kPa | 6 |
| Material | 40 espécies medidas + 5 classes D20 a D60 | 45 |

**24.300 casos.** A classe entra como se fosse mais uma madeira, com o mesmo estatuto de
uma espécie, mas o bloco de classes fica **fora do ajuste**, marcado `split = referencia`.
Ele produz a leitura oficial da fronteira, aquela que sai da norma; as espécies produzem a
nuvem em volta. A distância entre as duas é o resultado do artigo.

## Por que não NSGA-II

A 21 s por caso, medidos no piloto, a grade custaria cerca de 142 h de uma thread, e ainda
assim o resultado não seria o ótimo — o piloto encontrou 15,2 % de folga de volume ao
transferir geometria entre cenários.

O modelo é algébrico e monótono nas variáveis de projeto, e a única descontinuidade é a
contagem inteira de peças em `madeiras.restringir_espaco`. Fixadas `n_long` e `n_tab`, os
espaçamentos corrigidos ficam determinados e resta um sistema monótono de três incógnitas.
As contagens admissíveis são poucas, então a enumeração exaustiva resolve o problema de
forma exata, em minutos, e **sem semente**.

O NSGA-II continua sendo usado num subconjunto, de propósito, para medir a folga da
metaheurística frente ao ótimo exato. Isso vira nota de método, não resultado.

## Arquivos

| Arquivo | O quê | Estado |
|---|---|---|
| `gerar_casos.py` | Monta `casos_ia.xlsx`, a grade completa | pronto |
| `casos_ia.xlsx` | Abas `Casos` e `Materiais` | gerado |
| `solver_direto.py` | Solução exata por enumeração das contagens inteiras | **a escrever** |
| `rodar.py` | Executa o subconjunto de verificação em NSGA-II | a escrever |
| `consolidar.py` | Monta o dataset do PySR a partir dos resultados | a escrever |

## Convenções de material

Idênticas às do Artigo 2, senão os dois artigos discordam nos números.

- `E_c0` dos dois lados, medido para a espécie e tabelado para a classe.
- `f_m,k = f_c0,k`, item 6.3.4 da ABNT NBR 7190-1:2022.
- `f_v0,k` da espécie por fator 0,70 sobre a média, porque Dias e Rocco Lahr (2004) não
  publicam o característico de cisalhamento.
- Classes D20 a D60 da ABNT NBR 7190-3:2022, florestas nativas. Não confundir com a
  nomenclatura histórica C20 a C60, guardada em `classe_historica_C` na base de espécies.

## Bloqueador aberto

`madeiras.calcular_objetivos_restricoes_otimizacao` usa `esp_long_corr`, o espaçamento
**livre** entre longarinas, como largura tributária da longarina e como vão do tabuleiro.
Entre eixos seria `esp_long_corr + d`. No Artigo 2 o desvio se cancela na comparação
pareada; aqui não, porque as dimensões absolutas vão publicadas como regra de projeto, e
uma fronteira calculada com carga subestimada é uma fronteira otimista.

Decidir antes de rodar a grade definitiva.

## Uso

```powershell
.venv\Scripts\python.exe simulacao_ia\gerar_casos.py
.venv\Scripts\python.exe simulacao_ia\gerar_casos.py --passo-vao 1.0 --forcar
```
