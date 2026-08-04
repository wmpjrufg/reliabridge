# Paper 2 — Engineering Structures — guia de preenchimento

**Alvo:** Engineering Structures (Elsevier). Escolhido sobre o Journal of Bridge Engineering
porque o JBE cobra profundidade de modelagem de ponte — elementos finitos, ligações, ensaio
de campo — que este trabalho não tem, enquanto o ES publica rotineiramente estudos
paramétricos com formulação analítica desde que o achado seja real. O ES também tem fator
de impacto maior. Conferir os números atuais antes de decidir em definitivo.

**A tese, em uma frase:** classes de resistência são atribuídas por resistência, mas pontes
vicinais de madeira roliça são governadas por rigidez, e nas madeiras tropicais essas duas
propriedades se correlacionam mal o bastante para que o enquadramento erre — inclusive
contra a segurança.

## Os números que já estão no texto

Calculados a partir dos dados das 40 espécies, com conversão média → característico de
0,70 (compressão e flexão) e 0,54 (cisalhamento):

| Achado | Valor |
|---|---|
| R² de E_M0 contra f_c0 | 0,70 |
| Dispersão intraclasse de E_M0 em D30 / D40 | 70 % / 74 % |
| Passo de E entre classes vizinhas | 14 – 21 % |
| **Razão dispersão / passo** | **≈ 4×** |
| Espécies que mudam de classe se enquadradas por rigidez | 23 de 40 (58 %) |
| Espécies **menos rígidas** que a própria classe | 14 de 40 (35 %) |
| Pior caso contra a segurança | Angelim-pedra, −25,8 % |
| Pior caso de desperdício | Goiabão, +53,1 % |

O par que resume o artigo: **Angelim-pedra** é D40 e tem E = 10 755 MPa (abaixo do valor
tabelado de D30); **Goiabão** é D30 e tem E = 18 367 MPa (acima do de D50). A norma diz que
o Angelim-pedra é o material superior; na rigidez real o Goiabão é 71 % mais rígido.

## ⚠️ Antes de qualquer coisa: validar a conversão

Todos esses números dependem do fator média → característico. **Confira contra o artigo-fonte.**
Se ele já reportar valores característicos, use os originais e regenere as três tabelas
de `tabelas/`. A conclusão sobre dispersão intraclasse é robusta ao fator; a lista nominal
de qual espécie caiu em qual classe **não é**.

O script que gerou as tabelas está em `../../` (histórico da sessão) e pode ser refeito em
poucos minutos: são três tabelas derivadas de uma planilha de 40 linhas.

## Ordem de execução

1. **Validar a conversão** contra o artigo-fonte (acima).
2. **Gerar a Figura `E_vs_fc0.png`** — dispersão de E contra f_c0k com os degraus de classe
   sobrepostos. É rápida e já conta metade da história.
3. **Confirmar a migração do estado limite governante** (§4.1, Tabela `tab:governante`).
   Este é o passo que decide o formato do artigo:
   - se a flecha passar a governar conforme o vão cresce → o artigo é sobre a dependência
     do vão, como está escrito;
   - se a flecha governar em toda a faixa → reescrever em torno da magnitude do erro;
   - se a flecha nunca governar → o efeito estrutural é pequeno, e é preciso reescrever
     introdução e resumo em torno de um resultado negativo.

   **Não pule esta etapa nem assuma o desfecho.** As instruções para os três casos estão
   no bloco vermelho da §4.1.
4. **Varredura de espécies** (§4.2): 40 espécies × 4 vãos × 2 bases de propriedades =
   320 rodadas. Cronometre uma antes. Se for inviável, reduza para os vãos de 3 e 10 m,
   que são os que sustentam o argumento.
5. **Figura `continuo_vs_degraus.png`** — a figura central, um painel por vão.
6. **Reenquadramento na EN 338** (§4.3). Custa uma planilha e não toca no modelo de cálculo.
   Vale muito: é o que generaliza o achado para além da norma brasileira.
7. **Caso detalhado** (§4.4) e **limitações** (§4.5).
8. **Conclusões** (§5).

## Regra de redação que não pode ser violada

**O Engineering Structures não publica apresentação de software.** Se o artigo for lido como
"desenvolvemos uma plataforma e aplicamos NSGA-II", é rejeitado por novidade incremental.

A plataforma tem de ocupar no máximo meia página da metodologia, citando o artigo da
Matéria para os detalhes. A abertura é o problema do enquadramento, não a ferramenta.
Há um lembrete disso dentro de `03_methodology.tex` — não o apague sem ler.

## Pendências de coautoria e dados

`title_authors.tex` e `declarations.tex` têm blocos vermelhos sobre isto, e é assunto a
resolver **antes** de escrever, não depois: os dados experimentais das 40 espécies são de
terceiros. Alinhe coautoria ou forma de citação com os autores originais. O André Luís
Christoforo é coautor do grupo e trabalha exatamente com caracterização de madeiras
brasileiras — é o caminho natural para essa conversa, e também para descobrir se existem
desvios-padrão por espécie que não foram para a tabela publicada.

## Extensão futura, fora do caminho crítico

Com os desvios-padrão por espécie, ou com CoV do JCSS Probabilistic Model Code, dá para
calcular o índice de confiabilidade β de cada espécie dentro da sua classe e mostrar que
a classe produz pontes com probabilidades de falha diferentes. Isso é um **terceiro** artigo,
e é ele — não este — que teria chance real no Journal of Bridge Engineering.

Detalhe metodológico útil: usar **um mesmo CoV para todas as espécies** é preferível a usar
CoVs individuais, porque isola o efeito do enquadramento. O espalhamento de β passa a ser
atribuível puramente ao erro da classe. O fator 0,70 da NBR, aliás, implica CoV ≈ 22 % se
o característico for o percentil 5 % de uma lognormal.

## Antes de submeter

- [ ] Conversão média → característico validada contra a fonte
- [ ] Nenhum `\tofill` nem `fillblock` restante
- [ ] Nenhuma caixa "Missing figure" no PDF
- [ ] Coautoria / citação dos dados resolvida
- [ ] Valores da EN 338 conferidos contra a norma, não reproduzidos de memória
- [ ] Formato convertido para `elsarticle` e citações numéricas (o preâmbulo atual é
      genérico, com biblatex/APA)
