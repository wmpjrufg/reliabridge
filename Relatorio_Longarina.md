---
title: "Memória de Cálculo: Longarina de Madeira"
author: "Verificação NBR 7190"
date: "20/01/2026"
geometry: "left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm"
documentclass: article
output: pdf_document
---

# 1. Dados de Entrada
* **Seção Transversal:** Retangular
* **Base ($b_w$):** 15.0 cm
* **Altura ($h$):** 30.0 cm

* **Classe de Umidade:** 3
* **Classe de Carregamento:** Longa Duração
* **Madeira:** Madeira Natural
* **Coeficientes:** $\gamma_g = 1.4$, $\gamma_q = 1.4$, $\gamma_w = 1.4$
* **Coef. Impacto Vertical ($C_i$):** 1.353

---

# 2. Esforços de Cálculo (Majorados)

| Esforço | Carga Permanente ($G$) | Carga Variável ($Q$) |
| :--- | :---: | :---: |
| **Momento Máx.** | 62.50 kN.m | 332.50 kN.m |
| **Cortante Máx.** | 25.00 kN | 136.09 kN |

---

# 3. Verificações (ELU)

## 3.1 Flexão Simples
* **Tensão Atuante ($\sigma_{x,d}$):** 300.60 MPa
* **Resistência ($f_{md}$):** 8.00 MPa
* **Índice de Uso:** 3757.5%

> **Status:** **REPROVADO** $\times$

## 3.2 Cisalhamento
* **Tensão Atuante ($\tau_{sd}$):** 9.20 MPa
* **Resistência ($f_{vd}$):** 1.20 MPa
* **Índice de Uso:** 766.7%

> **Status:** **REPROVADO** $\times$

---

# 4. Verificação de Deformação (ELS)

* **Flecha Calculada:** 119.63 cm
* **Flecha Limite ($L/360$):** 2.78 cm

> **Status:** **REPROVADO** $\times$
