# Artigo 2 — Engineering Structures

Reformulado em 2026-09-20 por solicitação do usuário.

**Pasta:** `paper/engstruct/`. **Idioma de trabalho:** português.

**Título:** Efeito da representação por classes de resistência no desempenho e no consumo de material de pontes de madeira tropical.

**Base experimental definida:** Wolenski, Dias, Peixoto, Christoforo e Lahr (2020), *Models for estimation of mechanical properties of compressive and tensile strength in the parallel direction to the grains*. DOI: 10.1590/s1678-86212020000100373.

## Pergunta e contribuição

Quanto a representação por classes altera deslocamentos e volume de madeira? O protocolo separa conversão da resistência, representação da rigidez e redimensionamento. O experimento principal altera somente a rigidez e conserva as demais hipóteses em cada par. A avaliação de desempenho ocorre reanalisando o projeto por classe com rigidez experimental.

Não pressupor inadequação das classes, violação de limite ou transição do estado limite governante. Delta V negativo não prova insegurança. A ferramenta computacional é instrumento; a contribuição é quantificar a consequência estrutural da representação das propriedades.

## Estado

Título, resumo, introdução, materiais, metodologia, roteiro de resultados, conclusões, nomenclatura, apêndices e disponibilidade de dados reformulados. A tabela antiga não integra o manuscrito. As análises do novo protocolo ainda não foram executadas.

Fonte disponível: médias, DP/CV, características e classes históricas. Pendentes: transcrição auditada, escolha/verificação do sistema normativo estrutural, relação E_c0–E_M0 e hipóteses para flexão, cisalhamento e densidade. A ausência da planilha original não impede transcrever as tabelas publicadas, mas impede reproduzir o estimador a partir de resultados individuais.

O gerador e os casos antigos não implementam o novo protocolo; não rodar a campanha anterior como se estivesse atualizada.

Plano operacional: [PREENCHIMENTO](../paper/engstruct/PREENCHIMENTO.md).
Leitura crítica da fonte: [Wolenski2020](notas/Wolenski2020.md).

## Autoria

A lista do manuscrito foi preservada: Wanderlei M. Pereira Junior, Matheus Henrique Morato de Moraes, André Luís Christoforo, Enzo Moura Rezende, Maria José Pereira Dantas e Fran Sergio Lobato. Confirmar composição final e contribuições com a equipe; a definição da base experimental não altera automaticamente a autoria.

## Transferência editorial da Matéria

Formulação mecânica e otimização incorporadas sem resultados em `03a_structural_model.tex` e `03b_optimization_protocol.tex`. Introdução reforçada com antecedentes de pontes rurais e otimização; bibliografia ampliada. Ver as pendências concretas de distribuição de cargas, domínio da carga móvel e combinações de serviço no guia de preenchimento. A compilação do manuscrito não equivale à validação dessas rotinas. Nenhuma alteração no código foi realizada nesta transferência.
