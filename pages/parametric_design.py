import streamlit as st
import numpy as np
import pandas as pd

from madeiras import *

# Flags
lang = st.session_state.get("lang", "pt")
if "geo_ok" not in st.session_state:
    st.session_state["geo_ok"] = False
if "geo" not in st.session_state:
    st.session_state["geo"] = {}

# Cria o dicionário com os textos DESSA página específica
textos = {
            "pt": {
                    "titulo": "Projeto paramétrico de uma Longarina de madeira",
                    "entrada_comprimento": "Comprimento da viga (m)",
                    "pista": "Largura da pista (cm)",
                    "entrada_tipo_secao": "Tipo de seção",
                    "tipo_secao": ["Circular"],
                    "diametro minimo": "Diâmetro mínimo (cm)",
                    "diametro maximo": "Diâmetro máximo (cm)",
                    "carga_permanente": "Carga permanente (kN/m)",
                    "carga_roda": "Carga por roda (kN)",
                    "carga_multidao": "Carga de multidão (kN/m²)",
                    "distancia_eixos": "Distância entre eixos (m)",
                    "classe_carregamento": "Classe de carregamento",
                    "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                    "classe_madeira": "Classe de madeira", 
                    "classe_madeira_opcoes": ["Madeira natural","Madeira recomposta"],
                    "classe_umidade": "Classe de umidade",
                    "gamma_g": "γg – Coeficiente parcial de segurança da carga permanente",
                    "gamma_q": "γq – Coeficiente parcial de segurança da carga variável",
                    "gamma_w": "γw – Coeficiente parcial de segurança do material",
                    "f_ck": "Resistência característica à compressão paralela às fibras (MPa)",
                    "f_tk": "Resistência característica à tração paralela às fibras (MPa)",
                    "e_modflex": "Módulo de elasticidade à flexão (GPa)",
                    "gerador desempenho": "Gerar desemepenho estrutural",
                    "resultado": "A resistência calculada é: "
                  },
            "en": {
                    "titulo": "Parametric design of a wooden Stringer",
                    "entrada_comprimento": "Beam length (m)",
                    "tipo_secao": ["Circular"],
                    "pista": "Track width (cm)",
                    "diametro minimo": "Minimum diameter (cm)",
                    "diametro maximo": "Maximum diameter (cm)",
                    "entrada_tipo_secao": "Section type",
                    
                    "base": "Width (cm)",
                    "altura": "Height (cm)",
                    "diametro": "Diameter (cm)",
                    
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
                    "e_modflex": "Modulus of elasticity in bending (GPa)",
                    "botao": "Check beam",
                    "resultado": "The calculated resistance is: "
                  }
         }   
t = textos[lang]

# Calculadora da página
st.header(t["titulo"])

# Geometria
with st.form("form_geometria", clear_on_submit=False):
    l = st.number_input(t["entrada_comprimento"], min_value=3.0, value=6.0)
    b_wpista_cm = st.number_input(t["pista"], value=15.0)
    tipo_secao = st.selectbox(t["entrada_tipo_secao"], t["tipo_secao"])
    if tipo_secao == "Circular":
        d_cm_min = st.number_input(t["diametro minimo"], value=30.0)
        d_cm_max = st.number_input(t["diametro maximo"], value=100.0)
    else:
        pass
    p_gk = st.number_input(t["carga_permanente"], value=10.0)    
    p_rodak = st.number_input(t["carga_roda"], value=40.0)
    p_qk = st.number_input(t["carga_multidao"], value=4.0)
    a = st.number_input(t["distancia_eixos"], value=1.5)
    classe_carregamento = st.selectbox(t["classe_carregamento"], t["classe_carregamento_opcoes"]).lower()
    if classe_carregamento == "permanent":
        classe_carregamento = "Permanente"
    elif classe_carregamento == "long-term":
        classe_carregamento = "Longa duração"
    elif classe_carregamento == "medium-term":
        classe_carregamento = "Média duração"
    elif classe_carregamento == "short-term":
        classe_carregamento = "Curta duração"
    elif classe_carregamento == "instantaneous":
        classe_carregamento = "Instantânea"
    classe_madeira = st.selectbox(t["classe_madeira"], t["classe_madeira_opcoes"]).lower()
    if classe_madeira == "natural wood":
        classe_madeira = "madeira natural"
    else: 
        classe_madeira = "madeira recomposta"
    classe_umidade = st.selectbox(t["classe_umidade"], [1, 2, 3, 4])
    gamma_g = st.number_input(t["gamma_g"], value=1.40, step=0.1)
    gamma_q = st.number_input(t["gamma_q"], value=1.40, step=0.1)
    gamma_w = st.number_input(t["gamma_w"], value=1.40, step=0.1)
    f_ck = st.number_input(t["f_ck"], value=20.0)
    f_tk = st.number_input(t["f_tk"], value=15.0)
    e_modflex = st.number_input(t["e_modflex"], value=12.0)
    f_ck *=  1E3
    f_tk *= 1E3
    e_modflex *= 1E6
    submitted_design = st.form_submit_button(t["gerador desempenho"])
    if submitted_design:
        n_mc = 500
        d_cm = list(np.linspace(d_cm_min, d_cm_max, n_mc))
        for d in d_cm:
            geo = {"d": d/100}
            res_m, res_delta, res_v = checagem_longarina_madeira_flexao(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)


    

if submitted:
    # Salva a geometria no estado
    st.session_state["geo"] = geo
    st.session_state["n_long"] = int(n_long)
    st.session_state["esp_cm"] = float(esp_cm)
    st.session_state["l_m"] = float(l)
    st.session_state["geo_ok"] = True

if st.session_state["geo_ok"]:
    fig = plot_longarinas_circulares(n_longarinas=st.session_state["n_long"], diametro_cm=st.session_state["geo"]["d"], espacamento_cm=st.session_state["esp_cm"])
    st.pyplot(fig)

# Cargas e materiais



# if st.button(t["botao"]):
    
#     # Análise final
#     res_m, res_delta, res_v = checagem_longarina_madeira_flexao(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)
    
#     # Tabela de Flexão
#     st.subheader("Flexão (ELU)")
#     # Converte o dicionário para tabela (orient='index' deixa as chaves nas linhas)
#     df_m = pd.DataFrame.from_dict(res_m, orient='index', columns=['Valor'])
#     st.table(df_m)

#     # Tabela de Flecha
#     st.subheader("Flecha (ELS)")
#     df_delta = pd.DataFrame.from_dict(res_delta, orient='index', columns=['Valor'])
#     st.table(df_delta)
    
#     # Mensagem final resumida
#     if res_m['analise'] == 'OK' and res_delta['analise'] == 'OK':
#         st.success("Resultado Final: APROVADO")
#     else:
#         st.error("Resultado Final: REPROVADO")
