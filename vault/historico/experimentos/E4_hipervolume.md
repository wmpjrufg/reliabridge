# E4 — Hipervolume e convergência

Alimenta a Seção 3.8 do LaTeX (`sec:hipervolume`): Figura `fig:convergencia_hv` e
Tabela `tab:hv`.

**Status: código pronto.** `scripts/gerar_convergencia_hv.py`.

## Como rodar

```bash
# teste rápido da mecânica (segundos)
python scripts/gerar_convergencia_hv.py --pop 20 --geracoes 40 --checagens 3

# execução do artigo, um caso
python scripts/gerar_convergencia_hv.py

# dois casos sobrepostos na mesma figura
python scripts/gerar_convergencia_hv.py \
    --caso "Ponte 01:Bridge 01:beam_data_01.xlsx" \
    --caso "Ponte 02:Bridge 02:beam_data_02.xlsx"
```

Saída em `paper/final/figuras/`: `convergencia_hv_pt.png`, `convergencia_hv_en.png`
e um CSV por caso (geração, hipervolume, n_solucoes, n_avaliacoes).

## Como o hipervolume é calculado

Os objetivos são normalizados pelo ideal e pelo nadir observados **ao longo de toda
a execução**, e o ponto de referência é (1,1; 1,1) no espaço normalizado. Isso torna
o HV adimensional e a curva comparável entre execuções de escalas diferentes.

⚠️ **Para a Tabela `tab:hv`, que compara HV entre níveis de $\rho$, isso não basta.**
Como cada execução normaliza pelo próprio ideal/nadir, os valores não são
diretamente comparáveis entre si. Duas saídas:

1. Passar o mesmo `ponto_referencia` (em espaço **não** normalizado) para todas as
   execuções — exige alterar `historico_hipervolume` para aceitar ideal/nadir fixos;
2. Ou reportar apenas a **geração de estabilização** e a forma da curva na tabela,
   deixando o HV absoluto de fora da comparação entre $\rho$.

A opção 2 é suficiente para o argumento do artigo (justificar $N_{gen}$) e não exige
código novo. Decidir antes de preencher a tabela.

## Uso como critério de verificação

O script imprime, por caso:

```
soluções na fronteira final : 20
hipervolume final           : 1.093839
estabiliza (1% do final) em : geração 16 de 40
```

A linha de estabilização é a leitura objetiva de "a partir daqui o algoritmo não
melhora mais". Se ela vier próxima do número total de gerações, $N_{gen}$ está
curto; se vier muito cedo, está sobrando esforço computacional.

## Observação sobre não monotonicidade

A curva pode apresentar pequenas quedas no platô (~0,3% no teste). Isso não é bug:
`algorithm.opt` no pymoo devolve o conjunto não dominado da **população corrente**,
não um arquivo cumulativo, então uma solução boa pode ser perdida entre gerações.
Vale uma frase no texto, caso a queda apareça na figura final.

## Pendente

- [ ] Rodar no tamanho final ($N_{pop}=75$, $N_{gen}=300$, $N_c=15$), depois de
      corrigidos o $e<0$ e os limites das variáveis
- [ ] Decidir o tratamento do HV entre níveis de $\rho$ (ver aviso acima)
- [ ] Calcular o *spacing* da fronteira — ainda não implementado
