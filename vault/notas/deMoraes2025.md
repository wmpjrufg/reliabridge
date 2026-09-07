# Fichamento: de Moraes & Buttignol (2025)

**Referência completa:** DE MORAES, V. N.; BUTTIGNOL, T. E. T. Parametric modeling for
automated intelligent design of concrete beam bridges: A global and local optimization
approach. *Structural Concrete*, v. 26, p. 4083–4102, 2025.
**DOI:** 10.1002/suco.70247 · Open access CC-BY
**Chave BibTeX:** `deMoraes2025`
**Afiliação:** Unicamp (Departamento de Estruturas)

> Já era a referência declarada de rigor e organização do rascunho
> ([paper/final/README.md](../../paper/final/README.md)). Agora está lida.

---

## 1. Problema tratado

Projeto automatizado ("intelligent design") de pontes em vigas de concreto protendido,
acoplando modelagem paramétrica 3D, otimização e análise estrutural em um único fluxo.

## 2. Formulação

- **Duas camadas:**
  - **Global** — algoritmo genético (Galapagos/Grasshopper) minimiza o **número de
    apoios**, via função custo de "volume fictício equivalente de concreto"
    (volume real × fator de ajuste AF por elemento, Tabela 2).
  - **Local** — **método Simplex** define o **domínio viável** no plano
    (altura da viga $h$ × força de protensão $P_i$), a partir de 7 inequações de
    ELS/ELU. O projetista escolhe o ponto dentro da região viável.
- **Ferramentas:** Rhinoceros (CAD) + Grasshopper (AAD) + Galapagos (GA) +
  Karamba3D (MEF) + Python (equações de dimensionamento).
- **Norma:** ABNT NBR 6118, 7187, 7188.
- **Incerteza:** **nenhuma.** É inteiramente determinístico.
- **Multiobjetivo:** **não.** GA monoobjetivo + Simplex.

## 3. Como validam

Dois estudos de caso **comparativos com a literatura**, não experimentais:

1. Contra Aydn & Ayvaz (otimização de custo por GA modificado) — chegam a
   US$ 2.487.200 vs US$ 2.686.504, e discutem a diferença.
2. Contra as vigas padrão de Caltrans / AASHTO / DNIT e Jahjouh & Erhan (harmony
   search) — comparação por índices de eficiência estrutural (Eqs. 29 e 30).

Além disso: análise modal (frequências naturais, Tabela 3) como etapa final.

## 4. Figuras e tabelas que valem imitar

| Figura/Tabela | O que mostra | Equivalente no ReliaBridge |
|---|---|---|
| **Fig. 1** | Evolução projeto clássico → BIM → intelligent design, em 3 faixas horizontais | A introdução do rascunho já faz esse argumento em texto — virar figura seria ganho direto |
| **Fig. 3** | Fluxograma dividido em faixa "GLOBAL PROCEDURE" e "LOCAL PROCEDURE" | Substituir o `fluxograma.jpeg` atual, que é bem mais pobre |
| **Fig. 15/18** | Domínio viável (Simplex) com as 7 curvas de restrição e a região cinza | Não se aplica direto (temos Pareto), mas a ideia de **plotar as curvas de restrição junto com o espaço de soluções** é ótima |
| **Fig. 16** | **Barras de "utilization capacity" por verificação**, com faixas UC>100% / 70–100% / ≤70% | **É exatamente o que a `\sugestao` de [appendices.tex:7](../../paper/final/appendices.tex#L7) pede.** Copiar o formato |
| **Fig. 19** | $h$ × $P_i$ com o vão $L$ em escala de cor, e **equação ajustada $h = 0{,}066L - 0{,}24$** | **Modelo para o R2.3**: ábaco de pré-dimensionamento $d = f(L)$ para longarina roliça. Entregável de engenharia de alto valor |
| **Tab. 2 / 5** | Custo por m³ + fator de ajuste AF por elemento | Se algum dia trocarmos área por **custo** como $f_1$ |

## 5. O que trazer para o nosso artigo

- [ ] Figura de utilização por verificação (Fig. 16) — barata e fecha uma `\sugestao`
- [ ] Ábaco/equação de pré-dimensionamento em função do vão (Fig. 19) — R2.3
- [ ] Fluxograma em duas camadas (Fig. 3)
- [ ] Validação **por comparação com a literatura**, já que não temos ensaio
- [ ] Análise modal como seção final? Provavelmente fora de escopo para vão de 5 m

## 6. Onde nos diferenciamos

Forte, e vale explicitar na introdução e na carta de submissão:

| | de Moraes & Buttignol | ReliaBridge |
|---|---|---|
| Incerteza | Nenhuma (determinístico) | Otimização robusta (perturbação nas variáveis) |
| Objetivos | Mono-objetivo (GA) + Simplex | Bi-objetivo, fronteira de Pareto (NSGA-II) |
| Material | Concreto protendido | Madeira roliça (variabilidade natural alta → robustez é *necessária*, não opcional) |
| Acesso | Depende de Rhino + Grasshopper (licenças comerciais) | Plataforma web livre, sem licença |

O último ponto é o mais forte e está subexplorado no rascunho: **a cadeia
Rhino/Grasshopper/Karamba é toda proprietária e cara.** Uma plataforma web gratuita
que faz o mesmo papel para pontes de madeira em estrada vicinal tem apelo real de
acessibilidade — e é o público (municípios, estradas vicinais) que menos tem acesso
a software comercial.

## 7. Referências deste artigo que devemos ler

- **Aydn & Ayvaz** — otimização de custo de vigas protendidas por GA
- **Jahjouh & Erhan** — harmony search para geometria de vigas I pré-moldadas
- **Rempling et al.** — projeto estrutural automático, validado em 3 pontes suecas
  reais, redução de 20–60% em custo e CO₂ (bom benchmark de "quanto se ganha")
- **Girardet & Boton** — BIM paramétrico para pontes
- **Nawari** — origem do termo "intelligent design"
