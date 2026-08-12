# Linha nova — ciência de dados + otimização

**Status:** ideia declarada em 2026-08-12, ainda sem escopo fechado.
**Origem:** o usuário quer explorar o modelo das 40 espécies como **problema de dados**,
não só como estudo paramétrico.

Este arquivo existe para que a ideia não se perca e para que uma IA futura não a
reinvente do zero. **Nada aqui está decidido.**

---

## Por que faz sentido

O Artigo 2 já produz, ou vai produzir, um conjunto de dados que não existe na literatura:

- **40 espécies × 5 propriedades medidas** (ρ, f_c0, f_m, f_v0, E_M0)
- **× 4 vãos × 2 (ou 3) bases de propriedades** de saída da otimização
- cada saída com **5 variáveis de projeto** (d, b_w, h, esp_long, esp_tab), volume,
  utilização das 6 restrições e a verificação governante

São 320–480 projetos ótimos rotulados. Isso é um dataset, não uma tabela de resultados.

## Perguntas que o dataset permite responder

Em ordem aproximada de retorno por esforço:

1. **Meta-modelo / surrogate.** Treinar um regressor (v_total, d_ótimo) = f(L, ρ, f_m,k,
   f_v0,k, E) sobre as rodadas. Se ele acertar bem, vira um **ábaco contínuo** — o
   projetista entra com as propriedades reais da espécie disponível e sai com a
   pré-dimensão, sem rodar NSGA-II. Isso é diretamente a "alternativa ao enquadramento
   em classe" que o Artigo 2 recomenda mas não entrega.
2. **Qual propriedade realmente comanda o projeto.** Já há Sobol na plataforma sobre as
   *variáveis de projeto*. Falta o Sobol sobre as **propriedades do material**, que é o
   que sustenta quantitativamente a tese "rigidez importa mais que resistência" — e a
   sensibilidade deve migrar com o vão. Este é o resultado mais alinhado ao Artigo 2.
3. **Classificação induzida por dados.** Em vez de aceitar D20–D60, **descobrir** os
   agrupamentos: quantas classes, e indexadas por qual propriedade, minimizam o erro de
   projeto sobre as 40 espécies? Isso responde diretamente a §4.3 ("a limitação está no
   número de classes?") de forma construtiva em vez de crítica. É o artigo mais
   ambicioso da série.
4. **Otimização em duas camadas.** Camada externa escolhe a espécie e a classe; interna
   dimensiona. Objetivo conjunto: volume, custo, disponibilidade regional.

## O que ainda falta decidir

- **Isto é seção do Artigo 2, ou artigo 3?** Recomendação: **artigo 3.** Enfiar o
  surrogate no Artigo 2 dilui a tese e reabre a acusação de "apresentação de ferramenta"
  que a decisão D-01 existe justamente para evitar.
- **Dataset é suficiente?** 40 espécies é pouco para treinar qualquer coisa não trivial.
  Pode ser preciso **amostrar o espaço de propriedades sinteticamente** (LHS sobre
  faixas plausíveis de ρ, f_m, E) em vez de usar só as 40 espécies reais, e usar as 40
  como conjunto de validação. Esta é provavelmente a decisão de projeto mais importante
  da linha.
- **Qual biblioteca.** O repositório já tem `pymoo` e `UQpy`. Acrescentar `scikit-learn`
  é natural; evitar deep learning, que não se justifica nessa escala de dados e é difícil
  de defender em revista de estruturas.

## Desdobramento irmão: confiabilidade (β por espécie)

Já registrado como "extensão futura" e **fora do caminho crítico** dos Artigos 1 e 2.

Com os desvios-padrão por espécie — ou com CoV do JCSS Probabilistic Model Code — dá para
calcular o **índice de confiabilidade β de cada espécie dentro da sua classe** e mostrar
que a classe produz pontes com **probabilidades de falha diferentes**. É esse trabalho,
não o Artigo 2, que teria chance real no Journal of Bridge Engineering.

**Detalhe metodológico decidido (D-12):** usar **um mesmo CoV para todas as espécies** é
preferível a CoVs individuais, porque isola o efeito do enquadramento — o espalhamento de
β passa a ser atribuível puramente ao erro da classe. O fator 0,70 da NBR implica
**CoV ≈ 22 %** se o característico for o percentil 5 % de uma lognormal.

Há `confia_mad.py` no repositório, que é o ponto de partida.

## Relação entre as três linhas

```
Artigo 1 (Matéria) ──► a plataforma existe e é confiável
        │
        └─► Artigo 2 (Eng. Structures) ──► o enquadramento por resistência erra a rigidez
                    │
                    ├─► Artigo 3 (ciência de dados) ──► então indexe por outra coisa: eis como
                    │
                    └─► Artigo 4 (confiabilidade / JBE) ──► e a classe não entrega β uniforme
```

Cada um só faz sentido depois do anterior. **Não começar o 3 antes de o 2 ter a
`tab:governante` preenchida** (P-12), porque é ela que diz se a rigidez de fato comanda.
