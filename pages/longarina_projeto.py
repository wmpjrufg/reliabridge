import streamlit as st
# from madeiras import *

import numpy as np


# Home
lang = st.session_state.get("lang", "pt")

# Cria o dicionário com os textos DESSA página específica
textos = {
            "pt": {
                    "titulo": "Verificação de uma Longarina – Flexão Pura (NBR 7190)",
                    "entrada_tipo_secao": "Tipo de seção",
                    "tipo_secao": ["Retangular", "Circular"],
                    "base": "Base (m)",
                    "altura": "Altura (m)",
                    "diametro": "Diâmetro (m)",
                    "entrada_comprimento": "Comprimento da viga (m)",
                    "carga_permanente": "Carga permanente (kN/m)",
                    "trem_tipo": "Tipo de trem",
                    "tipo_tb": ["TB-240", "TB-450"],
                    "classe_carregamento": "Classe de carregamento",
                    "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                    "classe_madeira": "Classe de madeira", 
                    "classe_madeira_opcoes": ["Madeira natural","Madeira recomposta"],
                    "classe_umidade": "Classe de umidade",
                    "gamma_g": "γg – Coeficiente da carga permanente",
                    "gamma_q": "γq – Coeficiente da carga variável",
                    "gamma_w": "γw – Coeficiente do material",
                    "botao": "Calcular Resistência",
                    "resultado": "A resistência calculada é: "
                  },
            "en": {
                    "titulo": "Verification of a Stringer – Pure Bending (NBR 7190)",
                    "entrada_tipo_secao": "Section type",
                    "tipo_secao": ["Rectangular", "Circular"],
                    "base": "Width (m)",
                    "altura": "Height (m)",
                    "diametro": "Diameter (m)",
                    "entrada_comprimento": "Beam length (m)",
                    "carga_permanente": "Permanent load (kN/m)",
                    "trem_tipo": "Load train type",
                    "tipo_tb": ["TB-240", "TB-450"],
                    "classe_carregamento": "Load duration class",
                    "classe_carregamento_opcoes": ["Permanent", "Long-term", "Medium-term", "Short-term", "Instantaneous"],
                    "classe_madeira": "Wood class",
                    "classe_madeira_opcoes": ["Natural wood", "Engineered wood"],
                    "classe_umidade": "Moisture class",
                    "gamma_g": "γg – Permanent load factor",
                    "gamma_q": "γq – Variable load factor",
                    "gamma_w": "γw – Material factor",
                    "botao": "Calculate Resistance",
                    "resultado": "The calculated resistance is: "
                  }
         }   
t = textos[lang]

# Calculadora da página
st.header(t["titulo"])
tipo_secao = st.selectbox(t["entrada_tipo_secao"], t["tipo_secao"])
if tipo_secao == "Retangular" or tipo_secao == "Rectangular":
    b = st.number_input("Base (m)", min_value=0.05, value=0.20)
    h = st.number_input("Altura (m)", min_value=0.05, value=0.50)
    geo = {"b_w": b, "h": h}
else:
    d = st.number_input("Diâmetro (m)", min_value=0.05, value=0.30)
    geo = {"d": d}
l = st.number_input(t["entrada_comprimento"], value=10.0)

col1, col2 = st.columns(2)
with col1:
    p_gk = st.number_input("Carga permanente (kN/m)", value=8.0)    
with col2:
    p_qk = st.selectbox(t["trem_tipo"], t["tipo_tb"])
classe_carregamento = st.selectbox("Classe de carregamento", ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"])
classe_carregamento = str(classe_carregamento).lower()
classe_madeira = st.selectbox("Classe de madeira", ["madeira natural", "madeira recomposta"])
classe_madeira = str(classe_madeira).lower()
classe_umidade = st.selectbox("Classe de umidade", [1, 2, 3, 4])
classe_umidade = str(classe_umidade).lower()
gamma_g = st.number_input("γg", value=1.40, step=0.1)
gamma_q = st.number_input("γq", value=1.40, step=0.1)
gamma_w = st.number_input("γw", value=1.40, step=0.1)

if st.button(t["botao"]):
    res = checagem_flexao_simples_ponte()
    st.success(f"{t['resultado']} {res} kNm")
