"""Contém funções para cálculo e verificação de estruturas de madeira."""
import numpy as np


def prop_madeiras(geo: dict) -> tuple[float, float, float, float, float, float, float, float]:
    """Calcula propriedades geométricas de seções retangulares e circulares de madeira.
    
    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]

    :return: [0] Área da seção transversal [m²], [1] Módulo de resistência em relação ao eixo x [m³], [2] Módulo de resistência em relação ao eixo y [m³], [3] Momento de inércia em relação ao eixo x [m4], [4] Momento de inércia em relação ao eixo y [m4], [5] Raio de giração em relação ao eixo x [m], [6] Raio de giração em relação ao eixo y [m], [7] Coeficiente de correção do tipo da seção transversal
    """

    # Propriedades da seção transversal
    if 'd' in geo:
        area = (np.pi * (geo['d'] ** 2)) / 4
        inercia = (np.pi * (geo['d'] ** 4)) / 64
        i_x = inercia
        i_y = inercia
        w_x = inercia / (geo['d'] / 2)
        w_y = w_x
        r_x = np.sqrt(i_x / area)
        r_y = r_x
        k_m = 1.0
    else:
        area = geo['b_w'] * geo['h']
        i_x = (geo['b_w'] * (geo['h'] ** 3)) / 12
        i_y = (geo['h'] * (geo['b_w'] ** 3)) / 12
        w_x = i_x / (geo['h'] / 2)
        w_y = i_y / (geo['b_w'] / 2)
        r_x = np.sqrt(i_x / area)
        r_y = np.sqrt(i_y / area)
        k_m = 0.70

    return area, w_x, w_y, i_x, i_y, r_x, r_y, k_m


def k_mod_madeira(classe_carregamento: str, classe_madeira: str, classe_umidade: int) -> tuple[float, float, float]:
    """Retorna o coeficiente de modificação kmod para madeira conforme NBR 7190:1997.

    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4

    :return: [0] Tipo de produto de madeira e a duração da carga (kmod1), [1] Tipo do produto e a classe de umidade (kmod2), [2] Coeficiente de modificação total (kmod)
    """

    kmod1_tabela = {
                        'permanente': {'madeira natural': 0.60, 'madeira recomposta': 0.30},
                        'longa duração': {'madeira natural': 0.70, 'madeira recomposta': 0.45},
                        'média duração': {'madeira natural': 0.80, 'madeira recomposta': 0.55},
                        'curta duração': {'madeira natural': 0.90, 'madeira recomposta': 0.65},
                        'instantânea': {'madeira natural': 1.10, 'madeira recomposta': 1.10}
                    }
    kmod2_tabela = {
                        1: {'madeira natural': 1.00, 'madeira recomposta': 1.00},
                        2: {'madeira natural': 0.90, 'madeira recomposta': 0.95},
                        3: {'madeira natural': 0.80, 'madeira recomposta': 0.93},
                        4: {'madeira natural': 0.70, 'madeira recomposta': 0.90}
                    }
    k_mod1 = kmod1_tabela[classe_carregamento][classe_madeira]
    k_mod2 = kmod2_tabela[classe_umidade][classe_madeira]
    k_mod = k_mod1 * k_mod2

    return k_mod1, k_mod2, k_mod


def flexao_obliqua(area: float, w_x: float, w_y: float, p: float, m_x: float, m_y: float) -> tuple[float, float, float]:
    """Calcula a resistência à flexão oblíqua da madeira.

    :param area: Área da seção transversal [m²]
    :param w_x: Módulo de resistência em relação ao eixo x [m³]
    :param w_y: Módulo de resistência em relação ao eixo y [m³]
    :param p: Força axial [kN]
    :param m_x: Momento fletor em relação ao eixo x [kN.m]
    :param m_y: Momento fletor em relação ao eixo y [kN.m]

    :return: [0] Tensão normal devido à força axial [kN/m²], [1] Tensão de flexão em relação ao eixo x [kN/m²], [2] Tensão de flexão em relação ao eixo y [kN/m²]  
    """

    f_p = p / area
    f_md_x = m_x / w_x
    f_md_y = m_y / w_y

    return f_p, f_md_x, f_md_y


def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
    """Calcula a resistência de cálculo da madeira conforme NBR 7190.

    :param f_k: Resistência característica da madeira [kN/m²]
    :param gamma_w: Coeficiente de segurança para madeira
    :param k_mod: Coeficiente de modificação da resistência da madeira

    :return: Resistência de cálculo da madeira [kN/m²]
    """

    f_d = (f_k / gamma_w) * k_mod
    
    return f_d


def checagem_tensoes(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> tuple[float, str]:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param sigma_x: Tensão normal em relação ao eixo x [kN/m²]
    :param sigma_y: Tensão normal em relação ao eixo y [kN/m²]
    :param f_md: Resistência de cálculo da madeira [kN/m²]

    :return: [0] fator de utilização, [1] Descrição do Fator de utilização
    """

    verif_1 = (sigma_x / f_md) + k_m * (sigma_y / f_md)
    verif_2 = k_m * (sigma_x / f_md) + (sigma_y / f_md)
    fator = max(verif_1, verif_2)
    analise = 'Passou na verificação' if fator <= 1 else 'Não passou na verificação'

    return fator, analise


def checagem_flexao_simples_viga(area, w_x: float, k_m: float, m_gk: float, m_qk: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float) -> dict:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param area: Área da seção transversal [m²]
    :param w_x: Módulo de resistência em relação ao eixo x [m³] 
    :param m_gk: Momento fletor devido à carga permanente [kN.m]
    :param m_qk: Momento fletor devido à carga variável [kN.m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente de segurança para carga permanente
    :param gamma_q: Coeficiente de segurança para carga variável
    :param gamma_w: Coeficiente de segurança para madeira
    :param f_c0k: Resistência característica à compressão paralela às fibras [kN/m²]
    :param f_t0k: Resistência característica à tração paralela às fibras [kN/m²]

    return:  Analise da verificação de tensões: {"fator_utilização":fator de utilização, "analise": descrição do fator de utilização, "r_min": raio de giração mínimo [m]}     
    """

    # Ações de cálculo
    m_sd = m_gk * gamma_g + m_qk * gamma_q

    # k_mod
    k_mod1, k_mod2, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões
    _, f_x, f_y = flexao_obliqua(area, w_x, 1E-12, 0.0, m_sd, 0.0)

    # Resistência de cálculo (caso mais desfavorável)
    f_md = min(resistencia_calculo(f_c0k, gamma_w, k_mod), resistencia_calculo(f_t0k, gamma_w, k_mod))                
    
    # Verificação
    fator, analise = checagem_tensoes(k_m, f_x, f_y, f_md)

    return {
                "k_mod1": k_mod1,
                "k_mod2": k_mod2,
                "k_mod": k_mod,
                "sigma_x [kN/m²]": f_x,
                "f_md [kN/m²]": f_md,
                "fator_utilizacao": fator,
                "analise": analise,
            }


def checagem_longarina_madeira(geo: dict, p_gk: float, trem_tipo: str, l: float) -> tuple[dict, dict, dict]:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gk: Carga permanente característica, uniformemente distribuída [kN/m]
    :param trem_tipo: Tipo de trem, ex: 'TB-240' ou 'TB-450'
    :param l: Comprimento do vão [m]
    """

    # Geometria, Propriedades da seção transversal
    area, w_x, _, i_x, _, r_x, _, k_m = prop_madeiras(geo)

    # Momentos fletores de cálculo carga permanente e variável
    m_gk, m_qk, v_gk, v_qk, delta_gk, delta_qk = converte_carga_linear_esforco_maximo(p_gk, trem_tipo, l)

    # Verificação da flexão simples
    res_flex = checagem_flexao_simples_viga(area, w_x, i_x, r_x, k_m, m_gk, m_qk, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k)

    # Verificação do cisalhamento (a implementar)

    # Verificação de deslocamento (a implementar)

    return res_flex, res_cis, res_des


def converte_carga_linear_esforco_maximo(p_gk: float, trem_tipo: str, l: float) -> tuple[float, float, float, float, float, float]:
    """Converte cargas distribuídas em momentos fletores, esforços cortantes e deformações máximas.
    """

    # Carga variável característica
    p_qkint, p_qkext, p_roda = converte_tb_em_carga(trem_tipo)
    
    
    # Momentos fletores máximos
    m_gk = 
    m_qk = 

    # Esforços cortantes máximos
    v_gk = 
    v_qk = 

    # Deslocamento máximo
    delta_gk = 
    delta_qk = 

    return m_gk, m_qk, v_gk, v_qk, delta_gk, delta_qk


def converte_tb_em_carga(trem_tipo: str) -> tuple[float, float, float]:
    """Converte o tipo de trem em carga distribuída e carga de roda.
    """

    if trem_tipo == "TB-240":
        p_qkint = 24.0  # kN/m
        p_qkext = 16.0  # kN/m
        p_roda = 130.0  # kN
    else:  # TB-450
        p_qkint = 45.0  # kN/m
        p_qkext = 30.0  # kN/m
        p_roda = 220.0  # kN

    return p_qkint, p_qkext, p_roda
