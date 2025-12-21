
# from madeiras import *

import numpy as np
import streamlit as st



def prop_madeiras(geo: dict) -> tuple[float, float, float, float, float, float, float]:
    """Calcula propriedades geométricas de seções retangulares e circulares de madeira.
    
    :param geo: Parâmetros geométricos da seção transversal. Se chaves = 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m] = retangular, se chave = 'd': Diâmetro da seção transversal [m] = circular

    :return: [0] area da seção transversal [m²], 
             [1] módulo de resistência em relação ao eixo x [m³], 
             [2] módulo de resistência em relação ao eixo y [m³], 
             [3] momento de inércia em relação ao eixo x [m^4], 
             [4] momento de inércia em relação ao eixo y [m^4], 
             [5] raio de giração em relação ao eixo x [m], 
             [6] raio de giração em relação ao eixo y [m], 
             [7] coeficiente de correção do tipo da seção transversal
    """

    # Propriedades da seção transversal
    if 'd' in geo:
        area = (np.pi * (geo['d'] ** 2)) / 4
        inercia = (np.pi * (geo['d'] ** 4)) / 64

        i_x = inercia
        i_y = inercia

        w_x = inercia / (geo['d'] / 2)
        w_y = w_x

        # Raio de giração
        r_x = np.sqrt(i_x / area)
        r_y = r_x

        k_m = 1.0
    else:
        area = geo['b_w'] * geo['h']

        i_x = (geo['b_w'] * (geo['h'] ** 3)) / 12
        i_y = (geo['h'] * (geo['b_w'] ** 3)) / 12

        w_x = i_x / (geo['h'] / 2)
        w_y = i_y / (geo['b_w'] / 2)

        # Raio de giração
        r_x = np.sqrt(i_x / area)
        r_y = np.sqrt(i_y / area)

        k_m = 0.70

    return area, w_x, w_y, i_x, i_y, r_x, r_y, k_m


def k_mod_madeira(classe_carregamento: str, classe_madeira: str, classe_umidade: int) -> tuple[float, float, float]:

    """Retorna o coeficiente de modificação kmod para madeira conforme NBR 7190:1997.

    :param classe_carregamento: Permanente, Longa Duração, Média Duração, Curta Duração ou Instantânea
    :param classe_madeira: madeira_natural ou madeira_recomposta
    :param classe_umidade: 1, 2, 3, 4
    """

    kmod1_tabela = {
                        'Permanente': {'madeira_natural': 0.60, 'madeira_recomposta': 0.30},
                        'Longa duração': {'madeira_natural': 0.70, 'madeira_recomposta': 0.45},
                        'Média duração': {'madeira_natural': 0.80, 'madeira_recomposta': 0.55},
                        'Curta duração': {'madeira_natural': 0.90, 'madeira_recomposta': 0.65},
                        'Instantânea': {'madeira_natural': 1.10, 'madeira_recomposta': 1.10}
                }
    kmod2_tabela = {
                        1: {'madeira_natural': 1.00, 'madeira_recomposta': 1.00},
                        2: {'madeira_natural': 0.90, 'madeira_recomposta': 0.95},
                        3: {'madeira_natural': 0.80, 'madeira_recomposta': 0.93},
                        4: {'madeira_natural': 0.70, 'madeira_recomposta': 0.90}
                    }
    k_mod1 = kmod1_tabela[classe_carregamento][classe_madeira]
    k_mod2 = kmod2_tabela[classe_umidade][classe_madeira]
    k_mod = k_mod1 * k_mod2

    return k_mod1, k_mod2, k_mod


def flexao_obliqua(area: float, w_x: float, w_y: float, p: float, m_x: float, m_y: float) -> float:
    """Calcula a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param area: Área da seção transversal [m²]
    :param w_x: Módulo de resistência em relação ao eixo x [m³]
    :param w_y: Módulo de resistência em relação ao eixo y [m³]
    :param p: Força axial [kN]
    :param m_x: Momento fletor em relação ao eixo x [kN.m]
    :param m_y: Momento fletor em relação ao eixo y [kN.m]

    :return: [0] f_p: tensão normal devido à força axial [kN/m²], 
             [1] f_md_x1: tensão de flexão em relação ao eixo x [kN/m²], 
             [2] f_md_y1: tensão de flexão em relação ao eixo y [kN/m²]    
    """

    f_p = p / area
    f_md_x1 = m_x / w_x
    f_md_y1 = m_y / w_y

    return f_p, f_md_x1, f_md_y1


def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
    """Calcula a resistência de cálculo da madeira conforme NBR 7190.
    :param f_k: resistência característica da madeira [kN/m²]
    :param gamma_w: coeficiente de segurança para madeira
    :param k_mod: coeficiente de modificação da resistência da madeira
    :return: resistência de cálculo da madeira [kN/m²]

    """

    f_d = (f_k / gamma_w) * k_mod
    
    return f_d


def checagem_tensoes(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> float:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param sigma_x: Tensão normal em relação ao eixo x [kN/m²]
    :param sigma_y: Tensão normal em relação ao eixo y [kN/m²]
    :param f_md: Resistência de cálculo da madeira [kN/m²]
    """

    verif_1 = (sigma_x / f_md) + k_m * (sigma_y / f_md)
    verif_2 = k_m * (sigma_x / f_md) + (sigma_y / f_md)
    fator = max(verif_1, verif_2)
    analise = 'Passou na verificação' if fator <= 1 else 'Não passou na verificação'

    return fator, analise


def checagem_flexao_simples_ponte(geo: dict, m_gkx: float, m_qkx: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float, p_k: float, m_gky: float, m_qky: float)  -> str:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190:1997.
    :param geo: Parâmetros geométricos da seção transversal. Se chaves = 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m] = retangular, se chave = 'd': Diâmetro da seção transversal [m] = circular
    :param m_gkx: Momento fletor devido à carga permanente em relação ao eixo x [kN.m]
    :param m_qkx: Momento fletor devido à carga variável em relação ao eixo x [kN.m]
    :param classe_carregamento: Permanente, Longa Duração, Média Duração, Curta Duração ou Instantânea
    :param classe_madeira: madeira_natural ou madeira_recomposta    
    """

    # Geometria, Propriedades da seção transversal
    area, w_x, w_y, *_ , r_x, r_y, k_m = prop_madeiras(geo)
    

    # Ações de cálculo
    m_sd_x = m_gkx * gamma_g + m_qkx * gamma_q
    m_sd_y = m_gky * gamma_g + m_qky * gamma_q
    p_sd = gamma_g * p_k

    # k_mod
    k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões
    f_p, f_x, f_y = flexao_obliqua(area, w_x, w_y, p_sd, m_sd_x, m_sd_y)

    # Resistência de cálculo (caso mais desfavorável)
    f_md = min(
        resistencia_calculo(f_c0k, gamma_w, k_mod),
        resistencia_calculo(f_t0k, gamma_w, k_mod)
              )
    
    # Verificação
    fator, analise = checagem_tensoes(
        k_m,
        sigma_x=f_x + f_p,
        sigma_y=f_y,
        f_md=f_md
)

    return {
        "fator_utilizacao": fator,
        "analise": analise,
        "r_min": min(r_x, r_y)
    }
    


# Tela ############################################################
# Recupera o idioma que foi definido lá no app.py
lang = st.session_state.get("lang", "pt")

# Cria o dicionário com os textos DESSA página específica
textos = {
            "pt": {
                    "titulo": "Cálculo de Longarina",
                    "entrada_comprimento": "Comprimento da viga (m)",
                    "entrada_carga": "Carga aplicada (kN)",
                    "botao": "Calcular Resistência",
                    "resultado": "A resistência calculada é: "
                  },
            "en": {
                    "titulo": "Stringer Calculation",
                    "entrada_comprimento": "Beam length (m)",
                    "entrada_carga": "Applied load (kN)",
                    "botao": "Calculate Resistance",
                    "resultado": "The calculated resistance is: "
                  }
         }   
t = textos[lang]

# Calculadora da página
st.header(t["titulo"])
col1, col2 = st.columns(2)
with col1:
    comprimento = st.number_input(t["entrada_comprimento"], value=10.0)
with col2:
    carga = st.number_input(t["entrada_carga"], value=50.0)

if st.button(t["botao"]):
    res = checagem_flexao_simples_ponte()
    st.success(f"{t['resultado']} {res} kNm")

