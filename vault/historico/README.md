# Histórico — material da fase anterior (julho de 2026)

Este material foi produzido quando o projeto tinha **um artigo só**, cujo rascunho vivia
em `paper/final/` e era destinado a *Structures* (Elsevier) ou a *Structural and
Multidisciplinary Optimization*. Nada disso vale mais:

- `paper/final/` não existe. O trabalho virou **dois artigos**, em `paper/materia/`
  (Revista Matéria) e `paper/engstruct/` (Engineering Structures). Ver **D-01** e **D-02**
  em [`../04_decisoes.md`](../04_decisoes.md).
- Os marcadores de pendência eram `\sugestao{...}`; hoje são `\tofill{...}` e `fillblock`.
- A comparação de revistas em `02_revistas_alvo.md` ficou superada pela D-02.

**Está aqui por dois motivos:** o raciocínio ainda é útil, e alguns itens continuam
abertos. Ler com a data em mente, e conferir contra os arquivos numerados do `vault/`
antes de agir sobre qualquer coisa daqui.

| Arquivo | O que é | Ainda vale? |
|---|---|---|
| `00_auditoria_codigo.md` | Auditoria do código contra o que o paper afirmava, de 2026-07-25 | Parcialmente — B1 e B2 foram corrigidos; conferir o resto contra o código atual |
| `01_roadmap.md` | Plano priorizado da fase anterior | Superado por [`../06_proximos_passos.md`](../06_proximos_passos.md) |
| `02_revistas_alvo.md` | Structures vs. SMO | Superado pela D-02 |
| `experimentos/` | Especificação dos experimentos numéricos E1–E4 | E1 (custo da robustez) e E4 (hipervolume) continuam pertinentes ao Artigo 1; **E3 (validação Monte Carlo) saiu do escopo** pela D-14 |
| `LEIA-ME_do_vault_antigo.md` | O README do antigo `_vault/` | Só como registro. A afirmação de que a pasta é ignorada pelo git deixou de valer na unificação |

As notas de leitura e as referências saíram daqui e passaram a viver em
[`../notas/`](../notas/) e [`../refs/`](../refs/), porque continuam atuais e são usadas
pelos dois artigos.
