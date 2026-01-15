import streamlit as st
import pandas as pd
from madeiras import checagem_completa_longarina_madeira_flexao, plot_longarinas_circulares

lang = st.session_state.get("lang", "pt")
if "diametro_desejado" not in st.session_state:
    st.session_state["diametro_desejado"] = 0.0

textos = {
    "pt": {
        "titulo": "Projeto paramétrico de uma Longarina de madeira",
        "projeto": "Projeto da Longarina de madeira",
        "entrada_dados": "Tipo de entrada dos dados:",
        "opcoes_entrada_dados": ["Dados da interface", "Importar arquivo Excel"],
        "upload_label": "Selecione o arquivo Excel",
        "botao_importar": "Importar dados do Excel",
        "diametro_desejado": "Diâmetro comercial desejado (cm):",
        "gerador_projeto": "Gerar dimensionamento",
        "res": "Resultados da eficiência do dimensionamento considerando a razão S/R (S = Solicitação, R = Resistência), com os coeficientes de segurança devidamente aplicados.",
    },
    "en": {
        "titulo": "Parametric design of a wooden stringer",
        "projeto": "Wooden stringer design",
        "entrada_dados": "Type of data input:",
        "opcoes_entrada_dados": ["Interface data", "Import Excel file"],
        "upload_label": "Select the Excel file",
        "botao_importar": "Import data from Excel",
        "diametro_desejado": "Desired commercial diameter (cm):",
        "gerador_projeto": "Generate design",
        "res": "Results of the design efficiency considering the S/R ratio (S = Demand, R = Resistance), with safety factors duly applied.",

    },
}

# UI
t = textos.get(lang, textos["pt"])
st.header(t["titulo"])
st.subheader(t["projeto"])

# 1) Seleção do modo de upload das informações
tipo_dados = st.selectbox(t["entrada_dados"], t["opcoes_entrada_dados"])
if tipo_dados == t["opcoes_entrada_dados"][1]:
    uploaded_file = st.file_uploader(t["upload_label"], type=["xlsx"])
    if uploaded_file is not None:
        df_input = pd.read_excel(uploaded_file)
        df_input = df_input.drop(columns=["d_cm_min", "d_cm_max"])
        st.write(df_input.T)
    else:
        st.info("Faça upload do arquivo .xlsx para continuar.")
else:
    dados = st.session_state.get("dados_projeto")
    dados = pd.DataFrame([dados])
    dados = dados.T
    st.write(dados)

# 2) Informando as seções comerciais desejadas para dimensionamento
with st.form("form_dados_design", clear_on_submit=False):
    tipo_secao = dados.loc["tipo_secao"].values[0]
    if tipo_secao.lower() == "circular":
        diametro_desejado = st.number_input(t["diametro_desejado"], step=0.5, key="diametro_desejado")
        geo = {"d": diametro_desejado / 100} 
    else:
        pass
    submitted = st.form_submit_button(t["gerador_projeto"])
    if submitted:
        l = dados.loc["l (m)"].values[0]
        b_wpista_m = dados.loc["b_wpista (m)"].values[0]
        p_gk = dados.loc["p_gk (kN/m)"].values[0]
        p_rodak = dados.loc["p_rodak (kN)"].values[0]
        p_qk = dados.loc["p_qk (kN/m²)"].values
        a = dados.loc["a (m)"].values[0]
        classe_carregamento = dados.loc["classe_carregamento"].values[0]
        classe_madeira = dados.loc["classe_madeira"].values[0]
        classe_umidade = dados.loc["classe_umidade"].values[0]
        gamma_g = dados.loc["gamma_g"].values[0]
        gamma_q = dados.loc["gamma_q"].values[0]
        gamma_w = dados.loc["gamma_w"].values[0]
        f_ck = dados.loc["f_ck (MPa)"].values[0]
        f_tk = dados.loc["f_tk (MPa)"].values[0]
        f_mk = dados.loc["f_mk (MPa)"].values[0]
        f_vk = dados.loc["f_vk (MPa)"].values[0]
        e_cm = dados.loc["e_modflex (GPa)"].values[0]
        # MPa -> kPa (1e3); GPa -> kPa (1e6)
        f_ck = f_ck * 1e3
        f_tk = f_tk * 1e3
        f_mk = f_mk * 1e3
        f_vk = f_vk * 1e3
        e_cm = e_cm * 1e6
        res_m, res_v, res_f_var, res_f_total, relat = checagem_completa_longarina_madeira_flexao(
                                                                                                    geo,
                                                                                                    p_gk,
                                                                                                    p_qk,
                                                                                                    p_rodak,
                                                                                                    a,
                                                                                                    l,
                                                                                                    classe_carregamento,
                                                                                                    classe_madeira,
                                                                                                    classe_umidade,
                                                                                                    gamma_g,
                                                                                                    gamma_q,
                                                                                                    gamma_w,
                                                                                                    f_ck,
                                                                                                    f_tk,
                                                                                                    f_mk,
                                                                                                    f_vk,
                                                                                                    e_cm,
                                                                                                )
        eff = {"sigma_sd/f_md": res_m["sigma_sd/f_md"], "tau_sd/f_vd": res_v["tau_sd/f_vd"]}
        df_resultado = pd.DataFrame(eff, index=[f"{diametro_desejado} cm"])
        st.write(t["res"])
        st.dataframe(df_resultado.T)