# Fichamento: Miluccio, Losanno & Parisi (2026) — Q-BRIDGE

**Referência completa:** MILUCCIO, G.; LOSANNO, D.; PARISI, F. Q-BRIDGE:
Computer-aided structural assessment of concrete bridge decks under traffic loads.
*Structures*, v. 91, 112665, 2026.
**DOI:** 10.1016/j.istruc.2026.112665 · Open access CC BY-NC-ND
**Chave BibTeX:** `Miluccio2026`
**Afiliação:** University of Naples Federico II

> ⭐ **Este é o paper mais importante do lote.** Está publicado **exatamente na
> revista alvo** (*Structures*), é **do mesmo gênero** (artigo de plataforma
> computacional aberta), e é **de 2026**. É o template estrutural a seguir.

---

## 1. Problema tratado

Ferramenta computacional aberta (MATLAB, com GUI) para avaliação estrutural rápida
de tabuleiros de pontes de concreto (armado e protendido) existentes sob cargas de
tráfego, fazendo **tanto verificação determinística normativa quanto análise
probabilística de fragilidade** no mesmo ambiente.

## 2. Formulação

- **Domínio:** tabuleiros em grelha, vigas I ou T, simplesmente apoiados.
- **Análise:** simplificada (Courbon–Engesser para distribuição transversal), não MEF.
  *Nota: eles assumem explicitamente a simplificação como virtude — "screening-level
  assessment", eficiência computacional. Mesmo argumento que sustenta o modelo
  analítico do ReliaBridge frente a um MEF.*
- **Incerteza:** variáveis aleatórias e **modelos de correlação definidos pelo
  usuário**, atribuídos a propriedades geométricas e de material; incertezas em
  cargas permanentes, propriedades dos materiais, geometria e modelos de capacidade.
- **Saída probabilística:** curvas de fragilidade multiníveis.
- **Normas:** Eurocode + diretrizes italianas (várias TLMs — traffic load models).
- **Deterioração:** modelada via degradação definida pelo usuário das propriedades.

## 3. Como validam — **o ponto crítico**

**Validação contra resultado experimental**: ensaio de prova de carga (*proof load
test*) em um tabuleiro de ponte existente, comparando resposta estrutural prevista e
medida. Depois, aplicação a uma ponte real representativa do acervo italiano de
pontes protendidas.

**O ReliaBridge não tem nenhuma seção de validação.** É a lacuna mais grave para
*Structures* depois dos bugs de código.

## 4. Estrutura do artigo — copiar

```
1. Introduction
2. Research significance          ← seção curta e dedicada; Structures gosta
3. Q-BRIDGE software: methodology and tool modules
   3.1 Methodology and applicability domain
       3.1.1 Structural modelling and deck response analysis
4. Probabilistic module
5. Deterministic module
6. Software validation            ← contra ensaio experimental
7. Illustrative example (ponte real)
8. Conclusions + future developments
```

Compare com o rascunho atual (Introdução / Metodologia / Resultados / Conclusões):
faltam **"Research significance"** e **"Validation"** como seções próprias.

## 5. Figuras e tabelas que valem imitar

| Figura | O que mostra | Equivalente no ReliaBridge |
|---|---|---|
| **Fig. 1** | Fluxograma com **bifurcação** "Code-based safety check? → Sim: caminho determinístico / Não: caminho probabilístico" | Nosso fluxograma pode bifurcar em "verificação determinística" / "otimização robusta" |
| Capturas da GUI | Módulos da interface | Já temos (Figs. `interface_inicial`, `interface_dimensionamento`) — mas precisamos mostrar **os módulos**, não só telas soltas |

## 6. O que trazer para o nosso artigo

- [ ] **Seção "Research significance"** — 3 parágrafos declarando a lacuna e o que
      o trabalho acrescenta. Barato e sinaliza para o editor de *Structures*.
- [ ] **Seção de validação própria.** Sem ensaio, as opções são: (a) verificar o
      dimensionamento contra o exemplo manual do Calil Júnior (ver [Calil2006](Calil2006.md));
      (b) comparar com uma ponte executada (R1.6); (c) validar o FORM contra Monte
      Carlo. Idealmente as três.
- [ ] Declarar explicitamente o **"applicability domain"** da ferramenta — o que ela
      cobre e o que não cobre. Revisor pergunta, e antecipar transmite maturidade.
- [ ] Justificar a **análise simplificada** como escolha deliberada (screening/
      otimização exige milhares de avaliações), não como limitação.

## 7. Onde nos diferenciamos

Q-BRIDGE é **avaliação de ponte existente**; ReliaBridge é **projeto de ponte nova**.
Q-BRIDGE é concreto/Eurocode; ReliaBridge é madeira/NBR. Q-BRIDGE não otimiza.

Não há risco de parecer derivativo — mas **citar Q-BRIDGE é obrigatório**: mostra
que conhecemos o estado da arte na própria revista, e o parágrafo deles
*"easy-to-use tools for structural assessment of bridges under other natural or
anthropic hazards are totally lacking"* é gancho direto para a nossa lacuna.

## 8. Referências deste artigo que devemos ler

- **Lee et al.** — fragilidade de pontes sob cheia usando FORM, com ferramenta
  Python acoplada (FERUM + ABAQUS). Precedente de acoplar confiabilidade a
  ferramenta aberta.
- **Silva et al. (SYNER-G)** — *fragility function manager tool*
- **Baltzopoulos et al.** — DYANAS, GUI para OpenSees
