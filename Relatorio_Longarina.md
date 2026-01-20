---
title: "RELÁTORIO: Longarina"
author: "X"
date: "20/01/2026"
geometry: "left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm"
documentclass: article
output: pdf_document
---

# 1. Dados de Entrada
* **Seção Transversal:** Retangular
* **Base ($b_w$):** 15.0 cm
* **Altura ($h$):** 30.0 cm

* **Classe de Umidade:** 2
* _**Classe de Carregamento:** Longa Duração_
* **Madeira:** Madeira Natural
* **Coeficientes:** $\gamma_g = 1.4$, $\gamma_q = 1.4$, $\gamma_w = 1.4$
* **Coef. Impacto Vertical ($C_i$):** 1.350

---

# 2. Esforços de Cálculo (Majorados)

| Esforço | Carga Permanente ($G$) | Carga Variável ($Q$) |
| :--- | :---: | :---: |
| **Momento Máx.** | 6.25 kN.m | 17.50 kN.m |
| **Cortante Máx.** | 5.00 kN | 15.42 kN |

---

# 3. Verificações (ELU)

## 3.1 Flexão Simples
* **Tensão Atuante ($\sigma_{x,d}$):** 17.64 MPa
* **Resistência ($f_{md}$):** 13.50 MPa
* **Índice de Uso:** 130.6%

> **Status:** **APROVADO** [OK]

## 3.2 Cisalhamento
* **Tensão Atuante ($\tau_{sd}$):** 1.14 MPa
* **Resistência ($f_{vd}$):** 1.80 MPa
* **Índice de Uso:** 63.4%

> **Status:** **APROVADO** [OK]

---

# 4. Verificação de Deformação (ELS)

* **Flecha Calculada:** 1.23 cm
* **Flecha Limite ($L/360$):** 1.39 cm

> **Status:** **APROVADO** [OK]
