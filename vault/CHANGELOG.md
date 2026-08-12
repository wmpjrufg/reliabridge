# Changelog da pesquisa

Uma linha por evento relevante. Novidades no topo.

---

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
