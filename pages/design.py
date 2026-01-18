import streamlit as st
import pandas as pd
from madeiras import textos_design


# Idioma: vem da HOME
lang = st.session_state.get("lang", "pt")
textos = textos_design()
t = textos.get(lang, textos["pt"])

# UI
st.header(t["titulo"])
st.subheader(t["projeto"])

# Seleção dos dados iniciais
uploaded_file = st.file_uploader(t["upload_label"], type=["xlsx"])
if uploaded_file is None:
    st.info("Faça o upload de um arquivo .xlsx para continuar.")
    st.stop()
df_input = pd.read_excel(uploaded_file)
st.write(df_input.T)

# 


# # 2) Informando as seções comerciais desejadas para dimensionamento
# with st.form("form_dados_design", clear_on_submit=False):
#     tipo_secao = dados.loc["tipo_secao"].values[0]
#     if tipo_secao.lower() == "circular":
#         diametro_desejado = st.number_input(t["diametro_desejado"], step=0.5, key="diametro_desejado")
#         geo = {"d": diametro_desejado / 100} 
#     else:
#         pass
#     submitted = st.form_submit_button(t["gerador_projeto"])
#     if submitted:
#         l = dados.loc["l (m)"].values[0]
#         b_wpista_m = dados.loc["b_wpista (m)"].values[0]
#         p_gk = dados.loc["p_gk (kN/m)"].values[0]
#         p_rodak = dados.loc["p_rodak (kN)"].values[0]
#         p_qk = dados.loc["p_qk (kN/m²)"].values
#         a = dados.loc["a (m)"].values[0]
#         classe_carregamento = dados.loc["classe_carregamento"].values[0]
#         classe_madeira = dados.loc["classe_madeira"].values[0]
#         classe_umidade = dados.loc["classe_umidade"].values[0]
#         gamma_g = dados.loc["gamma_g"].values[0]
#         gamma_q = dados.loc["gamma_q"].values[0]
#         gamma_w = dados.loc["gamma_w"].values[0]
#         f_ck = dados.loc["f_ck (MPa)"].values[0]
#         f_tk = dados.loc["f_tk (MPa)"].values[0]
#         f_mk = dados.loc["f_mk (MPa)"].values[0]
#         f_vk = dados.loc["f_vk (MPa)"].values[0]
#         e_cm = dados.loc["e_modflex (GPa)"].values[0]
#         # MPa -> kPa (1e3); GPa -> kPa (1e6)
#         f_ck = f_ck * 1e3
#         f_tk = f_tk * 1e3
#         f_mk = f_mk * 1e3
#         f_vk = f_vk * 1e3
#         e_cm = e_cm * 1e6
#         res_m, res_v, res_f_var, res_f_total, relat = checagem_completa_longarina_madeira_flexao(
#                                                                                                     geo,
#                                                                                                     p_gk,
#                                                                                                     p_qk,
#                                                                                                     p_rodak,
#                                                                                                     a,
#                                                                                                     l,
#                                                                                                     classe_carregamento,
#                                                                                                     classe_madeira,
#                                                                                                     classe_umidade,
#                                                                                                     gamma_g,
#                                                                                                     gamma_q,
#                                                                                                     gamma_w,
#                                                                                                     f_ck,
#                                                                                                     f_tk,
#                                                                                                     f_mk,
#                                                                                                     f_vk,
#                                                                                                     e_cm,
#                                                                                                 )
#         eff = {"sigma_sd/f_md": res_m["sigma_sd/f_md"], "tau_sd/f_vd": res_v["tau_sd/f_vd"]}
#         df_resultado = pd.DataFrame(eff, index=[f"{diametro_desejado} cm"])
#         st.write(t["res"])
#         st.dataframe(df_resultado.T)