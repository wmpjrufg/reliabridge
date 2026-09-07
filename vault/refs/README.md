# Referências base

PDFs dos trabalhos que servem de norte para o ReliaBridge. Esta pasta é ignorada
pelo git, então os arquivos ficam só na máquina local (respeitando o direito autoral
das editoras).

Origem: `G:\Drives compartilhados\2024-1_pedro_henrique_gomes\01 - Baús\Finais`

## Índice

| Arquivo | Autores / Ano | Veículo | Por que é relevante | Fichamento |
|---|---|---|---|---|
| `art - vinicius nascimento de moraes - parametric modeling...pdf` | de Moraes & Buttignol, 2025 | *Structural Concrete* 26:4083 | Projeto paramétrico + otimização de pontes; já era a referência declarada de estilo do rascunho. Determinístico e mono-objetivo — é sobre ele que nos diferenciamos | [deMoraes2025](../notas/deMoraes2025.md) |
| `art - fulvio parisi - q_bridge...pdf` | Miluccio, Losanno & Parisi, 2026 | ***Structures* 91:112665** | ⭐ **Mesmo gênero (plataforma aberta), na revista alvo, em 2026.** Template estrutural a seguir | [Miluccio2026_QBridge](../notas/Miluccio2026_QBridge.md) |
| `art - sotiria stefanidou - an online platform...pdf` | Stefanidou et al., 2022 | *Bull. Earthquake Eng.* 20:1717 | Artigo de plataforma online; fragilidade de sistema em série é aproveitável | [Stefanidou2022](../notas/Stefanidou2022.md) |
| `art - lu deng - state-of-the-art review...pdf` | Deng, Wang & Yu, 2015 | *J. Perform. Constr. Facil.* (ASCE) | Motivação de introdução: imperfeição de projeto/construção como causa documentada de colapso → justifica a robustez | [Deng2015](../notas/Deng2015.md) |
| `art - andrés batista cheung - confiabilidade estrutural...pdf` | Cheung et al., 2017 | *Ambiente Construído* 17(2):221 | ⭐ **Não estava na lista.** Confiabilidade + ponte de madeira + Brasil. Traz a declaração de lacuna que falta na nossa introdução | [Cheung2017](../notas/Cheung2017.md) |
| `liv - carlito calil júnior - manual de projeto...pdf` | Calil Junior | livro | ⭐ **Não estava na lista.** Referência canônica de pontes de madeira no Brasil; provável fonte de exemplo de validação e de variabilidade da roliça | [Calil2006](../notas/Calil2006.md) ⏳ |

⏳ = fichamento pendente ou incompleto.

## Leituras pendentes, por prioridade

1. **Calil Júnior (manual)** — capítulo de longarinas roliças. Pode resolver de uma
   vez a validação (B6) e a justificativa de $\rho$ e dos COVs (R2.4).
2. **Cheung et al. (2017)** — seções de método e resultados, para extrair
   distribuições, COVs e valores de $\beta$ de referência para madeira.
3. **Q-BRIDGE** — seções 4 a 7 (módulos probabilístico/determinístico, validação,
   estudo de caso), para calibrar profundidade e formato da nossa seção de validação.

## Como adicionar mais

1. Salve o PDF aqui.
2. Registre a linha no índice acima.
3. Crie o fichamento em `../notas/AutorAno.md` a partir de
   `../notas/_template_leitura.md`.
4. Acrescente a entrada em `entradas.bib` e, quando for citar, em
   [paper/final/references.bib](../../paper/final/references.bib).

## Lacunas de literatura ainda a cobrir

A bibliografia do rascunho tem ~4,5 KB — insuficiente para *Structures*, que espera
40–60 referências. Os seis itens acima ajudam, mas continuam faltando buscas em:

- `robust design optimization` + `timber structures`
- `reliability-based design optimization` + `bridge`
- `NSGA-II` + `bridge design optimization` / `multi-objective` + `timber`
- `round timber` / `roundwood` + `diameter variability` (para o $\rho$ e os COVs)
- Pontes de madeira **fora do Brasil** — Escandinávia, USDA Forest Products
  Laboratory, Austrália. O texto atual é quase todo nacional, o que limita alcance
  internacional e é o tipo de coisa que editor de revista Q1 nota.
