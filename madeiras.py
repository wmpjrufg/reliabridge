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


def momento_max_carga_permanente(p_gk: float, l: float) -> float:
    """Calcula o momento fletor máximo devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]

    :return: momento fletor máximo devido à carga permanente [kN·m]
    """
    return p_gk * l**2 / 8


def flecha_max_carga_permanente(p_gk: float, l: float, e_modflex: float, i_x: float) -> float:
    """Calcula a flecha máxima devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kN/m²]
    :param i_x: momento de inércia da seção transversal [m⁴]

    :return: flecha máxima devido à carga permanente [m]
    """
    return 5 * p_gk * l**4 / (384 * e_modflex * i_x)


def reacao_apoio_carga_permanente(p_gk: float, l: float) -> float:
    """Calcula a reação de apoio máxima devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]

    :return: reação de apoio devido à carga permanente [kN]
    """
    return p_gk * l / 2


def definir_trem_tipo (tipo_tb: str) -> tuple[float, float]:
    """Define a carga variável característica de multidão, carga por roda do trem tipo especificado e a distância entre eixos.

    :param tipo_tb: Tipo de trem, ex: 'TB-240' ou 'TB-450'

    :return: [0] Carga variável característica por roda [kN], [1] Carga variável característica de multidão [kN/m], e [2] Distância entre eixos [m]
    """

    if tipo_tb == "TB-240":
        p_roda = 40
        p_q = 4
        a = 1.5
    else:
        p_roda = 75
        p_q = 5
        a = 1.5

    return p_roda, p_q, a


def coef_impactovertical() -> float:

    return


def momento_max_carga_variavel(l: float, tipo_tb: str) -> float:
    """Calcula o momento fletor máximo devido à carga variável.
    
    :param l: vão teórico da viga [m]
    :param tipo_tb: Tipo de trem, ex: 'TB-240' ou 'TB-450'

    :return: momento fletor máximo devido à carga variável [kN·m]
    """

    p_roda, p_q, a = definir_trem_tipo (tipo_tb)
    if l > 6:
        m_gk = 
    else:
        m_gk =

    return m_gk


def flecha_max_carga_variável(p_qk: float, l: float, e_modflex: float, i_x: float, tipo_tb: str) -> float:
    """Calcula a flecha máxima devido à carga variável.
    
    :param p_qk: carga variável distribuída [kN/m]
    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kN/m²]
    :param i_x: momento de inércia da seção transversal [m⁴]
    :param tipo_tb: Tipo de trem, ex: 'TB-240' ou 'TB-450'

    :return: flecha máxima devido à carga variável [m]
    """

    p_roda, p_q, a = definir_trem_tipo (tipo_tb)
    delta_qk =

    return delta_qk 


def reacao_apoio_carga_variavel(p_qk: float, l: float, tipo_tb: str) -> float:
    """Calcula a reação de apoio máxima devido à carga variável.
    
    :param p_qk: carga variável distribuída [kN/m]
    :param l: vão teórico da viga [m]
    :param tipo_tb: Tipo de trem, ex: 'TB-240' ou 'TB-450'

    :return: reação de apoio devido à carga variável [kN]
    """

    p_roda, p_q, a = definir_trem_tipo (tipo_tb)
    r_qk =

    return r_qk


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


def flexao_obliqua(w_x: float, m_x: float, w_y: float = 1E-12, m_y: float = 0.0, area: float = 1E-12, p: float = 0.0) -> tuple[float, float, float]:
    """Calcula a resistência à flexão oblíqua da madeira.

    :param w_x: Módulo de resistência em relação ao eixo x [m³]
    :param m_x: Momento fletor em relação ao eixo x [kN.m]
    :param w_y: Módulo de resistência em relação ao eixo y [m³]. Padroniza-se w_y = 1E-12 para flexão simples
    :param m_y: Momento fletor em relação ao eixo y [kN.m]. Padroniza-se m_y = 0.0 para flexão simples
    :param area: Área da seção transversal [m²]. Padroniza-se area = 1E-12 para flexão simples
    :param p: Força axial [kN]. Padroniza-se p = 0.0 para flexão simples

    :return: [0] Tensão de flexão em relação ao eixo x [kN/m²], [1] Tensão de flexão em relação ao eixo y [kN/m²], [2] Tensão normal devido à força axial [kN/m²]
    """

    f_p = p / area
    f_md_x = m_x / w_x
    f_md_y = m_y / w_y

    return f_md_x, f_md_y, f_p 


def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
    """Calcula a resistência de cálculo da madeira conforme NBR 7190.

    :param f_k: Resistência característica da madeira [kN/m²]
    :param gamma_w: Coeficiente parcial de segurança para madeira
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
    analise = 'OK' if fator <= 1 else 'N OK'

    return fator, analise


def checagem_flexao_simples_viga(w_x: float, k_m: float, m_gk: float, m_qk: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float) -> dict:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param w_x: Módulo de resistência em relação ao eixo x [m³] 
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param m_gk: Momento fletor devido à carga permanente [kN.m]
    :param m_qk: Momento fletor devido à carga variável [kN.m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_c0k: Resistência característica à compressão paralela às fibras [kN/m²]
    :param f_t0k: Resistência característica à tração paralela às fibras [kN/m²]

    return:  Analise da verificação de tensões: {"fator_utilização":fator de utilização, "analise": descrição do fator de utilização, "r_min": raio de giração mínimo [m]}     
    """

    # Ações de cálculo
    m_sd = m_gk * gamma_g + m_qk * gamma_q

    # k_mod
    k_mod1, k_mod2, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões
    f_x, _, _ = flexao_obliqua(w_x, m_sd)

    # Resistência de cálculo (caso mais desfavorável)
    f_md = min(resistencia_calculo(f_c0k, gamma_w, k_mod), resistencia_calculo(f_t0k, gamma_w, k_mod))                
    
    # Verificação
    fator, analise = checagem_tensoes(k_m, f_x, _, f_md)

    return {
                "m_sd [kN.m]": m_sd,
                "k_mod1": k_mod1,
                "k_mod2": k_mod2,
                "k_mod": k_mod,
                "sigma_x [kN/m²]": f_x,
                "f_md [kN/m²]": f_md,
                "fator_utilizacao": fator,
                "analise": analise,
            }


def checagem_longarina_madeira_flexao(geo: dict, p_gk: float, trem_tipo: str, l: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k: float, e_modflex: float) -> tuple[dict, dict, dict]:
    """Verifica a longarina de madeira submetida à flexão simples conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gk: Carga permanente característica, uniformemente distribuída [kN/m]
    :param trem_tipo: Tipo de trem, ex: 'TB-240' ou 'TB-450'
    :param l: Comprimento do vão [m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_c0k: Resistência característica à compressão paralela às fibras [kN/m²]
    :param f_t0k: Resistência característica à tração paralela às fibras [kN/m²]
    :param e_modflex: Módulo de elasticidade à flexão [kN/m²]

    """

    # Geometria, Propriedades da seção transversal
    _, w_x, _, _, _, _, _, k_m = prop_madeiras(geo)

    # Momentos fletores de cálculo carga permanente e variável
    m_gk = momento_max_carga_permanente(p_gk, l)
    m_qk = momento_max_carga_variavel(l, trem_tipo)

    # Coeficiente de Impacto Vertical
    ci = coef_impactovertical()

    # Combinação de ações
    m_sd = m_gk * gamma_g + gamma_q * (m_qk + 0.75 * (ci - 1) * m_qk)


    # Verificação da flexão simples
    res_flex = checagem_flexao_simples_viga(w_x, k_m, m_gk, m_qk, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k)

    # Verificação do cisalhamento (a implementar)

    # Verificação de deslocamento (a implementar)

    return res_flex

