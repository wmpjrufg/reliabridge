# Artigo 3 — desenho científico

**Refinado em 22/09/2026.** Recorte adotado, pré-dimensionamento explícito de pontes de madeira roliça, com a capacidade de carga entrando como operação inversa das mesmas expressões. Nenhuma equação foi ajustada e nenhuma campanha foi executada.

## O fato que reorganiza o artigo

O núcleo estrutural é inteiramente algébrico. Momento, cortante e flecha são expressões fechadas do vão, das cargas e das propriedades da seção, e as resistências não dependem do carregamento móvel. Duas consequências.

**Primeira.** Para geometria fixa, os esforços são lineares no multiplicador do carregamento móvel, já que as envoltórias são máximos sobre um conjunto finito de arranjos. O multiplicador que esgota cada verificação sai por inversão exata, sem ajuste e sem erro. Regressão simbólica sobre esse rótulo aprenderia uma função que já se conhece em forma fechada, e um revisor de revista de estruturas vai apontar isso. **A capacidade de carga não sustenta um artigo de IA.**

**Segunda.** O próprio problema de dimensionamento é quase diretamente resolvível. As quatro verificações estruturais são monótonas em `d`, `bw` e `h`, e a única fonte de descontinuidade é a contagem inteira de peças em `restringir_espaco`, que escolhe `n` entre o piso e o teto de uma estimativa contínua. Fixados `n_long` e `n_tab`, os espaçamentos corrigidos ficam determinados, as verificações viram um sistema monótono de três incógnitas e o volume mínimo daquela combinação sai por iteração. Como as contagens admissíveis são poucas, dezenas de combinações por cenário, a enumeração exaustiva resolve o problema inteiro.

Isso não é um detalhe de implementação. É a primeira pergunta que o artigo precisa responder, antes de gerar qualquer base de treinamento.

## Marco zero — o solucionador direto

Implementar a solução direta e medi-la contra o NSGA-II nos oito casos do piloto e em um punhado de casos adicionais. Comparar volume obtido, tempo e reprodutibilidade.

| Desfecho | O que o artigo passa a ser | Papel da regressão simbólica |
|---|---|---|
| A — a solução direta é exata e rápida | Método direto de pré-dimensionamento, com a metaheurística mostrada como desnecessária nesta classe de problema | Converter o procedimento enumerativo em expressão de bolso, com erro declarado |
| B — é exata, mas o resultado depende de qual restrição governa e da disposição inteira, sem forma comunicável | Mapa de regimes mais equações compactas verificadas | Contribuição central, a forma legível de um procedimento ramificado |
| C — o acoplamento entre largura tributária, vão do tabuleiro e contagens impede a solução direta | Metamodelo explícito da otimização | Contribuição central, com justificativa forte |

O desfecho A é o mais provável e é o mais interessante dos três, porque um resultado negativo sobre metaheurísticas em problemas pequenos de projeto de madeira tem público. Os três são publicáveis se relatados com honestidade. Nenhum deles pode ser presumido antes de rodar o marco zero.

O piloto já dá o indício. Uma geometria transferida entre cenários reduziu 15,2 % do volume em relação ao alvo escolhido pelo NSGA-II, o que significa que o alvo atual não é o ótimo do problema. Treinar sobre esse alvo ajustaria ruído do otimizador.

## Pergunta principal

Dadas as entradas de anteprojeto, vão, largura de pista, carga permanente adicional, perfil do veículo e propriedades da madeira, qual é a superestrutura admissível de menor volume, e é possível entregá-la como expressões explícitas cujas geometrias previstas passem no conjunto completo de verificações?

A pergunta subordinada, respondida pelas mesmas expressões invertidas, é qual multiplicador do carregamento móvel uma configuração dada suporta e qual verificação a limita.

## Separação dos três artigos

| Linha | Contribuição |
|---|---|
| Artigo 1 — `paper/materia` | Plataforma, otimização e estudo paramétrico, com uma equação simples de volume |
| Artigo 2 — `paper/engstruct` | Consequência estrutural da representação por classes frente às propriedades medidas |
| Artigo 3 — esta pasta | Solução direta do dimensionamento, expressões explícitas com propriedades contínuas e verificação das geometrias previstas |

O artigo 3 cita o primeiro pelo modelo e compara sua equação de volume com as novas. Cita o segundo pela base de espécies e pelo achado sobre rigidez. Não reapresenta interface, validação nem estudo paramétrico como novidade.

## O material entra contínuo, não por classe

A base de 40 espécies de Dias e Rocco Lahr (2004), auditada em `paper/engstruct/dados/base_especies.csv`, traz densidade, `f_c0`, `f_M`, `f_v0`, `E_c0` e `E_M0` medidos por espécie. Usar essas propriedades como entradas contínuas resolve o problema que inviabiliza a versão por classes, onde cinco perfis colineares impedem separar o efeito de rigidez, resistência e densidade.

Com 40 espécies reais há variação suficiente para ajuste e uma partição legítima por espécie, que testa transferência para madeira não vista. As classes D20 a D60 permanecem como uma linha de comparação, ligando o resultado ao artigo 2, não como a representação principal.

O que a base não permite continua valendo. Propriedades de espécies reais são correlacionadas, então importância estatística não vira causalidade mecânica, e sortear combinações independentes de densidade alta com módulo baixo produziria madeiras que não existem.

## Hipóteses a testar

1. A solução direta enumerativa reproduz ou supera o NSGA-II em volume, com tempo várias ordens de grandeza menor.
2. Uma única lei de potência perde precisão quando mudam veículo, carregamento e disposição inteira de peças.
3. As descontinuidades do volume ótimo vêm da contagem inteira de peças e das trocas de envoltória, não de comportamento estrutural novo.
4. O erro médio de volume pode ser pequeno enquanto dimensões previstas violam restrições, de modo que a utilidade exige reanálise completa das seções.

É desfecho aceitável concluir que a regressão simples basta. Nesse caso o artigo demonstra a suficiência da expressão e o domínio em que ela vale, sem alegar superioridade de método complexo.

## Alvo, entradas e saídas

O alvo é o volume mínimo entre as configurações que atendem a todas as seis restrições na avaliação de pior caso da grade de robustez. Com a solução direta, esse alvo passa a ser bem definido, e não uma amostra condicionada a semente e número de gerações.

Entradas disponíveis no momento da previsão, `L`, `B`, `p_gk`, perfil do veículo e as propriedades medidas da madeira. Nada calculado pelo modelo entra como entrada. O estado limite governante é saída, nunca entrada de uma previsão que pretende descobri-lo.

Saídas, o diâmetro da longarina, largura e altura das peças do tabuleiro, as duas contagens inteiras e o volume. Como as contagens são inteiras, comparar uma família de expressões contínuas com um modelo híbrido que classifica a disposição e regride as dimensões.

## Família de expressões candidatas

Referência dimensionalmente consistente por razões adimensionais.

```text
V / V0 = C (L/L0)^a (B/B0)^b (f_cl/f0)^c
         (1 + p_gk/p0)^d (P_roda/P0)^e (E/E0)^f
```

`L0 = 1 m`, `B0 = 1 m`, `V0 = 1 m³`, `f0 = 1 MPa`, `p0 = 1 kPa`, `P0 = 1 kN` e `E0 = 1 GPa` são escalas de referência, não parâmetros ajustados. Os expoentes ainda não foram estimados. O termo de módulo só faz sentido na versão com propriedades contínuas.

Operadores permitidos, soma, subtração, produto, divisão protegida, potências restritas e, se necessário, `max` ou trechos. Restringir complexidade e singularidades. Expressões de dimensões têm escala de saída própria. O marcador de entrada da multidão acima de 6 m é derivado do vão e pertence ao modelo de carregamento, não é achado estrutural.

## Comparações mínimas

1. **Solução direta enumerativa**, a referência exata. Toda expressão é medida contra ela, não contra o NSGA-II.
2. **Inversão analítica por estado limite**, mostrando o diâmetro exigido por flexão, cortante e flecha isoladamente.
3. **Equação de volume do artigo 1**, com o domínio original indicado. Fora dele, apenas referência de extrapolação.
4. **Lei de potência multidimensional** ajustada no treinamento, com versão por partes.
5. **Regressão simbólica** com limite de complexidade, candidata à expressão final.
6. **Gradient boosting** como teto de capacidade preditiva. Explicações SHAP ou ALE são complementares e não produzem equação.

Hiperparâmetros e complexidade escolhidos na validação. O teste abre uma vez, depois de congelar o método.

## Evidência necessária

- MAE em unidades físicas, erro relativo mediano, percentil 95, máximo, viés e R².
- Erros estratificados por vão, veículo, espécie, carga e proximidade dos limites da busca.
- Frequência de subestimativa e violações após reanálise nominal das geometrias previstas, verificando em conjunto flexão, cisalhamento, flecha, tabuleiro e as duas restrições de disposição.
- Volume adicional após corrigir as previsões que falham, e tempo comparado tanto ao NSGA-II quanto à solução direta.
- Estabilidade das expressões em reamostragens agrupadas por espécie.
- Curva de aprendizado, para decidir se mais cenários contribuem.

Uma margem calibrada de volume não garante viabilidade das seções. Correção conservadora, se adotada, calibra-se nas dimensões e na disposição, e valida-se na estrutura completa. A grade de robustez no diâmetro não é probabilidade de falha.

## Bloqueadores, todos anteriores à campanha

**B-01 · Largura tributária e vão do tabuleiro.** `calcular_objetivos_restricoes_otimizacao` usa `esp_long_corr`, o espaçamento livre entre longarinas, como largura tributária da longarina e como vão do tabuleiro. O valor entre eixos seria `esp_long_corr + d`. No artigo 2 o desvio se cancela, porque a comparação é pareada entre cenários do mesmo caso. No artigo 3 não se cancela, porque as dimensões absolutas vão publicadas como regra de projeto. Resolver antes de qualquer campanha.

**B-02 · Rótulos enganosos em `scripts/dataset.py`.** `volume_robust_mean_m3` é numericamente idêntico a `volume_nominal_m3`, porque o núcleo avalia os objetivos no ponto nominal. `g_robust_mean` é o pior caso sobre a grade de diâmetro, não uma média, e `feasible_robust_mean` implica `feasible_nominal`, já que o multiplicador unitário pertence à grade. A regra de seleção que exige as duas condições é redundante. Renomear, remover os campos duplicados e corrigir `02_dataset.md`, que descreve trinta perturbações aleatórias e média, o que o código não faz.

**B-03 · Transições do modelo de carregamento.** As trocas de envoltória em `L ≈ 3,34 m` e `L = 6 m` são mudanças de expressão. Qualquer regime que apareça ali é atribuído ao modelo, nunca a comportamento físico descoberto pelas equações.

**B-04 · Domínio das cargas em vão longo.** Zonas de exclusão da multidão, envoltórias e distribuição transversal permanecem em auditoria. Os oito pilotos não validam essas hipóteses.

## Estrutura pretendida do manuscrito

Introdução e lacuna. Modelo estrutural e domínio. Solução direta do dimensionamento e sua verificação. Geração e auditoria da base. Expressões explícitas e seleção. Desempenho fora do treinamento e reanálise das geometrias previstas. Mapa de estados limites governantes e capacidade por inversão. Aplicação de anteprojeto. Limitações. Conclusões.

Figuras centrais, domínio amostrado, solução direta contra NSGA-II em volume e tempo, erro contra complexidade, paridade fora do treinamento, mapa de regime governante e o exemplo de aplicação.
