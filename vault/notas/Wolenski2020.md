# Wolenski et al. (2020) — leitura e implicações para Engineering Structures

Referência: *Models for estimation of mechanical properties of compressive and tensile strength in the parallel direction to the grains*. Ambiente Construído, 20(1), 263–276. DOI: https://doi.org/10.1590/s1678-86212020000100373.

Leitura do PDF fornecido pelo usuário (`/home/casa-wand/Documentos/download.pdf`), em 2026-09-20. O título inglês consta na primeira página. O usuário informou que não dispõe atualmente da planilha de origem, mas poderá obtê-la.

## O que a fonte efetivamente fornece

- 40 espécies nativas de folhosas (Tabela 1, p. 266).
- Ensaios de compressão e tração paralelas às fibras no LaMEM/EESC/USP, segundo NBR 7190:1997, Anexo B; 12 corpos de prova por espécie e modalidade, total de 960 determinações; correção para 12% de umidade (p. 265).
- Médias, DP, CV e IC de `f_c0`, `f_t0`, `E_c0` e `E_t0` (Tabelas 3–6, pp. 268–270).
- Resistências características de compressão e tração e classes históricas (Tabela 7, p. 271).
- Não fornece os dados de flexão, cisalhamento e densidade da tabela atualmente usada no manuscrito. Não detalha a procedência geográfica de cada lote nem publica resultados individuais ordenados.

## Classificação e inconsistências a conferir

O procedimento descrito nas pp. 266–267 usa os resultados individuais ordenados, o estimador da Eq. 5 e os limites inferior amostral e `0,70 × média`. Portanto, os valores característicos publicados não devem ser substituídos automaticamente por `0,70 × média`.

A Tabela 2 traz C20, C30, C40 e C60 da norma de 1997. O reenquadramento D20–D60 do manuscrito é outra operação e precisa de referência normativa própria, com conferência da parte da norma, tabela e tipo de produto. Não basta trocar a letra C por D.

A Tabela 7 foi conferida também na imagem da página: mandioqueira (53,70 MPa), oiticica-amarela (58,00 MPa) e quina-rosa (55,00 MPa) aparecem como C60, apesar do limiar de 60 MPa da Tabela 2; piolho (39,80 MPa) aparece como C40. Tratar como aparentes inconsistências a esclarecer, sem corrigir silenciosamente a fonte.

## A base anterior não é idêntica

| Item | PDF | Manuscrito atual |
|---|---|---|
| Angelim-pedra, Hymenolobium petraeum | Ausente da Tabela 1 | Presente e usado como caso extremo |
| Goiabão: compressão média | 48,46 MPa | 49 MPa |
| Goiabão: compressão característica | 43,10 MPa | 34,3 MPa, calculados como 0,70 × 49 |
| Goiabão: módulo | E_c0 = 18 717 MPa; E_t0 = 18 267 MPa | E_M0 = 18 367 MPa |

Os módulos acima não são intercambiáveis. O exemplo do goiabão mudaria de D30 para D40 pela regra operacional do manuscrito se fosse utilizado o `f_c0,k` publicado, mas isso não autoriza combinar esse valor com o módulo à flexão de outra amostra.

## Como melhorar a investigação

1. **Rastreabilidade primeiro:** obter a planilha original e registrar, por espécie e propriedade, nome científico, fonte/tabela, modalidade de ensaio, umidade, n, média, DP e valor característico. Distinguir valores medidos, estimados e de classe. Não inferir identidade de lotes pela coincidência do nome popular.
2. **Separar efeitos:** comparar o enquadramento baseado em resistência característica publicada com o cenário de conversão simplificada, apenas para amostras correspondentes. Quantificar mudanças de classe e de resultados estruturais. Isso separa o efeito da conversão do efeito da discretização em classes.
3. **Comparar a mesma propriedade:** usar E_c0 experimental versus E_c0 da classe para estudar a representação por classe. Para calcular flexão com E_M0, documentar a transformação adotada e sua incerteza, ou usar ensaios de flexão rastreados. A relação E_c0 = E_t0 examinada na fonte não resolve a passagem para E_M0.
4. **Erro por espécie e consequência estrutural:** reportar erro assinado, erro absoluto, extremos e dispersão por classe, além de R². A ausência de diferença de médias na ANOVA não é demonstração formal de equivalência nem garantia de precisão individual. Comparações entre modalidades na mesma espécie devem considerar o pareamento.
5. **Isolar a rigidez:** para a mesma geometria e carregamento, variar somente E e comparar flechas; no modelo elástico com os demais parâmetros fixos, a flecha varia inversamente com E. Depois comparar os projetos reotimizados. Separar a mudança de E das mudanças de resistência e peso próprio.
6. **Incerteza intraespécie:** explorar os DP/CV publicados apenas para suas respectivas propriedades e populações. Sem dados individuais e covariâncias, não chamar reamostragem de médias de bootstrap dos ensaios nem assumir independência entre propriedades sem análise de sensibilidade. Distinguir dispersão de corpos de prova de incerteza da média.
7. **Validação de predição:** se forem ajustadas novas regressões, avaliar erro fora da amostra (por exemplo, retirando uma espécie por vez), além do ajuste na base de treinamento. Não apresentar correlação compressão–tração da fonte como correlação resistência–rigidez.

Até reconciliar as fontes, os percentuais 58%, 35%, a dispersão de 70–74% e o contraste angelim-pedra/goiabão são resultados provisórios da base atual, não resultados validados pelo PDF. A robustez desses achados à alteração da base ainda precisa ser demonstrada.

## Decisão posterior do usuário — 2026-09-20

Adotar este artigo como base da investigação reformulada. A tabela anterior foi excluída do manuscrito ativo, e seus percentuais não são mais apresentados como resultados provisórios deste estudo. O novo protocolo e suas pendências constam em `../../paper/engstruct/PREENCHIMENTO.md`.
