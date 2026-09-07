# Revistas alvo

## Comparação

| | **Structures** (Elsevier) | **Structural and Multidisciplinary Optimization** (Springer) |
|---|---|---|
| Foco | Engenharia estrutural aplicada, ampla | Métodos e teoria de otimização estrutural |
| Valoriza | Estudo de caso real, aplicabilidade, validação experimental | Rigor da formulação, indicadores de qualidade, comparação de algoritmos |
| Tolera | Uso de algoritmo consagrado sem contribuição algorítmica | Menos: espera novidade metodológica ou benchmark sólido |
| Norma nacional | Aceitável se bem contextualizada | Precisa ser abstraída — o problema tem que interessar fora do Brasil |
| Idioma | Inglês | Inglês |

## Diagnóstico do trabalho atual

O artigo hoje é **muito mais um artigo de *Structures*** do que de SMO:

- A contribuição é a **plataforma aplicada** + o acoplamento com a NBR 7190, não um
  método de otimização novo. NSGA-II é usado como caixa-preta (pymoo).
- Faltam os elementos que SMO cobra por padrão: indicador de hipervolume,
  comparação entre algoritmos, análise de convergência, formulação probabilística
  formal.
- A robustez, como está formulada (perturbação uniforme de 5% + média), é a versão
  mais simples possível de otimização robusta. Em SMO isso seria considerado
  incremental.

## Dois caminhos

### Caminho A — *Structures* (menor risco)
Manter o escopo atual. Investir em **R1.6** (estudo de caso com ponte real) e
**R2.3** (estudo paramétrico + ábacos de pré-dimensionamento). Fechar todas as
caixas `\sugestao`. Enfatizar a plataforma de acesso livre como entregável.

Perfil resultante: *"Uma plataforma de projeto automatizado e otimização robusta
para pontes de madeira roliça em estradas vicinais, validada contra projetos
executados."*

### Caminho B — SMO (maior risco, maior retorno)
Exige **R2.1** (acoplar confiabilidade → RBRDO), **R2.2** (comparar algoritmos) e
**R1.4** (hipervolume/convergência). Reformular o problema em termos genéricos
(vigas circulares + tabuleiro sobre apoios múltiplos), com a NBR 7190 como
*instanciação* das restrições, não como o objeto do artigo.

Perfil resultante: *"Otimização robusta baseada em confiabilidade de sistemas
viga-tabuleiro com incerteza geométrica: formulação, custo da robustez e aplicação
a pontes de madeira roliça."*

## Evidência decisiva: *Structures* publica exatamente este gênero

O Q-BRIDGE ([Miluccio2026](notas/Miluccio2026_QBridge.md)) saiu em ***Structures*
v. 91, 2026** — é um artigo de **plataforma computacional aberta** para pontes,
com verificação normativa determinística + módulo probabilístico, validado contra
um ensaio de prova de carga e aplicado a uma ponte real.

Isso resolve a dúvida de encaixe: o ReliaBridge é o mesmo gênero, na mesma revista,
no mesmo ano. Vale seguir a estrutura deles (ver o fichamento), com dois ajustes que
o rascunho não tem hoje:

- uma seção curta **"Research significance"** após a introdução;
- uma seção de **validação** própria — Q-BRIDGE valida contra ensaio experimental,
  e o ReliaBridge não valida contra nada.

Sem risco de parecer derivativo: Q-BRIDGE é *avaliação de ponte existente* em
concreto sob Eurocode, sem otimização. Mas **citá-lo é obrigatório**.

## Recomendação

**Caminho A**, agora com mais convicção. O material de campo em
[paper/pedro/imgs/](../paper/pedro/imgs/) sugere que o estudo de caso real está ao
alcance, e é a alavanca mais barata para um artigo forte. Se R2.1 sair bem, o
trabalho pode ser cindido em dois artigos — o aplicado em *Structures* e o
metodológico em SMO.

Ordem de submissão sugerida: *Structures* como alvo primário; se houver rejeição
por escopo (e não por mérito), *Engineering Structures* ou *Journal of Building
Engineering*.

## Alternativas, se houver rejeição

- *Engineering Structures* (Elsevier) — mais seletiva que *Structures*, mesmo perfil.
- *Journal of Building Engineering* (Elsevier) — aceita bem plataforma + estudo de caso.
- *Construction and Building Materials* — só se o foco migrar para o material.
- *Advances in Engineering Software* — encaixe bom se a plataforma for o produto central.
