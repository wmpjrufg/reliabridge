# Artigo 3 — IA explicável para capacidade de carga

**Atualização de recorte em 21/09/2026:** após discutir capacidade de carga, o usuário solicitou o boneco do artigo. Roteiro atual em [`05_boneco_capacidade_carga.md`](../paper/ia_explicavel/05_boneco_capacidade_carga.md): geometria fixa, limites de serviço/resistência e identificação do governante; pré-dimensionamento como aplicação secundária. O dataset e o piloto descritos abaixo são da etapa anterior de otimização, não rótulos de capacidade.

Criado por solicitação do usuário em 21/09/2026, a partir da sugestão do professor de ampliar vãos, cargas permanentes e trens-tipo.

**Pasta e estado canônico:** [paper/ia_explicavel/README.md](../paper/ia_explicavel/README.md).

Proposta independente dos dois manuscritos existentes: equações explícitas multidimensionais para pontes roliças de 3 a 10 m, com avaliação fora do treinamento e reanálise das geometrias previstas. Prioridade editorial sugerida: Structures; decisão de submissão ainda não tomada.

## Estado atual

- Estrutura da pesquisa, aplicação em anteprojeto, revistas e referências iniciais documentadas.
- Matriz de 2.700 entradas JSONL gerada, com configuração reproduzível e separação por vão.
- Gerador/executor acrescentado somente na nova pasta, usando o núcleo existente. Piloto exploratório concluído: oito execuções com solução viável na média robusta e nominalmente; reavaliação e reconstrução de volumes conferidas. Resumo em `paper/ia_explicavel/results/PILOTO.md`.
- Nenhuma equação de IA treinada ou conclusão de desempenho alegada.
- A conferência cruzada encontrou uma geometria viável com volume médio 15,2% menor que a referência de um piloto. Investigar convergência/seleção do alvo antes de treinar; o relatório preserva os valores originais.
- A tabela antiga das 40 espécies, desativada em 20/09, não foi usada.

## Decisões de planejamento, ainda propostas

Interpretar “tb4540” como TB-450; incluir p_gk = 0,1/0,5/1/2/3/5 kPa e larguras 3,5/4,0/4,5 m. Manter os limites da D-19 e robustez 5%. Preservar perfis vinculados às cinco classes; efeitos independentes das propriedades só poderão ser investigados numa base apropriada.

A solicitação atual autoriza iniciar a estrutura do artigo 3; substitui, para esta etapa de planejamento e piloto, a sugestão antiga de aguardar o fechamento do artigo 2 em `07_linha_ciencia_de_dados.md`. Não pressupõe o resultado de nenhum dos outros artigos.

## Próximo marco

Fechar a convenção do multiplicador de carga, auditar o modelo e implementar a determinação de capacidade de geometrias fixas. Redesenhar a amostragem e as partições antes da nova campanha. O boneco está pronto, mas o executor e o dataset de capacidade ainda não foram produzidos. Os resultados do piloto anterior não são resultados do novo recorte.
