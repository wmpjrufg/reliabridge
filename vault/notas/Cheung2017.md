# Fichamento: Cheung et al. (2017)

**Referência completa:** CHEUNG, A. B.; SCALIANTE, R. de M.; LINDQUIST, M.;
CHRISTOFORO, A. L.; CALIL JUNIOR, C. Confiabilidade estrutural de uma ponte
protendida de madeira considerando o tráfego real. *Ambiente Construído*, Porto
Alegre, v. 17, n. 2, p. 221–232, abr./jun. 2017.
**DOI:** 10.1590/s1678-86212017000200154
**Chave BibTeX:** `Cheung2017`

> Não estava na sua lista, mas é o paper **mais próximo do tema** de todo o lote:
> confiabilidade estrutural + ponte de madeira + Brasil + estrada vicinal.
> Coautoria de Calil Junior.

---

## 1. Problema tratado

Avaliação da confiabilidade estrutural da ponte de madeira laminada protendida sobre
o Rio Monjolinho (São Carlos/SP) — a primeira do tipo no Brasil — com foco na
resistência à flexão e na perda de protensão, sob um conjunto variado de trens-tipo.

## 2. Formulação

- Tabuleiro modelado como **viga equivalente** (largura efetiva), a partir do
  comportamento de placa ortotrópica — mesma família de simplificação que usamos.
- **Ações reais**: dados de tráfego da concessionária Centrovias, não só trem-tipo
  normativo.
- Estados limites: flexão e perda de protensão.

## 3. Resultado principal

A ponte apresentou índices de confiabilidade compatíveis para a maioria dos
carregamentos simulados, **mas para alguns tipos de caminhão ficou abaixo do
recomendado pelas normas internacionais**.

Ou seja: projeto que passa na verificação normativa determinística pode ter $\beta$
insuficiente sob tráfego real. É argumento direto para o ReliaBridge — reforça tanto
a robustez quanto o caminho R2.1 (confiabilidade acoplada).

## 4. A citação mais valiosa

Da introdução (p. 222), sobre pontes de madeira no Brasil:

> "a grande maioria [é] projetada sem o recurso de análises baseadas em
> confiabilidade, visto que a norma brasileira NBR 7190 (ABNT, 1997) não apresenta
> as premissas, os métodos de cálculo e os índices de confiabilidade para a análise
> de estruturas considerando-se o critério de confiabilidade estrutural"

**Esta é a declaração de lacuna que falta na nossa introdução**, e vem de fonte
brasileira especializada. Verificar se a NBR 7190:2022 (versão nova, que usamos)
corrigiu isso — se não corrigiu, a lacuna continua aberta e o argumento fica ainda
mais forte; se corrigiu, o enquadramento muda para "a norma agora permite, e faltam
ferramentas".

Também útil: *"No Brasil pequenas pontes de estradas vicinais são essenciais para o
transporte de produtos agrícolas"* — motivação socioeconômica pronta para o primeiro
parágrafo.

## 5. O que trazer para o nosso artigo

- [ ] A citação de lacuna acima, na introdução
- [ ] O argumento "aprovado no determinístico ≠ confiável" na discussão
- [ ] Verificar quais **COVs e distribuições** eles adotam para madeira — é a fonte
      brasileira para justificar os valores hoje *hardcoded* em `confia_mad.py`
      (ver B4/R2.4). **Ler as seções de método e resultados por inteiro para isso.**
- [ ] Possível benchmark: se rodarmos a nossa ferramenta numa configuração parecida,
      dá para comparar ordem de grandeza de $\beta$

## 6. Onde nos diferenciamos

Cheung et al. **avaliam uma ponte já projetada**; ReliaBridge **projeta**. Eles usam
laminada protendida; nós, roliça sobre longarinas. Eles não otimizam.

## 7. Pendência

Li só resumo e introdução. **Falta ler método e resultados** para extrair os modelos
probabilísticos (distribuições, COVs, valores de $\beta$ obtidos). É a leitura de
maior retorno pendente no vault.
