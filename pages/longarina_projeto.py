import streamlit as st
import numpy as np
import pandas as pd

from madeiras import *

# Home
lang = st.session_state.get("lang", "pt")

# Cria o dicionário com os textos DESSA página específica
textos = {
            "pt": {
                    "titulo": "Verificação de uma Longarina – Flexão Pura (NBR 7190)",
                    "entrada_tipo_secao": "Tipo de seção",
                    "tipo_secao": ["Retangular", "Circular"],
                    "base": "Base (cm)",
                    "altura": "Altura (cm)",
                    "diametro": "Diâmetro (cm)",
                    "entrada_comprimento": "Comprimento da viga (m)",
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
                    "densidade": "Densidade a 12% (kg/m³)",
                    "botao": "Verificar viga",
                    "resultado": "A resistência calculada é: "
                  },
            "en": {
                    "titulo": "Verification of a Stringer – Pure Bending (NBR 7190)",
                    "entrada_tipo_secao": "Section type",
                    "tipo_secao": ["Rectangular", "Circular"],
                    "base": "Width (cm)",
                    "altura": "Height (cm)",
                    "diametro": "Diameter (cm)",
                    "entrada_comprimento": "Beam length (m)",
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
                    "densidade": "Density at 12% (kg/m³)",
                    "botao": "Check beam",
                    "resultado": "The calculated resistance is: "
                  }
         }   
t = textos[lang]

# Calculadora da página
st.header(t["titulo"])
opcoes_secao = ["–", "Retangular", "Circular"]
tipo_secao = st.selectbox("Tipo da seção", opcoes_secao)

def num_input_vazio(label, placeholder="–"):
    valor_str = st.text_input(label, placeholder=placeholder)
    if valor_str.strip() == "":
        return None
    try:
        return float(valor_str.replace(",", "."))
    except:
        st.error(f"Valor inválido em '{label}'. Digite um número.")
        return None

def select_vazio(label, opcoes):
    opcoes_mod = ["–"] + list(opcoes)
    escolha = st.selectbox(label, opcoes_mod)

    if escolha == "–":
        return None
    return escolha

if tipo_secao in ["Retangular", "Rectangular"]:
    b_cm = num_input_vazio(t["base"])
    h_cm = num_input_vazio(t["altura"])
    b = (b_cm or 0) / 100
    h = (h_cm or 0) / 100
    geo = {"b_w": b, "h": h}
else:
    d_cm = num_input_vazio(t["diametro"])
    d = (d_cm or 0) / 100
    geo = {"d": d}

l = num_input_vazio(t["entrada_comprimento"])
p_gk = num_input_vazio(t["carga_permanente"])
p_rodak = num_input_vazio(t["carga_roda"])
p_qk = num_input_vazio(t["carga_multidao"])
a = num_input_vazio(t["distancia_eixos"])
classe_carregamento = select_vazio(t["classe_carregamento"], t["classe_carregamento_opcoes"])
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

classe_madeira = select_vazio(t["classe_madeira"], t["classe_madeira_opcoes"])
classe_madeira = "madeira natural" if classe_madeira == "natural wood" else "madeira recomposta"
classe_umidade = select_vazio(t["classe_umidade"], [1, 2, 3, 4])
gamma_g = num_input_vazio(t["gamma_g"])
gamma_q = num_input_vazio(t["gamma_q"])
gamma_w = num_input_vazio(t["gamma_w"])
f_ck = num_input_vazio(t["f_ck"])
f_tk = num_input_vazio(t["f_tk"])
e_modflex = num_input_vazio(t["e_modflex"])
densidade = num_input_vazio(t["densidade"])
if f_ck: f_ck *= 1E3
if f_tk: f_tk *= 1E3
if e_modflex: e_modflex *= 1E6

if st.button(t["botao"]):
    
    # Análise final
    res_m, res_delta, res_v = checagem_longarina_madeira_flexao(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)
    
    # Tabela de Flexão
    st.subheader("Flexão (ELU)")
    # Converte o dicionário para tabela (orient='index' deixa as chaves nas linhas)
    df_m = pd.DataFrame.from_dict(res_m, orient='index', columns=['Valor'])
    st.table(df_m)

    # Tabela de Flecha
    st.subheader("Flecha (ELS)")
    df_delta = pd.DataFrame.from_dict(res_delta, orient='index', columns=['Valor'])
    st.table(df_delta)
    
    # Mensagem final resumida
    if res_m['analise'] == 'OK' and res_delta['analise'] == 'OK':
        st.success("Resultado Final: APROVADO")
    else:
        st.error("Resultado Final: REPROVADO")
