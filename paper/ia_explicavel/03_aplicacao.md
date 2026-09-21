# Ponto de aplicação: anteprojeto de pontes vicinais

## Usuário e decisão

Uma equipe de engenharia municipal precisa comparar alternativas para uma travessia e estimar a ordem de grandeza das peças e do consumo de madeira antes do dimensionamento detalhado. Ela informa o vão, a largura, a carga permanente adicional, a classe disponível e o veículo de referência.

O produto científico será uma família de expressões utilizável em calculadora/planilha e, depois, uma opção na página de pré-dimensionamento do ReliaBridge. Esta etapa define o uso e prepara os dados; ainda não instala um modelo de IA na interface.

## Fluxo pretendido

```mermaid
flowchart LR
    A[Entradas do anteprojeto] --> B[Conferir domínio]
    B --> C[Equações explícitas]
    C --> D[Dimensões e disposição das peças]
    D --> E[Reanálise estrutural]
    E --> F[Alternativa conferida ou redimensionamento]
```

Mostrar diâmetro e dimensões do tabuleiro, quantidade de peças, volume nominal reconstruído, faixa de erro observada no conjunto de validação e verificações atendidas. A explicação pode indicar o efeito previsto de trocar o veículo ou aumentar a carga, preservadas as demais entradas. Uma relação estatística de importância não deve ser apresentada como causalidade do material.

Se a entrada estiver fora do domínio ou a geometria estimada não passar na reanálise, o fluxo encaminha o caso ao dimensionamento completo. A expressão de volume, isoladamente, serve a uma estimativa de consumo; não determina uma seção estrutural suficiente.

## Estudo de aplicação proposto para o artigo

Travessia hipotética com **L = 7,5 m, B = 4,0 m, classe D40**, comparando TB-240 e TB-450, e `p_gk = 0,5`, `2,0` e `5,0 kPa`. São seis alternativas sob as mesmas hipóteses de material e geometria global. O vão 7,5 m está reservado ao teste; não usar seus resultados para escolher a expressão.

Perguntas de aplicação:

- Quanto mudam diâmetro e consumo quando muda o veículo?
- Qual o efeito do carregamento permanente sobre as seis alternativas?
- A solução prevista mantém todas as verificações após ajustar o número inteiro de peças?
- Qual o acréscimo de volume se for necessário corrigir a previsão?
- Quanto tempo se economiza em comparação ao processo completo?

Não existem ainda respostas numéricas para esse estudo de aplicação. Os oito pilotos usam outros vãos e servem à infraestrutura de dados.

## Critério de sucesso a definir antes de abrir o teste

Proposta inicial para discussão: buscar erro relativo mediano de volume até 5%, reportando também percentil 95 e máximo; medir diretamente a taxa de violação das seções previstas. O limite de 5% é uma meta de pesquisa sugerida, não um resultado e não uma exigência normativa. O fluxo só apresenta uma alternativa como conferida após passar no modelo completo, e mesmo isso não constitui validação por ponte construída.

A transferência para projeto executivo exige o conjunto de verificações e detalhamentos aplicáveis, que vai além da superestrutura idealizada pelo modelo. No artigo, delimitar a aplicação às peças e hipóteses efetivamente estudadas.
