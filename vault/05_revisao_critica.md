# Revisão crítica do caminho escrito

Leitura do Artigo 2 feita em **2026-08-12**, na posição de revisor do Engineering
Structures. Ordenado por gravidade. Os itens 🔴 podem derrubar o artigo se chegarem
à revisão sem tratamento.

> **Veredito geral: o caminho está certo.** A tese é real, é original, o mecanismo
> (migração do critério governante com o vão) é bem escolhido, e o achado tem
> consequência prática. Os problemas abaixo são de *execução e atribuição*, não de
> concepção. Nenhum deles exige mudar a pergunta do artigo.

---

## 🔴 C-01 · O ΔV vai medir a coisa errada

**O problema.** O protocolo (§3.4) compara o projeto pela espécie contra o projeto pela
classe usando **todas** as propriedades diferentes ao mesmo tempo: E, f_m,k, f_v0,k e
massa específica. Mas a §2.3 já diz que a classe subestima a resistência à flexão em
**2 a 92 %**, sempre a favor da segurança. Uma conservadorismo dessa magnitude vai
**dominar** o ΔV nos vãos curtos, onde flexão governa — e a massa específica tabelada
muda o peso próprio, que muda tudo.

Resultado provável: ΔV enorme e positivo em toda a faixa, dirigido pela resistência.
O efeito de rigidez, que é a tese do artigo, fica enterrado. O revisor escreve:
*"the reported ΔV conflates the stiffness misrepresentation with a much larger,
systematic strength conservatism; the paper does not isolate its own claimed effect."*

**Como corrigir.** Rodar **três** variantes por espécie e vão, não duas:

| Variante | f_m,k, f_v0,k, ρ | E | Mede |
|---|---|---|---|
| A — espécie | medidos | medido | referência |
| B — classe | tabelados | tabelado | custo total do enquadramento |
| **C — híbrida** | **medidos** | **tabelado** | **custo isolado do erro de rigidez** |

`ΔV_C` é o número que sustenta a tese. `ΔV_B − ΔV_C` é o custo do erro de resistência,
e vira um resultado secundário útil. O custo é 50 % mais rodadas (480 em vez de 320),
mas sem isso o artigo não prova o que afirma provar.

---

## 🔴 C-02 · E_M0 medido está sendo comparado com E_c0,med tabelado

**O problema.** As Tabelas `tab_dispersao` e `tab_discordancia` confrontam o módulo de
elasticidade **na flexão** (E_M0, medido) contra o módulo **na compressão paralela**
(E_c0,med, tabelado pela NBR). São propriedades distintas, medidas em ensaios distintos.
Parte do "erro de representação" pode ser simplesmente o *offset sistemático* entre
flexão e compressão, e não erro de enquadramento.

**O que sobrevive e o que não sobrevive:**

| Resultado | Sensível ao offset? |
|---|---|
| Dispersão intraclasse (70 %, 74 %) e a razão ≈ 4× | ❌ **Não** — offset sistemático cancela numa razão máx/mín. Este resultado está seguro. |
| Coluna "desvio frente ao valor tabelado" | ✅ Sim |
| "14 espécies menos rígidas que a classe" | ✅ **Sim — é o achado de segurança, e é o mais frágil** |
| Enquadramento por rigidez (as 23 discordâncias) | ✅ Sim |

**Como corrigir.** Uma das três:
1. verificar se a fonte experimental também reporta E_c0 e usar esse valor;
2. justificar no texto, com referência normativa, que a NBR 7190 admite E_M0 ≈ E_c0 para
   fins de dimensionamento (e mostrar que o viés é pequeno na população);
3. aplicar uma conversão explícita e **fazer a análise de sensibilidade ao fator de
   conversão**, mostrando que a conclusão não muda.

Qualquer uma resolve; nenhuma pode ser omitida. Este é o primeiro parágrafo que um
revisor de madeira vai atacar.

---

## 🟠 C-03 · "Dispersão" e "passo" não são grandezas comparáveis

`max/min − 1` sobre n espécies contra um incremento único entre duas classes. A razão
"≈ 4×" é retoricamente forte mas estatisticamente frouxa: a amplitude **cresce com n**,
e os n por classe são 4, 11, 12, 9, 4. Que D20 (n=4) mostre 13,5 % e D40 (n=12) mostre
73,7 % é em parte tamanho de amostra, não física.

**Como corrigir.** Manter a razão como número de impacto, mas acompanhá-la de pelo menos
uma medida livre de escala, reportada na mesma tabela:
- CoV intraclasse de E_M0, ou
- fração de espécies cujo erro de rigidez excede **metade do passo de classe** — que é o
  enunciado honesto de "a classe não resolve esta espécie".

Com a segunda métrica o argumento fica imune à objeção e não perde força.

---

## 🟠 C-04 · Os 35 % incluem duas espécies no ruído

Das 14 espécies "menos rígidas que a classe", duas estão a distância desprezível:

| Espécie | Desvio |
|---|---|
| Angico-preto | **−0,0 %** (16 498 contra 16 500 tabelado) |
| Oiticica-amarela | −0,1 % |

Chamar isso de "projeto contra a segurança" não sobrevive à revisão. O número
defensável é **12 espécies (30 %)**, e vale reportar os dois: *"14 espécies (35 %) têm
E_M0 abaixo do tabelado; em 12 delas (30 %) o défice excede 1 %."*

---

## 🟠 C-05 · Extrair a solução de volume mínimo da fronteira é o ponto mais instável

A §3.4 afirma que, com mesmo algoritmo e mesma semente, "a diferença é atribuível
exclusivamente às propriedades do material". Isso é mais forte do que se pode sustentar:
mudar as propriedades muda a paisagem de aptidão, e a mesma semente **não** garante
qualidade de convergência equivalente. Pior, a solução de volume mínimo é o **extremo**
da fronteira, que é justamente a região menos densamente povoada e mais sensível a ruído
de convergência.

**Como corrigir.** Escolher uma das duas e declarar:
- repetir cada rodada com **k sementes** (k = 5 já basta) e reportar ΔV como média ±
  desvio; ou
- reportar hipervolume por rodada e descartar/repetir as que não atingirem um patamar.

Sem isso, um ΔV de poucos por cento é indistinguível de ruído do otimizador — e o artigo
depende de ΔV pequenos serem reais.

---

## 🟡 C-06 · "A verificação ao cisalhamento diminui com o vão" está mal enunciado

§1, quarto parágrafo. Para seção fixa, o esforço cortante **cresce** com o vão; o que
diminui é a utilização do cisalhamento **relativamente** à de flexão. Como está escrito,
soa errado e entrega ao revisor uma correção fácil logo na introdução.

**Correção:** "*relativamente à verificação de flexão*, a utilização do cisalhamento
decresce com o vão, enquanto a de deslocamento cresce aproximadamente com o quadrado do
vão." Uma frase, e o parágrafo fica correto.

---

## 🟡 C-07 · Vão de 10 m com longarina de madeira roliça pode ser inviável

A faixa da §3.5 vai a 10,0 m. Duas consequências não tratadas no texto:
1. o diâmetro necessário pode ultrapassar o que existe comercialmente em tora — e a
   otimização não sabe disso, então vai devolver uma solução matemática inexistente;
2. é o vão em que a rotina pode levantar `ValueError` por inviabilidade.

Adicionar um limite superior explícito de diâmetro, justificado por disponibilidade
comercial, e declarar no texto. Se 10 m for inviável, isso é **resultado** e deve ser
reportado como tal — não motivo para relaxar restrição.

---

## 🟡 C-08 · Não existe script versionado que gere as três tabelas

`paper/engstruct/tabelas/*.tex` foram gerados em sessão anterior; o script não está no
repositório. Como a conversão média → característico tem boa chance de mudar (é a
pendência nº 1), isso significa refazer 40 linhas à mão. Escrever
`scripts/gera_tabelas_especies.py` + planilha de origem e commitar. É meia hora e
protege todo o resto.

---

## 🟡 C-09 · Normas aparecem só na prosa, nunca citadas formalmente

NBR 7190-3, NBR 7188, NBR 8681 e EN 338 sustentam o artigo inteiro e não têm `\parencite`.
O `.bib` só tem `NBR7190-1:2022`, e mesmo essa nunca é citada. Em periódico Elsevier isso
volta na revisão editorial. Acrescentar as entradas e citar na primeira menção de cada.

---

## ✅ O que já está bem resolvido (não mexer)

- **A tese e o mecanismo.** Indexar classe por resistência num sistema governado por
  rigidez é uma boa pergunta, ainda em aberto, e a dependência do vão é o eixo certo.
- **A honestidade do §4.1.** O bloco vermelho que instrui o que fazer nos três desfechos
  possíveis da migração do critério governante é excelente prática e deve permanecer até
  o resultado existir.
- **A comparação com a EN 338.** Custa uma planilha e é o que internacionaliza o artigo.
  Prioridade alta pelo retorno.
- **O par angelim-pedra / goiabão.** É a imagem que vende o artigo. Mantê-lo no resumo,
  na figura e nas conclusões.
- **A recusa a apresentar a plataforma.** Correta e bem sinalizada no texto.
- **Aritmética.** Todos os percentuais das tabelas foram reconferidos e batem. O único
  erro encontrado ("duas espécies diferem em duas classes", quando são quatro) já foi
  corrigido em `02_materials.tex` e `05_conclusions.tex`.
