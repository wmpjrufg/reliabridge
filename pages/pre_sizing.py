import streamlit as st
import numpy as np
import pandas as pd

from madeiras import checagem_completa_longarina_madeira_flexao, textos_pre_sizing_l, montar_excel, chamando_nsga2, ProjetoOtimo

# Idioma: vem da HOME
lang = st.session_state.get("lang", "pt")
textos = textos_pre_sizing_l()
t = textos.get(lang, textos["pt"])

# UI
st.header(t["titulo"])
st.subheader(t["pre"])
with st.form("form_geometria", clear_on_submit=False):
    l = st.number_input(t["entrada_comprimento"], min_value=3.0)
    larg = st.number_input(t["pista"], min_value=0.5)

    tipo_secao_longarina = st.selectbox(t["entrada_tipo_secao_longarina"], t["tipo_secao_longarina"])
    if tipo_secao_longarina.lower() == "circular":
        d_cm_min = st.number_input(t["diametro_minimo"])
        d_cm_max = st.number_input(t["diametro_maximo"])
    tipo_secao_tabuleiro = st.selectbox(t["tipo_secao_tabuleiro"], t["tipo_secao_tabuleiro_opcoes"])
    if tipo_secao_tabuleiro.lower() == "retangular":
        esp_min = st.number_input(t["espaçamento_entre_longarinas_min"])
        esp_max = st.number_input(t["espaçamento_entre_longarinas_max"])
        bw_min = st.number_input(t["largura_viga_tabuleiro_min"])
        bw_max = st.number_input(t["largura_viga_tabuleiro_max"])
        h_min = st.number_input(t["altura_viga_tabuleiro_min"])
        h_max = st.number_input(t["altura_viga_tabuleiro_max"])

    p_gk = st.number_input(t["carga_permanente"])
    p_rodak = st.number_input(t["carga_roda"])
    p_qk = st.number_input(t["carga_multidao"])
    a = st.number_input(t["distancia_eixos"])

    classe_carregamento_raw = st.selectbox(t["classe_carregamento"], t["classe_carregamento_opcoes"])
    classe_madeira_raw = st.selectbox(t["classe_madeira"], t["classe_madeira_opcoes"])
    classe_umidade = st.selectbox(t["classe_umidade"], [1, 2, 3, 4])

    gamma_g = st.number_input(t["gamma_g"], step=0.1)
    gamma_q = st.number_input(t["gamma_q"], step=0.1)
    gamma_w = st.number_input(t["gamma_w"], step=0.1)
    psi_2 = st.number_input(t["psi2"], step=0.1)
    fluencia = st.number_input(t["considerar_fluencia"], step=0.1)

    densidade_long = st.number_input(t["densidade_long"], step=1.0)
    f_mk_mpa = st.number_input(t["f_mk"], step=0.1)
    f_vk_mpa = st.number_input(t["f_vk"], step=0.1)
    e_modflex_gpa = st.number_input(t["e_modflex"], step=0.1)

    densidade_tab = st.number_input(t["densidade_tab"], step=1.0)
    f_mk_mpa_tab = st.number_input(t["f_mk_tab"], step=0.1) 

    submitted_design = st.form_submit_button(t["gerador_desempenho"])

# -------------------------------------------------------
# Download: sempre disponível (dados atuais do formulário)
# (não salva nada; só serializa e entrega)
# -------------------------------------------------------
if lang == "pt":
    dados_projeto = {
                        "l (cm)": l,
                        "b_wpista (cm)": larg,
                        "tipo_secao_longarina": tipo_secao_longarina,
                        "tipo_secao_tabuleiro": tipo_secao_tabuleiro,
                        "p_gk (kN/m²)": p_gk,
                        "p_rodak (kN)": p_rodak,
                        "p_qk (kN/m²)": p_qk,
                        "a (m)": a,
                        "classe_carregamento": classe_carregamento_raw.lower(),
                        "classe_madeira": classe_madeira_raw.lower(),
                        "classe_umidade": classe_umidade,
                        "gamma_g": gamma_g,
                        "gamma_q": gamma_q,
                        "gamma_w": gamma_w,
                        "psi_2": psi_2,
                        "phi": fluencia,
                        "densidade longarina (kg/m³)": densidade_long,
                        "resistência característica à flexão longarina (MPa)": f_mk_mpa,
                        "resistência característica ao cisalhamento longarina (MPa)": f_vk_mpa,
                        "módulo de elasticidade à flexão longarina (GPa)": e_modflex_gpa,
                        "densidade tabuleiro (kg/m³)": densidade_tab,
                        "resistência característica à flexão tabuleiro (MPa)": f_mk_mpa_tab,
                    }
else:
    pass
excel_bytes = montar_excel(dados_projeto)

# -------------------------------------------------------
# Cálculo: SOMENTE no submit
# Sem persistência do resultado
# -------------------------------------------------------
if submitted_design:
    out_en = {"d_cm": [], "esp_cm": [], "bw_cm": [], "h_cm": [], "area_m2": [], "deflection_m": [], "beam_g_m": [], "beam_g_v": [], "beam_g_f": [], "deck_g_m": []}
    out_pt = {"d_cm": [], "esp_cm": [], "bw_cm": [], "h_cm": [], "area_m2": [], "deflecção_m": [], "longarina_g_m": [], "longarina_g_v": [], "longarina_g_f": [], "tabuleiro_g_m": []}
    ds = [d_cm_min, d_cm_max]
    esps = [esp_min, esp_max]
    bws = [bw_min, bw_max]
    hs = [h_min, h_max]
    res_nsga = chamando_nsga2(dados_projeto, ds, esps, bws, hs)
    if lang == "pt":
        out_pt["d_cm"] = res_nsga["d [cm]"].tolist()
        out_pt["esp_cm"] = res_nsga["esp [cm]"].tolist()
        out_pt["bw_cm"] = res_nsga["bw [cm]"].tolist()
        out_pt["h_cm"] = res_nsga["h [cm]"].tolist()
        out_pt["area_m2"] = res_nsga["area [m²]"].tolist()
        out_pt["deflecção_m"] = res_nsga["delta [m]"].tolist()
        out_pt["longarina_g_m"] = res_nsga["flex lim beam [kPa]"].tolist()
        out_pt["longarina_g_v"] = res_nsga["cis lim beam [kPa]"].tolist()
        out_pt["longarina_g_f"] = res_nsga["defl lim beam [m]"].tolist()
        out_pt["tabuleiro_g_m"] = res_nsga["flex lim deck [kPa]"].tolist()
        df_resultados = pd.DataFrame(out_pt)
        st.subheader(t["gerador_desempenho"])
    else:
        out_en["d_cm"] = res_nsga["d [cm]"].tolist()
        out_en["esp_cm"] = res_nsga["esp [cm]"].tolist()
        out_en["bw_cm"] = res_nsga["bw [cm]"].tolist()
        out_en["h_cm"] = res_nsga["h [cm]"].tolist()
        out_en["area_m2"] = res_nsga["area [m²]"].tolist()
        out_en["deflection_m"] = res_nsga["delta [m]"].tolist()
        out_en["beam_g_m"] = res_nsga["flex lim beam [kPa]"].tolist()
        out_en["beam_g_v"] = res_nsga["cis lim beam [kPa]"].tolist()
        out_en["beam_g_f"] = res_nsga["defl lim beam [m]"].tolist()
        out_en["deck_g_m"] = res_nsga["flex lim deck [kPa]"].tolist()
        df_resultados = pd.DataFrame(out_en)
        st.subheader(t["gerador_desempenho"])
    st.dataframe(df_resultados)
    st.download_button(
                            label=t.get("botao_dados_down", "Download dos dados do projeto"),
                            data=excel_bytes,
                            file_name="beam_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
    
else:
    st.warning(t.get("aviso_gerar_primeiro", "Sem resultados atuais. Clique em “Gerar” para processar."))
