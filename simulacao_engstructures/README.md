# Campanha do Artigo 2 (Engineering Structures): espécie x classe

Receita da Revista Matéria (NSGA-II com população 50, 300 gerações, robustez de 5% no
diâmetro com grade de 5 pontos no pior caso), com quatro mudanças:

- vãos de 3 a 10 m em passo de 1 m;
- bloco de espécies de Dias e Lahr (2004);
- teto de esp_long ampliado de 200 para 250 cm (na primeira rodada, 5 soluções de espécie
  encostaram no teto em 6 e 8 m);
- 5 sementes por caso, ficando com o menor volume entre elas.

Os demais limites de busca são os da Matéria: d 20–100, b_w 20–50, h 5–15, esp_tab 2–5 cm.

## Por que 5 sementes

Com o teto de 250 cm, a execução única de CLS_D40_L05 parou 2,2% acima do volume já
conhecido. Num teste com 8 sementes em 4 casos, a distância do menor volume de k sementes
até o melhor das 8 foi:

| Sementes | Média | Pior caso |
|---|---|---|
| 1 | 0,2% a 1,9% | até 7,2% |
| 3 | 0,02% a 0,30% | até 1,8% |
| 5 | 0,01% a 0,10% | até 0,9% |

Com 5 sementes o erro de otimização fica abaixo de 1% no pior caso, bem abaixo dos ΔV que
o artigo compara.

## Arquivos

| Arquivo | Para quê |
|---|---|
| `gerar_casos.py` | Gera `casos_engstruct.xlsx` (360 casos × 5 sementes = 1800 execuções) |
| `rodar_paralelo.py` | Roda em paralelo, um caso por núcleo. **Use este na máquina potente** |
| `rodar.py` | Mesma coisa em série, pelo `rodar_lote.py` de sempre |
| `consolidar.py` | Junta tudo em `consolidado.xlsx`, com a melhor semente de cada caso e a dispersão |
| `diagnosticar_limites.py` | Detalha as execuções com variável no limite do intervalo (`limites_diagnostico.xlsx`) |
| `casos_engstruct_semente1_OBSOLETA.xlsx` | Planilha antiga (semente única, teto de 200 cm). Não usar |

## Casos

- **Base de classes (`CLS_Dxx_Lyy_sN`):** 5 classes × 8 vãos. É a matriz vão × classe e
  serve de cenário "classe" de todas as espécies. Sobol só na semente 1.
- **Espécies (`Enn_Lyy_esp_sN`):** 40 espécies × 8 vãos, com as propriedades medidas.

## Sequência na máquina potente

Na raiz do repositório, com o `.venv` do projeto:

```bat
REM 0) guardar a rodada anterior (senão o rodar_paralelo pula tudo)
ren simulacao_engstructures\resultados resultados_esp200_semente1

REM 1) gerar a planilha nova (1800 execuções)
.venv\Scripts\python.exe simulacao_engstructures\gerar_casos.py --forcar

REM 2) rodar tudo em paralelo
.venv\Scripts\python.exe simulacao_engstructures\rodar_paralelo.py

REM 3) consolidar e diagnosticar
.venv\Scripts\python.exe simulacao_engstructures\consolidar.py
.venv\Scripts\python.exe simulacao_engstructures\diagnosticar_limites.py
```

Se a execução for interrompida, rode o passo 2 de novo: ele pula o que já tem pacote
gravado. Para rodar só uma parte, use `--filtro` (por exemplo `--filtro CLS_` ou
`--filtro _s1`). Para usar menos núcleos, use `--processos 12`.

## Tempo

Entre 6 e 12 s por execução e por núcleo. As 1800 execuções levam de 3 a 6 h em série, ou
de 12 a 25 min com 16 processos.

## Saída do consolidar.py (`consolidado.xlsx`)

- `Casos`: uma linha por caso, com a melhor semente: dimensões, V, utilizações (U = 1 + g),
  verificação governante, `no_limite`, `semente_melhor`, `V_min/max/media_sementes`,
  `dispersao_pct` = V_max/V_min − 1 e `governante_igual_nas_sementes`.
- `Execucoes`: uma linha por execução (caso × semente).
- `Matriz_volume`, `Matriz_governante` e `Matriz_dispersao`: base de classes, vão × classe.
- `Conferencia_Materia`: CLS de 3 a 6 m contra a Matéria. Como a Matéria usou teto de 200 cm
  e uma semente, diferenças de 1 a 2% são esperadas, e o volume novo tende a ser menor.
- `Pares`: por espécie e vão, V_esp, V_cls, ΔV = V_cls/V_esp − 1, as dispersões dos dois lados,
  `dV_acima_ruido` (|ΔV| maior que a soma das dispersões), governantes e
  `U_flecha_CtoR_est`, a utilização de flecha do projeto da classe com o E da espécie
  (U_cls × E_cls/E_esp). Essa estimativa ignora a troca de densidade.

No terminal, o consolidar mostra a mediana, o p90 e o máximo da dispersão entre sementes e
quantos pares têm ΔV acima do ruído.

## Pontos de atenção

1. **Flecha variável sem multidão.** `flecha_max_carga_variavel` só soma as rodas. Para
   L > 6 m, a multidão entra no momento, mas não na flecha, o que subestima a flecha em
   cerca de 4% a 6% em 10 m. Já consta das pendências do PREENCHIMENTO.md.
2. **Limites construtivos.** Na primeira rodada, h no mínimo (3 e 4 m) e esp_tab nos limites
   apareceram em 23 casos. São limites construtivos, esperados. O `diagnosticar_limites.py`
   separa esses dos limites de domínio.
