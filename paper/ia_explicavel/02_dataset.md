# Dataset: domínio, rastreabilidade e rótulos

## Natureza e origem

Este é um dataset de **cenários computacionais sintéticos**, fundamentado no modelo existente. Classes e presets foram transcritos da tabela do artigo 1 e da interface. Os dados da tabela antiga de 40 espécies não foram importados, nem atribuídos à fonte Wolenski2020. A nova base experimental ainda não fornece diretamente todas as propriedades necessárias ao modelo; sua integração será uma versão posterior.

JSONL é o formato primário das entradas: texto UTF-8, uma estrutura por linha, legível com `json.loads` ou `pandas.read_json(..., lines=True)`. As saídas são JSON por caso e semente, contendo a fronteira completa. Isso preserva os vetores de restrições sem achatamento ou rótulos ambíguos.

## Dicionário das entradas

| Campo | Unidade / interpretação |
|---|---|
| `case_id` | Identificador físico estável, único na matriz |
| `span_m`, `width_m` | m; vão e largura de pista |
| `dead_load_kpa` | kPa = kN/m²; permanente adicional, **exclui o peso próprio calculado** |
| `vehicle` | TB240 ou TB450; categorias de cenário |
| `wheel_load_kn` | kN por roda, não por eixo ou peso total do veículo |
| `crowd_load_kpa` | kPa; carga móvel distribuída associada ao veículo |
| `axle_spacing_m` | 1,5 m; espaçamento longitudinal entre eixos |
| `material_class`, `material_basis` | Classe e origem `class_model` |
| `density_kg_m3` | kg/m³, mesma hipótese para longarina e tabuleiro |
| `fm_k_mpa`, `fv_k_mpa` | MPa; resistência característica no modelo |
| `E_gpa` | GPa; módulo adotado na classe |
| `status` | `planned` nas entradas; não informa execução |
| `split`, `group_id` | Partição proposta, agrupada por vão |
| `crowd_moment_branch` | Entrada ou ausência do termo de multidão no momento do modelo |
| `publication_ready` | `false`: planejamento/piloto, não base final validada |

Os coeficientes, umidade, duração, fluência, limites e robustez estão em `config.json`, copiados integralmente nos resultados. `manifest.json` fixa hashes da matriz e de suas fontes. Os resultados guardam versões do Python, NumPy, pymoo, hash do núcleo, do executor e da configuração, tempo e semente.

## Partições propostas

| Conjunto | Vãos | Cenários |
|---|---|---:|
| Treinamento | 3; 3,5; 4; 5; 6; 6,5; 7; 8; 9; 10 m | 1.800 |
| Validação | 5,5 e 8,5 m | 360 |
| Teste de interpolação em vão | 4,5; 7,5; 9,5 m | 540 |

Todos os pontos Pareto e sementes de um cenário permanecem na mesma partição. A geometria candidata não é a unidade independente de amostragem. Transformações e escalas aprendidas devem usar só o treinamento.

Essa divisão testa interpolação em vãos não vistos; não prova transferência para espécies, países, normas ou tipologias diferentes. Acrescentar ensaios de generalização separados: exclusão de uma classe, retenção de níveis intermediários de carga/largura e treinamento até 8 m com teste em 8,5–10 m. Se usar outro protocolo, gerar partições próprias; não somar resultados de testes incompatíveis como se fossem uma avaliação única.

Gerar também, após a auditoria mecânica, uma malha independente de diagnóstico perto de 3,34 m e 6 m (por exemplo 3,30/3,34/3,38 e 5,95/6,00/6,05 m), ligada às transições das expressões atuais. O piloto nos extremos não cobre essas transições.

## Rótulos de saída

Cada execução registra `status`, `frontier`, `selected` e `selection_rule`:

- `ok`: ao menos um candidato viável na média robusta e na avaliação nominal.
- `no_feasible_found`: o algoritmo não encontrou solução; **não é prova de inviabilidade matemática**.
- `no_nominal_feasible_candidate`: a fronteira retornada não tem candidato que também passe nominalmente.
- `error`: falha técnica explícita, sem rótulo de projeto inventado.

Para cada ponto são gravados `d_cm`, `bw_cm`, `h_cm`, os espaçamentos de entrada e os efetivos, números inteiros de peças, os dois objetivos médios, objetivos nominais e os seis `g`. A ordem é:

1. Flexão da longarina.
2. Cisalhamento da longarina.
3. Flecha da longarina (conjunto de verificações de serviço do núcleo).
4. Flexão do tabuleiro.
5. Restrição de disposição das longarinas.
6. Restrição de disposição do tabuleiro.

`governing_structural_nominal` considera os primeiros quatro, mantendo as duas restrições geométricas separadas. `near_bound` sinaliza proximidade a menos de 0,5% da amplitude de qualquer limite da busca; não excluir automaticamente, pois limites comerciais fazem parte do problema. Investigar e relatar essa condição.

`volume_robust_mean_m3` é média das perturbações do modelo; `volume_nominal_m3` corresponde à geometria nominal reconstruída. Não comparar os dois como se fossem a mesma quantidade. O núcleo minimiza ambos os objetivos, volume e razão de flecha; o texto antigo em `vault/10_solucao_ideal_fronteira.md` descreve outro sentido para o segundo e não é adotado aqui.

## Etapas da campanha

1. Oito pilotos nas combinações de `L={3,10}`, `p_gk={0,1;5}`, ambos os veículos, D40, B=4,5. Servem para verificar o fluxo e estimar tempo.
2. Diagnóstico ampliado em classes fraca/forte, transições e casos próximos a limites; repetir sementes e aumentar gerações para medir dispersão.
3. Resolver hipóteses do modelo e congelar sua versão. Ver pendências de carregamento no README e no guia do artigo 2.
4. Executar a matriz final, salvando inclusive falhas e casos sem solução. Não reduzir robustez nem expandir limites caso a caso para fabricar viabilidade.
5. Treinar somente em saídas consistentes e identificar a região sem solução encontrada. Separar erro do otimizador, erro do metamodelo e limites do modelo físico.

O custo aproximado é `2.700 × tempo por cenário`; cinco sementes em toda a matriz implicariam 13.500 execuções. Estimar com o piloto e medir novamente em materiais extremos. As 30 perturbações atuais representam restrições **médias**, não pior caso e não análise probabilística de segurança.

## Evolução para propriedades contínuas

Depois de obter propriedades experimentais rastreáveis, incorporar perfis completos por espécie. Preservar correlações ou justificar um modelo conjunto; não sortear independentemente valores extremos de densidade, resistência e módulo e chamá-los de madeiras reais. Separar treinamento, validação e teste por espécie/perfil, com a fonte de cada propriedade. A versão atual não permite concluir causalmente que rigidez ou resistência isoladamente domina o projeto.
