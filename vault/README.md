# Vault ReliaBridge — contexto de pesquisa

> **Se você é uma IA lendo isto pela primeira vez: leia este arquivo inteiro antes de
> responder qualquer coisa sobre o projeto.** Ele existe para que qualquer assistente
> (Claude, GPT, Gemini, Copilot, o que for) recupere o estado da pesquisa sem precisar
> reler o repositório inteiro nem refazer perguntas já respondidas.

**Última atualização:** 2026-09-07

---

## 1. O que é este projeto, em um parágrafo

ReliaBridge é uma plataforma computacional (Python + Streamlit) para dimensionamento
e otimização de **pontes de madeira roliça para estradas vicinais**, seguindo a ABNT
NBR 7190:2022. O modelo estrutural é integralmente paramétrico e está acoplado a uma
rotina de **otimização robusta multiobjetivo** (NSGA-II via `pymoo`), com análise de
sensibilidade global de Sobol (`UQpy`). Em torno dessa plataforma existe uma linha de
pesquisa com **dois artigos em redação** e **desdobramentos planejados**.

## 2. Mapa dos arquivos

| Caminho | O que é |
|---|---|
| `app.py`, `pages/` | Interface Streamlit da plataforma |
| `madeiras.py` | Núcleo de cálculo (o arquivo grande, ~158 kB) |
| `confia_mad.py` | Rotinas de confiabilidade |
| `beam_data.xlsx` | Dados de vigas |
| `paper/materia/` | **Artigo 1** — Revista Matéria (PT). Apresenta a plataforma |
| `paper/engstruct/` | **Artigo 2** — Engineering Structures. Erro de enquadramento em classe |
| `paper/priscilla/` | Dissertação da Priscilla |
| `paper/pedro/` | Trabalho do Pedro (formato Elsevier) |
| `paper/modelo/` | Template LaTeX base, não é conteúdo |
| `rodar_lote.py` | Roda a matriz de simulações sem a interface. Ver `09_lote_headless.md` |
| `simulacaoes_/` | Saídas das execuções, uma pasta por célula |
| `vault/` | **Este contexto.** Estado, decisões e pendências |

## 3. Índice do vault

| Arquivo | Conteúdo |
|---|---|
| [`01_paper_materia.md`](01_paper_materia.md) | Artigo 1: estado, configuração, pendências |
| [`02_paper_engstruct.md`](02_paper_engstruct.md) | Artigo 2: estado, tese, pendências |
| [`03_dados_40_especies.md`](03_dados_40_especies.md) | Os dados e todos os números já calculados (conferidos) |
| [`04_decisoes.md`](04_decisoes.md) | Decisões tomadas e o porquê — **não relitigar** |
| [`05_revisao_critica.md`](05_revisao_critica.md) | Furos identificados no caminho escrito, por gravidade |
| [`06_proximos_passos.md`](06_proximos_passos.md) | Fila de trabalho, em ordem |
| [`07_linha_ciencia_de_dados.md`](07_linha_ciencia_de_dados.md) | Direção nova: ciência de dados + otimização |
| [`08_preenchimento_materia.md`](08_preenchimento_materia.md) | Artigo 1: o que já foi preenchido com as 20 simulações, o que falta e a auditoria dos dados de entrada |
| [`09_lote_headless.md`](09_lote_headless.md) | Rodar a matriz por script em vez da interface: uso, limites recuperados e reprodutibilidade |
| [`10_solucao_ideal_fronteira.md`](10_solucao_ideal_fronteira.md) | Como escolher a solução de projeto a partir da fronteira eficiente |
| [`CHANGELOG.md`](CHANGELOG.md) | Histórico de evolução do trabalho |
| [`notas/`](notas/) | Fichamento de leitura, um arquivo por trabalho (`notas/_template_leitura.md` para novos) |
| [`refs/`](refs/) | Índice das referências base e `entradas.bib`. **Os PDFs ficam só na máquina**, fora do git, por direito autoral das editoras |
| [`historico/`](historico/) | Material de julho de 2026, de quando o projeto era um artigo só em `paper/final/`. Superado, mas o raciocínio serve — ler com a data em mente |

## 4. Convenções que valem em todo o repositório

- **Marcadores de pendência no LaTeX.** `\tofill{...}` é um número ou frase curta a
  substituir (sai em vermelho no PDF). O ambiente `fillblock` é um bloco de instrução
  do que escrever ali — apague o bloco inteiro e escreva o parágrafo no lugar.
  Enquanto houver vermelho no PDF, o texto não está pronto.
- **Objetivo da otimização é volume em m³**, nunca área. "m²" em qualquer lugar é
  resíduo de versão antiga.
- **Há MiKTeX instalado nesta máquina** (`latexmk -pdf main.tex` funciona), então
  alterações em `.tex` podem e devem ser validadas por compilação antes de subir para o
  Overleaf. Atenção: o Linux do Overleaf é *case-sensitive* nos nomes de figura, o
  Windows não — conferir maiúsculas/minúsculas.

## 5. Como manter este vault vivo

Ao concluir qualquer etapa relevante, atualize:
1. o arquivo do artigo correspondente (seção "Estado atual"),
2. `06_proximos_passos.md` (risque o que saiu, promova o que entrou),
3. `CHANGELOG.md` (uma linha com data).

Não duplique conteúdo entre arquivos: cada fato mora em um lugar só, e os outros
referenciam.
