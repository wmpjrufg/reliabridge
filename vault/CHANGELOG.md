# Changelog da pesquisa

Uma linha por evento relevante. Novidades no topo.

---

## 2026-09-08

- ✅ **Apêndice A escrito por completo; Apêndice B removido (D-16).** Validação genuína
  e independente: script à parte, sem importar `madeiras.py`, reimplementando as
  fórmulas documentadas — bateu com a avaliação nominal da plataforma a 1e-7. No
  processo, achado e corrigido um bug no MEU script (não no código do projeto: usei por
  engano o `h` do tabuleiro em vez do `d` da longarina no cortante), e uma equação real
  do código (`aux_ci = 1+0,75(CIV-1)`) que nunca tinha sido documentada em
  `03_methodology.tex` — adicionada como `eq:civaux`.
- ⚠️ **Descoberta importante para qualquer conferência manual futura:** os valores de
  g1-g6 na fronteira publicada são a MÉDIA sobre as 30 perturbações robustas, não o
  ponto nominal. Comparar "na mão" contra a Tabela 6 diretamente dá números errados por
  até 15%; o alvo certo é a avaliação nominal (sem a média), chamando
  `calcular_objetivos_restricoes_otimizacao` uma vez.
- **Achado honesto registrado no próprio apêndice:** a solução intermediária escolhida
  viola $g_6$ em 4,7% no ponto nominal, mas a média robusta (-5,5%) é viável — ilustra em
  miniatura o mesmo mecanismo do custo da robustez (§4.3.3).
- **Financiamento preenchido em `declarations.tex`**: CAPES, processo 88881.914003/2023-01.
- Corrigidos 7 `Overfull \hbox` no apêndice (equações duplas com `\qquad` que estouravam
  a coluna — cada uma virou dois `equation*` separados) e a tabela de síntese (fonte
  reduzida, como as demais tabelas largas do artigo).
- PDF compila limpo em 43 páginas. **Vermelho restante: só `title_authors.tex`** (e-mail
  institucional/ORCID/CEP dos autores — só eles preenchem) **e os 4 `	ofill` de
  `preamble.tex`**, que são as definições dos comandos, não pendências reais.

- ✅ **Custo da robustez fechado — §4.3.3 e o bloco de conclusão correspondente.**
  Criados `gerar_casos_robustez.py` (monta `robustez_casos.xlsx`, 4 linhas: só a C-13 em
  ρ = 0/2,5/5/10 %, D-06) e `rodar_lote_robustez.py` (roda o lote, grava em
  `simulacaoes_/custo_robustez_C13/`). As 4 rodadas levaram 57 s / 82 s / 107 s / 157 s
  (crescente com ρ; a maior parte do salto ρ=0→2,5 vem de N_c colapsar para 1 quando
  ρ = 0). `gerar_figuras_materia.py` ganhou `figura_custo_robustez()`, que sobrepõe as 4
  fronteiras em PT e EN.
  **Achado:** o custo da robustez não é uniforme na fronteira. Na solução de menor
  volume (extremo econômico): +0,4 % (ρ=2,5%), +2,8 % (ρ=5%), +10,1 % (ρ=10%) — mais que
  triplica de 5% para 10%. Em soluções intermediárias (3 níveis pareados de flecha): em
  média +0,3 %, +6,1 %, +6,3 % — satura entre 5% e 10%. Ou seja, a robustez penaliza
  desproporcionalmente as soluções mais coladas nas restrições ativas, que são
  justamente as que a otimização determinística produz. `tab:custo_robustez`, a
  discussão de §4.3.3, o bloco de conclusão e uma frase no resumo foram preenchidos com
  esses números. PDF compila limpo em 39 páginas. **Único vermelho restante: os dois
  apêndices** (conferência manual e memorial).
- ⚠️ **Achado um typo de path ao rodar o lote da robustez**: o destino default do script
  saiu como `simulacoes_/...` (faltando um "a") em vez do padrão do projeto
  `simulacaoes_/...`. Os resultados foram gerados corretamente, só na pasta errada;
  movidos para `simulacaoes_/custo_robustez_C13/` e o script corrigido. Vale conferir
  `git status` depois de rodar qualquer lote novo para pegar esse tipo de coisa cedo.

- **D-15: Artigo 1 fica na Revista Matéria, ponto final.** O Wanderlei perguntou se o
  artigo, como está, serviria para a *Structures*; a resposta foi que não é questão de
  polimento, e sim de gênero — apresentação de ferramenta + ábacos, sem achado
  generalizável, sem comparação com literatura, sem validação independente, exatamente o
  perfil que a D-01 já tinha identificado como não aceito pela *Structures*. Duas rotas
  foram oferecidas (manter como está e deixar a ambição internacional para o Artigo 2; ou
  internacionalizar este conteúdo fechando o custo da robustez + validação real) e o
  Wanderlei escolheu a primeira — não há ponte executada disponível para validar. Não
  relitigar.

## 2026-09-07

- **Introdução do Artigo 1 reforçada com literatura internacional recente**, a pedido do
  usuário, no estilo dos papers de referência do gênero (Buttignol/de Moraes 2025 e
  Miluccio/Parisi 2026, ambos já fichados em `vault/notas/`). Quatro citações novas, todas
  conferidas via Crossref antes de entrar no `.bib`:
  - **de Moraes & Buttignol (2025)**, *Structural Concrete* — projeto paramétrico
    automatizado de pontes de concreto, exemplo do mesmo paradigma de "projeto
    inteligente" aplicado a pontes;
  - **Miluccio, Losanno & Parisi (2026)**, *Structures* (já estava no `.bib`, sem
    nenhuma citação no texto até agora — corrigido) — plataforma computacional aberta
    de avaliação estrutural, mesmo gênero de artigo;
  - **Cheung et al. (2017)**, *Ambiente Construído* — ponte de madeira protendida
    brasileira em serviço com índice de confiabilidade abaixo do recomendado sob parte
    da frota real, evidência de campo que reforça a motivação da robustez;
  - **Moraes et al. (2022)**, *Rev. IBRACON Est. Mat.* — o DOI que o usuário trouxe
    (10.1590/S1983-41952022000600006). É trabalho do próprio Wanderlei com o Matheus
    H. M. de Moraes (coautor do Artigo 2): otimização de vigas de concreto para reduzir
    CO2. Citado no parágrafo de descarbonização.
  Acrescentado ainda um parágrafo com a lacuna explícita: a literatura de "projeto
  inteligente" em pontes é predominantemente de concreto; a extensão a madeira roliça,
  com sua variabilidade dimensional, é o que este trabalho preenche. PDF compila limpo
  em 37 páginas, sem warning de bibliografia. **Correção do usuário:** dissertação
  (`Moraes2023`) removida da introdução — regra do projeto é citar só artigo publicado,
  não teses/dissertações. A entrada permanece no `.bib`, sem uso, como já estava antes.

- ✅ **Matriz reprocessada com `a = 1,5 m` e o Artigo 1 inteiramente refeito.** As 20
  células rodaram em 10,2 min (30,7 s por célula: 24,4 s de NSGA-II e 5,9 s de Sobol),
  todas com `status = ok`, 50 soluções e Sobol executada. Auditoria confirma `a = 1,5` e
  os demais parâmetros fixos nas saídas; o volume mínimo subiu nas 20 células (+10,9 % em
  média), que é a direção esperada. Resumo, §4, §5, todas as tabelas e todas as figuras
  refeitos; PDF limpo em 36 páginas. O tempo médio fecha o `	ofill` que faltava na
  `tab:nsga2` e na conclusão.
- **Figuras agora em PT e EN.** `gerar_figuras_materia.py` produz as oito figuras nos dois
  idiomas: português em `figuras/` e inglês em `figuras/en/`, com os mesmos nomes, para
  que a versão em inglês só precise acrescentar `en/` ao `\graphicspath`.
- **Como os achados mudaram com o `a` correto:** a flecha e o cisalhamento continuam sem
  governar nenhuma célula, mas agora a longarina governa 12 e o tabuleiro 8 (antes era
  13 do tabuleiro); no vão de 3 m a saturação no diâmetro mínimo passa a valer só de D40
  para cima, e a redução D20→D60 sobe de 5,1 % para 23,5 %; o expoente da lei de potência
  cai de 1,84 (D20) a 1,37 (D60); e a matriz ficou integralmente monotônica, sem o empate
  D30/D40 no vão de 4 m que existia antes.
- **`_vault/` e `vault/` unificados.** Só existe `vault/`, versionado. As notas de leitura
  e o índice de referências vieram para `vault/notas/` e `vault/refs/`; o material de
  julho, escrito quando o projeto era um artigo só em `paper/final/` e mirava
  *Structures*/SMO, foi para `vault/historico/` com um README explicando o que ainda vale.
  **Os PDFs das editoras continuam fora do git** (`vault/refs/*.pdf` no `.gitignore`),
  como mandava a nota original — o índice e o `.bib` seguem versionados.
- **Lote do Artigo 2 preparado** — `gerar_casos_engstruct.py` monta `engstruct_casos.xlsx`
  (320 casos = 40 espécies × 4 vãos × 2 bases) lendo as espécies direto de
  `tabelas/tab_especies.tex`, e `rodar_lote_engstruct.py` executa. Sem Sobol, ~23 s por
  rodada, cerca de **2 h** o lote todo. **Por decisão do autor, os parâmetros fixos são os
  mesmos do Artigo 1** — a única coisa que muda entre os dois estudos é a faixa de vãos, e
  as propriedades das espécies, que são experimentais e ficam preservadas. A `tab:vaos` de
  `engstruct/03_methodology.tex` trazia `p_gk` = 1 kPa, umidade 1 e carregamento
  permanente, e foi corrigida para 0,1 kPa, umidade 3 e média duração.
- **Indício a favor da tese do Artigo 2:** em três casos de teste, `E05_L10_esp`
  (Angelim-pedra, 10 m) é governado pela **flecha**, enquanto os de 3 m são governados por
  flexão. É a migração que o passo 4 da ordem de execução manda confirmar. Indício, não
  resultado — mas afasta o cenário "a flecha nunca governa".
- **`rodar_lote.py` ganhou `--filtro`**, que casa por substring no id. É o que permite
  rodar só um vão (`--filtro _L03_`) ou só uma base (`--filtro _esp`) do lote do Artigo 2.
- **Lote headless criado** — `rodar_lote.py` (script) sobre `batch_pre_sizing.py`
  (módulo). Roda o
  mesmo caminho de cálculo da interface a partir de uma planilha com uma linha por
  simulação, gravando os mesmos artefatos e o zip no formato original. Substitui rodar o
  Streamlit 20 vezes à mão. `pages/pre_sizing.py` ficou intocado. Detalhes em
  `09_lote_headless.md`.
- **Limites de busca das 20 execuções recuperados por inversão** das colunas `g_esp`
  (erro 3e-16): `d` 30–150, `bw` 5–60, `h` 5–60, `esp_long` 30–200, `esp_tab` 2–5 cm.
  `bw_max` e `h_max`, que não aparecem em nenhuma restrição gravada, saíram por
  impressão digital das 6 primeiras gerações.
- ⚠️ **Reprodutibilidade tem limite entre máquinas.** O modelo reproduz os valores
  gravados nas 20 células com erro de 1e-14 (precisão de máquina), mas re-rodar a C-13
  com as entradas originais bate só até a geração 6 e depois diverge: a fronteira sai
  equivalente, não idêntica (`vmin` 3,935 contra 3,991). Alguns ULP invertem uma
  comparação de dominância e a busca segue por outro caminho. **Reprocessar muda os
  números do artigo mesmo mantendo tudo igual** — vale declarar as sementes no texto.
- **Descoberto que os arquivos soltos em `simulacaoes_/simulacao_C_XX/` não são os
  artefatos originais**: o `pre_sizing_results_optimized.xlsx` foi editado à mão nas 20
  células (coluna "G" e linhas de agregado). O zip é a única referência confiável, e o
  lote nunca escreve nessas pastas.
- **Planilha `batch_pre_sizing_casos.xlsx` gerada** com as 20 células e `a = 1,5 m`,
  pronta para o reprocessamento.
- **Custo medido:** uma célula completa leva 147 s (116 s de NSGA-II + 28 s de Sobol), o
  que põe o lote das 20 em torno de 50 minutos. O NSGA-II domina, não a Sobol.

## 2026-09-06

- **Artigo 1 (Matéria) preenchido com as 20 simulações** (ρ = 5 %, em `simulacaoes_/`).
  Resumo, `tab:solucoes_ref`, utilização, hipervolume, Sobol, estatística descritiva,
  `tab:resultados_matriz`, ábacos e três dos cinco blocos de conclusão. PDF compila
  limpo em 37 páginas. Detalhamento em `08_preenchimento_materia.md`.
- **Três achados contrariam o roteiro** — ⚠️ obsoletos, serão refeitos: a flecha não
  governa nenhuma célula (o tabuleiro governa 13 das 20); no vão de 3 m tudo satura no
  diâmetro mínimo de 30 cm e a classe deixa de importar (só 5,1 % de D20 a D60); e
  nenhuma célula deu inviável, nem a C-16 (6 m + D20).
- 🔴 **A auditoria dos dados de entrada achou um erro real: `a = 2,0 m` estava errado, o
  correto é 1,5 m** (D-13). O valor vinha do preset `VEICULOS_PADRAO` de
  `pages/pre_sizing.py`. `a` é o espaçamento **longitudinal** entre os três eixos — a
  fórmula da flecha, `b = (L − 2a)/2`, só fecha assim — e não a bitola transversal de
  2,00 m. **17 das 20 soluções ficam inviáveis** sob o valor correto: a matriz será
  reprocessada pelo aluno e todo o preenchimento refeito. Já corrigidos o preset do
  código e a `tab:parametros`; resumo, §4 e §5 marcados em vermelho como provisórios.
- **Conferir junto no reprocessamento:** o `φ = 0,60` usado contra 0,80 no texto original
  (Tabela 20 da NBR 7190-1; impacto pequeno, mexe só em `f₂`); e a inconsistência entre o
  `4a` do momento e o `3a` do cortante e da reação, que **importa para o Artigo 2**.
- O resto do desenho experimental está correto: variam só o vão e as cinco propriedades
  de classe, as outras 18 colunas são constantes nas 20 células, e as propriedades batem
  com a `tab:classes_madeira`.
- **D-14: Monte Carlo sai do Artigo 1.** Removidas a §4.3.2 (comparação com amostragem
  aleatória) e a §4.3.5 (validação por simulação independente), com tabelas, figuras e o
  bloco de conclusão correspondente — o algoritmo já foi validado e funciona. As
  subseções seguintes foram renumeradas (custo da robustez: 4.3.4 → **4.3.3**). D-11
  revogada. PDF passou a 36 páginas, compila limpo. **O custo da robustez continua no
  artigo** e segue pendente.
- **Figuras novas:** `utilizacao_C13.png` e os três ábacos. `Inicio.png` renomeado para
  `inicio.png` (quebraria no Overleaf, que é case-sensitive).
- **MiKTeX está instalado nesta máquina** — `.tex` agora pode ser validado por
  compilação local. Nota corrigida no `README.md` do vault.

## 2026-08-12

- **Resumo do Artigo 2 reescrito** (`abstract_keywords.tex`). Quatro mudanças de fundo:
  (1) abre com o problema geral — normas indexam classes por uma propriedade e tabelam
  as demais, o concreto faz igual com f_ck → E_cm — para ficar legível aos leitores de
  ES que não são de madeira; (2) a pergunta ("a partir de que vão") passa ao primeiro
  parágrafo, antes era premissa e o leitor montava a pergunta sozinho; (3) "contrário à
  segurança no ELS" trocado por **"uma ponte dimensionada para L/250 entrega L/185"**;
  (4) fecho circular ("verificar a rigidez quando o ELS governar") trocado por um
  **critério de vão**, que o projetista consulta antes de projetar.
  Dois `\tofill` novos: `$L/185$` (depende de C-02) e `X~m`, o vão-limite (depende de P-12).
- **Vault criado.** Contexto de pesquisa consolidado em `vault/` para que qualquer IA
  recupere o estado sem reler o repositório.
- **Artigo 2 (engstruct) traduzido para o português** — versão de trabalho. `babel`
  alterado para `[brazil]` e `\DeclareLanguageMapping{brazil}{brazilian-apa}` reativado.
  ⚠️ Retraduzir para o inglês antes de submeter ao Engineering Structures (D-09).
  Traduzidos: `abstract_keywords`, `00_nomenclature`, `01_introduction`, `02_materials`,
  `03_methodology`, `04_results`, `05_conclusions`, `declarations`, `appendices`,
  `title_authors`, e as três tabelas de `tabelas/`.
- **Autoria definida (D-08).** Artigo 2: Wanderlei (1º, correspondente), Matheus, André,
  Enzo, Maria José, Fran. Do Artigo 1 saíram Enzo, Maria José e Fran, restando Wanderlei,
  Priscilla, Pedro, Wellington, André, Matheus e João Paulo. `pages/home.py` mantido como
  está, por decisão explícita.
- **Erro factual corrigido:** o texto afirmava que "duas espécies diferem em duas classes
  inteiras"; a `tab_discordancia` lista **quatro** (angelim-pedra, piolho, casca-grossa,
  goiabão). Corrigido em `02_materials.tex` e `05_conclusions.tex`.
- **Nomes populares acentuados** nas tabelas (Goiabão, Itaúba, Cupiúba, Ipê, Jatobá,
  Maçaranduba, Canafístula, Copaíba, Cutiúba, Guaicará), que estavam em ASCII por virem
  de geração automática.
- **Aritmética das três tabelas reconferida** — todos os percentuais batem. Registro em
  `03_dados_40_especies.md`.
- **Revisão crítica do Artigo 2** registrada em `05_revisao_critica.md`: 9 achados, dois
  deles capazes de derrubar o artigo (ΔV conflaciona resistência com rigidez; E_M0 medido
  comparado com E_c0,med tabelado).
- **Linha de ciência de dados** registrada em `07_linha_ciencia_de_dados.md`.

## Antes de 2026-08-12

- Artigo 1 (Matéria) redigido de ponta a ponta, com resultados pendentes marcados em
  vermelho. Nenhuma das 20 células rodada.
- Artigo 2 (Engineering Structures) redigido até §3, com §2 completa: as três tabelas das
  40 espécies calculadas e o achado de dispersão intraclasse estabelecido. Nenhuma das
  320 rodadas de otimização feita.
- Plataforma ReliaBridge no ar: <https://reliabridge.streamlit.app/>
