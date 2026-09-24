"""Junta os blocos de `resultados/` com a planilha de casos e monta o dataset do PySR.

Uma linha por caso, com as colunas separadas por papel. A separação não é cosmética: se
uma coluna de diagnóstico entrar como entrada, a equação passa a prever o resultado com o
resultado dentro.

    identificacao  id, bloco, especie_id, especie, classe
    entrada        vao_m, largura_m, p_gk_kpa, veiculo_tb450, p_roda_kn,
                   E_mpa, f_mk_mpa, f_vk_mpa, densidade_kgm3
    alvo           d_cm, bw_cm, h_cm, n_long, n_tab, esp_long_corr_cm,
                   esp_tab_corr_cm, volume_m3
    diagnostico    governante, g_*, flecha_ratio, d_no_teto, status
    particao       split_especie, split_vao, split_aleatorio

Três cuidados embutidos.

**Veículo é uma coluna só.** `p_roda_kn` e a multidão são funções do veículo, não
variáveis independentes. Com dois perfis não há como identificar seus efeitos em separado,
então as duas formas ficam disponíveis, `veiculo_tb450` binária e `p_roda_kn` contínua, e o
treino usa **uma** delas. A multidão não é exportada como entrada justamente para o PySR
não combinar as duas em termos espúrios.

**As classes ficam fora do ajuste.** Em todas as partições, as linhas de classe recebem
`referencia`. Elas produzem a leitura oficial da fronteira; se entrassem no treino, a curva
da classe viraria um ponto que a equação já viu.

**Três partições, três perguntas.** `split_aleatorio` é exploratório e otimista, porque as
540 linhas de uma espécie compartilham as mesmas propriedades e toda linha de teste tem
quase-gêmea no treino. `split_especie` responde se a equação serve para madeira não vista.
`split_vao` responde se ela interpola no vão. Os dois últimos é que vão para o artigo.

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_ia\\consolidar.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
CASOS_PADRAO = PASTA / "casos_ia.xlsx"
RESULTADOS = PASTA / "resultados"
SAIDA_PADRAO = PASTA / "dataset_ia.parquet"

# Vãos intermediários retidos. Ficam entre valores vistos no treino, então medem
# interpolação, não extrapolação.
VAOS_TESTE = [4.5, 7.5, 9.5]
# Espécies retidas, uma a cada cinco dentro de cada classe, para o teste cobrir as cinco.
PASSO_ESPECIE = 5

ENTRADAS = ["vao_m", "largura_m", "p_gk_kpa", "veiculo_tb450", "p_roda_kn",
            "E_mpa", "f_mk_mpa", "f_vk_mpa", "densidade_kgm3"]
ALVOS = ["d_cm", "bw_cm", "h_cm", "n_long", "n_tab", "esp_long_corr_cm",
         "esp_tab_corr_cm", "volume_m3"]

P_RODA = {"TB240": 40.0, "TB450": 75.0}


def especies_retidas(df: pd.DataFrame) -> list[int]:
    """Uma espécie a cada `PASSO_ESPECIE` dentro de cada classe, ordenadas por módulo.

    Escolha determinística, sem sorteio, para a partição ser reproduzível sem semente e
    para o teste conter madeira de todas as cinco classes.
    """
    esp = (df[df["bloco"] == "especie"][["especie_id", "classe", "E_mpa"]]
           .drop_duplicates().sort_values(["classe", "E_mpa", "especie_id"]))
    retidas = []
    for _, grupo in esp.groupby("classe", sort=True):
        retidas.extend(grupo["especie_id"].iloc[::PASSO_ESPECIE].tolist())
    return sorted(int(v) for v in retidas)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--casos", type=Path, default=CASOS_PADRAO)
    p.add_argument("--resultados", type=Path, default=RESULTADOS)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--fracao-teste", type=float, default=0.2,
                   help="fração do split_aleatorio exploratório (padrão 0,2)")
    p.add_argument("--semente", type=int, default=1, help="semente do split_aleatorio")
    args = p.parse_args()

    blocos = sorted(args.resultados.glob("bloco_*.parquet"))
    if not blocos:
        print(f"nenhum bloco em {args.resultados}\nRode antes: simulacao_ia/rodar.py",
              file=sys.stderr)
        return 1

    res = pd.concat([pd.read_parquet(b) for b in blocos], ignore_index=True)
    res = res.drop_duplicates(subset="id", keep="last")

    casos = pd.read_excel(args.casos, sheet_name="Casos")
    meta = casos[["id"] + [c for c in casos.columns if c.startswith("cfg_ref_")]].copy()
    meta.columns = [c.replace("cfg_ref_", "") for c in meta.columns]
    meta = meta.rename(columns={"E_MPa": "E_mpa", "f_mk_MPa": "f_mk_mpa",
                                "f_vk_MPa": "f_vk_mpa", "split": "origem"})

    df = meta.merge(res, on="id", how="left")
    df["status"] = df["status"].fillna("nao_executado")

    df["veiculo_tb450"] = (df["veiculo"] == "TB450").astype(int)
    df["p_roda_kn"] = df["veiculo"].map(P_RODA)

    # Partições. A classe é referência em todas, nunca entra no ajuste.
    e_classe = df["bloco"] == "classe"
    retidas = especies_retidas(df)

    df["split_especie"] = np.where(
        e_classe, "referencia",
        np.where(df["especie_id"].isin(retidas), "teste", "treino"))
    df["split_vao"] = np.where(
        e_classe, "referencia",
        np.where(df["vao_m"].isin(VAOS_TESTE), "teste", "treino"))

    rng = np.random.default_rng(args.semente)
    sorteio = rng.random(len(df))
    df["split_aleatorio"] = np.where(
        e_classe, "referencia",
        np.where(sorteio < args.fracao_teste, "teste", "treino"))

    ordem = (["id", "bloco", "especie_id", "especie", "classe", "veiculo"]
             + ENTRADAS + ALVOS
             + ["governante", "flecha_ratio", "d_no_teto", "status"]
             + [c for c in df.columns if c.startswith("g_")]
             + ["split_especie", "split_vao", "split_aleatorio", "avaliacoes", "tempo_s"])
    df = df[[c for c in ordem if c in df.columns]]

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.saida, index=False)
    df.to_csv(args.saida.with_suffix(".csv"), index=False)

    ok = df[df["status"] == "ok"]
    print(f"{args.saida.name}: {len(df)} linhas, {len(ok)} com solução")
    faltando = int((df["status"] == "nao_executado").sum())
    if faltando:
        print(f"  ATENÇÃO: {faltando} caso(s) sem resultado. Rode `rodar.py` até o fim.")
    print(f"  sem solução : {int((df['status'] == 'sem_solucao').sum())}")
    print(f"  erro        : {int(df['status'].str.startswith('erro').sum())}")
    print(f"  d no teto   : {int(ok['d_no_teto'].sum())} (candidatos a fronteira)")
    print(f"\n  espécies retidas ({len(retidas)}): {retidas}")
    print(f"  vãos retidos: {VAOS_TESTE}")
    for coluna in ("split_especie", "split_vao", "split_aleatorio"):
        contagem = df[coluna].value_counts().to_dict()
        print(f"  {coluna:16s} {contagem}")
    if not ok.empty:
        print("\n  governante:")
        for nome, n in ok["governante"].value_counts().items():
            print(f"    {nome:20s} {n:6d}")
    print(f"\n{args.saida}\nPróximo: simulacao_ia/treinar_pysr.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
