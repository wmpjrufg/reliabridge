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

### D-11 · Semente distinta na validação de Monte Carlo
A semente das perturbações da validação (§4.3.5 do Artigo 1) tem de ser **diferente** da
usada na otimização. Reaproveitar os mesmos multiplicadores faz a validação validar a si
mesma.

### D-12 · Um único CoV para todas as espécies na linha de confiabilidade
Preferível a CoVs individuais **porque isola o efeito do enquadramento**: o espalhamento
de β passa a ser atribuível puramente ao erro da classe. Ver `07_linha_ciencia_de_dados.md`.
