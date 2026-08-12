# Artigo 2 — Engineering Structures

**Pasta:** `paper/engstruct/`
**Idioma:** **português** desde 2026-08-12 (era inglês) — ver "Idioma" abaixo
**Título:** *O enquadramento em classe de resistência não representa a rigidez das
madeiras tropicais: uma análise dependente do vão em pontes de madeira roliça para
estradas vicinais*

## A tese, em uma frase

> Classes de resistência são atribuídas **por resistência**, mas pontes vicinais de
> madeira roliça são governadas **por rigidez**, e nas madeiras tropicais essas duas
> propriedades se correlacionam mal o bastante para que o enquadramento erre —
> inclusive contra a segurança.

## Relação com o Artigo 1

Complemento, não repetição. O Artigo 1 apresenta a plataforma; o Artigo 2 a **usa como
instrumento** para produzir um achado sobre a norma, com 40 espécies reais em vez de
5 classes teóricas.

## Autoria (definida em 2026-08-12)

1. Wanderlei M. Pereira Junior — UFCAT (correspondente)
2. Matheus Henrique Morato de Moraes — UFG
3. André Luís Christoforo — UFSCar
4. Enzo Moura Rezende — UFCAT
5. Maria José Pereira Dantas — UFCAT
6. Fran Sergio Lobato — UFU

**Pendência aberta:** falta incluir o(s) autor(es) do artigo experimental que originou
os dados das 40 espécies. Há um `fillblock` em `title_authors.tex` sobre isso. Reutilizar
dataset publicado sem coautoria ou acordo prévio é fonte previsível de atrito — resolver
**antes** de escrever mais, não depois. O André Luís Christoforo trabalha com
caracterização de madeiras brasileiras e é o caminho natural para essa conversa (e
também para descobrir se existem desvios-padrão por espécie fora da tabela publicada).

## Idioma — ler antes de submeter

O texto foi traduzido para português em 2026-08-12 como **versão de trabalho**, a pedido,
para servir de base à linha de ciência de dados (`07_linha_ciencia_de_dados.md`).

O **Engineering Structures publica em inglês**. Antes da submissão é preciso:
- retraduzir o corpo para o inglês;
- reverter `preamble.tex`: `\usepackage[brazil]{babel}` → `[english]`, e comentar de
  novo o `\DeclareLanguageMapping{brazil}{brazilian-apa}`;
- converter o formato para `elsarticle` com citações numéricas (o preâmbulo atual é
  genérico, com biblatex/APA).

Alternativa a considerar: se a linha de ciência de dados crescer, talvez faça mais
sentido submeter **este** texto a periódico brasileiro e levar a versão com dados +
otimização para o Engineering Structures. Decisão em aberto.

## Escolha do periódico

Engineering Structures (Elsevier), escolhido sobre o Journal of Bridge Engineering
porque o JBE cobra profundidade de modelagem de ponte — elementos finitos, ligações,
ensaio de campo — que este trabalho não tem, enquanto o ES publica rotineiramente
estudos paramétricos com formulação analítica desde que o achado seja real. O ES também
tem fator de impacto maior. *Conferir os números atuais antes de decidir em definitivo.*

## Regra de redação que não pode ser violada

**O Engineering Structures não publica apresentação de software.** Se o artigo for lido
como "desenvolvemos uma plataforma e aplicamos NSGA-II", é rejeitado por novidade
incremental. A plataforma ocupa **no máximo meia página** da metodologia, citando o
Artigo 1 para os detalhes. A abertura é o problema do enquadramento, não a ferramenta.
Há um lembrete disso dentro de `03_methodology.tex` — não apagar sem ler.

## Estado atual

**Redigido:** introdução, população de espécies e enquadramento (§2, com as três tabelas
já calculadas e conferidas), metodologia, protocolo de comparação, esqueleto de
resultados, conclusões 1–3.

**Pendente:** toda a parte estrutural. Nenhuma das 320 rodadas de otimização foi feita.

Números já no texto: ver `03_dados_40_especies.md` (todos reconferidos em 2026-08-12).

## Ordem de execução pendente

1. **Validar a conversão média → característico** contra o artigo-fonte. Se a fonte já
   reportar valores característicos, usar os originais e regenerar as três tabelas de
   `tabelas/`. A conclusão sobre dispersão intraclasse é robusta ao fator; a lista
   nominal de qual espécie caiu em qual classe **não é**.
2. **Resolver a questão E_M0 × E_c0,med** — ver `05_revisao_critica.md`, item crítico.
3. **Gerar a Figura `figuras/E_vs_fc0.png`** — dispersão de E contra f_c0k com os degraus
   de classe sobrepostos. É rápida e já conta metade da história.
4. **Confirmar a migração do estado limite governante** (§4.1, Tabela `tab:governante`).
   Este passo decide o formato do artigo:
   - flecha passa a governar conforme o vão cresce → artigo é sobre a dependência do
     vão, como está escrito;
   - flecha governa em toda a faixa → reescrever em torno da magnitude do erro;
   - flecha nunca governa → efeito estrutural pequeno; reescrever introdução e resumo
     em torno de um resultado negativo (publicável, mas outro artigo).

   **Não pular esta etapa nem assumir o desfecho.** As instruções para os três casos
   estão no bloco vermelho da §4.1.
5. **Varredura de espécies** (§4.2): 40 espécies × 4 vãos × 2 bases de propriedades =
   **320 rodadas**. Cronometrar uma antes. Se inviável, reduzir para os vãos de 3 e 10 m,
   que são os que sustentam o argumento.
6. **Figura `figuras/continuo_vs_degraus.png`** — a figura central, um painel por vão.
7. **Reenquadramento na EN 338** (§4.3). Custa uma planilha e não toca no modelo de
   cálculo. Vale muito: generaliza o achado para além da norma brasileira.
8. **Caso detalhado** (§4.4) e **limitações** (§4.5).
9. **Conclusões** (§5).

## Antes de submeter

- [ ] Conversão média → característico validada contra a fonte
- [ ] Questão E_M0 × E_c0,med resolvida e justificada no texto
- [ ] Coautoria / forma de citação dos dados resolvida
- [ ] Valores da EN 338 conferidos contra a norma, não reproduzidos de memória
- [ ] Normas citadas formalmente (hoje NBR 7190-3, NBR 7188 e EN 338 aparecem só na
      prosa; só existe `NBR7190-1:2022` no `.bib` e ele nunca é `\parencite`-ado)
- [ ] Texto retraduzido para o inglês e `babel` revertido
- [ ] Formato convertido para `elsarticle` e citações numéricas
- [ ] Nenhum `\tofill` nem `fillblock` restante
- [ ] Nenhuma caixa "Missing figure" no PDF
