import streamlit as st
import numpy as np
import pandas as pd
import io

from madeiras import checagem_completa_longarina_madeira_flexao, plot_longarinas_circulares


lang = st.session_state.get("lang", "pt")
if "df_filter" not in st.session_state:
    st.session_state["df_filter"] = None
if "dados_projeto" not in st.session_state:
    st.session_state["dados_projeto"] = None


textos = {
            "pt": {
                "titulo": "Projeto paramétrico de uma Longarina de madeira",
                "pre": "Pré-dimensionamento da seção transversal",
                "entrada_comprimento": "Comprimento da viga (m)",
                "pista": "Largura da pista (m)",
                "entrada_tipo_secao": "Tipo de seção",
                "tipo_secao": ["Circular"],
                "diametro_minimo": "Diâmetro mínimo (cm)",
                "diametro_maximo": "Diâmetro máximo (cm)",
                "carga_permanente": "Carga permanente (kN/m)",
                "carga_roda": "Carga por roda (kN)",
                "carga_multidao": "Carga de multidão (kN/m²)",
                "distancia_eixos": "Distância entre eixos (m)",
                "classe_carregamento": "Classe de carregamento",
                "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                "classe_madeira": "Classe de madeira",
                "classe_madeira_opcoes": ["Madeira natural", "Madeira recomposta"],
                "classe_umidade": "Classe de umidade",
                "gamma_g": "γg – Coeficiente parcial de segurança da carga permanente",
                "gamma_q": "γq – Coeficiente parcial de segurança da carga variável",
                "gamma_w": "γw – Coeficiente parcial de segurança do material",
                "f_ck": "Resistência característica à compressão paralela às fibras (MPa)",
                "f_tk": "Resistência característica à tração paralela às fibras (MPa)",
                "f_mk": "Resistência característica à flexão (MPa)",
                "f_vk": "Resistência característica ao cisalhamento (MPa)",
                "e_modflex": "Módulo de elasticidade à flexão (GPa)",
                "botao_dados_down": "Download dos dados do projeto",
                "gerador_desempenho": "Gerar desempenho estrutural para pré-dimensionamento",
                "tabela_desempenho": "Tabela de desempenho estrutural via Análise de Monte Carlo",
                "aviso_gerar_primeiro": "Gere o desempenho antes de realizar o download.",
            },
            "en": {
                "titulo": "Parametric design of a wooden stringer",
                "pre": "Pre-sizing of the cross-section",
                "entrada_comprimento": "Beam length (m)",
                "pista": "Track width (m)",
                "entrada_tipo_secao": "Section type",
                "tipo_secao": ["Circular"],
                "diametro_minimo": "Minimum diameter (cm)",
                "diametro_maximo": "Maximum diameter (cm)",
                "carga_permanente": "Dead load (kN/m)",
                "carga_roda": "Load per wheel (kN)",
                "carga_multidao": "Crowd load (kN/m²)",
                "distancia_eixos": "Distance between axles (m)",
                "classe_carregamento": "Load duration class",
                "classe_carregamento_opcoes": ["Dead", "Long-term", "Medium-term", "Short-term", "Instantaneous"],
                "classe_madeira": "Wood class",
                "classe_madeira_opcoes": ["Natural wood", "Engineered wood"],
                "classe_umidade": "Moisture class",
                "gamma_g": "γg – Partial safety factor for dead load",
                "gamma_q": "γq – Partial safety factor for variable load",
                "gamma_w": "γw – Partial safety factor for material",
                "f_ck": "Characteristic compressive strength parallel to grain (MPa)",
                "f_tk": "Characteristic tensile strength parallel to grain (MPa)",
                "f_mk": "Characteristic bending strength (MPa)",
                "f_vk": "Characteristic shear strength (MPa)",
                "e_modflex": "Modulus of elasticity in bending (GPa)",
                "botao_dados_down": "Download project data",
                "gerador_desempenho": "Generate structural performance for pre-sizing",
                "tabela_desempenho": "Performance table via Monte Carlo analysis",
                "aviso_gerar_primeiro": "Generate performance before downloading.",
            },
        }

t = textos.get(lang, textos["pt"])
def build_excel_bytes(dados: dict) -> bytes:
    """
    Serializa os dados do projeto para XLSX em memória.
    """
    df = pd.DataFrame([dados])  # 1 linha
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
    buffer.seek(0)
    return buffer.getvalue()

# UI
st.header(t["titulo"])
st.subheader(t["pre"])

with st.form("form_geometria", clear_on_submit=False):
    l = st.number_input(t["entrada_comprimento"], min_value=3.0, value=6.0)
    b_wpista_m = st.number_input(t["pista"], value=15.0)

    tipo_secao = st.selectbox(t["entrada_tipo_secao"], t["tipo_secao"])
    d_cm_min, d_cm_max = None, None
    if tipo_secao == "Circular":
        d_cm_min = st.number_input(t["diametro_minimo"], value=30.0)
        d_cm_max = st.number_input(t["diametro_maximo"], value=100.0)

    p_gk = st.number_input(t["carga_permanente"], value=10.0)
    p_rodak = st.number_input(t["carga_roda"], value=40.0)
    p_qk = st.number_input(t["carga_multidao"], value=4.0)
    a = st.number_input(t["distancia_eixos"], value=1.5)

    classe_carregamento_raw = st.selectbox(t["classe_carregamento"], t["classe_carregamento_opcoes"])
    classe_carregamento = classe_carregamento_raw.lower()

    classe_madeira_raw = st.selectbox(t["classe_madeira"], t["classe_madeira_opcoes"])
    classe_madeira = classe_madeira_raw.lower()

    classe_umidade = st.selectbox(t["classe_umidade"], [1, 2, 3, 4])

    gamma_g = st.number_input(t["gamma_g"], value=1.40, step=0.1)
    gamma_q = st.number_input(t["gamma_q"], value=1.40, step=0.1)
    gamma_w = st.number_input(t["gamma_w"], value=1.40, step=0.1)

    f_ck_mpa = st.number_input(t["f_ck"], value=0.0)
    f_tk_mpa = st.number_input(t["f_tk"], value=0.0)
    f_mk_mpa = st.number_input(t["f_mk"], value=0.0)
    f_vk_mpa = st.number_input(t["f_vk"], value=0.0)
    e_modflex_gpa = st.number_input(t["e_modflex"], value=12.0)

    submitted_design = st.form_submit_button(t["gerador_desempenho"])


# Dados do projeto (armazenamento e download fora do form)
dados_projeto = {
                    "l (m)": l,
                    "b_wpista (m)": b_wpista_m,
                    "tipo_secao": tipo_secao,
                    "p_gk (kN/m)": p_gk,
                    "p_rodak (kN)": p_rodak,
                    "p_qk (kN/m²)": p_qk,
                    "a (m)": a,
                    "classe_carregamento": classe_carregamento,
                    "classe_madeira": classe_madeira,
                    "classe_umidade": classe_umidade,
                    "gamma_g": gamma_g,
                    "gamma_q": gamma_q,
                    "gamma_w": gamma_w,
                    "f_ck (MPa)": f_ck_mpa,
                    "f_tk (MPa)": f_tk_mpa,
                    "f_mk (MPa)": f_mk_mpa,
                    "f_vk (MPa)": f_vk_mpa,
                    "e_modflex (GPa)": e_modflex_gpa,
                }

# Persistência (para não “sumir” ao clicar em download)
st.session_state["dados_projeto"] = dados_projeto


# Download (sempre disponível; não apaga tabela, pois resultados ficam no state)
excel_bytes = build_excel_bytes(st.session_state["dados_projeto"])
st.download_button(
                    label=t["botao_dados_down"],
                    data=excel_bytes,
                    file_name="dados_projeto.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )


# Cálculo (somente no submit) + persistência do resultado
if submitted_design:
    # Conversões coerentes:
    # MPa -> kPa (1e3); GPa -> kPa (1e6)
    f_ck = f_ck_mpa * 1e3
    f_tk = f_tk_mpa * 1e3
    f_mk = f_mk_mpa * 1e3
    f_vk = f_vk_mpa * 1e3
    e_modflex = e_modflex_gpa * 1e6

    n_mc = 100
    d_cm_vals = np.linspace(d_cm_min, d_cm_max, n_mc)

    out = {"d_cm": [], "g_m": [], "g_v": [], "g_f": []}

    for d in d_cm_vals:
        geo = {"d": d / 100.0}  # cm -> m
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
                                                                                                    e_modflex,
                                                                                                )
        out["d_cm"].append(d)
        out["g_m"].append(res_m["g [kN/m²]"])
        out["g_v"].append(res_v["g [kN]"])
        out["g_f"].append(res_f_var["g [m]"])

    df_resultados = pd.DataFrame(out)
    df_filter = df_resultados[
                                (df_resultados["g_m"] >= 0.0)
                                & (df_resultados["g_v"] >= 0.0)
                                & (df_resultados["g_f"] >= 0.0)
                            ].copy()

    st.session_state["df_filter"] = df_filter

# Renderização (sempre que existir no session_state)
if st.session_state.get("df_filter") is not None:
    st.subheader(t["tabela_desempenho"])
    st.dataframe(st.session_state["df_filter"])
