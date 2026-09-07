# Experimentos numéricos

Um arquivo por experimento. Cada um especifica: o que rodar, com que parâmetros,
qual figura/tabela do paper produz e qual `\sugestao` fecha.

**Pré-requisito comum:** os bloqueadores R0.1–R0.3 de `../01_roadmap.md` precisam
estar corrigidos. Rodar qualquer experimento antes disso gera resultado que será
descartado.

## Convenções

- **Semente:** `seed=1` para o NSGA-II (já é o padrão em
  [madeiras.py:1649](../../madeiras.py#L1649)); *common random numbers* fixos para
  as perturbações de robustez.
- **Saída:** cada experimento grava em `_vault/resultados/<ID>/` um CSV com a
  população final e um PNG por figura. Nada de resultado só na memória do notebook.
- **Figuras:** manter o padrão de `fronteira_pareto()`
  ([madeiras.py:123](../../madeiras.py#L123)) — 10×10 cm, 600 dpi, fonte 10 pt.
  As revistas alvo aceitam bem esse formato.

## Índice

| ID | Experimento | Fecha | Prioridade |
|---|---|---|---|
| E1 | Custo da robustez ($\rho$ = 0 / 2,5 / 5 / 10%) | `\sugestao` 02_meth:177, 03_res:174 | 🔴 alta |
| E2 | Quais variáveis perturbar (todas vs. só geometria de fabricação) | decisão de B1 | 🔴 alta |
| E3 | Validação Monte Carlo independente da robustez | `\sugestao` 03_res:176 | 🔴 alta |
| E4 | Hipervolume, *spacing* e convergência | Seção 3.8 do LaTeX (`sec:hipervolume`) | ✅ **código pronto** — `scripts/gerar_convergencia_hv.py` gera figura PT+EN e CSV; falta rodar no tamanho final e preencher `tab:hv` |
| E5 | Média vs. pior caso na agregação | `\sugestao` 02_meth:179 | 🟠 média |
| E6 | Índices de Sobol | Seção 3.9 do LaTeX (`sec:sobol`) | ✅ código pronto (`chamar_sobol`, `plot_sobol_total_indices`) — falta rodar e colar figura/tabela |
| E11 | Dispersão das variáveis de projeto na fronteira (boxplot) | Seção 3.10 do LaTeX (`sec:dispersao`) | ✅ código pronto (`plot_boxplot_variaveis_fronteira`) — falta rodar e colar figura |
| E7 | Estudo de caso com ponte real | `\sugestao` 03_res:180 | 🟠 média (alta se alvo = *Structures*) |
| E8 | Confiabilidade acoplada (FORM/MC → $\beta$) | R2.1 | 🟡 alta se alvo = SMO |
| E9 | Comparação NSGA-II × NSGA-III × MOEA/D | R2.2 | 🟡 baixa |
| E10 | Estudo paramétrico de vãos (5 / 8 / 12 m) | R2.3 | 🟠 média |
