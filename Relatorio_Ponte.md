
<div style="text-align: center">
  <h1>RELIABRIDGE</h1>
  <h2>Memorial de Cálculo Detalhado</h2>
  <p><strong>Grupo de Pesquisa e Estudos em Engenharia - GPEE</strong></p>
  <p>Data de emissão: 23/01/2026</p>
</div>

---

_**Disclaimer:** Este software é parte de um projeto de pesquisa, desenvolvido para fins educacionais. Não nos responsabilizamos por quaisquer danos diretos ou indiretos decorrentes do uso deste software._

---

# 1. Dados de Entrada e Materiais

| Parâmetro | Valor | Unidade | Descrição |
| :--- | :---: | :---: | :--- |
| **Vão ($l$)** | 500.00 | cm | Comprimento do vão livre |
| **Carga Perm. ($p_{gk}$)** | 0.72 | kN/m | Carga distribuída na longarina |
| **Carga Roda ($P_{rodak}$)** | 40.00 | kN | Carga pontual característica |
| **Carga Multidão ($p_{qk}$)** | 4.00 | kPa | Carga distribuída de multidão |
| **Classe Madeira** | Madeira Natural | - | Umidade: 1 |
| **$f_{mk}$ Longarina** | 50.0 | MPa | Resistência característica flexão |
| **$E_{m}$ Longarina** | 20.0 | GPa | Módulo de Elasticidade |
| **Coef. Segurança** | $\gamma_g=1.4, \gamma_q=1.4$ | - | Majoradores de carga |

---

# 2. Geometria e Propriedades da Seção

## 2.1 Dimensões Adotadas
* **Longarina:** Seção Circular com $d = 45.0$ cm.
* **Tabuleiro:** Seção Retangular com $b_w = 11.0$ cm e $h = 35.0$ cm.
* **Espaçamento:** 120.0 cm entre longarinas.

## 2.2 Propriedades Geométricas Calculadas (Longarina)

| Propriedade | Símbolo | Valor Calculado | Unidade |
| :--- | :---: | :---: | :---: |
| **Área da Seção** | $A$ | 1590.43 | $cm^2$ |
| **Módulo Resistente** | $W_x$ | 8946.18 | $cm^3$ |
| **Momento de Inércia** | $I_x$ | 201288.96 | $cm^4$ |
| **Momento Estático** | $S_x$ | 35784.70 | $cm^3$ |

---

# 3. Detalhamento dos Esforços (Longarina)

Aqui apresentamos os esforços característicos (sem coeficientes de segurança) e os fatores de impacto utilizados.

| Esforço / Fator | Símbolo | Valor | Unidade/Obs |
| :--- | :---: | :---: | :--- |
| **Coef. Impacto Vertical** | $C_i$ | 1.350 | Calculado via norma |
| **Auxiliar Impacto** | $Aux_{ci}$ | 1.263 | - |
| **Momento Permanente** | $M_{gk}$ | 8.91 | kN.m |
| **Momento Variável** | $M_{qk}$ | 113.63 | kN.m |
| **Momento de Cálculo** | **$M_{sd}$** | **171.55** | **kN.m** (Majorado) |

---

# 4. Verificação ELU: Longarina

## 4.1 Flexão Simples
**Status:** ✅ APROVADO

* **Tensão Atuante ($\sigma_{x,d}$):** 19.18 MPa
* **Resistência ($f_{md}$):** 21.43 MPa
* **Coeficientes de Modificação ($k_{mod}$):**
    * $k_{mod,1} = 0.6$ (Carregamento)
    * $k_{mod,2} = 1.0$ (Umidade)
    * $k_{mod,3} = 1.00$ (Categoria)
    * **$k_{mod, total} = 0.6$**

## 4.2 Cisalhamento
**Status:** ✅ APROVADO

* **Cortante de Cálculo ($V_{sd}$):** 120.39 kN
* **Tensão Atuante ($\tau_{sd}$):** 4.76 MPa
* **Resistência ($f_{vd}$):** 8.57 MPa

---

# 5. Verificação ELS: Deformação (Flecha)

**Status:** ✅ APROVADO

| Componente | Valor Calculado | Limite Normativo | Análise |
| :--- | :---: | :---: | :---: |
| **Flecha Instantânea ($Q$)** | 0.55 cm | - | - |
| **Flecha Fluência** | 0.19 cm | - | $\phi = 0.8$ |
| **Flecha Variável (Lim.)** | **1.43 cm** | **- cm** | **OK** |
| **Flecha Total** | 2.00 cm | - | Informativo |

---

# 6. Tabuleiro: Verificação Local

**Status Flexão:** ✅ APROVADO

* **Momento de Cálculo ($M_{sd}$):** 13.31 kN.m
* **Tensão Atuante ($\sigma_{x,d}$):** 5.93 MPa
* **Resistência ($f_{md}$):** 17.14 MPa
* **Coeficientes:** $k_{mod} = 0.6$ ($k_{mod1}=0.6, k_{mod2}=1.0$)

---
*Relatório gerado automaticamente pelo sistema RELIABRIDGE em 23/01/2026 às 17:58.*
