# Artigo 3 — desenho científico

**Refinado em 22/09/2026**, em discussão com o usuário. Nenhuma equação ajustada, nenhuma campanha executada, o solucionador direto ainda não existe. A seção [Onde paramos](#onde-paramos) traz as decisões pendentes.

## A pergunta de projeto

**Até onde a ponte de madeira roliça serve, e o que define esse limite?**

Na forma que um projetista ou uma prefeitura faz, para qual vão e qual veículo ainda faz sentido esta tipologia, com a tora que existe para comprar.

A pergunta se decompõe em três.

1. **O que governa, e onde troca.** O estado limite governante sobre vão × veículo × madeira. A migração de resistência para flecha tem posição, e essa posição se desloca com a espécie. É a continuação construtiva do artigo 2.
2. **Qual propriedade dimensiona.** O volume ótimo como função de `E`, `f_m,k` e `ρ` medidos, resposta que muda com o vão. Diz o que o projetista deve especificar ao comprar madeira, que é o que o artigo 2 recomenda e não entrega.
3. **Quanto custa o veículo mais pesado.** ΔV entre TB-240 e TB-450 ao longo do vão. No piloto, 14,7 para 20,0 m³ a 10 m, mais 36 % de madeira.

O que torna a pergunta boa é que a restrição que fecha a fronteira não é normativa. Não é flexão, nem cortante, nem flecha, é o diâmetro comercial de tora disponível. Responder isso exige o ótimo exato em todo o domínio, não um punhado de casos, e é por isso que o solucionador direto vem antes.

O sinal já aparece nos dados existentes. No piloto, o diâmetro da longarina vai de 32,8 cm em `L = 3 m` com TB-240 a 82,0 cm em `L = 10 m` com TB-450, contra um teto de busca de 100 cm. E `simulacao_engstructures/diagnosticar_limites.py` já separa limite `construtivo` de limite de `domínio` — no artigo 2 isso é ruído a controlar, porque enviesa o ΔV pareado; aqui é o resultado.

## Por que o modelo permite responder

O núcleo estrutural é inteiramente algébrico. Momento, cortante e flecha são expressões fechadas do vão, das cargas e das propriedades da seção, e as resistências não dependem do carregamento móvel. Duas consequências.

**O dimensionamento admite solução direta.** As quatro verificações são monótonas em `d`, `bw` e `h`, e a única descontinuidade é a contagem inteira de peças em `restringir_espaco`, que escolhe `n` entre o piso e o teto de uma estimativa contínua. Fixados `n_long` e `n_tab`, os espaçamentos corrigidos ficam determinados e resta um sistema monótono de três incógnitas. As contagens admissíveis são poucas, então a enumeração exaustiva resolve o problema.

**A capacidade de carga sai por inversão exata.** Para geometria fixa os esforços são lineares no multiplicador do carregamento móvel, já que as envoltórias são máximos sobre um conjunto finito de arranjos. Regressão simbólica sobre esse rótulo aprenderia uma função já conhecida em forma fechada, e um revisor de revista de estruturas aponta isso. A capacidade entra como leitura inversa das mesmas expressões, não como artigo próprio. O boneco em [`05_boneco_capacidade_carga.md`](05_boneco_capacidade_carga.md) está marcado como superado, com registro do que dele vira seção.

## A campanha

Para cada combinação, o projeto admissível de menor volume. Saída por caso, `d*`, `bw*`, `h*`, número de longarinas, número de pranchas, volume e qual das quatro verificações governa.

| Eixo | Valores | n |
|---|---|---:|
| Vão | 3 a 10 m, passo 0,5 | 15 |
| Veículo | TB-240, TB-450 | 2 |
| Largura de pista | 3,5 / 4,0 / 4,5 m | 3 |
| `p_gk` | 0,1 / 0,5 / 1 / 2 / 3 / 5 kPa | 6 |
| Madeira | 40 espécies medidas mais 5 classes | 45 |

São **24.300 casos**. No NSGA-II, a 21 s cada, isso dá 142 horas de uma thread, e o resultado ainda não seria o ótimo, porque o piloto mostrou 15,2 % de folga de volume entre cenários. Com o solucionador direto são minutos, e é exato.

O solucionador não é resultado de método. É a única forma de a pergunta de projeto caber num artigo.

## Sementes

O solucionador direto **não tem semente**. Enumera e resolve um sistema monótono, mesma entrada e mesma saída sempre. Não há repetição a fazer nem dispersão a reportar, e os 24.300 casos são uma passada só. A grade de robustez também já é determinística, cinco níveis fixos aplicados só ao diâmetro em `madeiras.py`, onde o sorteio aleatório foi retirado por enviesar a média conforme a semente.

As sementes migram para dois lugares, e nos dois viram resultado.

1. **Na comparação com o NSGA-II**, de propósito, para medir o quanto a metaheurística erra frente ao ótimo exato. Bastam 50 a 100 casos representativos × 5 sementes, não a grade inteira. Vira nota de método ou apêndice.
2. **Na regressão simbólica**, que é estocástica. Rodar uma vez e publicar a expressão que saiu é furo que revisor cobra. k sementes no ajuste, com relato de quantas vezes a forma selecionada se repetiu.

A partição treino, validação e teste é **agrupada por espécie e por vão**, declarada, não sorteada. O que se repete com reamostragem é a estabilidade dos coeficientes, e essa reamostragem tem semente reportada.

## O que sai

1. **A curva de fronteira.** `d*` contra o vão, uma linha por veículo, com a faixa de diâmetro comercial de tora marcada. Onde a linha cruza a faixa, acaba a tipologia.
2. **O mapa de governante** sobre vão × módulo de elasticidade.
3. **O custo do veículo**, ΔV entre TB-240 e TB-450 ao longo do vão.
4. **As equações explícitas** de `d*` e `V*`, ajustadas sobre as soluções exatas, com espécies e vãos retidos fora do ajuste, e cada geometria prevista reanalisada no modelo completo.
5. **A leitura inversa**, o multiplicador de carga que uma ponte existente aceita, obtido por inversão.

## Ordem de trabalho

| # | O quê | Custo | Depende de |
|---|---|---|---|
| 1 | `solver_direto.py`, enumera contagens inteiras e resolve o sistema monótono. Conferir contra os 8 casos do piloto | ~1 dia | nada |
| 2 | Decidir **B-01**, a largura tributária, e medir o impacto nos artigos 1 e 2 antes de mexer | ~meio dia | nada |
| 3 | Obter o **diâmetro comercial máximo de tora** | externo | usuário |
| 4 | Rodar a grade de 24.300 casos | minutos | 1, 2 |
| 5 | Ajustar as equações com retenção, reanalisar tudo que for previsto | ~2 dias | 4 |
| 6 | Escrever | — | 5 |

Sem o passo 3 o artigo fica com as equações e sem a fronteira, porque a curva de `d*` não tem eixo vertical contra o que ser lida. É a pendência P-13 do vault, que deixa de ser detalhe de campanha e vira condição do artigo.

## O material entra contínuo, não por classe

A base de 40 espécies de Dias e Rocco Lahr (2004), auditada em `paper/engstruct/dados/base_especies.csv`, traz densidade, `f_c0`, `f_M`, `f_v0`, `E_c0` e `E_M0` medidos por espécie. Usar essas propriedades como entradas contínuas resolve o que inviabiliza a versão por classes, onde cinco perfis colineares impedem separar o efeito de rigidez, resistência e densidade.

Com 40 espécies reais há variação suficiente para ajuste e uma partição legítima por espécie, que testa transferência para madeira não vista. As classes D20 a D60 permanecem como linha de comparação, ligando o resultado ao artigo 2.

O que a base não permite continua valendo. Propriedades de espécies reais são correlacionadas, então importância estatística não vira causalidade mecânica, e sortear combinações independentes de densidade alta com módulo baixo produziria madeiras que não existem.

## Alvo, entradas e saídas

O alvo é o volume mínimo entre as configurações que atendem às seis restrições na avaliação de pior caso da grade de robustez. Com a solução direta esse alvo é bem definido, e não uma amostra condicionada a semente e número de gerações.

Entradas disponíveis no momento da previsão, `L`, `B`, `p_gk`, perfil do veículo e as propriedades medidas da madeira. Nada calculado pelo modelo entra como entrada. O estado limite governante é saída, nunca entrada de uma previsão que pretende descobri-lo.

Saídas, o diâmetro da longarina, largura e altura das peças do tabuleiro, as duas contagens inteiras e o volume. Como as contagens são inteiras, comparar uma família de expressões contínuas com um modelo híbrido que classifica a disposição e regride as dimensões.

## Família de expressões candidatas

```text
V / V0 = C (L/L0)^a (B/B0)^b (f_cl/f0)^c
         (1 + p_gk/p0)^d (P_roda/P0)^e (E/E0)^f
```

`L0 = 1 m`, `B0 = 1 m`, `V0 = 1 m³`, `f0 = 1 MPa`, `p0 = 1 kPa`, `P0 = 1 kN` e `E0 = 1 GPa` são escalas de referência, não parâmetros ajustados. Os expoentes ainda não foram estimados. O termo de módulo só faz sentido na versão com propriedades contínuas.

Operadores permitidos, soma, subtração, produto, divisão protegida, potências restritas e, se necessário, `max` ou trechos. Restringir complexidade e singularidades. Expressões de dimensões têm escala de saída própria.

## Comparações mínimas

1. **Solução direta enumerativa**, a referência exata. Toda expressão é medida contra ela, não contra o NSGA-II.
2. **Inversão analítica por estado limite**, o diâmetro exigido por flexão, cortante e flecha isoladamente.
3. **Equação de volume do artigo 1**, com o domínio original indicado.
4. **Lei de potência multidimensional** ajustada no treinamento, com versão por partes.
5. **Regressão simbólica** com limite de complexidade.
6. **Gradient boosting** como teto de capacidade preditiva. SHAP e ALE são complementares e não produzem equação.

Hiperparâmetros e complexidade escolhidos na validação. O teste abre uma vez, depois de congelar o método.

## Evidência necessária

- MAE em unidades físicas, erro relativo mediano, percentil 95, máximo, viés e R².
- Erros estratificados por vão, veículo, espécie, carga e proximidade dos limites de busca.
- Frequência de subestimativa e violações após reanálise nominal das geometrias previstas, verificando em conjunto flexão, cisalhamento, flecha, tabuleiro e as duas restrições de disposição.
- Volume adicional após corrigir as previsões que falham, e tempo comparado ao NSGA-II e à solução direta.
- Estabilidade das expressões em reamostragens agrupadas por espécie.
- Curva de aprendizado, para decidir se mais cenários contribuem.

Uma margem calibrada de volume não garante viabilidade das seções. Correção conservadora, se adotada, calibra-se nas dimensões e na disposição e valida-se na estrutura completa. A grade de robustez no diâmetro não é probabilidade de falha.

## Bloqueadores

**B-01 · Largura tributária e vão do tabuleiro.** `calcular_objetivos_restricoes_otimizacao` usa `esp_long_corr`, o espaçamento livre entre longarinas, como largura tributária da longarina e como vão do tabuleiro. O valor entre eixos seria `esp_long_corr + d`. No artigo 2 o desvio se cancela, porque a comparação é pareada entre cenários do mesmo caso. Aqui não se cancela, porque as dimensões absolutas vão publicadas como regra de projeto, e uma fronteira publicada com carga subestimada é uma fronteira otimista.

**B-02 · Rótulos enganosos em `scripts/dataset.py`.** `volume_robust_mean_m3` é numericamente idêntico a `volume_nominal_m3`, porque o núcleo avalia os objetivos no ponto nominal. `g_robust_mean` é o pior caso sobre a grade de diâmetro, não uma média, e `feasible_robust_mean` implica `feasible_nominal`, já que o multiplicador unitário pertence à grade. Renomear, remover os campos duplicados e corrigir `02_dataset.md`, que descreve trinta perturbações aleatórias com média, o que o código não faz.

**B-03 · Transições do modelo de carregamento.** As trocas de envoltória em `L ≈ 3,34 m` e `L = 6 m` são mudanças de expressão. Qualquer regime que apareça ali é atribuído ao modelo, nunca a comportamento físico descoberto pelas equações.

**B-04 · Domínio das cargas em vão longo.** Zonas de exclusão da multidão, envoltórias e distribuição transversal permanecem em auditoria.

## Alvo editorial

Condicionado ao que a campanha mostrar, detalhado em [`04_revistas_e_referencias.md`](04_revistas_e_referencias.md). Com a fronteira da tipologia como resultado central, **Engineering Structures** é defensável pelo mérito, porque é achado estrutural e não exercício de ajuste. **Structures** permanece como alvo padrão se a fronteira não se sustentar e sobrarem as equações.

## Onde paramos

Decidido nesta discussão.

- A pergunta do artigo é a fronteira de uso da tipologia, não o desempenho de um metamodelo.
- O solucionador direto é instrumento, não contribuição. A comparação com NSGA-II vira nota de método.
- A capacidade de carga não é artigo, é leitura inversa.
- O material passa de classe para espécie, com propriedades contínuas.
- A campanha não precisa de sementes; elas sobram só na comparação com NSGA-II e na regressão simbólica.

Em aberto.

- **O diâmetro comercial máximo de tora**, por espécie ou por região, e a fonte dele. Sem isso não há fronteira.
- **B-01**, se corrige agora, e o que isso faz com os resultados já publicados do artigo 1.
- Se a grade de 24.300 casos vai com passo de vão 0,5 m ou 1,0 m, e se os seis níveis de `p_gk` se sustentam fisicamente.
- Revisão bibliográfica de metamodelo substituto de otimização estrutural e de fronteiras de aplicabilidade de tipologia, ainda não feita.

Próximo passo combinado, escrever `solver_direto.py` e conferir contra os oito casos do piloto.
