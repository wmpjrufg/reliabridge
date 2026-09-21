# Pergunta e desenho científico

## Pergunta principal

É possível obter equações compactas que estimem o pré-dimensionamento econômico de pontes de madeira roliça de 3 a 10 m, considerando carga permanente, veículo, classe e largura, com erro controlado e verificações estruturais satisfeitas após a reconstrução da geometria?

## Separação dos artigos

| Linha | Contribuição |
|---|---|
| Artigo 1 — `paper/materia` | Plataforma, otimização e estudo paramétrico original; já contém uma equação simples de volume |
| Artigo 2 — `paper/engstruct` | Consequência estrutural da representação por classes versus propriedades experimentais, no protocolo reformulado |
| Artigo 3 — esta pasta | Generalização multidimensional, expressões explícitas e desempenho de anteprojeto em cenários retidos |

A numeração preserva as duas pastas existentes. O novo artigo cita o primeiro para o modelo e compara sua equação com as novas; não reapresenta interface, validação ou os mesmos resultados como novidade.

## Hipóteses a testar, sem pressupor resultados

1. Uma única lei de potência pode perder precisão quando mudam o veículo, o carregamento e a disposição inteira de peças.
2. Regressão simbólica com operadores fisicamente motivados pode melhorar a relação erro–complexidade, comparada com regressão log-linear e expressões por partes.
3. O erro médio de volume pode ser pequeno enquanto algumas dimensões previstas violam restrições; a utilidade exige reanálise das seções completas.
4. Algumas mudanças de regime podem decorrer das fórmulas do simulador ou do arredondamento construtivo. Não atribuí-las automaticamente a uma descoberta física da IA.

É um resultado aceitável concluir que a regressão simples vence. Nesse caso, o artigo deve demonstrar a suficiência da expressão e o domínio em que isso acontece, sem afirmar superioridade de IA complexa.

## Variáveis e saídas

Na fase 1, as entradas independentes são `(L, B, p_gk, classe, veículo)`. Para apresentação de uma equação, o índice de resistência `f_cl` pode representar a classe; o significado é interpolação no sistema de classes, não variação isolada da resistência.

Não ajustar simultaneamente `E`, `f_m,k`, `f_v,k` e densidade e interpretar suas importâncias como efeitos independentes: são cinco perfis associados às classes. Da mesma forma, carga de roda e multidão estão vinculadas aos dois veículos; não há identificação separada de seus efeitos com somente esses dois perfis.

Saídas desejadas: diâmetro, largura e espessura das peças do tabuleiro, contagens/disposição de peças e volume. Manter o volume nominal separado do volume médio nas perturbações. Como a disposição contém variáveis inteiras, comparar uma família de equações com um modelo híbrido de classificação de contagem e regressão de dimensões.

O alvo inicial é a solução de menor volume médio encontrada na fronteira que também passa na verificação nominal. É uma solução de referência numérica condicionada ao algoritmo, às restrições e aos limites; não há certificado de ótimo global. Nunca misturar arbitrariamente o extremo econômico e o ponto de compromisso no mesmo alvo.

## Família de expressões candidatas

Uma referência dimensionalmente consistente usa razões adimensionais:

```text
V / V0 = C (L/L0)^a (B/B0)^b (f_cl/f0)^c
         (1 + p_gk/p0)^d (P_roda/P0)^e
```

`L0 = 1 m`, `B0 = 1 m`, `V0 = 1 m³`, `f0 = 1 MPa`, `p0 = 1 kPa`, `P0 = 1 kN` são escalas de referência, não parâmetros aprendidos. `C,a,b,c,d,e` ainda não foram ajustados. A carga de roda representa aqui o perfil do veículo; a multidão associada deve ser informada no domínio.

Permitir operadores `+`, `-`, `*`, divisão protegida, potências restritas e, se necessário, `max`/trechos. Restringir complexidade e singularidades. Expressões para dimensões devem ter sua própria escala de saída. O marcador de entrada da multidão acima de 6 m pode ser derivado do vão e não é um resultado estrutural.

Não usar o estado limite governante, a geometria otimizada ou qualquer resultado calculado como entrada da previsão. Se uma família por estado limite for escolhida, o regime precisa ser previsto usando apenas entradas; avaliar o erro dessa escolha em conjunto com o erro da equação.

## Comparações mínimas

1. Equação original de volume do artigo 1, com seu domínio original claramente indicado. Fora dele, apenas referência de extrapolação.
2. Lei de potência multidimensional ajustada no treinamento e versão por partes.
3. Regressão simbólica com limite de complexidade, candidata à expressão final.
4. Gradient boosting como referência de capacidade preditiva; explicações SHAP/ALE são complementares e não produzem, sozinhas, uma equação.

Selecionar hiperparâmetros e complexidade na validação. Abrir o teste uma vez após congelar o método. Não escolher a melhor fórmula olhando seu erro no teste.

## Evidência necessária

- MAE em unidades físicas, erro relativo mediano, percentil 95, máximo e viés, além de R².
- Erros estratificados por vão, veículo, classe, carga e proximidade dos limites.
- Frequência de subestimativa e violações após reanálise nominal das geometrias previstas; verificar conjuntamente flexão, cisalhamento, flecha, tabuleiro e disposição.
- Volume adicional após a correção das previsões e tempo de cálculo comparado ao NSGA-II.
- Estabilidade das expressões em reamostragens agrupadas e repetição das otimizações; sementes não aumentam o número de cenários independentes.
- Curva de aprendizado para decidir se mais simulações contribuem.

Uma margem calibrada de volume não garante viabilidade das seções. Se adotar correção conservadora, calibrá-la nas dimensões/disposição e validar a estrutura completa. O `g <= 0` médio do algoritmo atual não equivale a probabilidade de falha nem a atendimento de todas as perturbações.

## Estrutura sugerida do futuro manuscrito

Introdução e lacuna; modelo e domínio; geração e auditoria do dataset; métodos interpretáveis; desempenho fora do treinamento; equações e regimes; aplicação de anteprojeto; limitações; conclusões. Figuras centrais: domínio amostrado, erro–complexidade, paridade fora do treinamento, mapas de erro/violação e exemplos da aplicação.
