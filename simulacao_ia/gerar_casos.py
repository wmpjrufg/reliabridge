"""Monta a planilha de casos da campanha do Artigo 3 (pré-dimensionamento explícito).

A grade varre cinco eixos. Os quatro primeiros descrevem a travessia, o quinto é o
material, e nele a classe entra como se fosse mais uma madeira, com o mesmo estatuto de
uma espécie medida.

    vão       3 a 10 m, passo 0,5                                     15
    veículo   TB-240 e TB-450                                          2
    largura   3,5 / 4,0 / 4,5 m                                        3
    p_gk      0,1 / 0,5 / 1 / 2 / 3 / 5 kPa                            6
    material  40 espécies medidas + 5 classes D20 a D60               45

                                                          15*2*3*6*45 = 24300 casos

O bloco de espécies treina as equações. O bloco de classes fica **fora do ajuste**, com
`split = referencia`, e serve para a leitura oficial da fronteira. Misturar os dois no
treino destruiria a comparação, porque a curva da classe passaria a ser um ponto que a
equação já viu.

Convenções de propriedade idênticas às do Artigo 2, senão os dois artigos discordam nos
números. E_c0 dos dois lados, f_m,k = f_c0,k e f_v0,k da espécie por fator sobre a média,
porque a fonte não publica o característico de cisalhamento.

A planilha é agnóstica ao solucionador. Ela descreve os casos; quem os resolve é o
`solver_direto.py` (grade inteira) ou o NSGA-II via `rodar.py` (apenas o subconjunto de
verificação, porque a grade inteira custaria cerca de 142 h).

Uso (na raiz do repositório):
    .venv\\Scripts\\python.exe simulacao_ia\\gerar_casos.py
    .venv\\Scripts\\python.exe simulacao_ia\\gerar_casos.py --passo-vao 1.0
    .venv\\Scripts\\python.exe simulacao_ia\\gerar_casos.py --forcar
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "paper" / "engstruct" / "scripts"))

import batch_pre_sizing as bps  # noqa: E402
from gerar_casos_engstruct import BASE_ESPECIES, FATOR_CISALHAMENTO  # noqa: E402

SAIDA_PADRAO = PASTA / "casos_ia.xlsx"

VAO_MIN_M, VAO_MAX_M = 3.0, 10.0
LARGURAS_M = [3.5, 4.0, 4.5]
P_GK_KPA = [0.1, 0.5, 1.0, 2.0, 3.0, 5.0]

# pages/pre_sizing.py, VEICULOS_PADRAO. A distância entre eixos é 1,5 m nos dois
# (vault/04_decisoes.md). Carga de roda e multidão são funções do veículo, não variáveis
# independentes: com dois perfis não há como identificar seus efeitos em separado.
VEICULOS = {
    "TB240": {"p_rodak_kn": 40.0, "p_qk_kpa": 4.0, "a_m": 1.5},
    "TB450": {"p_rodak_kn": 75.0, "p_qk_kpa": 5.0, "a_m": 1.5},
}

# ABNT NBR 7190-3:2022, florestas nativas. f_m,k = f_c0,k (NBR 7190-1:2022, item 6.3.4).
CLASSES_NBR = {
    "D20": {"densidade": 500.0, "f_mk": 20.0, "f_vk": 4.0, "e_mpa": 10000.0},
    "D30": {"densidade": 625.0, "f_mk": 30.0, "f_vk": 5.0, "e_mpa": 12000.0},
    "D40": {"densidade": 750.0, "f_mk": 40.0, "f_vk": 6.0, "e_mpa": 14500.0},
    "D50": {"densidade": 850.0, "f_mk": 50.0, "f_vk": 7.0, "e_mpa": 16500.0},
    "D60": {"densidade": 1000.0, "f_mk": 60.0, "f_vk": 8.0, "e_mpa": 19500.0},
}

# Iguais aos do Artigo 2, com o teto de esp_long já ampliado para 250 cm porque no teto
# antigo de 200 cm cinco soluções de espécie encostaram no limite.
LIMITES = bps.LimitesBusca(esp_long=(30.0, 250.0))

# Só usados pelo subconjunto de verificação em NSGA-II. O solucionador direto não tem
# semente, população nem gerações.
ALGORITMO = bps.ParametrosAlgoritmo(pop_size=50, n_gen=300, n_checagens=5, seed=1)

FIXOS = {
    "classe_carregamento": "curta duração",
    "classe_madeira": "madeira natural",
    "classe_umidade": 3,
    "gamma_g": 1.30,
    "gamma_q": 1.50,
    "gamma_wc": 1.80,
    "gamma_wf": 1.40,
    "psi2": 0.30,
    "phi": 0.80,
    "robustez_pct": 5,
}


def montar_dados(t: dict, l_cm: float, pista_cm: float, p_gk_kpa: float,
                 veiculo: dict, prop: dict) -> dict:
    """Dicionário de entrada com as chaves e a ordem do `beam_data.xlsx`.

    Difere do `montar_dados` do Artigo 2 por receber pista, carga permanente e veículo
    como parâmetros, em vez de lê-los de um bloco fixo. Longarina e tabuleiro recebem as
    mesmas propriedades, como no Artigo 1.
    """
    return {
        t["entrada_comprimento"]: l_cm,
        t["pista"]: pista_cm,
        # A lista de opções do widget, não um rótulo. O cabeçalho gravado no
        # `beam_data.xlsx` é a representação da lista, literalmente "['Circular']".
        f"{t['tipo_secao_longarina']}": "Circular",
        t["tipo_secao_tabuleiro"]: "Retangular",
        f"{t['carga_permanente']} (kPa)": p_gk_kpa,
        f"{t['carga_roda']} (kN)": veiculo["p_rodak_kn"],
        f"{t['carga_multidao']} (kPa)": veiculo["p_qk_kpa"],
        f"{t['distancia_eixos']} (m)": veiculo["a_m"],
        t["classe_carregamento"]: FIXOS["classe_carregamento"],
        t["classe_madeira"]: FIXOS["classe_madeira"],
        t["classe_umidade"]: FIXOS["classe_umidade"],
        t["gamma_g"]: FIXOS["gamma_g"],
        t["gamma_q"]: FIXOS["gamma_q"],
        t["gamma_wc"]: FIXOS["gamma_wc"],
        t["gamma_wf"]: FIXOS["gamma_wf"],
        t["psi2"]: FIXOS["psi2"],
        t["considerar_fluencia"]: FIXOS["phi"],
        t["percentual_robustez"]: FIXOS["robustez_pct"],
        f"{t['densidade_long']} (kg/m³)": prop["densidade"],
        f"{t['f_mk']} (MPa)": prop["f_mk"],
        f"{t['f_vk']} (MPa)": prop["f_vk"],
        f"{t['e_modflex']} (GPa)": round(prop["e_mpa"] / 1000.0, 3),
        f"{t['densidade_tab']} (kg/m³)": prop["densidade"],
        f"{t['f_mk_tab']} (MPa)": prop["f_mk"],
    }


def materiais(base: pd.DataFrame, fator_cis: float) -> list[dict]:
    """Os 45 perfis de material, espécies medidas primeiro, classes tabeladas depois.

    Cada perfil traz os quatro números que o modelo usa mais a procedência, que é o que
    separa o bloco de treino do bloco de referência.
    """
    perfis = []
    for _, esp in base.iterrows():
        perfis.append({
            "codigo": f"E{int(esp['id']):02d}",
            "bloco": "especie",
            "especie_id": int(esp["id"]),
            "especie": esp["nome"],
            "classe": esp["classe_D"],
            "split": "ajuste",
            "densidade": float(esp["rho_ap_kgm3"]),
            "f_mk": float(esp["f_c0_k_MPa"]),
            "f_vk": round(float(esp["f_v0_m_MPa"]) * fator_cis, 2),
            "e_mpa": float(esp["E_c0_m_MPa"]),
        })
    for classe, prop in CLASSES_NBR.items():
        perfis.append({
            "codigo": f"CLS_{classe}",
            "bloco": "classe",
            "especie_id": None,
            "especie": None,
            "classe": classe,
            "split": "referencia",
            **prop,
        })
    return perfis


def conferir_classes(base: pd.DataFrame) -> None:
    """A base traz as propriedades da classe de cada espécie; têm de bater com a norma."""
    equivalentes = {"f_mk": "f_mk_classe_MPa", "f_vk": "f_v0k_classe_MPa",
                    "e_mpa": "E_c0_classe_MPa", "densidade": "rho_classe_kgm3"}
    for _, esp in base.iterrows():
        ref = CLASSES_NBR[esp["classe_D"]]
        for chave, coluna in equivalentes.items():
            if abs(float(esp[coluna]) - ref[chave]) > 1e-9:
                raise ValueError(
                    f"{esp['nome']}: {chave} da classe {esp['classe_D']} = {esp[coluna]}, "
                    f"esperado {ref[chave]}"
                )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--saida", type=Path, default=SAIDA_PADRAO)
    p.add_argument("--passo-vao", type=float, default=0.5,
                   help="passo da varredura de vão, em m (padrão 0,5)")
    p.add_argument("--fator-cisalhamento", type=float, default=FATOR_CISALHAMENTO,
                   help="f_v0,k = fator x f_V0 médio da espécie (padrão 0,70)")
    p.add_argument("--forcar", action="store_true", help="sobrescreve a planilha existente")
    args = p.parse_args()

    if args.saida.exists() and not args.forcar:
        print(f"{args.saida.name} já existe. Use --forcar para regerar.", file=sys.stderr)
        return 1
    if not BASE_ESPECIES.exists():
        print(f"base não encontrada: {BASE_ESPECIES}\n"
              "Rode antes: paper/engstruct/scripts/gerar_base_especies.py", file=sys.stderr)
        return 1

    base = pd.read_csv(BASE_ESPECIES)
    conferir_classes(base)
    t = bps.textos("pt")

    vaos = np.round(np.arange(VAO_MIN_M, VAO_MAX_M + 1e-9, args.passo_vao), 3)
    perfis = materiais(base, args.fator_cisalhamento)

    casos, refs = [], {}
    for perfil in perfis:
        for l_m in vaos:
            for nome_veiculo, veiculo in VEICULOS.items():
                for b_m in LARGURAS_M:
                    for p_gk in P_GK_KPA:
                        cid = (f"{perfil['codigo']}_L{l_m * 10:04.0f}"
                               f"_{nome_veiculo}_B{b_m * 100:03.0f}_G{p_gk * 100:03.0f}")
                        casos.append(bps.CasoBatch(
                            id=cid,
                            dados=montar_dados(t, l_m * 100, b_m * 100, p_gk, veiculo, perfil),
                            limites=LIMITES,
                            algoritmo=ALGORITMO,
                            sobol=bps.ConfigSobol(ativo=False),
                        ))
                        refs[cid] = {
                            "bloco": perfil["bloco"], "especie_id": perfil["especie_id"],
                            "especie": perfil["especie"], "classe": perfil["classe"],
                            "split": perfil["split"], "vao_m": float(l_m),
                            "veiculo": nome_veiculo, "largura_m": b_m, "p_gk_kpa": p_gk,
                            "E_MPa": perfil["e_mpa"], "f_mk_MPa": perfil["f_mk"],
                            "f_vk_MPa": perfil["f_vk"], "densidade_kgm3": perfil["densidade"],
                        }

    df = bps.montar_planilha_casos(casos)
    colunas_ref = ["bloco", "especie_id", "especie", "classe", "split", "vao_m", "veiculo",
                   "largura_m", "p_gk_kpa", "E_MPa", "f_mk_MPa", "f_vk_MPa", "densidade_kgm3"]
    for pos, col in enumerate(colunas_ref, start=1):
        df.insert(pos, f"cfg_ref_{col}", [refs[i][col] for i in df["id"]])

    materiais_df = pd.DataFrame(perfis)[
        ["codigo", "bloco", "especie_id", "especie", "classe", "split",
         "densidade", "f_mk", "f_vk", "e_mpa"]
    ]

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(args.saida) as w:
        df.to_excel(w, index=False, sheet_name="Casos")
        materiais_df.to_excel(w, index=False, sheet_name="Materiais")

    n_esp = sum(1 for m in perfis if m["bloco"] == "especie")
    n_cls = len(perfis) - n_esp
    n_comb = len(vaos) * len(VEICULOS) * len(LARGURAS_M) * len(P_GK_KPA)
    print(f"{args.saida.name}: {len(df)} casos")
    print(f"  materiais  : {len(perfis)} ({n_esp} espécies medidas + {n_cls} classes)")
    print(f"  combinações: {n_comb} ({len(vaos)} vãos x {len(VEICULOS)} veículos x "
          f"{len(LARGURAS_M)} larguras x {len(P_GK_KPA)} cargas)")
    print(f"  vãos       : {vaos[0]:g} a {vaos[-1]:g} m, passo {args.passo_vao:g}")
    print(f"  ajuste     : {n_esp * n_comb} casos de espécie")
    print(f"  referência : {n_cls * n_comb} casos de classe, fora do ajuste")
    print(f"  limites cm : d {LIMITES.d}, bw {LIMITES.bw}, h {LIMITES.h}, "
          f"esp_long {LIMITES.esp_long}, esp_tab {LIMITES.esp_tab}")
    print("\n  O solucionador direto resolve a grade inteira e não tem semente.")
    print(f"  Em NSGA-II a 21 s por caso, a mesma grade custaria {len(df) * 21 / 3600:.0f} h.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
