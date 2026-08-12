# Dados das 40 espécies e números já calculados

Fonte primária dos dados: **artigo experimental de terceiros, ainda não citado no texto**
(`\tofill{[CITAR o artigo-fonte]}` em `paper/engstruct/02_materials.tex` e em
`tabelas/tab_especies.tex`). Preencher isso é pendência bloqueante.

Tabela completa das 40 espécies: `paper/engstruct/tabelas/tab_especies.tex`.

## Conversão adotada (⚠️ não validada contra a fonte)

Os valores da fonte são **médios**. Foram convertidos em característicos por:

| Propriedade | Fator | Origem |
|---|---|---|
| Compressão `f_c0` | `f_k = 0,70 · f_m` | ABNT NBR 7190-1:2022 |
| Flexão `f_m` | `f_k = 0,70 · f_m` | ABNT NBR 7190-1:2022 |
| Cisalhamento `f_v0` | `f_k = 0,54 · f_m` | ABNT NBR 7190-1:2022 |

**Todo o enquadramento em classe depende desses fatores.** Se a fonte já reportar
característicos, ou usar outro fator, refazer as três tabelas de `tabelas/` e todos os
percentuais do texto.

Nota útil: o fator 0,70 implica **CoV ≈ 22 %** se o característico for o percentil 5 %
de uma lognormal. Isso é insumo para a linha de confiabilidade (`07_...`).

## Classes da NBR 7190-3 (folhosas de florestas nativas)

| Classe | f_c0,k (MPa) | f_m,k (MPa) | f_v0,k (MPa) | E_c0,med (MPa) | ρ 12 % (kg/m³) |
|---|---|---|---|---|---|
| D20 | 20 | 26,0 | 4 | 10 000 | 500 |
| D30 | 30 | 39,0 | 5 | 12 000 | 625 |
| D40 | 40 | 51,9 | 6 | 14 500 | 750 |
| D50 | 50 | 64,9 | 7 | 16 500 | 850 |
| D60 | 60 | 77,9 | 8 | 19 500 | 1 000 |

`f_m,k = f_c0,k / 0,77` (relação normativa para folhosas).

## Resultados principais — **todos reconferidos aritmeticamente em 2026-08-12**

| Achado | Valor | Confere? |
|---|---|---|
| R² de E_M0 contra f_c0 | 0,70 | não reconferido (não há script no repo) |
| Dispersão intraclasse de E_M0 em D30 | 70,2 % | ✔ 18367/10794 − 1 |
| Dispersão intraclasse de E_M0 em D40 | 73,7 % | ✔ 18679/10755 − 1 |
| Passo de E entre classes vizinhas | 13,8 – 20,8 % | ✔ |
| **Razão dispersão / passo** | **≈ 4×** | ✔ |
| Espécies que mudam de classe pela rigidez | 23 de 40 (57,5 %) | ✔ |
| Espécies **menos rígidas** que a própria classe | 14 de 40 (35 %) | ✔ mas ver ressalva |
| Espécies com salto de **2 classes** | **4** (não 2) | ✔ corrigido no texto |
| Pior caso contra a segurança | Angelim-pedra, −25,8 % | ✔ 10755/14500 − 1 |
| Pior caso de desperdício | Goiabão, +53,1 % | ✔ 18367/12000 − 1 |

**Ressalva sobre os 35 %:** dois dos 14 estão no ruído — Angico-preto (−0,0 %, 16 498
contra 16 500) e Oiticica-amarela (−0,1 %). O número defensável de espécies
*materialmente* contra a segurança é **12 (30 %)**. Ver `05_revisao_critica.md`.

## População por classe

| Classe | n | Espécies |
|---|---|---|
| D20 | 4 | Cedro-amargo, Cedro-doce, Cedrorana, Quarubarana |
| D30 | 11 | Angelim-araroba, Branquilho, Canafístula, Casca-grossa, Castelo, Catanudo, Copaíba, Cupiúba, Goiabão, Louro-preto, Umirana |
| D40 | 12 | Angelim-amargoso, Angelim-pedra, Angelim-saia, Cafearana, Guaicará, Guarucaia, Itaúba, Mandioqueira, Oiticica-amarela, Parinari, Piolho, Rabo-de-arraia |
| D50 | 9 | Angelim-ferro, Angelim-pedra-verdadeiro, Angico-preto, Cutiúba, Garapa, Ipê, Maçaranduba, Oiuchu, Tatajuba |
| D60 | 4 | Champanhe, Jatobá, Sucupira, Tachi |

D30 + D40 = 23 espécies, ou seja, **58 % da população está nas duas classes de pior
dispersão**. Esse é o motivo de o achado importar na prática.

## O par que resume o artigo

| | Classe pela norma | E_M0 medido | Classe que a rigidez implicaria |
|---|---|---|---|
| **Angelim-pedra** (*Hymenolobium petraeum*) | D40 | 10 755 MPa | abaixo de D30 |
| **Goiabão** (*Planchonella pachycarpa*) | D30 | 18 367 MPa | acima de D50 |

A norma diz que o angelim-pedra é o material superior. Na rigidez real o goiabão é
**71 % mais rígido** (18 367 / 10 755 = 1,708).

## Amplitude da população

- Massa específica aparente a 12 %: 512 – 1 163 kg/m³
- Resistência à compressão paralela (média): 33 – 94 MPa
- Módulo de elasticidade à flexão: 8 842 – 25 174 MPa

## ⚠️ Não existe script versionado que gere estas tabelas

As três tabelas de `paper/engstruct/tabelas/` foram geradas em sessão anterior e o
script não foi commitado. **Isso é dívida técnica séria**: se a conversão mudar (e há
boa chance de mudar), não há como regenerar automaticamente. São 40 linhas — reescrever
o script e commitá-lo em, digamos, `scripts/gera_tabelas_especies.py`, junto com a
planilha de origem. Ver `06_proximos_passos.md`.
