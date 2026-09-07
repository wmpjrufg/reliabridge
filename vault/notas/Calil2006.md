# Fichamento: Calil Júnior — Manual de projeto e construção de pontes de madeira

**Referência completa:** CALIL JUNIOR, C.; DIAS, A. A.; GÓES, J. L. N. de;
CHEUNG, A. B.; STAMATO, G. C.; PIGOZZO, J. C.; OKIMOTO, F. S.; LOGSDON, N. B.;
BRAZOLIN, S.; LANA, É. L. *Manual de projeto e construção de pontes de madeira.*
São Carlos: Suprema, 2006. ISBN 85-98156-19-1.
**Chave BibTeX:** `CALIL2006` — já cadastrada em
[paper/final/references.bib](../../paper/final/references.bib) e citada em
[02_methodology.tex](../../paper/final/02_methodology.tex) (Eq. `eq:mgk`).

> ⏳ **Dados bibliográficos resolvidos; conteúdo ainda não lido.** Estava na
> pasta e não constava da sua lista, mas é a referência brasileira canônica de
> pontes de madeira — e Calil Junior é coautor de [Cheung2017](Cheung2017.md).

---

## Por que importa

Três usos prováveis, todos de alto valor:

1. **Validação do dimensionamento.** Se o manual traz exemplo numérico resolvido de
   ponte com longarinas roliças + tabuleiro, ele serve de caso de verificação para a
   rotina do ReliaBridge — que é hoje a lacuna apontada em
   [Miluccio2026_QBridge](Miluccio2026_QBridge.md) (falta seção de validação) e o
   item B6 da auditoria (falta teste de regressão).
2. **Valores de referência** para densidade, resistências e, principalmente,
   **variabilidade dimensional de madeira roliça** — o que sustentaria a escolha de
   $\rho$ na otimização robusta (hoje 5% sem fonte) e os COVs de `confia_mad.py`.
3. **Prática construtiva**: espaçamentos usuais de longarinas, tipos de tabuleiro,
   detalhes de ligação. Serve para justificar os intervalos das variáveis de projeto
   da Tabela de intervalos do rascunho, hoje aparentemente arbitrários.

## A ler, com prioridade

- [ ] Capítulo de dimensionamento de longarinas roliças → exemplo numérico para validação
- [ ] Tabelas de propriedades e de variabilidade da madeira roliça → justificar $\rho$ e COVs
- [ ] Espaçamentos e disposições construtivas usuais → justificar $x^{(L)}$ e $x^{(U)}$
- [ ] Confirmar dados bibliográficos completos para o `.bib`
