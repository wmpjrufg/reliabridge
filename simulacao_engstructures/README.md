# Campanha de semente única — Artigo 2 (Engineering Structures)

Mesma receita da Revista Matéria: uma execução do NSGA-II por caso, semente 1, população 50,
300 gerações, robustez de 5% no diâmetro (grade de 5 pontos, pior caso) e os mesmos limites de
busca (d 20–100, b_w 20–50, h 5–15, esp_long 30–200, esp_tab 2–5 cm). Muda só a faixa de vãos,
de 3 a 10 m em passo de 1 m, e entra o bloco de espécies de Dias e Lahr (2004).

## O que tem na pasta

| Arquivo | Para quê |
|---|---|
| `casos_engstruct_semente1.xlsx` | Planilha de casos (360), pronta para rodar. Abas extras: `Matriz_vao_classe` e `Especies` |
| `gerar_casos.py` | Regera a planilha (só se mudar vão ou base) |
| `rodar_paralelo.py` | Roda em paralelo, um caso por núcleo. **Use este na máquina potente** |
| `rodar.py` | Mesma coisa em série, pelo `rodar_lote.py` de sempre |
| `consolidar.py` | Junta tudo em `consolidado.xlsx` (volumes, governante, pares espécie × classe) |

## Casos

- **Base de classes (`CLS_Dxx_Lyy`), 40 casos:** 5 classes × 8 vãos. É a matriz vão × classe,
  igual à da Matéria. Ela serve também de cenário "cls" de todas as espécies, porque as
  propriedades da classe não dependem da espécie.
- **Espécies (`Enn_Lyy_esp`), 320 casos:** 40 espécies × 8 vãos, com todas as propriedades
  medidas da espécie.

Só entram cenários que existem como decisão de projeto: projetar pela espécie ou pela classe.

## Passo a passo na máquina potente

Na raiz do repositório, com o `.venv` do projeto (pymoo 0.6.1.6, UQpy 4.2.1):

```bat
REM 1) base de classes (~40 casos, poucos minutos)
.venv\Scripts\python.exe simulacao_engstructures\rodar_paralelo.py --filtro CLS_

REM 2) conferir: os casos de 3 a 6 m têm de bater com a Matéria
.venv\Scripts\python.exe simulacao_engstructures\consolidar.py

REM 3) espécies
.venv\Scripts\python.exe simulacao_engstructures\rodar_paralelo.py

REM 4) consolidar de novo
.venv\Scripts\python.exe simulacao_engstructures\consolidar.py
```

O padrão é usar (núcleos − 1) processos; para mudar, use `--processos 12`. O script pula
o que já tem pacote gravado, então pode interromper e relançar à vontade.

## Tempo

No teste em uma máquina de 2 núcleos, 8 casos (de 3 a 10 m) rodaram em 48 s: de 12 a 26 s
por caso com 4 processos disputando 2 núcleos. Com um núcleo por processo, conte algo entre
6 e 12 s por caso. As 360 rodadas ficam em torno de 1 h em série e em cerca de 5 min
com 16 processos.

## Conferências feitas antes de entregar

- A planilha é lida e validada por `batch_pre_sizing.ler_planilha_casos` sem erro (360 casos).
- As entradas de `CLS_D40_L05` são idênticas às da C-13 da Matéria.
- Rodei `CLS_D20_L03`, `CLS_D40_L05` e `CLS_D60_L06` e comparei com a Matéria: 2,987 contra
  2,988 m³, 5,090 contra 5,090 m³ e 5,637 contra 5,632 m³. A diferença máxima é de 0,09%.
- Rodei também `CLS_D20_L10`, `CLS_D60_L10`, `E40_L05_esp` e `E40_L10_esp` (umirana, E 38%
  abaixo da classe), todos com status ok.

## Pontos de atenção

1. **Flecha variável sem multidão.** `flecha_max_carga_variavel` só soma as rodas. Para
   L > 6 m, a multidão entra no momento, mas não na flecha. Pela minha conta, isso subestima
   a flecha em cerca de 4% a 6% em 10 m. A comparação é pareada no mesmo vão, então o ΔV
   quase não muda, mas o vão em que a flecha passa a governar fica um pouco adiado.
   Esse item já constava das pendências do PREENCHIMENTO.md.
2. **Limites de busca.** Em 10 m, algumas soluções chegam perto do teto (E40_L10_esp com
   esp_long = 197,9 cm, para um teto de 200 cm). O `consolidar.py` marca na coluna
   `no_limite` os casos com variável encostada no limite. Se aparecerem muitos, vale
   ampliar o intervalo antes da rodada com sementes.

## Saída do consolidar.py (`consolidado.xlsx`)

- `Casos`: solução de menor volume de cada caso, com dimensões, V, utilizações (U = 1 + g),
  verificação governante e `no_limite`.
- `Matriz_volume` e `Matriz_governante`: base de classes, vão × classe.
- `Conferencia_Materia`: CLS de 3 a 6 m contra os volumes publicados na Matéria.
- `Pares`: por espécie e vão, V_esp, V_cls, ΔV_cls = V_cls/V_esp − 1 (a decisão entre
  espécie e classe), governantes, e `U_flecha_CtoR_est`, que é a utilização de
  flecha do projeto da classe com o E da espécie (U_cls × E_cls/E_esp). Essa estimativa
  ignora a troca de densidade.
