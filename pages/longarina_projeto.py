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
                    "entrada_comprimento": "Comprimento da viga (m)",
                    "trem_tipo": "Tipo de trem",
                    "tipo_tb": ["TB-240", "TB-450"],
                    "entrada_carga": "Carga aplicada (kN)",
                    "botao": "Calcular Resistência",
                    "resultado": "A resistência calculada é: "
                  },
            "en": {
                    "titulo": "Verification of a Stringer – Pure Bending (NBR 7190)",
                    "entrada_tipo_secao": "Section type",
                    "tipo_secao": ["Rectangular", "Circular"],
                    "entrada_comprimento": "Beam length (m)",
                    "trem_tipo": "Load train type",
                    "tipo_tb": ["TB-240", "TB-450"],
                    "entrada_carga": "Applied load (kN)",
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
