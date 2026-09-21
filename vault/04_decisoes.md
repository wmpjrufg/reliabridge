# Decisões tomadas — não relitigar

Cada item aqui já foi decidido, com o motivo. Uma IA que leia este arquivo **não deve
reabrir estes pontos** nem propor alternativas, salvo se o usuário pedir.

---

### D-01 · Dois artigos, não um
**Decisão:** separar a apresentação da plataforma (Matéria, PT) do achado sobre
enquadramento em classe (Engineering Structures).
**Porquê:** o ES rejeita apresentação de software por novidade incremental. Juntar os
dois transformaria o achado em "aplicação da ferramenta" e mataria o artigo.

### D-02 · Alvo do Artigo 2 é Engineering Structures, não JBE
**Porquê:** o Journal of Bridge Engineering cobra profundidade de modelagem de ponte
(elementos finitos, ligações, ensaio de campo) que este trabalho não tem. O ES publica
estudo paramétrico analítico desde que o achado seja real, e tem FI maior.
**Pendente:** conferir os FIs atuais antes de fechar.

### D-03 · Objetivo da otimização é volume em m³
Nunca área. "m²" em qualquer lugar do código ou do texto é resíduo de versão antiga.

### D-04 · Robustez é geométrica, não material
As perturbações ρ aplicam-se às **variáveis de projeto** (dimensões), modelando a
variabilidade dimensional da madeira roliça. A variabilidade **material** não entra na
otimização — ela é o assunto do desdobramento de confiabilidade.

### D-05 · Faixa 3–6 m no Artigo 1, 3–10 m no Artigo 2
**Porquê:** 3–6 m mantém toda a matriz do Artigo 1 na mesma fórmula de momento
(`eq:mqk30`). O Artigo 2 precisa de vãos maiores porque a **migração do critério
governante** é o mecanismo investigado, e ela só aparece com vão longo. O Artigo 2
assume a descontinuidade de fórmula e a declara no texto.

### D-06 · Robustez ρ = 5 % como padrão
Com 0 / 2,5 / 5 / 10 % apenas na célula de referência C-13 do Artigo 1, para medir o
custo da robustez. **Não reduzir ρ para forçar viabilidade em célula inviável** —
inviabilidade é resultado.

### D-07 · Célula de referência é a C-13 (L = 5,0 m + D40)
Todas as análises detalhadas do Artigo 1 (fronteira, Sobol, hipervolume, boxplot) são
feitas nela.

### D-08 · Autoria — 2026-08-12
- **Artigo 2 (engstruct):** Wanderlei (1º, correspondente), Matheus, André, Enzo,
  Maria José, Fran.
- **Artigo 1 (matéria):** Enzo, Maria José e **Fran** removidos. Restam Wanderlei
  (correspondente), Priscilla, Pedro, Wellington, André, Matheus e João Paulo.
- **Matheus e André permanecem nos dois artigos**; Enzo, Maria José e Fran, só no
  Artigo 2.
- **`pages/home.py` fica como está.** Créditos da plataforma ≠ autoria do artigo.
  Decisão explícita do usuário. Não "corrigir" a divergência.

### D-09 · Artigo 2 traduzido para português — 2026-08-12
Versão de trabalho, para servir de base à linha de ciência de dados. **O ES publica em
inglês**: retraduzir antes de submeter, e reverter o `babel` no preâmbulo. Ver
`02_paper_engstruct.md`, seção "Idioma".

### D-10 · A plataforma ocupa no máximo meia página do Artigo 2
Citando o Artigo 1 para os detalhes de implementação. Resistir à tentação de detalhar a
interface. Há um lembrete disso dentro de `03_methodology.tex`.

### D-11 · ~~Semente distinta na validação de Monte Carlo~~ — revogada em 2026-09-06
Superada por **D-14**: a validação de Monte Carlo saiu do Artigo 1. A regra continua
valendo se a validação for retomada em algum desdobramento: a semente das perturbações
tem de ser **diferente** da usada na otimização, senão a validação valida a si mesma.
`ProjetoOtimo._criar_multiplicadores_robustez` usa `np.random.default_rng(1)` fixo.

### D-12 · Um único CoV para todas as espécies na linha de confiabilidade
Preferível a CoVs individuais **porque isola o efeito do enquadramento**: o espalhamento
de β passa a ser atribuível puramente ao erro da classe. Ver `07_linha_ciencia_de_dados.md`.

### D-13 · Distância entre eixos `a = 1,5 m` — 2026-09-06
**Decisão do Wanderlei:** o valor correto é **1,5 m**. As 20 simulações foram rodadas com
2,0 m, que estava errado, e **precisam ser reprocessadas**.

> Histórico, para não repetir a volta: em 2026-09-06 a questão foi levantada, o autor
> primeiro manteve 2,0 m e depois, ao ver onde o parâmetro entra, confirmou que é 1,5 m.
> Esta entrada substitui a versão anterior da D-13.

**Por que é 1,5 m.** `a` é o espaçamento **longitudinal** entre os três eixos do veículo
tipo, não a bitola transversal de 2,00 m. Entra em quatro fórmulas, todas da longarina:

| Onde | Fórmula | Local |
|---|---|---|
| Momento | `M_qk = 3PL/4 − P·a` | `madeiras.py:525` |
| Cortante | `e = L − 3a − 2h` | `madeiras.py:558` |
| Flecha | `b = (L − 2a)/2` | `madeiras.py:592` |
| Reação de apoio | `d = L − 3a` | `madeiras.py:619` |

A fórmula da flecha é a prova: `b = (L − 2a)/2` é a distância dos eixos externos até o
apoio, o que só fecha se os três eixos estiverem em `L/2 − a`, `L/2`, `L/2 + a`. E a
figura `figuras/trem_tipo.png`, da NBR 7188, cota 1,50 m nesse passo. No tabuleiro `a`
não entra: `momento_max_carga_variavel_tabuleiro` usa `a_r = 0,45 m`, o comprimento de
contato da roda.

**Impacto medido.** Reavaliando as 20 soluções publicadas com o protocolo robusto da
otimização (a coluna `a = 2,0` reproduz o `g_max` publicado exatamente nas 20, o que
valida a comparação): **17 das 20 ficam inviáveis com `a = 1,5`**. Só sobrevivem C-03,
C-04 e C-05, as de 3 m que tinham folga por estarem travadas no diâmetro mínimo. A
utilização máxima sobe para 115–127 % na maioria das células e chega a 185 % na C-01.

**Já feito:** preset `VEICULOS_PADRAO` em `pages/pre_sizing.py` corrigido para 1.5
(TB240 e TB450) e `tab:parametros` do Artigo 1 corrigida. **Pendente:** reprocessar as 20
células e refazer todo o preenchimento.

**Item técnico para conferir junto:** o código usa `4a` no momento (`c = (L − 4a)/2`) e
`3a` no cortante e na reação (`L − 3a`). Com `a = 1,5` isso dá 6,00 m e 4,50 m de zona
livre de multidão. O 6,00 bate com a figura da NBR; o 4,50 não. Pode ser proposital, já
que no cortante o veículo está encostado no apoio, mas vale verificar — e **importa para
o Artigo 2** (ver D-05), que vai até 10 m e usa a `eq:mqk45`.

### D-14 · Sai do Artigo 1 tudo que é Monte Carlo — 2026-09-06
**Decisão do Wanderlei:** removidas do Artigo 1 as duas seções baseadas em amostragem
aleatória — a §4.3.2 (comparação da fronteira com amostragem aleatória no espaço de
projeto) e a §4.3.5 (validação por simulação de Monte Carlo independente), com suas
tabelas, figuras e o bloco de conclusão correspondente.

**Porquê:** o algoritmo **já foi validado** e funciona; refazer a validação para o artigo
não agrega. Não é pendência, é escopo — não reintroduzir nem sugerir de volta.

**O que fica:** a §4.3.4 (custo da robustez, ρ = 0 / 2,5 / 10 %) **continua no artigo** e
segue pendente — é outra coisa, e é o resultado de maior originalidade (ver D-06). Nas
"Limitações e trabalhos futuros" permanece a menção a FORM e Monte Carlo como
desdobramento de confiabilidade: é a linha do `07_linha_ciencia_de_dados.md`, não a
validação removida.

### D-15 · Artigo 1 permanece na Revista Matéria, sem tentativa de subir para Structures — 2026-09-08
**Decisão do Wanderlei:** o Artigo 1 (plataforma + varredura paramétrica) fica na Revista
Matéria. Não haverá tentativa de elevá-lo a um periódico internacional de nível Structures
neste ciclo, nem de acrescentar uma seção de validação contra ponte executada — **não há
exemplo de ponte real disponível** para essa comparação.

**Contexto da pergunta.** O Wanderlei perguntou se este artigo, como está, serviria para a
*Structures*. A resposta foi que não, e por um motivo de gênero, não de polimento: é
apresentação de ferramenta + ábacos, sem achado científico generalizável, sem comparação
com literatura e sem validação independente — exatamente o perfil que a D-01 já
identificou como não aceito pela *Structures* por "novidade incremental", e é por isso
que o achado de verdade (classe de resistência não representar rigidez) foi separado no
Artigo 2. Duas rotas foram oferecidas: (1) manter a Matéria como está desenhada e deixar a
ambição internacional para o Artigo 2, que já carrega o achado certo; (2) internacionalizar
este conteúdo específico para um periódico de nível médio, o que exigiria fechar o custo
da robustez (§4.3.3) e acrescentar uma validação real, provavelmente contra uma ponte
executada. **A resposta foi a rota 1.**

**Não relitigar.** Se a pergunta "dá pra mandar pra uma revista melhor" voltar, a resposta
já está dada: não há ponte real para validar, e o veículo para ambição internacional é o
Artigo 2.

**O que isso implica para o Artigo 1:**
- A `tab:solucoes_ref` e o roteiro de verificação seguem sustentados apenas pelo Apêndice A
  (conferência manual) e pelo memorial da própria plataforma (Apêndice B) — não por uma
  ponte real. Isso é o que já estava escrito em "Limitações e trabalhos futuros"
  (`05_conclusions.tex`): a validação contra projeto executado "permanece como a
  verificação mais desejável e ainda pendente". Continua pendente, mas agora
  explicitamente **fora do escopo deste artigo**, não apenas adiada por falta de tempo.
- Pendências que continuam de pé e valem a pena fechar, porque pertencem ao escopo já
  definido da Matéria, não à ambição de Structures: custo da robustez (§4.3.3, D-06),
  Apêndice A (conferência manual), e-mails/ORCID/CEPs em `title_authors.tex`.


### D-16 · Apêndice B removido, só fica o A — 2026-09-08
**Decisão do Wanderlei:** o Apêndice B ("Relatório de verificação dos elementos", que
anexaria o memorial exportado pela plataforma) saiu do artigo. Fica só o **Apêndice A**
(demonstração manual do dimensionamento), que agora está escrito por completo.

**Como o Apêndice A foi validado:** não bastaria chamar as funções do `madeiras.py` e
chamar isso de "cálculo manual" — daria 0% de diferença por construção e não validaria
nada. Foi escrito um script à parte, que **não importa `madeiras.py`**, reimplementando
as fórmulas só a partir do que já está documentado em `03_methodology.tex`. Batimento
final: 1e-7 de diferença relativa nos 8 valores (V, f₂, g₁ a g₆) contra a avaliação
**nominal** da plataforma (não a fronteira publicada, que é a média robusta com ρ=5% —
ver adiante).

**Achados do processo de validação, que valem para o código, não só para o texto:**

1. **Bug pego no meu primeiro rascunho, não no `madeiras.py`.** `cortante_max_carga_variavel`
   tem um parâmetro genérico chamado `h`; para seção circular a plataforma passa `d`
   (diâmetro da própria longarina) nesse parâmetro, nunca um dado do tabuleiro. No
   primeiro rascunho do script eu reusei por engano a variável Python que guardava o
   `h` do tabuleiro. Corrigido; o `madeiras.py` estava certo o tempo todo.
2. **`aux_ci = 1 + 0,75(CIV-1)` não estava documentado em `03_methodology.tex`.** É um
   fator real, aplicado a `M_qk` e `Q_qk` tanto da longarina quanto do tabuleiro, só que
   nunca tinha virado equação no texto. Adicionada como `eq:civaux`.
3. **Os valores registrados na fronteira (`tab:solucoes_ref`, `tab:resultados_matriz`)
   são a MÉDIA sobre as $N_c=30$ perturbações robustas, não o ponto nominal.** Isso não
   é um erro nem uma surpresa — é exatamente o que a Seção 2.3 descreve — mas quebra
   qualquer tentativa de conferir "na mão" contra esses números diretamente: o alvo
   certo da conferência manual é a avaliação **nominal** (chamar
   `calcular_objetivos_restricoes_otimizacao` uma vez, sem a média), não o valor
   publicado. Isso ficou explícito no Apêndice A.
4. **Achado interessante, não um bug:** no ponto nominal da solução verificada, $g_6$
   (espaçamento do tabuleiro) é violado em 4,7% — a rotina de acomodação não acha, para
   `n_tab=10` nem `11`, um espaçamento que caiba nos limites de 2 a 5 cm. Ainda assim a
   solução é viável na fronteira porque a média robusta de $g_6$ ao longo das 30
   perturbações dá $-5,5\%$ (viável). Vira parágrafo no Apêndice A e ecoa o achado da
   D-06/§4.3.3: a robustez desloca o critério de aceitação do ponto nominal para o
   comportamento médio.

**Consequência textual:** as duas referências cruzadas a `Apêndice B` (em §4.3.2 e §4.5)
foram reescritas para apontar para o Apêndice A.

### D-17 · Envoltórias de momento e cortante corrigidas — 2026-09-20

As duas fórmulas fechadas da apostila supõem que o comboio inteiro cabe no vão. Quando
não cabe, ambas contam carga que não existe. Corrigidas as duas, no mesmo espírito:
preservar a forma fechada onde ela vale e tratar explicitamente o vão curto.

**Cortante** (`cortante_max_carga_variavel`) — dedução de terceiro, conferida aqui:

    Q_qk = (P/L)*[max(L-2h,0) + max(L-2h-a,0) + max(L-2h-2a,0)]
         + (q/(2L))*max(L-2h-3a,0)**2

Recupera `(P/L)(6a+3e) + q e²/(2L)` quando `L >= 2h+3a` (verificado em 17 076
combinações, |dif| < 6e-14). O afastamento 2h é normativo, NBR 7190-1 item 6.4.3.
Erro da forma antiga: +15 a +30 % em vão de 3 m, ~0 % em 6 m.

**Momento** (`momento_max_carga_variavel`) — envoltória de Barré:

    M_qk = max(3PL/4 - Pa,  P(2L-a)**2/(8L),  PL/4)

O arranjo centralizado deixa de ser o de Barré quando as rodas externas alcançam os
apoios (L = 2a). Em L = 3 m elas assentam exatamente sobre os apoios e a fórmula
degenera em PL/4. Validado contra varredura bruta da posição do comboio: diferença
zero de 2,5 a 6 m, e idêntico à forma antiga acima de 3,34 m e para vão longo.

**Flecha** — combinação rara passou a incluir a parcela permanente
(`delta_inst = delta_gk + delta_qk` contra L/500), como no SMath do Wanderlei. A
combinação quase permanente não mudou. Chaves renomeadas: `delta_qk [m]` para
`delta_inst [m]`, e `delta_lim_variavel [m]` para `delta_lim_inst [m]`.

**Descartado:** o limitador `min(2h, L/2)` que eu havia proposto. Não é normativo e
enfraqueceria o argumento no paper. O ponto cego (2h >= L zera o cortante) fica aberto
de propósito; o lugar de resolver é um limite de esbeltez no espaço de busca.

**Não era erro:** a conversão de `p_qk` de kPa para kN/m antes da chamada. Os dois
termos de multidão precisam de kN/m — `q*c²/2` com q em kPa daria força, não momento,
e o termo só fecha em `q*L²/8` quando a carga cobre o vão inteiro se q for kN/m.

**Custo:** com as seções publicadas, C-01, C-02 e C-03 vão a ~110 % de utilização na
flexão e C-04 a 100,2 % — inviáveis. Só C-05 sobrevive (85,5 %). O vão de 3 m tem de
ser refeito, e com ele o achado de saturação em d = 30 cm a partir de D40.

### D-18 · Alvo do Artigo 1 reaberto (substitui parcialmente a D-15) — 2026-09-20

A D-15 fixava o Artigo 1 na Revista Matéria. **Reaberta pelo Wanderlei**, a partir de
sugestão de consultor: escrever equações de pré-dimensionamento e mirar o Structures.

Minha recomendação, **ainda sem decisão do Wanderlei** ("por enquanto"):

- **Não converter o Artigo 1.** São 59 páginas em português, propositalmente extensas
  para servir de base à dissertação — o oposto do que o Structures pede.
- **Três papers sem canibalização:** P1 plataforma/método (Matéria, PT, quase pronto);
  P2 equações de pré-dimensionamento do DoE ampliado (candidato a Structures);
  P3 espécie vs. classe, 320 rodadas (Eng. Structures, tem lastro experimental).
- **Discordo da ideia de IA explicável como está posta:** V ∝ L^n já ajusta com R² >
  0,978 e dois parâmetros; regressão simbólica redescobriria a lei de potência e o
  revisor diria isso. Só se sustenta se o espaço de projeto virar genuinamente
  multidimensional (vão, classe, largura de pista, TB-240 e TB-450).
- **Bloqueios que equação nenhuma resolve:** o trabalho é inteiramente ABNT/TB-240, e
  não há validação contra estrutura executada (razão original da D-15).

**Três pré-requisitos antes de qualquer DoE ampliado:**

1. Acima de 6 m o momento troca de fórmula (multidão entra, eq:mqk45). Equação ajustada
   cruzando 6 m tem de ser por partes, ou ter o regime como variável.
2. **Inconsistência a resolver:** o momento usa zona de exclusão de multidão de `4a`
   (`c = (L-4a)/2`) e o cortante usa `3a`. Mesmo veículo, dois comprimentos. Só aparece
   acima de 6 m, por isso nunca incomodou até agora.
3. Células que saturam no contorno (d = 30 cm no vão de 3 m) não são ótimos e envenenam
   regressão — ampliar os limites ou excluir do ajuste.

O texto do próprio P1 cita `ritter1990`: vãos usuais de tora roliça vão de 6 a 18 m.
A matriz cobre 3 a 6 m, toda na ponta baixa. Ampliar até 10-12 m resolve a crítica de
relevância e dá amplitude para ajuste, de uma vez só.
