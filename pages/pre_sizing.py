# Tela de pré-dimensionamento com NSGA-II
import io
import json
import hashlib
import zipfile

import streamlit as st
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


def exibir_dataframe_html(df: pd.DataFrame, esconder_indice: bool = False) -> None:
    """Exibe uma tabela sem passar pela serializacao nativa do PyArrow."""
    tabela = df.to_html(
        index=not esconder_indice,
        border=0,
        classes="reliabridge-dataframe",
        justify="right",
        escape=True,
    )
    st.html(
        f"""
        <style>
        .reliabridge-table-wrapper {{
            max-width: 100%;
            overflow-x: auto;
            margin-bottom: 1rem;
        }}
        table.reliabridge-dataframe {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.875rem;
            white-space: nowrap;
        }}
        table.reliabridge-dataframe th,
        table.reliabridge-dataframe td {{
            border-bottom: 1px solid rgba(128, 128, 128, 0.25);
            padding: 0.35rem 0.65rem;
            text-align: right;
        }}
        table.reliabridge-dataframe th {{
            background: rgba(128, 128, 128, 0.08);
            position: sticky;
            top: 0;
        }}
        </style>
        <div class="reliabridge-table-wrapper">{tabela}</div>
        """
    )

from madeiras import (
                            textos_pre_sizing_l,
                            montar_excel,
                            montar_excel_df,
                            chamando_nsga2,
                            chamar_sobol,
                            fronteira_pareto,
                            plot_sobol_total_indices,
                            plot_boxplot_variaveis_fronteira,
                            estatistica_descritiva_variaveis,
                            historico_hipervolume,
                            geracao_estabilizacao_hipervolume,
                            plot_convergencia_hipervolume,
                        )


# -----------------------------
# Helpers: assinatura + invalidação
# -----------------------------
def make_signature(d: dict) -> str:
    payload = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(payload).hexdigest()

def invalidate_results():
    st.session_state["has_results"] = False
    for k in [
        "df_resultados",
        "excel_bytes_resultados",
        "excel_bytes_entrada",
        "fig_png",
        "boxplot_png",
        "convergencia_png",
        "sobol_png",
        "df_estatistica",
        "hist_hv",
        "gen_estab",
        "zip_bytes",
        "sig_last",
        "sobol_args",
        "sobol_result",
    ]:
        st.session_state.pop(k, None)


def figura_para_png(fig, dpi: int = 200) -> bytes:
    """Serializa uma figura matplotlib em PNG e libera a memória associada."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


def montar_zip_pacote() -> bytes:
    """Monta o pacote de download com planilhas e todas as figuras disponíveis.

    As figuras são geradas no idioma corrente da interface, de modo que o pacote
    saia inteiramente em português ou em inglês. É chamada novamente após a análise
    de Sobol, para que o mapa de sensibilidade também entre no pacote.
    """

    itens = [
        ("beam_data.xlsx", st.session_state.get("excel_bytes_entrada")),
        ("pre_sizing_results_optimized.xlsx", st.session_state.get("excel_bytes_resultados")),
        ("pareto_frontier.png", st.session_state.get("fig_png")),
        ("design_variables_boxplot.png", st.session_state.get("boxplot_png")),
        ("hypervolume_convergence.png", st.session_state.get("convergencia_png")),
        ("sobol_total_indices.png", st.session_state.get("sobol_png")),
    ]

    df_estatistica = st.session_state.get("df_estatistica")
    if df_estatistica is not None and not df_estatistica.empty:
        itens.append(("design_variables_statistics.xlsx", montar_excel_df(df_estatistica)))

    hist_hv = st.session_state.get("hist_hv")
    if hist_hv is not None and not hist_hv.empty:
        itens.append(("hypervolume_convergence.csv", hist_hv.to_csv(index=False).encode("utf-8")))

    sobol_result = st.session_state.get("sobol_result")
    if sobol_result is not None:
        itens.append(
            ("sobol_total_indices.xlsx", montar_excel_df(sobol_result["total_order"]))
        )

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nome, conteudo in itens:
            if conteudo:
                zf.writestr(nome, conteudo)
    buffer.seek(0)
    return buffer.getvalue()

if "has_results" not in st.session_state:
    st.session_state["has_results"] = False


# -----------------------------
# UI text
# -----------------------------
lang = st.session_state.get("lang", "pt")
textos = textos_pre_sizing_l()
t = textos.get(lang, textos["pt"])
SOBOL_N_SAMPLES = 20000

CLASSE_CARREGAMENTO_MAP = {
    "permanent": "permanente",
    "long-term": "longa duração",
    "medium-term": "média duração",
    "short-term": "curta duração",
    "instantaneous": "instantânea",
}
CLASSE_MADEIRA_MAP = {
    "solid timber": "madeira natural",
    "engineered timber": "madeira recomposta",
}


def normalizar_opcao(valor: str, mapa: dict[str, str]) -> str:
    valor_normalizado = str(valor).strip().lower()
    return mapa.get(valor_normalizado, valor_normalizado)

st.header(t["titulo"])
with st.container():
    st.markdown(t["pre"])


# ============================================================
# 1) FORM PARA ENTRADA DE DADOS
# ============================================================
with st.container():

    st.subheader(t["geometria_t"])
    col1, col2 = st.columns(2)
    with col1:
        l = st.number_input(t["entrada_comprimento"], min_value=300.0, key="l")
    with col2:
        larg = st.number_input(t["pista"], min_value=200.0, key="larg")

    st.divider()

    st.subheader(t["variaveis_otimizacao"])
    col1, col2 = st.columns(2)
    with col1:
        tipo_secao_longarina = st.selectbox(t["entrada_tipo_secao_longarina"], t["tipo_secao_longarina"], key="tipo_secao_longarina")
        if str(tipo_secao_longarina).lower() == "circular":
            d_cm_min = st.number_input(t["diametro_minimo"], min_value=1.0, key="d_cm_min")
            d_cm_max = st.number_input(t["diametro_maximo"], min_value=1.0, key="d_cm_max")
        else:
            d_cm_min, d_cm_max, n_max = None
        n_min_long = st.number_input(t["espaço_min_longarinas"], value=0.0, min_value=0.0, key="n_min_long")
        n_max_long = st.number_input(t["espaço_max_longarinas"], value=0.0, min_value=0.0, key="n_max_long")

    with col2:
        tipo_secao_tabuleiro = st.selectbox(t["tipo_secao_tabuleiro"], t["tipo_secao_tabuleiro_opcoes"], key="tipo_secao_tabuleiro")
        if str(tipo_secao_tabuleiro).lower() in ["retangular", "rectangular"]:
            bw_min  = st.number_input(t["largura_viga_tabuleiro_min"], key="bw_min")
            bw_max  = st.number_input(t["largura_viga_tabuleiro_max"], key="bw_max")
            h_min   = st.number_input(t["altura_viga_tabuleiro_min"], key="h_min")
            h_max   = st.number_input(t["altura_viga_tabuleiro_max"], key="h_max")
        else:
            bw_min = bw_max = h_min = h_max = None
        n_min_tab = st.number_input(t["espaço_min_tabuleiros"], value=0.0, min_value=0.0, key="n_min_tab")
        n_max_tab = st.number_input(t["espaço_max_tabuleiros"], value=0.0, min_value=0.0, key="n_max_tab")

    st.divider()

    st.subheader(t["robustez_t"])
    perc_robustez = st.number_input(
        t["percentual_robustez"],
        min_value=0.0,
        value=5.0,
        step=0.1,
        format="%.2f",
        key="perc_robustez",
    )

    st.divider()

    st.subheader(t["cargas_projeto"])

    # "eixos" é o espaçamento LONGITUDINAL entre os três eixos do veículo tipo (1,50 m
    # pela NBR 7188), e não a bitola transversal de 2,00 m. É esse valor que entra em
    # M_qk = 3PL/4 - P.a e na flecha, onde b = (L - 2a)/2 posiciona os eixos externos.
    VEICULOS_PADRAO = {
        "TB240": {"roda": 40.0, "multidao": 4.0, "eixos": 1.5},
        "TB450": {"roda": 75.0, "multidao": 5.0, "eixos": 1.5}

    }

    if "p_rodak" not in st.session_state:
        st.session_state["p_rodak"] = 0.0
        st.session_state["p_qk"] = 0.0
        st.session_state["a"] = 0.0

    def atualizar_valores_veiculo():
        v = st.session_state["sel_veiculo"]
        if v in VEICULOS_PADRAO:
            st.session_state["p_rodak"] = VEICULOS_PADRAO[v]["roda"]
            st.session_state["p_qk"] = VEICULOS_PADRAO[v]["multidao"]
            st.session_state["a"] = VEICULOS_PADRAO[v]["eixos"]

    def set_custom_veiculo():
        st.session_state["sel_veiculo"] = t.get("veiculo_personalizado", "Personalizado")

    opcoes_veiculos = [t.get("veiculo_personalizado", "Personalizado")] + list(VEICULOS_PADRAO.keys())

    st.selectbox(
        t.get("veiculo_tipo", "Veículo Tipo"),
        options=opcoes_veiculos,
        index=0, # Padrão que vem selecionado (Personalizado)
        key="sel_veiculo",
        on_change=atualizar_valores_veiculo
    )

    col1, col2 = st.columns(2)
    with col1:
        p_rodak = st.number_input(t["carga_roda"], step=10.0, key="p_rodak", on_change=set_custom_veiculo)
        a       = st.number_input(t["distancia_eixos"], step=0.5, key="a", on_change=set_custom_veiculo)
    with col2:
        p_qk    = st.number_input(t["carga_multidao"], step=1.0, key="p_qk", on_change=set_custom_veiculo)
        p_gk    = st.number_input(t["carga_permanente"], step=1.0, key="p_gk")

    st.divider()

    st.subheader(t["classes_mad_carga"])
    col1, col2, col3 = st.columns(3)
    with col1:
        classe_carregamento_raw = st.selectbox(
            t["classe_carregamento"],
            t["classe_carregamento_opcoes"],
            key="classe_carregamento"
        )
    with col2:
        classe_madeira_raw = st.selectbox(
            t["classe_madeira"],
            t["classe_madeira_opcoes"],
            key="classe_madeira"
        )
    with col3:
        classe_umidade = st.selectbox(
            t["classe_umidade"],
            [1, 2, 3, 4],
            key="classe_umidade"
        )

    st.divider()

    st.subheader(t["coeficientes_seguranca"])
    col1, col2, col3 = st.columns(3)
    with col1:
        gamma_g = st.number_input(t["gamma_g"], step=0.1, key="gamma_g")
        gamma_q = st.number_input(t["gamma_q"], step=0.1, key="gamma_q")
    with col2:
        gamma_wf = st.number_input(t["gamma_wf"], step=0.1, key="gamma_wf")
        gamma_wc = st.number_input(t["gamma_wc"], step=0.1, key="gamma_wc")
    with col3:
        psi_2 = st.number_input(t["psi2"], step=0.1, key="psi_2")
        fluencia = st.number_input(t["considerar_fluencia"], step=0.1, key="phi")

    st.divider()

    st.subheader(t["prop_madeira"])

    CLASSES_MADEIRA = {
        "D20": {"densidade": 500.0,  "f_mk": 25.97, "f_vk": 4.0, "e_mod": 10.0},
        "D30": {"densidade": 625.0,  "f_mk": 38.96, "f_vk": 5.0, "e_mod": 12.0},
        "D40": {"densidade": 750.0,  "f_mk": 51.95, "f_vk": 6.0, "e_mod": 14.5},
        "D50": {"densidade": 850.0,  "f_mk": 64.94, "f_vk": 7.0, "e_mod": 16.5},
        "D60": {"densidade": 1000.0, "f_mk": 77.92, "f_vk": 8.0, "e_mod": 19.5}
    }

    if "densidade_long" not in st.session_state:
        st.session_state["densidade_long"] = 0.0
        st.session_state["f_mk_mpa"] = 0.0
        st.session_state["f_vk_mpa"] = 0.0
        st.session_state["e_modflex_gpa"] = 0.0

    if "densidade_tab" not in st.session_state:
        st.session_state["densidade_tab"] = 0.0
        st.session_state["f_mk_mpa_tab"] = 0.0

    def atualizar_valores_long():
        c = st.session_state["sel_classe_long"]
        if c in CLASSES_MADEIRA:
            st.session_state["densidade_long"] = CLASSES_MADEIRA[c]["densidade"]
            st.session_state["f_mk_mpa"] = CLASSES_MADEIRA[c]["f_mk"]
            st.session_state["f_vk_mpa"] = CLASSES_MADEIRA[c]["f_vk"]
            st.session_state["e_modflex_gpa"] = CLASSES_MADEIRA[c]["e_mod"]

    def atualizar_valores_tab():
        c = st.session_state["sel_classe_tab"]
        if c in CLASSES_MADEIRA:
            st.session_state["densidade_tab"] = CLASSES_MADEIRA[c]["densidade"]
            st.session_state["f_mk_mpa_tab"] = CLASSES_MADEIRA[c]["f_mk"]

    def set_custom_long():
        st.session_state["sel_classe_long"] = t.get("classe_personalizada", "Personalizado")

    def set_custom_tab():
        st.session_state["sel_classe_tab"] = t.get("classe_personalizada", "Personalizado")

    opcoes_classes = [t.get("classe_personalizada", "Personalizado")] + list(CLASSES_MADEIRA.keys())
    
    st.markdown(f"**{t['longarina_t']}**")
    
    st.selectbox(
        t.get("classe_resistencia_long", "Classe de Resistência (NBR 7190)"),
        options=opcoes_classes,
        index=0, # Padrão que vem selecionado (D60)
        key="sel_classe_long",
        on_change=atualizar_valores_long
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        densidade_long = st.number_input(t["densidade_long"], step=1.0, key="densidade_long")
    with col2:
        f_mk_mpa = st.number_input(t["f_mk"], step=0.1, key="f_mk_mpa")
    with col3:
        f_vk_mpa = st.number_input(t["f_vk"], step=0.1, key="f_vk_mpa")
    with col4:
        e_modflex_gpa = st.number_input(t["e_modflex"], step=0.1, key="e_modflex_gpa")

    st.markdown(f"**{t['tabuleiro_t']}**")

    st.selectbox(
        t.get("classe_resistencia_tab", "Classe de Resistência (NBR 7190)"),
        options=opcoes_classes,
        index=0, # Padrão que vem selecionado (D60)
        key="sel_classe_tab",
        on_change=atualizar_valores_tab
    )

    col1, col2 = st.columns(2)
    with col1:
        densidade_tab = st.number_input(t["densidade_tab"], step=10.0, key="densidade_tab", on_change=set_custom_tab)
    with col2:
        f_mk_mpa_tab = st.number_input(t["f_mk_tab"], step=1.0, key="f_mk_mpa_tab", on_change=set_custom_tab)

    st.divider()

    submitted_design = st.button(t["gerador_desempenho"], type="primary", use_container_width=True)


# ============================================================
# 2) DADOS DO PROJETO (sempre disponíveis)
# ============================================================
dados_projeto = {
                    f"{t['entrada_comprimento']}": l,
                    f"{t['pista']}": larg,
                    f"{t['tipo_secao_longarina']}": tipo_secao_longarina,
                    f"{t['tipo_secao_tabuleiro']}": tipo_secao_tabuleiro,
                    f"{t['carga_permanente']} (kPa)": p_gk,
                    f"{t['carga_roda']} (kN)": p_rodak,
                    f"{t['carga_multidao']} (kPa)": p_qk,
                    f"{t['distancia_eixos']} (m)": a,
                    f"{t['classe_carregamento']}": normalizar_opcao(classe_carregamento_raw, CLASSE_CARREGAMENTO_MAP),
                    f"{t['classe_madeira']}": normalizar_opcao(classe_madeira_raw, CLASSE_MADEIRA_MAP),
                    f"{t['classe_umidade']}": classe_umidade,
                    f"{t['gamma_g']}": gamma_g,
                    f"{t['gamma_q']}": gamma_q,
                    f"{t['gamma_wc']}": gamma_wc,
                    f"{t['gamma_wf']}": gamma_wf,
                    f"{t['psi2']}": psi_2,
                    f"{t['considerar_fluencia']}": fluencia,
                    f"{t['percentual_robustez']}": perc_robustez,
                    f"{t['densidade_long']} (kg/m³)": densidade_long,
                    f"{t['f_mk']} (MPa)": f_mk_mpa,
                    f"{t['f_vk']} (MPa)": f_vk_mpa,
                    f"{t['e_modflex']} (GPa)": e_modflex_gpa,
                    f"{t['densidade_tab']} (kg/m³)": densidade_tab,
                    f"{t['f_mk_tab']} (MPa)": f_mk_mpa_tab,
                }
excel_bytes = montar_excel(dados_projeto)


# ============================================================
# 3) INVALIDAÇÃO AUTOMÁTICA (se inputs mudarem)
# ============================================================
sig_now = make_signature(
    {
        "dados_projeto": dados_projeto,
        "limites_otimizacao": {
            "d_cm": [d_cm_min, d_cm_max],
            "bw_cm": [bw_min, bw_max],
            "h_cm": [h_min, h_max],
            "esp_long_cm": [n_min_long, n_max_long],
            "esp_tab_cm": [n_min_tab, n_max_tab],
        },
    }
)
sig_last = st.session_state.get("sig_last")

if st.session_state.get("has_results", False) and (sig_last is not None) and (sig_now != sig_last):
    invalidate_results()


# ============================================================
# 4) COMPUTE (apenas quando clicar em Gerar)
# ============================================================
if submitted_design:
    erros = []

    # ------------------------------------------------------------
    # Geometria geral
    # ------------------------------------------------------------
    if l <= 0:
        erros.append(f"- {t['entrada_comprimento']}")
    if larg <= 0:
        erros.append(f"- {t['pista']}")

    # ------------------------------------------------------------
    # Variáveis de otimização - Longarinas
    # ------------------------------------------------------------
    if str(tipo_secao_longarina).lower() == "circular":
        if d_cm_min is None or d_cm_min <= 0:
            erros.append(f"- {t['diametro_minimo']}")
        if d_cm_max is None or d_cm_max <= 0:
            erros.append(f"- {t['diametro_maximo']}")
        if d_cm_min is not None and d_cm_max is not None and d_cm_min > d_cm_max:
            erros.append(f"- {t['diametro_minimo']} > {t['diametro_maximo']}")
        if n_max_long is None or n_max_long <= 0:
            erros.append(f"- {t['espaço_max_longarinas']}")
        if n_min_long is not None and n_max_long is not None and n_min_long > n_max_long:
            erros.append(f"- {t['espaço_min_longarinas']} > {t['espaço_max_longarinas']}")

    # ------------------------------------------------------------
    # Variáveis de otimização - Tabuleiro
    # ------------------------------------------------------------
    if str(tipo_secao_tabuleiro).lower() in ["retangular", "rectangular"]:
        if bw_min is None or bw_min <= 0:
            erros.append(f"- {t['largura_viga_tabuleiro_min']}")
        if bw_max is None or bw_max <= 0:
            erros.append(f"- {t['largura_viga_tabuleiro_max']}")
        if h_min is None or h_min <= 0:
            erros.append(f"- {t['altura_viga_tabuleiro_min']}")
        if h_max is None or h_max <= 0:
            erros.append(f"- {t['altura_viga_tabuleiro_max']}")
        if bw_min is not None and bw_max is not None and bw_min > bw_max:
            erros.append(f"- {t['largura_viga_tabuleiro_min']} > {t['largura_viga_tabuleiro_max']}")
        if h_min is not None and h_max is not None and h_min > h_max:
            erros.append(f"- {t['altura_viga_tabuleiro_min']} > {t['altura_viga_tabuleiro_max']}")
        if n_max_tab is None or n_max_tab <= 0:
            erros.append(f"- {t['espaço_max_tabuleiros']}")
        if n_min_tab is not None and n_max_tab is not None and n_min_tab > n_max_tab:
            erros.append(f"- {t['espaço_min_tabuleiros']} > {t['espaço_max_tabuleiros']}")

    # ------------------------------------------------------------
    # Cargas
    # ------------------------------------------------------------
    if p_gk <= 0:
        erros.append(f"- {t['carga_permanente']}")
    if p_rodak <= 0:
        erros.append(f"- {t['carga_roda']}")
    if p_qk <= 0:
        erros.append(f"- {t['carga_multidao']}")
    if a <= 0:
        erros.append(f"- {t['distancia_eixos']}")

    # ------------------------------------------------------------
    # Coeficientes de segurança
    # ------------------------------------------------------------
    if gamma_g <= 0:
        erros.append(f"- {t['gamma_g']}")
    if gamma_q <= 0:
        erros.append(f"- {t['gamma_q']}")
    if gamma_wf <= 0:
        erros.append(f"- {t['gamma_wf']}")
    if gamma_wc <= 0:
        erros.append(f"- {t['gamma_wc']}")
    if psi_2 <= 0:
        erros.append(f"- {t['psi2']}")
    if fluencia <= 0:
        erros.append(f"- {t['considerar_fluencia']}")
    if perc_robustez < 0:
        erros.append(f"- {t['percentual_robustez']}")

    # ------------------------------------------------------------
    # Propriedades da madeira
    # ------------------------------------------------------------
    if densidade_long <= 0:
        erros.append(f"- {t['densidade_long']}")
    if f_mk_mpa <= 0:
        erros.append(f"- {t['f_mk']}")
    if f_vk_mpa <= 0:
        erros.append(f"- {t['f_vk']}")
    if e_modflex_gpa <= 0:
        erros.append(f"- {t['e_modflex']}")

    if densidade_tab <= 0:
        erros.append(f"- {t['densidade_tab']}")
    if f_mk_mpa_tab <= 0:
        erros.append(f"- {t['f_mk_tab']}")

    # ------------------------------------------------------------
    # Resultado da validação
    # ------------------------------------------------------------
    if erros:
        st.error("Os seguintes campos devem ser preenchidos com valores maiores que zero:\n\n" + "\n".join(erros))
        st.stop()

    # Se passou na validação, segue o processamento
    st.success("Dados validados com sucesso.")
    st.session_state["sig_last"] = sig_now

    ds       = [float(d_cm_min), float(d_cm_max)]
    bws      = [float(bw_min),   float(bw_max)]
    hs       = [float(h_min),    float(h_max)]
    n_p_long = [float(n_min_long), float(n_max_long)]
    n_p_tab  = [float(n_min_tab),  float(n_max_tab)]

    # NSGA-II (com histórico, para a curva de convergência do hipervolume)
    try:
        res_nsga, res_pymoo = chamando_nsga2(
                                                    dados_projeto, ds, bws, hs, n_p_long, n_p_tab, t, salvar_historico=True
                                                )
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    # Convergência do hipervolume. Falha aqui não deve derrubar o pré-dimensionamento,
    # que é o resultado principal da tela.
    hist_hv, gen_estab = None, None
    try:
        hist_hv = historico_hipervolume(res_pymoo)
        gen_estab = geracao_estabilizacao_hipervolume(hist_hv)
    except Exception as exc:
        st.warning(f"Convergência não pôde ser calculada: {exc}")

    # padroniza DataFrame final (PT/EN)
    if lang == "pt":
        df_resultados = pd.DataFrame({
                                        "d_cm": res_nsga["d [cm]"].tolist(),
                                        "esp_cm": res_nsga["esp [cm]"].tolist(),
                                        "bw_cm": res_nsga["bw [cm]"].tolist(),
                                        "h_cm": res_nsga["h [cm]"].tolist(),
                                        "esp_tab_cm": res_nsga["esp tab [cm]"].tolist(),
                                        "of_volume_m3": res_nsga["volume [m³]"].tolist(),
                                        "of_fator_flecha": res_nsga["delta [-]"].tolist(),
                                        "longarina_g_m": res_nsga["flex lim beam [(Ms-Mr)/Mr]"].tolist(),
                                        "longarina_g_v": res_nsga["cis lim beam [(Vs-Vr)/Vr]"].tolist(),
                                        "longarina_g_f": res_nsga["delta lim beam [(ps-pr)/pr]"].tolist(),
                                        "tabuleiro_g_m": res_nsga["flex lim deck [(Ms-Mr)/Mr]"].tolist(),
                                        "longarina_g_esp": res_nsga["spacing beam"].tolist(),
                                        "tabuleiro_g_esp": res_nsga["spacing deck"].tolist(),
                                    })
        x = df_resultados["of_volume_m3"].to_numpy()
        y = df_resultados["of_fator_flecha"].to_numpy()
    else:
        df_resultados = pd.DataFrame({
                                        "d_cm": res_nsga["d [cm]"].tolist(),
                                        "esp_cm": res_nsga["esp [cm]"].tolist(),
                                        "bw_cm": res_nsga["bw [cm]"].tolist(),
                                        "h_cm": res_nsga["h [cm]"].tolist(),
                                        "deck_spacing_cm": res_nsga["esp tab [cm]"].tolist(),
                                        "of_volume_m3": res_nsga["volume [m³]"].tolist(),
                                        "of_deflection_factor": res_nsga["delta [-]"].tolist(),
                                        "beam_g_m": res_nsga["flex lim beam [(Ms-Mr)/Mr]"].tolist(),
                                        "beam_g_v": res_nsga["cis lim beam [(Vs-Vr)/Vr]"].tolist(),
                                        "beam_g_f": res_nsga["delta lim beam [(ps-pr)/pr]"].tolist(),
                                        "deck_g_m": res_nsga["flex lim deck [(Ms-Mr)/Mr]"].tolist(),
                                        "beam_g_spacing": res_nsga["spacing beam"].tolist(),
                                        "deck_g_spacing": res_nsga["spacing deck"].tolist(),
                                    })
        x = df_resultados["of_volume_m3"].to_numpy()
        y = df_resultados["of_deflection_factor"].to_numpy()

    # Excel dos resultados
    excel_bytes_resultados = montar_excel_df(df_resultados)

    # Figuras. Todas são geradas com o dicionário de textos do idioma corrente,
    # de modo que o pacote baixado sai inteiramente em português ou em inglês.
    coluna_esp_tab = "esp_tab_cm" if "esp_tab_cm" in df_resultados.columns else "deck_spacing_cm"
    colunas_variaveis = ["d_cm", "bw_cm", "h_cm", "esp_cm", coluna_esp_tab]

    fig_png = figura_para_png(
        fronteira_pareto(x.tolist(), y.tolist(), t["tag_x_fig"], t["tag_y_fig"])
    )
    boxplot_png = figura_para_png(
        plot_boxplot_variaveis_fronteira(
            df_resultados, colunas_variaveis,
            t["fronteira_variaveis_labels"], t["fronteira_variaveis_y"],
        )
    )
    convergencia_png = None
    if hist_hv is not None:
        convergencia_png = figura_para_png(
            plot_convergencia_hipervolume(
                {t["convergencia_serie"]: hist_hv},
                label_x=t["convergencia_x"], label_y=t["convergencia_y"],
            )
        )

    df_estatistica = estatistica_descritiva_variaveis(
        df_resultados, colunas_variaveis,
        t["fronteira_variaveis_labels"], t["estatistica_colunas"],
    )

    # Persistência (para sobreviver a reruns)
    st.session_state["df_resultados"] = df_resultados
    st.session_state["excel_bytes_resultados"] = excel_bytes_resultados
    st.session_state["fig_png"] = fig_png
    st.session_state["boxplot_png"] = boxplot_png
    st.session_state["convergencia_png"] = convergencia_png
    st.session_state["df_estatistica"] = df_estatistica
    st.session_state["excel_bytes_entrada"] = excel_bytes
    st.session_state["hist_hv"] = hist_hv
    st.session_state["gen_estab"] = gen_estab
    st.session_state["zip_bytes"] = montar_zip_pacote()
    st.session_state["sobol_args"] = {
        "dados": dados_projeto.copy(),
        "ds": ds,
        "bws": bws,
        "hs": hs,
        "n_long": n_p_long,
        "n_tab": n_p_tab,
        "t": t.copy(),
    }
    st.session_state.pop("sobol_result", None)
    st.session_state["has_results"] = True


# ============================================================
# 5) RENDER (sempre que houver resultados em cache)
# ============================================================
if st.session_state.get("has_results", False):
    st.subheader(t["gerador_desempenho"])
    exibir_dataframe_html(st.session_state["df_resultados"])

    # As figuras são reaproveitadas do PNG já gerado, e não redesenhadas a cada
    # rerun: a tela mostra exatamente o mesmo arquivo que vai no pacote de download.

    # --- Dispersão das variáveis de projeto (boxplot + estatística descritiva) ---
    st.subheader(t["fronteira_variaveis_head"])
    st.caption(t["fronteira_variaveis_info"])
    col_esq, col_meio, col_dir = st.columns([1, 4, 1])
    with col_meio:
        st.image(st.session_state["boxplot_png"])

    st.markdown(f"**{t['estatistica_head']}**")
    st.caption(t["estatistica_info"])
    exibir_dataframe_html(st.session_state["df_estatistica"], esconder_indice=True)

    # --- Fronteira eficiente ---
    st.subheader(t["fronteira_head"])
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        st.image(st.session_state["fig_png"])

    # --- Convergência do NSGA-II ---
    hist_hv_cached = st.session_state.get("hist_hv")
    convergencia_png_cached = st.session_state.get("convergencia_png")
    if convergencia_png_cached is not None:
        st.subheader(t["convergencia_head"])
        st.caption(t["convergencia_info"])
        col_esq, col_meio, col_dir = st.columns([1, 2, 1])
        with col_meio:
            st.image(convergencia_png_cached)

        gen_estab_cached = st.session_state.get("gen_estab")
        if gen_estab_cached and gen_estab_cached > 0 and hist_hv_cached is not None:
            st.info(
                t["convergencia_estabiliza"].format(
                    hv=float(hist_hv_cached["hipervolume"].iloc[-1]),
                    gen=gen_estab_cached,
                    total=len(hist_hv_cached),
                )
            )


    st.subheader(t["sobol_head"])
    st.caption(t["sobol_info"])

    sobol_args = st.session_state.get("sobol_args")
    if sobol_args is None:
        st.warning(t.get("aviso_gerar_primeiro", "Sem resultados atuais. Clique em Gerar para processar."))
    else:
        st.caption(
            "Intervalos usados no Sobol: "
            f"d={sobol_args['ds']} cm; bw={sobol_args['bws']} cm; "
            f"h={sobol_args['hs']} cm; esp. long.={sobol_args['n_long']} cm; "
            f"esp. tab.={sobol_args['n_tab']} cm."
        )
        # Nunca mantenha um mapa anterior se a nova análise falhar.
        st.session_state.pop("sobol_result", None)
        st.session_state.pop("sobol_png", None)
        try:
            with st.spinner(t["sobol_spinner"]):
                st.session_state["sobol_result"] = chamar_sobol(
                    sobol_args["dados"],
                    sobol_args["ds"],
                    sobol_args["bws"],
                    sobol_args["hs"],
                    sobol_args["n_long"],
                    sobol_args["n_tab"],
                    sobol_args["t"],
                    n_samples=SOBOL_N_SAMPLES,
                )
            # Gera a figura e reconstrói o pacote, para que o mapa de Sobol
            # também fique disponível no ZIP de download.
            st.session_state["sobol_png"] = figura_para_png(
                plot_sobol_total_indices(
                    st.session_state["sobol_result"]["total_order"],
                    label_x=t["sobol_axis_constraints"],
                    label_y=t["sobol_axis_variables"],
                    x_labels=t["sobol_constraint_labels"],
                    y_labels=t["sobol_variable_labels"],
                )
            )
            st.session_state["zip_bytes"] = montar_zip_pacote()
        except Exception as exc:
            st.error(str(exc))

    if "sobol_result" in st.session_state and st.session_state.get("sobol_png"):
        sobol_result = st.session_state["sobol_result"]
        st.markdown(f"**{t['sobol_total_order']}**")
        st.caption(
            "Modelo Sobol executado: "
            f"{sobol_result.get('model_version', 'versão antiga/sem identificação')} · "
            f"{sobol_result.get('n_samples', '?')} amostras base"
        )
        col_esq, col_meio, col_dir = st.columns([1, 4, 1])
        with col_meio:
            st.image(st.session_state["sobol_png"])

        sobol_export = sobol_result["total_order"].assign(indice="total_order")
        st.download_button(
            label=t["sobol_download"],
            data=montar_excel_df(sobol_export),
            file_name="sobol_constraints.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.download_button(
        label=t["botao_dados_down"],
        data=st.session_state["zip_bytes"],
        file_name="pre_sizing_package.zip",
        mime="application/zip",
    )

else:
    st.warning(t.get("aviso_gerar_primeiro", "Sem resultados atuais. Clique em “Gerar” para processar."))
