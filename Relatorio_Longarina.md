---
title: "Relatório de Longarina de Madeira"
author: "Engenharia Automatizada"
date: "19/01/2026"
geometry: "left=2.5cm,right=2.5cm,top=2.5cm,bottom=2.5cm"
documentclass: article
output: pdf_document
---

# 1. Parâmetros de Projeto

* **Tipo de Seção:** Retangular
* **Base ($b_w$):** 15.0 cm
* **Altura ($h$):** 30.0 cm

## 1.2 Propriedades Mecânicas e Coeficientes
* **Classe de Umidade:** 2
* **Classe de Carregamento:** Longa Duração
* **Madeira:** Madeira Natural
* **Coeficientes Parciais:** $\gamma_g = 1.4$, $\gamma_q = 1.4$, $\gamma_w = 1.4$
* **Coeficiente de Impacto Vertical ($C_i$):** 1.350



# 2. Esforços Solicitantes de Cálculo

Os esforços foram majorados pelos coeficientes de ponderação e impacto vertical.

| Esforço | Carga Permanente ($G$) | Carga Variável ($Q$) |
| :--- | :---: | :---: |
| **Momento Fletor máx.** | 6.25 kN.m | 17.50 kN.m |
| **Cortante máx.** | 5.00 kN | 15.42 kN |



# 3. Verificações de Segurança (ELU)

## 3.1 Flexão Simples
Verificação das tensões normais na borda da seção.

* **Tensão Atuante ($\sigma_{md}$):** 0.00 MPa
* **Resistência de Cálculo ($f_{md}$):** 0.00 MPa
* **Índice de Aproveitamento:** 0.0%

> **Resultado:** **REPROVADO** $\times$

## 3.2 Cisalhamento
Verificação das tensões tangenciais máximas.

* **Tensão Atuante ($\tau_{vd}$):** 0.00 MPa
* **Resistência de Cálculo ($f_{vd}$):** 0.00 MPa
* **Índice de Aproveitamento:** 0.0%

> **Resultado:** **REPROVADO** $\times$



# 4. Verificação de Deformação (ELS)

Verificação da flecha máxima sob cargas variáveis.

* **Flecha Calculada:** 0.00 cm
* **Flecha Limite:** 0.00 cm

> **Resultado:** **REPROVADO** $\times$
