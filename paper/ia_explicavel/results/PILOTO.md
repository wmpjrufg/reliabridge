# Piloto exploratório — resultados e conferência

Entradas conferidas: **2700**. Execuções do piloto: **8/8**.

Valores de soluções calculadas pelo modelo existente; não são resultados de uma equação de IA.

| Cenário | Status | d (cm) | Volume nominal (m³) | Tempo (s) |
|---|---|---:|---:|---:|
| L0300_G010_B450_TB240_D40 | ok | 32.79 | 2.137 | 28.8 |
| L0300_G010_B450_TB450_D40 | ok | 47.50 | 3.270 | 27.1 |
| L0300_G500_B450_TB240_D40 | ok | 33.48 | 2.196 | 22.3 |
| L0300_G500_B450_TB450_D40 | ok | 40.64 | 2.888 | 20.2 |
| L1000_G010_B450_TB240_D40 | ok | 66.70 | 14.658 | 21.3 |
| L1000_G010_B450_TB450_D40 | ok | 79.79 | 19.967 | 20.5 |
| L1000_G500_B450_TB240_D40 | ok | 71.09 | 16.100 | 20.0 |
| L1000_G500_B450_TB450_D40 | ok | 81.98 | 20.711 | 21.0 |

Mediana observada: 21.2 s/caso. Projeção bruta para uma semente em 2.700 casos: 15.9 h.
Essa projeção usa somente D40 e oito extremos; não inclui repetições, revisão do modelo ou casos difíceis.

## Diagnóstico de qualidade do alvo

A transferência de geometrias entre cargas encontrou candidatos mais econômicos, também viáveis na média e nominalmente:

- Em `L0300_G010_B450_TB450_D40`, a geometria de `L0300_G500_B450_TB450_D40` reduz o volume médio em **15.2%**.

Isso demonstra que o extremo econômico selecionado no piloto não é uma referência convergida em todos os casos. Preservamos os resultados originais e registramos o diagnóstico. Antes de treinar, investigar sementes, gerações, retenção do melhor candidato econômico e eventualmente uma busca escalar de volume após o NSGA-II.

Conferidos IDs, hashes, separação por vão, limites atuais, reavaliação das soluções e reconstrução do volume nominal.
A reavaliação usa o mesmo núcleo e verifica a integração. A revisão física do modelo, as transições de carregamento, a convergência e a repetição de sementes permanecem pendentes.
