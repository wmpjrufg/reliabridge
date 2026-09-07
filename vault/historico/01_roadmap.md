# Roadmap até a submissão

Ordenado por dependência e por retorno científico. Cada item indica o artefato que
produz no paper.

---

## Fase 0 — Bloqueadores (nada avança sem isso)

**Atualização 2026-07-25:** R0.1 e R0.2 já foram corrigidos no código (ver
`00_auditoria_codigo.md`). **R0.3 (sinal de $f_2$) segue em aberto** e é hoje o
único bloqueador real restante — sem ele, o argumento de "objetivos antagônicos"
do paper não se sustenta (ver B3). O texto do LaTeX já foi atualizado com a nova
estrutura de resultados e placeholders (`\fill{...}`), prontos para receber os
números assim que as análises forem rodadas — mas decidir R0.3 antes de rodar
tudo evita ter que refazer as fronteiras duas vezes.

| # | Tarefa | Ref. auditoria | Artefato | Status |
|---|---|---|---|---|
| ~~R0.1~~ | ~~Implementar a perturbação real no `_evaluate`~~ | B1 | Todos os resultados | ✅ feito |
| ~~R0.2~~ | ~~Corrigir o mapeamento de colunas do DataFrame do NSGA-II~~ | B2 | Tabelas de geometria ótima | ✅ feito |
| **R0.3** | **Decidir e corrigir o sinal/definição de $f_2$** | B3 | Eq. `eq:f2`, todas as fronteiras | 🔴 pendente |
| R0.4 | Script único `reproduz_paper.py` com semente fixa | B6 | Reprodutibilidade | pendente |

Depois de R0.3, **todas** as figuras e tabelas do rascunho precisam ser
regeradas. As figuras já reutilizadas no LaTeX (`z_fronteira_eficiente*.png`)
estão marcadas com `\fill{[REGENERAR...]}` na legenda para não passar batido.

---

## Fase 1 — Resultados que fecham as caixas `\sugestao` existentes

As caixas vermelhas já no LaTeX, priorizadas:

### R1.1 — Custo da robustez: fronteira para $\rho \in \{0; 2{,}5; 5; 10\}\%$
`\sugestao` em [02_methodology.tex:177](../paper/final/02_methodology.tex#L177)
Fronteiras sobrepostas + tabela do acréscimo percentual de área. **É o resultado
que justifica o título do artigo** — sem ele não há "otimização robusta", só
otimização. Ver `experimentos/E1_custo_robustez.md`.

### R1.2 — Média vs. pior caso na agregação
`\sugestao` em [02_methodology.tex:179](../paper/final/02_methodology.tex#L179)
Barato (só muda `.mean()` por `.max()` nas restrições) e de alto valor: mostra que
a média deixa passar soluções que violam em ~50% das realizações.

### R1.3 — Validação Monte Carlo independente da robustez
`\sugestao` em [03_results.tex:176](../paper/final/03_results.tex#L176)
Pegar uma solução determinística e uma robusta de **mesma área**, aplicar $10^4$
perturbações de $\pm5\%$, reportar % de violação por restrição. É a prova empírica
direta do ganho. Ver `experimentos/E3_validacao_mc.md`.

### R1.4 — Hipervolume e convergência
`\sugestao` em [03_results.tex:126](../paper/final/03_results.tex#L126) e
[:128](../paper/final/03_results.tex#L128)
HV + *spacing* da fronteira; curva HV × geração para justificar $N_{gen}=400$.
O pymoo já traz `pymoo.indicators.hv.HV`; basta rodar com `save_history=True`
(hoje está `False` em [madeiras.py:1648](../madeiras.py#L1648)).
**Indicador de qualidade de fronteira é obrigatório em SMO.** Ver
`experimentos/E4_hipervolume.md`.

### R1.5 — Índices de Sobol
`\sugestao` em [03_results.tex:178](../paper/final/03_results.tex#L178)
Sensibilidade global das variáveis sobre as funções de estado limite. Conecta
diretamente com controle de qualidade na fabricação de madeira roliça — bom gancho
para a discussão. Usar `SALib` ou o módulo de sensibilidade do UQpy (já é
dependência).

### R1.6 — Estudo de caso real
`\sugestao` em [03_results.tex:180](../paper/final/03_results.tex#L180)
As pontes reais em [paper/pedro/imgs/](../paper/pedro/imgs/) (Rio do Braço, Três
Bocas, Mascarenhas de Morais) sugerem que já existe material de campo no grupo.
Confrontar consumo de material da solução otimizada com o projeto executado.
**Maior alavanca para *Structures***, que valoriza aplicação real.

### R1.7 — Relatório de utilização no apêndice
`\sugestao` em [appendices.tex:7](../paper/final/appendices.tex#L7)
Gráfico de barras de grau de solicitação por verificação, para uma solução da
fronteira. Fácil — a plataforma já emite o relatório.

---

## Fase 2 — Elevação de nível (o que separa "aceitável" de "bom periódico")

### R2.1 — Acoplar confiabilidade ao NSGA-II (RBRDO)
Ref. auditoria B4. Reconstruir `obj_confia` sobre a API atual de `madeiras.py`,
consertar `confia_mad.py`, e usar $\beta$ (via FORM, com Monte Carlo como
verificação) como segundo objetivo ou como restrição probabilística
$\beta \geq \beta_{alvo}$.

Isso transforma o artigo de "otimização multiobjetivo com perturbação determinística"
em **otimização robusta baseada em confiabilidade**, que é a classe de problema que
SMO publica. É o item de maior retorno e o de maior custo.

Ponto de atenção: FORM dentro do laço do NSGA-II com pop=500 × 400 gerações é
inviável direto. Alternativas: (a) metamodelo/kriging para $\beta$, (b) $\beta$
avaliado só nas soluções finais da fronteira (mais barato, menos ambicioso),
(c) reduzir pop/gerações e justificar com a curva de HV de R1.4.

### R2.2 — Comparação com outro algoritmo
NSGA-II sozinho é fraco como contribuição algorítmica. Comparar com NSGA-III ou
MOEA/D (ambos no pymoo, custo marginal quase zero) e reportar HV — inocula contra
o comentário "por que NSGA-II?".

### R2.3 — Ampliar o conjunto de casos
Duas pontes hipotéticas que diferem só no trem tipo é pouco. Variar o vão (5, 8,
12 m) e a classe de madeira gera um estudo paramétrico e permite propor
**ábacos/regras de pré-dimensionamento** — entregável de engenharia que revisores
de *Structures* gostam.

### R2.4 — Justificar os modelos probabilísticos
Os COVs *hardcoded* (0.10 / 0.20) precisam de fonte: JCSS Probabilistic Model
Code para madeira, ou literatura brasileira de madeira roliça. Sem referência,
é o primeiro alvo do revisor.

---

---

## Fase 2b — Itens que vieram da leitura das referências

Ver os fichamentos em [notas/](notas/).

### R2.5 — Seção "Research significance"
De [Miluccio2026](notas/Miluccio2026_QBridge.md). Seção curta e dedicada, logo após
a introdução, declarando a lacuna e o que o trabalho acrescenta. É padrão em
*Structures*. Custo: meia página de texto. Retorno: alto.

### R2.6 — Seção de validação
De [Miluccio2026](notas/Miluccio2026_QBridge.md). **O ReliaBridge não valida contra
nada hoje** — é a lacuna mais grave depois dos bugs. Sem ensaio disponível, três
caminhos combináveis:

- (a) verificar o dimensionamento contra exemplo numérico resolvido do manual do
  Calil Júnior ([Calil2006](notas/Calil2006.md)) — vira também o teste de regressão de B6;
- (b) confrontar com ponte executada (R1.6);
- (c) validar o FORM contra Monte Carlo (parte de R2.1).

### R2.7 — Figura de utilização por verificação
De [deMoraes2025](notas/deMoraes2025.md), Fig. 16: barras de *utilization capacity*
por verificação, com faixas >100% / 70–100% / ≤70%. Fecha a `\sugestao` de
[appendices.tex:7](../paper/final/appendices.tex#L7) e é barata — os dados já saem
do relatório da plataforma.

### R2.8 — Ábaco de pré-dimensionamento
De [deMoraes2025](notas/deMoraes2025.md), Fig. 19: eles ajustam
$h = 0{,}066L - 0{,}24$ a partir das soluções ótimas de vários vãos e entregam isso
como regra de projeto. Fazer o análogo — $d = f(L)$ para a longarina roliça — a
partir dos resultados de R2.3. **Entregável de engenharia com valor prático real**,
e o tipo de coisa que faz um artigo aplicado ser citado.

### R2.9 — Ancorar a robustez em evidência de campo
De [Deng2015](notas/Deng2015.md): "método imperfeito de projeto e construção" é
causa humana documentada de colapso de pontes. Converte o argumento de robustez de
conceitual para empírico, em duas frases na introdução. Ver o fichamento para o
cuidado de tom.

### R2.10 — Declaração de lacuna com fonte brasileira
De [Cheung2017](notas/Cheung2017.md): pontes de madeira no Brasil são projetadas sem
análise de confiabilidade porque a NBR 7190 não traz as premissas nem os índices.
**Conferir se a versão 2022 mudou isso** — o enquadramento da introdução depende da
resposta.

### R2.11 — Probabilidade de falha do sistema
De [Stefanidou2022](notas/Stefanidou2022.md): fragilidade de sistema em série, com
limites superior/inferior por correlação entre componentes. Aplicar às nossas 6
restrições — o número que interessa ao projetista é a probabilidade de violar
*qualquer* uma, não cada uma isolada. Entra direto na tabela de
[E3](experimentos/E3_validacao_mc.md).

---

## Fase 3 — Preparação editorial

- [ ] Decidir revista (ver `02_revistas_alvo.md`) e **traduzir para inglês** — nenhuma
      das duas aceita português.
- [ ] Adequar o LaTeX ao template da revista escolhida.
- [ ] Revisar a bibliografia: [references.bib](../paper/final/references.bib) tem só
      ~4,5 KB. Para *Structures*/SMO espera-se 40–60 referências, com peso em
      trabalhos internacionais recentes de otimização de pontes e de estruturas de
      madeira. Hoje o texto está muito ancorado em norma brasileira e literatura
      nacional.
- [ ] Publicar o código com DOI (Zenodo) e citar no *Data availability*.
- [ ] Preencher [declarations.tex](../paper/final/declarations.tex) (CRediT,
      financiamento, conflito de interesses).
- [ ] Consolidar autoria — o material vem de `pedro/`, `priscilla/` e do código.

---

## Sequência mínima recomendada

```
R0.1 → R0.2 → R0.3 → R0.4         (corrige a base — nada vale antes disso)
     → R1.1 → R1.2 → R1.3         (dá substância à palavra "robusta")
     → R1.4                        (satisfaz o revisor de otimização)
     → R2.6                        (validação — maior lacuna estrutural do artigo)
     → R1.6 + R2.3 → R2.8          (estudo de caso real + ábaco: o miolo aplicado)
     → R1.7/R2.7, R2.5, R2.9, R2.10 (itens baratos de texto e figura)
     → Fase 3
```

R2.1 (confiabilidade acoplada) fica fora da sequência principal: é o desvio para SMO.
Só entrar nele se houver folga de cronograma depois de R2.6.

## Itens baratos, alto retorno — se estiver com pouco tempo

Nesta ordem, sem depender de rodar otimização nenhuma: **R2.5** (research
significance), **R2.9** e **R2.10** (dois parágrafos de introdução com fonte),
**R2.7** (figura de utilização). São horas, não semanas, e melhoram visivelmente a
recepção editorial.
