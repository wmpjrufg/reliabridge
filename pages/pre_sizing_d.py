import streamlit as st
import numpy as np
import pandas as pd

from madeiras import checagem_completa_longarina_madeira_flexao, textos_pre_sizing_d, montar_excel


# Idioma: vem da HOME
lang = st.session_state.get("lang", "pt")
textos = textos_pre_sizing_d()
t = textos.get(lang, textos["pt"])

# UI
st.header(t["titulo"])
st.subheader(t["pre"])

with st.form("form_geometria", clear_on_submit=False):
    l = st.number_input(t["entrada_comprimento"], min_value=3.0, value=6.0)

    espaco_min = st.number_input(t["espaçamento_entre_longarinas_min"], value=0.50)
    espaco_max = st.number_input(t["espaçamento_entre_longarinas_max"], value=2.50)
    bw_min_tab = st.number_input(t["largura_minima_tab"], value=3.0)
    bw_max_tab = st.number_input(t["largura_maxima_tab"], value=10.0)
    h_min_tab = st.number_input(t["altura_minima_tab"], value=0.20)
    h_max_tab = st.number_input(t["altura_maxima_tab"], value=0.00)

    p_gk = st.number_input(t["carga_permanente"], value=10.0)
    p_rodak = st.number_input(t["carga_roda"], value=40.0)
    p_qk = st.number_input(t["carga_multidao"], value=4.0)
    a = st.number_input(t["distancia_eixos"], value=1.5)

    classe_carregamento_raw = st.selectbox(
                                            t["classe_carregamento"],
                                            t["classe_carregamento_opcoes"],
                                        )
    classe_madeira_raw = st.selectbox(
                                        t["classe_madeira"],
                                        t["classe_madeira_opcoes"],
                                    )
    classe_umidade = st.selectbox(t["classe_umidade"], [1, 2, 3, 4])

    gamma_g = st.number_input(t["gamma_g"], value=1.40, step=0.1)
    gamma_q = st.number_input(t["gamma_q"], value=1.40, step=0.1)
    gamma_w = st.number_input(t["gamma_w"], value=1.40, step=0.1)

    f_mk_mpa = st.number_input(t["f_mk"], value=0.0)
    f_vk_mpa = st.number_input(t["f_vk"], value=0.0)
    e_modflex_gpa = st.number_input(t["e_modflex"], value=12.0)

    submitted_design = st.form_submit_button(t["gerador_desempenho"])

# -------------------------------------------------------
# Download: sempre disponível (dados atuais do formulário)
# (não salva nada; só serializa e entrega)
# -------------------------------------------------------
dados_projeto = {
    "l (m)": l,
    "tipo_secao": tipo_secao,
    "p_gk (kN/m)": p_gk,
    "p_rodak (kN)": p_rodak,
    "p_qk (kN/m²)": p_qk,
    "a (m)": a,
    "classe_carregamento": classe_carregamento_raw.lower(),
    "classe_madeira": classe_madeira_raw.lower(),
    "classe_umidade": classe_umidade,
    "gamma_g": gamma_g,
    "gamma_q": gamma_q,
    "gamma_w": gamma_w,
    "f_mk (MPa)": f_mk_mpa,
    "f_vk (MPa)": f_vk_mpa,
    "e_modflex (GPa)": e_modflex_gpa,
}
excel_bytes = montar_excel(dados_projeto)

# -------------------------------------------------------
# Cálculo: SOMENTE no submit
# Sem persistência do resultado
# -------------------------------------------------------
if submitted_design:
    # Conversões coerentes (as suas)
    f_mk = f_mk_mpa * 1e3               # MPa -> kPa
    f_vk = f_vk_mpa * 1e3               # MPa -> kPa
    e_modflex = e_modflex_gpa * 1e6     # GPa -> kPa

    # flexão da longarina de madeira
    n_mc = 1000
    d_cm_vals = np.linspace(d_cm_min, d_cm_max, n_mc)
    out = {"d_cm": [], "g_m": [], "g_v": [], "g_f": []}

    for d in d_cm_vals:
        geo_long = {"d": d / 100.0}  # cm -> m
        res_m, res_v, res_f_var, res_f_total, relat = checagem_completa_longarina_madeira_flexao(
                                                                                                    geo_long,
                                                                                                    p_gk,
                                                                                                    p_qk,
                                                                                                    p_rodak,
                                                                                                    a,
                                                                                                    l,
                                                                                                    classe_carregamento_raw.lower(),
                                                                                                    classe_madeira_raw.lower(),
                                                                                                    classe_umidade,
                                                                                                    gamma_g,
                                                                                                    gamma_q,
                                                                                                    gamma_w,
                                                                                                    f_mk,
                                                                                                    f_vk,
                                                                                                    e_modflex,
                                                                                                )

        out["d_cm"].append(d)
        out["g_m"].append(res_m["g [kN/m²]"])
        out["g_v"].append(res_v["g [kN]"])
        out["g_f"].append(res_f_var["g [m]"])

    df_resultados = pd.DataFrame(out)
    df_filter_longarina = df_resultados[
                                            (df_resultados["g_m"] >= 0.0)
                                            & (df_resultados["g_v"] >= 0.0)
                                            & (df_resultados["g_f"] >= 0.0)
                                        ].copy()

    st.subheader(t.get("tabela_desempenho", "Tabela de desempenho estrutural via Análise de Monte Carlo"))
    st.dataframe(df_filter_longarina)
    st.download_button(
                            label=t.get("botao_dados_down", "Download dos dados do projeto"),
                            data=excel_bytes,
                            file_name="deck_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

else:
    st.warning(t.get("aviso_gerar_primeiro", "Sem resultados atuais. Clique em “Gerar” para processar."))
