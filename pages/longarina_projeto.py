import streamlit as st
import numpy as np
import pandas as pd

from madeiras import *


# def prop_madeiras(geo: dict) -> tuple[float, float, float, float, float, float, float]:
#     """Calcula propriedades geométricas de seções retangulares e circulares de madeira.
    
#     :param geo: Parâmetros geométricos da seção transversal. Se chaves = 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m] = retangular, se chave = 'd': Diâmetro da seção transversal [m] = circular

#     :return: [0] 
#     """

#     # Propriedades da seção transversal
#     if 'd' in geo:
#         area = (np.pi * (geo['d'] ** 2)) / 4
#         inercia = (np.pi * (geo['d'] ** 4)) / 64
#         i_x = inercia
#         i_y = inercia
#         w_x = inercia / (geo['d'] / 2)
#         w_y = w_x
#         k_m = 1.0
#         r_x = (i_x / area)**(1/2)
#         r_y = (i_y / area)**(1/2)
#     else:
#         area = geo['b_w'] * geo['h']
#         i_x = (geo['b_w'] * (geo['h'] ** 3)) / 12
#         i_y = (geo['h'] * (geo['b_w'] ** 3)) / 12
#         w_x = i_x / (geo['h'] / 2)
#         w_y = i_y / (geo['b_w'] / 2)
#         k_m = 0.70
#         r_x = (i_x / area)**(1/2)
#         r_y = (i_y / area)**(1/2)

#     return area, w_x, w_y, i_x, i_y, r_x, r_y, k_m


# def k_mod_madeira(classe_carregamento: str, classe_madeira: str, classe_umidade: int) -> tuple[float, float, float]:
#     """Retorna o coeficiente de modificação kmod para madeira conforme NBR 7190:1997.

#     :param classe_carregamento: Permanente, Longa Duração, Média Duração, Curta Duração ou Instantânea
#     :param classe_madeira: madeira_natural ou madeira_recomposta
#     :param classe_umidade: 1, 2, 3, 4
#     """

#     kmod1_tabela = {
#                         'Permanente': {'madeira_natural': 0.60, 'madeira_recomposta': 0.30},
#                         'Longa duração': {'madeira_natural': 0.70, 'madeira_recomposta': 0.45},
#                         'Média duração': {'madeira_natural': 0.80, 'madeira_recomposta': 0.55},
#                         'Curta duração': {'madeira_natural': 0.90, 'madeira_recomposta': 0.65},
#                         'Instantânea': {'madeira_natural': 1.10, 'madeira_recomposta': 1.10}
#                 }
#     kmod2_tabela = {
#                         1: {'madeira_natural': 1.00, 'madeira_recomposta': 1.00},
#                         2: {'madeira_natural': 0.90, 'madeira_recomposta': 0.95},
#                         3: {'madeira_natural': 0.80, 'madeira_recomposta': 0.93},
#                         4: {'madeira_natural': 0.70, 'madeira_recomposta': 0.90}
#                     }
#     k_mod1 = kmod1_tabela[classe_carregamento][classe_madeira]
#     k_mod2 = kmod2_tabela[classe_umidade][classe_madeira]
#     k_mod = k_mod1 * k_mod2

#     return k_mod1, k_mod2, k_mod


# def flexao_obliqua(area: float, w_x: float, w_y: float, p: float, m_x: float, m_y: float) -> float:
#     """Calcula a resistência à flexão oblíqua da madeira conforme NBR 7190.

#     :param area: Área da seção transversal [m²]
#     :param w_x: Módulo de resistência em relação ao eixo x [m³]
#     :param w_y: Módulo de resistência em relação ao eixo y [m³]
#     :param p: Força axial [kN]
#     :param m_x: Momento fletor em relação ao eixo x [kN.m]
#     :param m_y: Momento fletor em relação ao eixo y [kN.m]

#     :ret
#     """

#     f_p = p / area
#     f_md_x1 = m_x / w_x
#     f_md_y1 = m_y / w_y

#     return f_p, f_md_x1, f_md_y1


# def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
#     """Calcula a resistência de cálculo da madeira conforme NBR 7190.
#     """

#     f_d = (f_k / gamma_w) * k_mod
    
#     return f_d


# def checagem_tensoes(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> float:
#     """Verifica as tensões na madeira conforme NBR 7190.
    
#     :param k_m: Coeficiente de correção do tipo da seção transversal
#     """

#     verif_1 = (sigma_x / f_md) + k_m * (sigma_y / f_md)
#     verif_2 = k_m * (sigma_x / f_md) + (sigma_y / f_md)
#     fator = max(verif_1, verif_2)
#     analise = 'Passou na verificação' if fator <= 1 else 'Não passou na verificação'

#     return fator, analise


# def flecha_max_carga_permanente(p_gk: float, l: float, E: float, i_x: float) -> float:
#     """
#     Esta função calcula a flecha máxima devido à carga permanente.
    
#     :param p_gk: carga permanente distribuída (kN/m)
#     :param l: vão teórico da viga (m)
#     :param E: módulo de elasticidade da madeira (kN/m²)
#     :param i_x: momento de inércia da seção transversal (m⁴)

#     :return: flecha máxima devido à carga permanente (m)
#     """
#     return 5 * p_gk * l**4 / (384 * E * i_x)

# def reacao_apoio_carga_permanente(p_gk: float, l: float) -> float:
#     """
#     Esta função calcula a reação de apoio devido à carga permanente.
    
#     :param p_gk: carga permanente distribuída (kN/m)
#     :param l: vão teórico da viga (m)

#     :return: reação de apoio devido à carga permanente (kN)
#     """
#     return p_gk * l / 2

# def cortante_max_carga_permanente(p_gk: float, l: float) -> float:
#     """
#     Esta função calcula a cortante máxima devido à carga permanente.
    
#     :param p_gk: carga permanente distribuída (kN/m)
#     :param l: vão teórico da viga (m)

#     :return: cortante máxima devido à carga permanente (kN)
#     """
#     return p_gk * l / 2

# def momento_max_tabuleiro(P: float, ar: float, Lr: float) -> float:
#     """
#     Esta função calcula o momento fletor máximo no tabuleiro devido à carga acidental aplicada por uma roda.
    
#     :param P: carga da roda do veículo-tipo (kN)
#     :param ar: largura de influência da roda (m)
#     :param Lr: vão do tabuleiro (distância entre longarinas) (m)

#     :return: momento fletor máximo no tabuleiro (kN·m)
#     """
#     qr = P / ar
#     return qr * (Lr - ar) / 4

# def load_train(a, l, p_tyre, p_q, l_GC, l_TT, dist_GCR1, dist_eixos):

#     """
#     Esta função calcula os efeitos da carga de multidão e da carga do trem-tipo
#     utilizando o método da linha de influência.

#     :param a: posição do veículo em relação ao apoio (m)
#     :param l: vão da estrutura (m)
#     :param p_tyre: carga por eixo do veículo (kN)
#     :param p_q: carga distribuída de multidão (kN/m)
#     :param l_GC: comprimento do guarda-corpo (m)
#     :param l_TT: comprimento total do trem-tipo (m)
#     :param dist_GCR1: distância do guarda-corpo até o primeiro eixo (m)
#     :param dist_eixos: distância entre os eixos do veículo (m)

#     :return: [0] = P  → efeito da carga concentrada (veículo)
#              [1] = Qi → efeito interno da carga de multidão
#              [2] = Qe → efeito externo da carga de multidão
#     """

#     # Pontos da linha de influência
#     x0, y0 = 0, 0
#     x1, y1 = l, 1

#     # Coeficiente angular
#     m = (y1 - y0) / (x1 - x0)

#     # Intercepto
#     b = y0 - m * x0

#     x_Qe = l + a - l_GC
#     x_Qi = l + a - l_GC - l_TT
#     x_P1 = l + a - l_GC - dist_GCR1
#     x_P2 = l + a - l_GC - dist_GCR1 - dist_eixos

#     y_Qe = m * x_Qe + b
#     y_Qi = m * x_Qi + b
#     y_P1 = m * x_P1 + b
#     y_P2 = m * x_P2 + b

#     # Primeiro caso, considera apenas multidão
#     Qe = p_q * ((y_Qe * x_Qe)/2)

#     # Segundo caso, considera carga e multidão
#     Qi = p_q * ((y_Qi * x_Qi)/2)
#     P = p_tyre * y_P1 + p_tyre * y_P2 

#     return P, Qi, Qe


# def checagem_flexao_simples_ponte(geo: dict, m_gkx: float, m_qkx: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float, p_k: float, m_gky: float, m_qky: float)  -> str:
#     """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190:1997.
#     """

#     area, w_x, w_y, i_x, i_y, r_x, r_y, k_m = prop_madeiras(geo)
#     # Combinação das cargas
#     m_sd_x = m_gkx * gamma_g + m_qkx * gamma_q
#     m_sd_y = m_gky * gamma_g + m_qky * gamma_q
#     # flexao() lembrar de  passar as entradas
#     # Resistências de cálculo
#     # Checagem tensoes

#     analise_final = { 
#                         "area": area,
#                         "analise": analise
#                     }

#     return analise_final

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
                    "trem_tipo": "Tipo de trem",
                    "tipo_tb": ["TB-240", "TB-450"],
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
                    "trem_tipo": "Load train type",
                    "tipo_tb": ["TB-240", "TB-450"],
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
tipo_secao = st.selectbox(t["entrada_tipo_secao"], t["tipo_secao"])
if tipo_secao in ["Retangular", "Rectangular"]:
    b_cm = st.number_input(t["base"], min_value=0.05, value=20.)
    h_cm = st.number_input(t["altura"], min_value=0.05, value=50.)
    b = b_cm / 100
    h = h_cm / 100
    geo = {"b_w": b, "h": h}
else:
    d_cm = st.number_input(t["diametro"], min_value=0.05, value=30.)
    d = d_cm / 100
    geo = {"d": d}
carga_pp = 8.0
l = st.number_input(t["entrada_comprimento"], min_value=3.0, value=6.0)
col1, col2 = st.columns(2)
with col1:
    p_gk = st.number_input(t["carga_permanente"], value=carga_pp)    
with col2:
    p_qk = st.selectbox(t["trem_tipo"], t["tipo_tb"])
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
f_ck *=  1000  # Converte MPa para kN/m²
f_tk *= 1000  # Converte MPa para kN/m²
e_modflex *= 1E9  # Converte GPa para kN/m²

if st.button(t["botao"]):
    
    # Análise final
    res_m, res_delta = checagem_longarina_madeira_flexao(geo, p_gk, p_qk, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)
    
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
