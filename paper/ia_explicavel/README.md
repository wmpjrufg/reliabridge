# Artigo 3 — pré-dimensionamento explícito de pontes de madeira roliça

**Estado em 22/09/2026.** Plano refinado em discussão com o usuário. Nenhuma equação ajustada, nenhuma campanha executada, solucionador direto ainda não escrito.

**Pergunta do artigo.** Até onde a ponte de madeira roliça serve, e o que define esse limite. A restrição que fecha a fronteira não é normativa, é o diâmetro comercial de tora disponível.

O documento que orienta o trabalho é [`01_proposta.md`](01_proposta.md), que traz a campanha de 24.300 casos, o que sai dela, a ordem de trabalho e a seção **Onde paramos**, com o que ficou decidido e o que continua em aberto.

## Duas consequências de o modelo ser algébrico

O dimensionamento admite **solução direta**, por enumeração das disposições inteiras e solução do sistema monótono de três dimensões. É o que torna a grade completa computável em minutos, contra 142 horas de NSGA-II, e é o que permite fazer a pergunta de projeto em todo o domínio em vez de em alguns casos.

A **capacidade de carga sai por inversão exata**, porque os esforços são lineares no multiplicador do carregamento móvel. Não sustenta um artigo de IA e entra como leitura inversa das mesmas expressões.

O piloto indica que o alvo do NSGA-II não está convergido, com 15,2 % de folga de volume entre cenários. Treinar sobre ele ajustaria ruído do otimizador.

## Arquivos

| Arquivo | Conteúdo | Estado |
|---|---|---|
| [01_proposta.md](01_proposta.md) | Pergunta, desfechos possíveis, alvo, comparações e bloqueadores | **Atual** |
| [04_revistas_e_referencias.md](04_revistas_e_referencias.md) | Estratégia editorial condicionada ao marco zero | **Atual** |
| [03_aplicacao.md](03_aplicacao.md) | Uso em anteprojeto e estudo de aplicação proposto | Válido, entradas de material a atualizar |
| [02_dataset.md](02_dataset.md) | Planejamento, campos e partições | **Desatualizado**, ver B-02 |
| [05_boneco_capacidade_carga.md](05_boneco_capacidade_carga.md) | Boneco do recorte de capacidade | **Superado**, aproveitável como seção |
| [config.json](config.json) | Faixas, propriedades, trens-tipo e parâmetros editáveis | Válido |
| [data/cenarios.jsonl](data/cenarios.jsonl) | 2.700 cenários de entrada por classe de resistência | Histórico |
| [scripts/dataset.py](scripts/dataset.py) | Gerador e executor do piloto de otimização | Rótulos a corrigir, ver B-02 |
| [results/PILOTO.md](results/PILOTO.md) | Oito execuções calculadas e a conferência de integração | Válido |

Os 2.700 cenários **não são 2.700 pontes nem 2.700 simulações concluídas**. O arquivo de entradas não contém dimensões previstas nem resultados. A existência de um arquivo de resultado registra uma execução, e o campo `status` diz se houve solução utilizável.

## Mudança de material, de classe para espécie

A matriz histórica varre cinco classes de resistência, cujos perfis são colineares e impedem separar o efeito de rigidez, resistência e densidade. A campanha nova usa as propriedades medidas das 40 espécies de `paper/engstruct/dados/base_especies.csv`, com partição por espécie. As classes ficam como linha de comparação, ligando o resultado ao artigo 2.

## Bloqueadores

Detalhados em [`01_proposta.md`](01_proposta.md).

- **B-01** · `esp_long_corr` é usado como largura tributária e como vão do tabuleiro, quando o valor entre eixos seria `esp_long_corr + d`. No artigo 2 o desvio se cancela na comparação pareada, aqui não.
- **B-02** · `volume_robust_mean_m3` é idêntico a `volume_nominal_m3` e `g_robust_mean` é pior caso, não média. Renomear e corrigir `02_dataset.md`.
- **B-03** · As transições de envoltória em `L ≈ 3,34 m` e `L = 6 m` são trocas de expressão do modelo, não comportamento estrutural.
- **B-04** · Domínio das cargas em vão longo ainda em auditoria.

## Executar o que existe

Na raiz do repositório, com o ambiente já existente.

```powershell
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py gerar
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py piloto
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py executar --case-id L0600_G100_B400_TB450_D40 --seed 2
.venv/Scripts/python.exe paper/ia_explicavel/scripts/verificar.py
```

O piloto usa oito combinações dos extremos de vão e carga, ambos os veículos, D40 e largura 4,5 m, com 50 indivíduos e 300 gerações. Resultados existentes da mesma versão são preservados, e o executor exige arquivar os antigos se o código ou a configuração mudou. Não dispara a matriz completa implicitamente.

Mediana medida no piloto, 21,2 s por caso. A campanha por espécie precisa de dimensionamento próprio, que só faz sentido depois do marco zero, porque a solução direta muda a ordem de grandeza do custo.
