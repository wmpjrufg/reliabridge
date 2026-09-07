## Escolha da solucao ideal a partir da fronteira eficiente

A planilha gerada no pre-dimensionamento contem as solucoes viaveis encontradas pelo algoritmo NSGA-II. Cada linha representa uma configuracao estrutural possivel para a ponte, contendo as variaveis de projeto, os valores das funcoes objetivo e os indicadores das restricoes.

Neste problema, a escolha da solucao ideal nao e feita olhando apenas uma variavel isolada. A ponte deve ser analisada como um problema multiobjetivo, no qual se deseja:

- minimizar o volume total de madeira;
- maximizar o aproveitamento da flecha admissivel.

Assim, a solucao ideal e escolhida a partir da fronteira eficiente, procurando uma alternativa equilibrada entre economia de material e desempenho estrutural.

### Variaveis usadas na escolha

A planilha contem duas colunas principais para essa decisao:

- `of_area_m2`: representa o volume/consumo de madeira da solucao. Quanto menor, melhor.
- `of_fator_flecha`: representa o fator de aproveitamento da flecha admissivel. Quanto maior, melhor.

A logica adotada e:

- menor `of_area_m2` indica uma solucao mais economica;
- maior `of_fator_flecha` indica uma solucao que utiliza melhor a capacidade estrutural disponivel, ficando mais proxima do limite admissivel de deslocamento.

### Normalizacao dos objetivos

Como os dois objetivos possuem escalas diferentes, primeiro eles sao normalizados para uma escala comum entre 0 e 1.

Para o volume de madeira, como o objetivo e minimizar:

```text
area_norm = (area - area_min) / (area_max - area_min)
```

Nesse caso:

- `area_norm = 0` representa a menor area/volume da fronteira;
- `area_norm = 1` representa a maior area/volume da fronteira.

Para o fator de flecha, como o objetivo e maximizar:

```text
flecha_norm = (flecha_max - flecha) / (flecha_max - flecha_min)
```

Nesse caso:

- `flecha_norm = 0` representa o maior aproveitamento da flecha;
- `flecha_norm = 1` representa o menor aproveitamento da flecha.

Dessa forma, depois da normalizacao, os dois objetivos passam a ter a mesma interpretacao:

```text
quanto menor o valor normalizado, melhor
```

### Ponto ideal

Apos a normalizacao, define-se um ponto ideal teorico:

```text
ponto_ideal = (0, 0)
```

Esse ponto representa uma solucao hipotetica que teria, ao mesmo tempo:

- o menor volume de madeira possivel;
- o maior fator de flecha possivel.

Na pratica, esse ponto geralmente nao corresponde a uma solucao real da fronteira, pois existe um compromisso entre os objetivos. Por isso, busca-se a solucao real mais proxima desse ponto.

### Distancia ate o ponto ideal

Para cada solucao da planilha, calcula-se a distancia Euclidiana ate o ponto ideal:

```text
distancia_ideal = sqrt(area_norm^2 + flecha_norm^2)
```

A solucao ideal equilibrada e aquela com a menor distancia:

```text
solucao_ideal = linha com menor distancia_ideal
```

Essa solucao representa o melhor compromisso entre economia de material e aproveitamento estrutural.

### Solucoes de referencia

Alem da solucao equilibrada, e util destacar outras duas solucoes da fronteira.

#### Solucao mais economica

E a solucao com menor consumo de madeira:

```text
menor of_area_m2
```

Essa alternativa prioriza economia de material.

#### Solucao com maior aproveitamento da flecha

E a solucao com maior fator de flecha:

```text
maior of_fator_flecha
```

Essa alternativa prioriza o uso mais intenso da capacidade estrutural admissivel.

#### Solucao equilibrada

E a solucao com menor distancia ao ponto ideal normalizado:

```text
menor distancia_ideal
```

Essa alternativa representa um compromisso entre os dois objetivos.

### Interpretacao final

A solucao ideal nao deve ser entendida como uma verdade absoluta, mas como uma recomendacao baseada nos criterios definidos.

Se o objetivo principal for reduzir material, a solucao mais economica pode ser escolhida.

Se o objetivo for explorar melhor a capacidade estrutural, a solucao com maior fator de flecha pode ser escolhida.

Se o objetivo for obter uma alternativa intermediaria, a solucao equilibrada pela distancia ao ponto ideal e a mais indicada.

Essa abordagem permite transformar a fronteira eficiente em uma decisao de projeto mais clara e justificavel.
