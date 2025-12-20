"""Contém funções para cálculo e verificação de estruturas de madeira."""
import numpy as np


def prop_madeiras(geo: dict) -> tuple[float, float, float, float, float, float, float]:
    """Calcula propriedades geométricas de seções retangulares e circulares de madeira.
    
    :param geo: Parâmetros geométricos da seção transversal. Se chaves = 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m] = retangular, se chave = 'd': Diâmetro da seção transversal [m] = circular

    """

    # Propriedades da seção transversal
    if 'd' in geo:
        area = (np.pi * (geo['d'] ** 2)) / 4
        inercia = (np.pi * (geo['d'] ** 4)) / 64
        i_x = inercia
        i_y = inercia
        w_x = inercia / (geo['d'] / 2)
        w_y = w_x
        k_m = 1.0
    else:
        area = geo['b_w'] * geo['h']
        i_x = (geo['b_w'] * (geo['h'] ** 3)) / 12
        i_y = (geo['h'] * (geo['b_w'] ** 3)) / 12
        w_x = i_x / (geo['h'] / 2)
        w_y = i_y / (geo['b_w'] / 2)
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

    """

    f_p = p / area
    f_md_x1 = m_x / w_x
    f_md_y1 = m_y / w_y

    return f_p, f_md_x1, f_md_y1


def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
    """Calcula a resistência de cálculo da madeira conforme NBR 7190.
    """

    f_d = (f_k / gamma_w) * k_mod
    
    return f_d


def checagem_tensoes(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> float:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    """

    verif_1 = (sigma_x / f_md) + k_m * (sigma_y / f_md)
    verif_2 = k_m * (sigma_x / f_md) + (sigma_y / f_md)
    fator = max(verif_1, verif_2)
    analise = 'Passou na verificação' if fator <= 1 else 'Não passou na verificação'

    return fator, analise


def checagem_flexao_simples_ponte(geo: dict, m_gkx: float, m_qkx: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float, p_k: float = 0.0, m_gky: float = 0.0, m_qky: float = 0.0)  -> str:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190:1997.
    """

    area, w_x, w_y, i_x, i_y, r_x, r_y, k_m = prop_madeiras(geo)
    # props
    # Combinação das cargas
    m_sd_x = m_gkx * gamma_g + m_qkx * gamma_q
    m_sd_y = m_gky * gamma_g + m_qky * gamma_q
    # flexao() lembrar de  passar as entradas
    # Resistências de cálculo
    # Checagem tensoes

    analise_final = { 
                        "area": area,
                        "analise": analise
                    }

    return analise_final


if __name__ == "__main__":
    pass