# Fichamento: Stefanidou et al. (2022)

**Referência completa:** STEFANIDOU, S. P.; PARASKEVOPOULOS, E. A.; PAPANIKOLAOU,
V. K.; KAPPOS, A. J. An online platform for bridge-specific fragility analysis of
as-built and retrofitted bridges. *Bulletin of Earthquake Engineering*, v. 20,
p. 1717–1737, 2022.
**DOI:** 10.1007/s10518-021-01299-3
**Chave BibTeX:** `Stefanidou2022`
**Plataforma:** www.thebridgedatabase.com

---

## 1. Problema tratado

Plataforma online ("toolkit", não só "manager tool") para análise de fragilidade
sísmica específica de pontes, novas e reforçadas, combinando banco de dados de curvas
genéricas com software ad-hoc para derivação de curvas específicas.

## 2. Formulação

- **Arquitetura "two-track":** (a) selecionar curva genérica de um catálogo por
  tipologia; (b) derivar curva específica rodando o software online.
- Metodologia **baseada em componentes**: fragilidade de pilares, aparelhos de apoio
  e encontros, combinadas em fragilidade de sistema **em série**, com limites
  superior e inferior (componentes não correlacionados vs. totalmente correlacionados).
- Modelo de ponte **totalmente parametrizado**, com entrada de geometria pelo usuário.
- Implementada em Python + OpenSeesPy.
- Três opções alternativas para os limiares de estado limite (listas de literatura,
  relações fechadas, ou pushover inelástico rodado online).

## 3. Como validam

Dois estudos de caso, com pontes de sistemas estruturais e propriedades diferentes.
Sem validação experimental — **o mesmo caso do ReliaBridge**. Precedente útil de que
dá para publicar bem sem ensaio, desde que os casos sejam bem escolhidos e
contrastantes.

## 4. O que é diretamente aproveitável

- **Fragilidade de sistema em série.** Nós temos 6 restrições avaliadas
  independentemente; a probabilidade de o *sistema* violar qualquer uma delas é o
  número que interessa ao projetista. É exatamente a linha "qualquer uma (sistema)"
  do experimento [E3](../experimentos/E3_validacao_mc.md). Os limites
  superior/inferior por correlação dão um jeito rigoroso e barato de reportar isso.
- **A plataforma como objeto do artigo.** Eles dedicam a Seção 2 inteira à interface
  web e à estrutura de menus. Legitima o que o rascunho já faz na Seção 3.1, mas
  sugere ir além de duas capturas de tela.
- **Interatividade / contribuição de usuários** como diferencial declarado. O
  ReliaBridge poderia declarar algo análogo (código aberto, aceita contribuição,
  extensível a outras normas).

## 5. O que **não** copiar

O domínio (fragilidade sísmica) está longe do nosso. Serve como referência de
**gênero de artigo de plataforma**, não de método. Citar em uma frase da introdução,
junto com Q-BRIDGE, ao posicionar "plataformas online para análise de pontes".

## 6. Onde nos diferenciamos

Avaliação sísmica de pontes existentes × projeto otimizado de pontes novas.
Sem otimização, sem robustez.
