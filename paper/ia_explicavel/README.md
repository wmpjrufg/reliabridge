# Artigo 3 — Equações explicáveis de capacidade de carga

**Recorte atual:** capacidade de carga de geometrias fixas, com limites de serviço e resistência separados; pré-dimensionamento como aplicação secundária. O [boneco do artigo](05_boneco_capacidade_carga.md) contém título, resumo provisório, sumário comentado e figuras/tabelas propostas. Ele orienta a próxima etapa.

**Atenção à versão dos dados:** a matriz e o piloto abaixo pertencem à proposta anterior de otimização de dimensões. Foram preservados como histórico; não são o dataset de capacidade. O novo estudo precisa acrescentar geometrias fixas e calcular os multiplicadores de carga. A robustez média de 5% do piloto anterior não define automaticamente a capacidade do novo estudo.

## Histórico da primeira etapa: pré-dimensionamento por otimização

**Criado em 21/09/2026. Estado: proposta e dataset de entradas; piloto computacional exploratório.**

**Conferência concluída:** 2.700 entradas auditadas e oito execuções do piloto com solução. As soluções selecionadas foram reavaliadas no núcleo e seus volumes nominais reconstruídos; resultados em [PILOTO.md](results/PILOTO.md). Isso verifica a integração dos dados, não substitui a validação física do modelo.

**Achado do piloto:** uma geometria transferida entre cargas passou nas verificações e reduziu em 15,2% o volume médio em relação ao alvo escolhido para L=3 m/TB-450/p_gk=0,1 kPa. Portanto, a qualidade do alvo econômico precisa ser revista antes do treinamento. O diagnóstico e as saídas originais foram preservados.

**Título anterior:** Equações multidimensionais explicáveis para o pré-dimensionamento de pontes de madeira roliça sob diferentes cargas rodoviárias.

**Título em inglês:** Explainable multidimensional preliminary-design equations for roundwood bridges under different road loads.

Proposta: usar o ReliaBridge para produzir cenários de projeto, aprender expressões matemáticas compactas e verificar quanto elas preservam o desempenho das soluções de referência. A contribuição pretendida é uma regra de anteprojeto com domínio e erro conhecidos. Aumento do dataset, gráficos SHAP ou um bom R² isoladamente não sustentam a novidade.

## O que foi preparado

| Arquivo | Conteúdo |
|---|---|
| [05_boneco_capacidade_carga.md](05_boneco_capacidade_carga.md) | **Roteiro atual:** capacidade de carga, resumo e sumário comentado |
| [01_proposta.md](01_proposta.md) | Pergunta, hipóteses, distinção dos outros artigos e método |
| [02_dataset.md](02_dataset.md) | Planejamento, campos, partições, rótulos e pendências |
| [03_aplicacao.md](03_aplicacao.md) | Uso em anteprojeto e estudo de aplicação proposto |
| [04_revistas_e_referencias.md](04_revistas_e_referencias.md) | Revistas candidatas e fontes consultadas |
| [config.json](config.json) | Faixas, propriedades, trens-tipo e parâmetros editáveis |
| [data/cenarios.jsonl](data/cenarios.jsonl) | 2.700 cenários de entrada, uma linha JSON por cenário |
| [data/manifest.json](data/manifest.json) | Contagens e hashes das fontes |
| [scripts/dataset.py](scripts/dataset.py) | Gerador e executor com gravação por caso/semente |
| `results/piloto/` | Resultados efetivamente calculados, separados das entradas |
| [results/PILOTO.md](results/PILOTO.md) | Resumo dos resultados calculados e da conferência de integração |

Os 2.700 cenários **não são 2.700 pontes construídas nem 2.700 simulações concluídas**. O arquivo de entradas não contém dimensões previstas ou resultados inventados. A existência de um arquivo de resultado registra uma execução; seu campo `status` informa se houve solução utilizável.

## Matriz inicial

**15 vãos × 6 cargas × 2 trens-tipo × 5 classes × 3 larguras = 2.700 cenários.**

- Vão: 3,0 a 10,0 m, a cada 0,5 m.
- Carga permanente adicional `p_gk`: 0,1; 0,5; 1; 2; 3; 5 kPa. O nível 0,1 mantém uma ligação com o artigo 1. A faixa ampliada é proposta, sujeita à caracterização do revestimento real.
- TB-240 e TB-450, conforme os presets existentes. “tb4540” foi interpretado provisoriamente como TB-450.
- Classes: D20, D30, D40, D50 e D60.
- Largura de pista: 3,5; 4,0; 4,5 m, como cenários de pista única; não se está generalizando para múltiplas faixas.
- Robustez geométrica: 5%; demais fatores preservados em `config.json`.

**Não foi usada a tabela antiga das 40 espécies.** Ela está explicitamente desativada no repositório. Uma segunda versão com propriedades experimentais exige a base auditada e hipóteses de conversão documentadas. Nesta primeira versão, as propriedades são vinculadas à classe.

## Executar

Na raiz do repositório, com o ambiente já existente:

```powershell
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py gerar
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py piloto
.venv/Scripts/python.exe paper/ia_explicavel/scripts/dataset.py executar --case-id L0600_G100_B400_TB450_D40 --seed 2
.venv/Scripts/python.exe paper/ia_explicavel/scripts/verificar.py
```

O piloto usa oito combinações dos extremos de vão e carga, ambos os veículos, D40 e largura 4,5 m. Usa os mesmos 50 indivíduos, 300 gerações e 30 perturbações por avaliação do protocolo atual. Não calcula Sobol nem exporta figuras por caso. O executor aceita outras sementes do otimizador; as perturbações geométricas continuam com a semente 1 do núcleo.

Resultados existentes da mesma versão são preservados. Se o código ou a configuração mudou, o executor exige arquivar os resultados antigos antes de reutilizar o destino. Não dispara a matriz completa implicitamente. Para uma campanha selecionada, pode-se repetir `--case-id` no comando.

## Pendências do protocolo anterior de otimização

1. Resolver a revisão de cargas para vãos longos, incluindo as zonas de exclusão `4a` e `3a`, a envoltória e a distribuição transversal. Não tratar os oito pilotos como validação dessas hipóteses.
2. Confirmar o domínio físico da carga permanente e da largura; manter os limites comerciais atuais, identificando resultados que os atingem.
3. Medir convergência e repetibilidade em casos representativos, congelar o protocolo e executar a campanha.
4. Ajustar referências simples e regressão simbólica, reservando os conjuntos de validação e teste previamente definidos.
5. Reavaliar as geometrias previstas e relatar falhas, subestimativas e necessidade de redimensionamento.

Revista prioritária sugerida: **Structures**, condicionada a resultados que demonstrem ganho e generalização. Não há manuscrito pronto nem equação final treinada nesta etapa.
