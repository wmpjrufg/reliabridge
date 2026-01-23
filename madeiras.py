"""Contém funções para cálculo e verificação de estruturas de madeira."""
import numpy as np
import pandas as pd
import io
from scipy import stats as st

from UQpy.distributions import TruncatedNormal
from UQpy.distributions.collection.GeneralizedExtreme import GeneralizedExtreme
from UQpy.run_model.model_execution.PythonModel import PythonModel
from UQpy.run_model import RunModel
from UQpy.reliability import FORM
from UQpy.sampling import MonteCarloSampling, LatinHypercubeSampling
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams.update({
                        'font.family': 'serif',
                        'mathtext.fontset': 'cm',
                        'axes.unicode_minus': False
                    })
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.termination import get_termination
from pymoo.optimize import minimize


def beta_from_pf(pf: float) -> float:
    pf = float(np.clip(pf, 1e-20, 1 - 1e-20))
    return -st.norm.ppf(pf)


def plot_longarinas_circulares(n_longarinas: int, diametro_cm: float, espacamento_cm: float) -> Figure:
    fig, ax = plt.subplots(figsize=(8, 3))
    raio = diametro_cm / 2
    for i in range(n_longarinas):
        x = i * espacamento_cm
        y = raio  # alinhamento inferior (base em y = 0)

        circulo = Circle(
            (x, y),
            raio,
            fill=False,
            linewidth=2
        )
        ax.add_patch(circulo)
    ax.set_aspect("equal")
    ax.set_xlabel("cm")
    ax.set_ylabel("cm")
    ax.grid(True)

    ax.set_xlim(-raio, (n_longarinas - 1) * espacamento_cm + raio)
    ax.set_ylim(0, diametro_cm * 1.2)

    return fig


def fronteira_pareto(x: list, y: list, label_x: str, label_y: str) -> Figure:
    ### Figure name and DPI
    dpi = 600                                                       # Change as you wish
    name = 'scatter'                                                # Change as you wish

    ### Chart dimensions (in centimeters)
    b_cm = 10                                                       # Change as you wish
    h_cm = 10                                                       # Change as you wish
    inches_to_cm = 1 / 2.54
    b_input = b_cm * inches_to_cm
    h_input = h_cm * inches_to_cm

    ### Axis and labels (For LateX font format use the dollar sign $)
    size_label = 10                                                 # Change as you wish
    color_label = 'black'                                           # or hexadecimal. Change as you wish
    size_axis = 10                                                  # Change as you wish
    color_axis = 'black'                                            # or hexadecimal. Change as you wish

    ### Scatter
    alpha_scatter = 1.0                                             # Change as you wish
    color_scatter = 'blue'                                          # Change as you wish
    size_scatter = 10                                               # Change as you wish

    ### Grid
    on_or_off = True
    line_width_grid = 0.5                                           # Change as you wish
    alpha_grid = 0.3                                                # Change as you wish
    style_grid = '-'                                                # Change as you wish
    color_grid = 'gray'                                             # or hexadecimal. Change as you wish

    ### Figure
    fig, ax = plt.subplots(figsize=(b_input, h_input))
    ax.tick_params(axis='both', which='major', labelsize=size_axis, colors=color_axis)
    ax.set_xlabel(label_x, fontsize=size_label, color=color_label)
    ax.set_ylabel(label_y, fontsize=size_label+2, color=color_label)

    ### Title. Do you need a title? Use the cell bellow:
    # ax.set_title('Sine Wave Plot', fontsize=16)

    ### Config grid
    plt.grid(on_or_off, which='both', linestyle=style_grid, linewidth=line_width_grid, color=color_grid, alpha=alpha_grid)

    ### Plot data
    ax.scatter(x, y, alpha=alpha_scatter, color=color_scatter, s=size_scatter)

    return fig


def montar_excel(dados: dict) -> bytes:
    """Serializa os dados do projeto para XLSX em memória.
    """
    
    df = pd.DataFrame([dados])  # 1 linha
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Dados")
    buffer.seek(0)
    
    return buffer.getvalue()


def montar_excel_df(df: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
    buffer.seek(0)
    return buffer.getvalue()


def prop_madeiras(
                    geo: dict
                 ) -> tuple[float, float, float, 
                            float, float, float, 
                            float, float, float, 
                            float]:
    """Calcula propriedades geométricas de seções retangulares e circulares de madeira.
    
    :param geo: Parâmetros geométricos da seção transversal. 
                Se retangular: Chaves: 'b_w': Largura da seção transversal [m] 
                e 'h': Altura da seção transversal [m]. 
                Se circular: Chaves: 'd': Diâmetro da seção transversal [m]

    :return: [0] Área da seção transversal [m²], 
             [1] Módulo de resistência em relação ao eixo x [m³], 
             [2] Módulo de resistência em relação ao eixo y [m³], 
             [3] Momento de inércia em relação ao eixo x [m4], 
             [4] Momento de inércia em relação ao eixo y [m4], 
             [5] Momento estático da seção em relação a x [m³], 
             [6] Momento estático da seção em relação a y [m³], 
             [7] Raio de giração em relação ao eixo x [m], 
             [8] Raio de giração em relação ao eixo y [m], 
             [9] Coeficiente de correção do tipo da seção transversal
    """

    # Propriedades da seção transversal
    if 'd' in geo:
        area = (np.pi * (geo['d'] ** 2)) / 4
        inercia = (np.pi * (geo['d'] ** 4)) / 64
        i_x = inercia
        i_y = inercia
        s_x = area * (geo['d'] / 2)
        s_y = area * (geo['d'] / 2)
        w_x = inercia / (geo['d'] / 2)
        w_y = w_x
        r_x = np.sqrt(i_x / area)
        r_y = r_x
        k_m = 1.0
    else:
        area = geo['b_w'] * geo['h']
        i_x = (geo['b_w'] * (geo['h'] ** 3)) / 12
        i_y = (geo['h'] * (geo['b_w'] ** 3)) / 12
        s_x = area * (geo['h'] / 2)
        s_y = area * (geo['b_w'] / 2)
        w_x = i_x / (geo['h'] / 2)
        w_y = i_y / (geo['b_w'] / 2)
        r_x = np.sqrt(i_x / area)
        r_y = np.sqrt(i_y / area)
        k_m = 0.70

    return area, w_x, w_y, i_x, i_y, s_x, s_y, r_x, r_y, k_m


def peso_proprio_longarina(densidade: float, area_secao: float, g: float = 9.81) -> float:
    """Calcula o peso próprio (PP) da longarina.

    :param densidade: densidade da madeira [kg/m³]
    :param area_secao: área da seção transversal da longarina [m²]
    :param g: aceleração da gravidade [m/s²] (padrão = 9.81)

    :return: peso próprio por metro linear [kN/m]
    """

    return densidade * area_secao * g / 1E3


def coef_impacto_vertical(liv: float) -> float:
    """Cálculo do Coeficiente de Impacto Vertical (CIV) conforme NBR 7188:2024 item 5.1.3.1. 
        CIV = Coeficiente que majora os esforços para considerar efeitos dinâmicos e vibrações do tráfego.

    :param liv: Vão teórico da estrutura [m] - distância entre apoios para cálculo do impacto
    
    :return: Valor do coeficiente de impacto vertical (CIV)
    """

    if liv < 10.0:
        return 1.35  
    elif 10.0 <= liv <= 200.0:
        return 1 + 1.06 * (20 / (liv + 50))  
    else:
        return 1.0   


def momento_max_carga_permanente(p_gk: float, l: float) -> float:
    """Calcula o momento fletor máximo devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]

    :return: momento fletor máximo devido à carga permanente [kN·m]
    """
    
    return p_gk * l**2 / 8


def momento_max_carga_variavel(l: float, p_rodak: float, p_qk: float, a: float) -> float:
    """Calcula o momento fletor máximo M_q,k conforme expressão normativa para longarinas das Classes 30 e 45.

    :param l: vão teórico da longarina [m]
    :param p_rodak: carga variável característica por roda [kN]
    :param p_qk: carga variável característica de multidão [kN/m]
    :param a: distância entre eixos [m]

    :return: momento fletor máximo devido à carga variável [kN·m]
    """
    
    m_qk = (3 * p_rodak * l) / 4 - p_rodak * a
    if l > 6:
        c = (l - 4 * a) / 2
        m_qk += p_qk * c**2 / 2
        
    return m_qk


def cortante_max_carga_permanente(p_gk: float, l: float) -> float:
    """Calcula o cortante máximo devido à carga permanente distribuída.

    :param p_gk: Carga permanente característica distribuída [kN/m]
    :param l: Vão teórico da viga [m]

    :return: Cortante máximo devido à carga permanente [kN]
    """

    v_gk = p_gk * l / 2

    return v_gk


def cortante_max_carga_variavel(l: float, p_rodak: float, p_qk: float, a: float, h: float) -> float:
    """Calcula a reação de apoio máxima devido à carga variável conforme esquema de trem-tipo.
    
    :param l: vão teórico da viga [m]
    :param p_rodak: carga variável característica por roda [kN]
    :param p_qk: carga variável característica de multidão [kPa]
    :param a: distância entre eixos [m]
    :param h: altura média da viga [m]

    :return: Cortante máximo devido à carga variável [kN]
    """

    e = l - 3 * a - 2 * h
    v_qk = (p_rodak / l) * (6 * a + 3 * e) + (p_qk * e**2) / (2 * l)

    return v_qk


def flecha_max_carga_permanente(p_gk: float, l: float, e_modflex: float, i_x: float) -> float:
    """Calcula a flecha máxima devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kPa]
    :param i_x: momento de inércia da seção transversal [m⁴]

    :return: flecha máxima devido à carga permanente [m]
    """

    return (5 * p_gk * l**4) / (384 * e_modflex * i_x)


def flecha_max_carga_variavel(l: float, e_modflex: float, i_x: float, p_rodak: float, a: float) -> float:
    """Calcula a flecha máxima devido à carga variável.
    
    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kPa]
    :param i_x: momento de inércia da seção transversal [m⁴]
    :param p_rodak: carga variável característica por roda [kN]
    :param a: distância entre eixos [m]

    :return: flecha máxima devido à carga variável [m]
    """

    b = (l - 2 * a) / 2
    aux = (l**3 + 2 * b * (3 * l**2 - 4 * b**2))

    return (p_rodak * aux) / (48 * e_modflex * i_x) 


def reacao_apoio_carga_permanente(p_gk: float, l: float) -> float:
    """Calcula a reação de apoio máxima devido à carga permanente.
    
    :param p_gk: carga permanente distribuída [kN/m]
    :param l: vão teórico da viga [m]

    :return: reação de apoio devido à carga permanente [kN]
    """

    return p_gk * l / 2


def reacao_apoio_carga_variavel(l: float, p_rodak: float, p_qk: float, a: float) -> float:
    """Calcula a reação de apoio máxima devido à carga variável.
    
    :param l: vão teórico da viga [m]
    :param p_rodak: carga variável característica por roda [kN]
    :param p_qk: carga variável característica de multidão [kPa]
    :param a: distância entre eixos [m]

    :return: reação de apoio devido à carga variável [kN]
    """

    d = l - 3 * a
    r_qk = ((p_rodak / l) * (l + 3 * a + 2 * d) + (p_qk * d**2) / (2 * l))

    return r_qk


def k_mod_madeira(classe_carregamento: str, classe_madeira: str, classe_umidade: int) -> tuple[float, float, float]:
    """Retorna o coeficiente de modificação kmod para madeira conforme NBR 7190:1997.

    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4

    :return: [0] Tipo de produto de madeira e a duração da carga (kmod1), 
             [1] Tipo do produto e a classe de umidade (kmod2), 
             [2] Coeficiente de modificação total (kmod)
    """

    # Conversão para língua pt
    if classe_carregamento == "dead":
        classe_carregamento = "permanente"
    elif classe_carregamento == "long-therm":
        classe_carregamento = "longa duração"
    elif classe_carregamento == "medium-therm":
        classe_carregamento = "média duração"
    elif classe_carregamento == "short-therm":
        classe_carregamento = "curta duração"
    elif classe_carregamento == "instantaneous":
        classe_carregamento = "instantânea"
    if classe_madeira == "natural wood":
        classe_madeira = "madeira natural"
    elif classe_madeira == "engineered wood":
        classe_madeira = "madeira recomposta"
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


def flexao_obliqua(
                    w_x: float, 
                    m_x: float, 
                    w_y: float = 1E-12, 
                    m_y: float = 0.0, 
                    area: float = 1E-12, 
                    p: float = 0.0
                  ) -> tuple[float, float, float]:
    """Calcula a resistência à flexão oblíqua da madeira.

    :param w_x: Módulo de resistência em relação ao eixo x [m³]
    :param m_x: Momento fletor em relação ao eixo x [kN.m]
    :param w_y: Módulo de resistência em relação ao eixo y [m³]. Padroniza-se w_y = 1E-12 para flexão simples
    :param m_y: Momento fletor em relação ao eixo y [kN.m]. Padroniza-se m_y = 0.0 para flexão simples
    :param area: Área da seção transversal [m²]. Padroniza-se area = 1E-12 para flexão simples
    :param p: Força axial [kN]. Padroniza-se p = 0.0 para flexão simples

    :return: [0] Tensão de flexão em relação ao eixo x [kPa], 
             [1] Tensão de flexão em relação ao eixo y [kPa],  
             [2] Tensão normal devido à força axial [kPa]
    """

    f_md_x = m_x / w_x
    f_md_y = m_y / w_y
    f_p = p / area

    return f_md_x, f_md_y, f_p 


def resistencia_calculo(f_k: float, gamma_w: float, k_mod: float) -> float:
    """Calcula a resistência de cálculo da madeira conforme NBR 7190.

    :param f_k: Resistência característica da madeira [kPa]
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param k_mod: Coeficiente de modificação da resistência da madeira

    :return: Resistência de cálculo da madeira [kPa]
    """

    f_d = (f_k / gamma_w) * k_mod
    
    return f_d


def checagem_tensoes_normais(
                                k_m: float,
                                sigma_x: float,
                                sigma_y: float,
                                f_md: float
                            ) -> tuple[float, str]:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param sigma_x: Tensão normal em relação ao eixo x [kPa]
    :param sigma_y: Tensão normal em relação ao eixo y [kPa]
    :param f_md: Resistência de cálculo da madeira na flexão [kPa]

    :return: [0] Equação Estado Limite, [1] Descrição do Fator de utilização
    """

    verif_1 = (sigma_x + k_m * sigma_y) - f_md
    verif_2 = (sigma_y + k_m * sigma_x) - f_md
    g = max(verif_1/f_md, verif_2/f_md)
    analise = 'OK' if g <= 0 else 'N OK'

    return g, analise


def checagem_momento_fletor_viga(
                                    w_x: float, 
                                    k_m: float, 
                                    m_gk: float, 
                                    m_qk: float, 
                                    classe_carregamento: str, 
                                    classe_madeira: str, 
                                    classe_umidade: int, 
                                    gamma_g: float, 
                                    gamma_q: float, 
                                    gamma_w: float, 
                                    f_mk: float
                                ) -> dict:
    """Verificação da função estado limite para momento fletor de uma 
        viga de madeira conforme NBR 7190.

    :param w_x: Módulo de resistência em relação ao eixo x [m³] 
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param m_gk: Momento fletor devido à carga permanente [kN.m]
    :param m_qk: Momento fletor devido à carga variável [kN.m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 
                                'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_mk: Resistência característica à flexão da madeira [kPa]

    :return:  Analise da verificação de tensões para momento fletor com as seguintes chaves: 
                "m_sd [kN.m]": Momento fletor de cálculo, 
                "k_mod1": Coeficiente de modificação 1, 
                "k_mod2": Coeficiente de modificação 2, 
                "k_mod": Coeficiente de modificação, 
                "sigma_x [kPa]": Tensão normal de cálculo em relação ao eixo x, 
                "f_md [kPa]": Resistência de cálculo da madeira, 
                "g_otimiz [-]": Equação Estado Limite no formato (S - R) / R,
                "g_confia [kPa]": Equação Estado Limite no formato R - S, 
                "analise": descrição se a viga passa ou não passa na verificação de tensões normais     
    """

    # Ações de cálculo
    m_sd = m_gk * gamma_g + m_qk * gamma_q

    # k_mod
    k_mod1, k_mod2, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões normais
    s_xd, _, _ = flexao_obliqua(w_x, m_sd)

    # Resistência de cálculo
    f_md = resistencia_calculo(f_mk, gamma_w, k_mod)                
    
    # Verificação de tensões normais
    g, analise = checagem_tensoes_normais(k_m, s_xd, 0.00, f_md)

    return {
                "m_sd [kN.m]": m_sd,
                "k_mod1": k_mod1,
                "k_mod2": k_mod2,
                "k_mod": k_mod,
                "sigma_x [kPa]": s_xd,
                "f_md [kPa]": f_md,
                "g_otimiz [-]": g,
                "g_confia [kPa]": f_md - s_xd,
                "analise": analise,
            }


def checagem_cisalhamento_viga(
                                    i_x: float, 
                                    area: float, 
                                    tipo_secao: str,
                                    v_gk: float, 
                                    v_qk: float, 
                                    classe_carregamento: str, 
                                    classe_madeira: str, 
                                    classe_umidade: int, 
                                    gamma_g: float, 
                                    gamma_q: float, 
                                    gamma_w: float, 
                                    f_vk: float
                                ) -> dict:
    """Verifica a função estado limite para cisalhamento de uma 
        viga de madeira conforme NBR 7190.

    :param s_x: Momento estático da seção em relação a x [m³]
    :param b_medio: Largura ou somatória das larguras no ponto da seção em estudo [m]
    :param i_x: Momento de inércia em relação ao eixo x [m4]
    :param area: Área da seção transversal da viga [m²]
    :param tipo_secao: 'Retangular' ou 'Circular'
    :param v_gk: Esforço cortante característico devido às cargas permanentes [kN]
    :param v_qk: Esforço cortante característico devido às cargas variáveis [kN]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 
                                'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_vk: Resistência característica ao cisalhamento da madeira [kPa]

    :return:  Analise da verificação de tensões para cisalhamento com as seguintes chaves:
             "v_sd [kN]": Cortante de cálculo,
             "f_vd [kPa]": Resistência de cálculo ao cisalhamento,
             "tau_sd [kPa]": Tensão de cisalhamento solicitante de cálculo,
             "g_otimiz [-]": Equação Estado Limite no formato (S - R) / R,
             "g_confia [kPa]": Equação Estado Limite no formato R - S, 
             "analise": descrição se a viga passa ou não passa na verificação de tensões cisalhantes     
    """

    # Ações de cálculo
    v_sd = v_gk * gamma_g + v_qk * gamma_q

    # k_mod
    _, _, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Resistência de cálculo
    f_vd = resistencia_calculo(f_vk, gamma_w, k_mod)     

    # Tensão de cálculo
    if tipo_secao == "Circular":
        tau_sd = (4/3) * v_sd / area
    else:
        tau_sd = (1.5 * v_sd) / area

    # Verificação
    g =  (tau_sd - f_vd) / f_vd

    return {
                "v_sd [kN]": v_sd,
                "f_vd [kPa]": f_vd,
                "tau_sd [kPa]": tau_sd,
                "g_otimiz [-]": g,
                "g_confia [kPa]": f_vd - tau_sd,
                "analise": 'OK' if g <= 0 else 'N OK',
            }


def checagem_flecha_viga(
                            l: float,
                            delta_gk: float,
                            delta_qk: float,
                            psi2: float,
                            phi: float
                        ) -> dict:
    """Verificação da função estado limite para flecha de uma viga de madeira
        conforme NBR 7190. São verificadas as flechas totais e para carga variável.

    :param l: vão teórico da viga [m]
    :param delta_gk: flecha devido a carga permanente [m]
    :param delta_qk: flecha devido a carga variável [m]
    :param psi2: Coeficiente de combinação simultânea para carga variável
    :param phi: Coeficiente de fluência para carga variável

    :return:  Analise da verificação de flecha com as seguintes chaves:
                "delta_lim [m]": limite de flecha para carga total, 
                "delta_lim_variavel [m]": limite de flecha para carga variável,
                "delta_fluencia [m]": flecha máxima devido à fluência,
                "delta_qk [m]": flecha máxima devido à carga variável, 
                "g_otimiz [-]": Equação Estado Limite no formato (S - R) / R, 
                "g_confia [m]": Equação Estado Limite no formato R - S, 
                "of [-]": Desempenho da viga em relação ao limite de flecha considerando fluência,
                "analise": descrição se a viga passa ou não passa na verificação de flecha     
    """

    # Verificação flecha total
    delta_sd_1 = delta_gk + psi2 * phi * delta_qk
    lim_1 = l / 250
    g_sd1 = (delta_sd_1 - lim_1) / lim_1

    # Verificação flecha variável
    delta_sd_2 = delta_qk
    lim_2 = l / 350
    g_sd2 = (delta_sd_2 - lim_2) / lim_2
    g_sd = max(g_sd1, g_sd2)

    return {
                "delta_lim_total [m]": lim_1,
                "delta_lim_variavel [m]": lim_2,
                "delta_fluencia [m]": delta_sd_1,
                "delta_qk [m]": delta_sd_2,
                "g_otimiz [-]": g_sd,
                "g_confia [m]": max(lim_1 - delta_sd_1, lim_2 - delta_sd_2),
                "of [-]": delta_sd_1/lim_1,
                "analise": 'OK' if g_sd <= 0 else 'N OK',
            }


def checagem_completa_longarina_madeira_flexao(
                                                geo: dict, 
                                                p_gk: float, 
                                                p_qk: float, 
                                                p_rodak: float, 
                                                a: float, 
                                                l: float, 
                                                classe_carregamento: str, 
                                                classe_madeira: str, 
                                                classe_umidade: int, 
                                                gamma_g: float, 
                                                gamma_q: float, 
                                                gamma_w: float,
                                                psi2: float,
                                                phi: float,
                                                f_mk: float,
                                                f_vk: float,
                                                e_modflex: float, 

                                            ) -> tuple[dict, dict, dict, dict]:
    """Verifica a longarina de madeira nas  condições de flexão, cisalhamento e flecha conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gk: Carga permanente característica, uniformemente distribuída [kN/m] na longarina
    :param p_qk: Carga variável característica de multidão [kPa]
    :param p_rodak: carga variável característica por roda [kN]
    :param a: distância entre eixos [m]
    :param l: Comprimento do vão [m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param psi2: Coeficiente de combinação para carga variável
    :param phi: Coeficiente de fluencia para carga variável
    :param f_mk: Resistência caracteristica à flexão [kPa]
    :param f_vk: Resistência caracteristica ao cisalhamento [kPa]
    :param e_modflex: Módulo de elasticidade à flexão [kPa]
    """

    # Geometria, Propriedades da seção transversal e coeficiente de correção para impacto vertical
    area, w_x, w_y, i_x, i_y, s_x, s_y, r_x, r_y, k_m = prop_madeiras(geo)
    ci = coef_impacto_vertical(l)
    aux_ci = (1 + 0.75 * (ci - 1))

    # Momentos fletores devido a carga permanente e variável
    m_gk = momento_max_carga_permanente(p_gk, l)
    m_qk = momento_max_carga_variavel(l, p_rodak, p_qk, a)
    m_qk *= aux_ci
    
    # Cisalhamento devido a carga permanente e variável
    v_gk = cortante_max_carga_permanente(p_gk, l)
    if 'd' in geo:
        v_qk = cortante_max_carga_variavel(l, p_rodak, p_qk, a, geo['d'])
        tipo_secao = "Circular"
    else:
        v_qk = cortante_max_carga_variavel(l, p_rodak, p_qk, a, geo['h'])    
        tipo_secao = "Retangular"
    v_qk *= aux_ci

    # Flecha devido a carga peermanente e variável
    delta_gk = flecha_max_carga_permanente(p_gk, l, e_modflex, i_x)
    delta_qk = flecha_max_carga_variavel(l, e_modflex, i_x, p_rodak, a)

    # Verificação da flexão pura
    res_flex = checagem_momento_fletor_viga(
                                                w_x, k_m, 
                                                m_gk, m_qk, 
                                                classe_carregamento, 
                                                classe_madeira, classe_umidade, 
                                                gamma_g, gamma_q, gamma_w, f_mk
                                            )
    
    # Verificação do cisalhamento
    res_cis = checagem_cisalhamento_viga(
                                            i_x, area, tipo_secao, 
                                            v_gk, v_qk, 
                                            classe_carregamento,
                                            classe_madeira, classe_umidade,
                                            gamma_g, gamma_q, gamma_w, f_vk
                                        )

    # Verificação de deslocamento carga variável e total com fluência
    res_flecha = checagem_flecha_viga(l, delta_gk, delta_qk, psi2, phi)

    # Relatório
    relat =  {
                    "area [m2]": area,
                    "w_x [m3]": w_x,
                    "i_x [m4]": i_x,
                    "s_x [m3]": s_x,
                    "coeficiente_impacto_vertical": ci,
                    "m_gk [kN.m]": m_gk,
                    "aux_ci": aux_ci,
                    "m_qk [kN.m]": m_qk,
                    "m_sd [kN.m]": res_flex["m_sd [kN.m]"],
                    "k_mod1": res_flex["k_mod1"],
                    "k_mod2": res_flex["k_mod2"],
                    "k_mod": res_flex["k_mod"],
                    "sigma_x [kPa]": res_flex["sigma_x [kPa]"],
                    "f_md [kPa]": res_flex["f_md [kPa]"],
                    "g_flexao [-]": res_flex["g_confia [kPa]"],
                    "analise_flexao": res_flex["analise"],
                    "v_gk [kN]": v_gk,
                    "v_qk [kN]": v_qk,
                    "v_sd [kN]": res_cis["v_sd [kN]"],
                    "f_vd [kPa]": res_cis["f_vd [kPa]"],
                    "tau_sd [kPa]": res_cis["tau_sd [kPa]"],
                    "g_cisalhamento [-]": res_cis["g_confia [kPa]"],
                    "analise_cisalhamento": res_cis["analise"],
                    "delta_gk [m]": delta_gk,
                    "delta_qk [m]": delta_qk,
                    "delta_fluencia [m]": res_flecha["delta_fluencia [m]"],
                    "delta_lim_total [m]": res_flecha["delta_lim_total [m]"],
                    "delta_lim_variavel [m]": res_flecha["delta_lim_variavel [m]"],
                    "g_flecha [-]": res_flecha["g_confia [m]"]
                }

    return res_flex, res_cis, res_flecha, relat


def checagem_completa_tabuleiro_madeira_flexao(
                                                geo: dict,
                                                p_gtabk: float, 
                                                p_rodak: float, 
                                                esp: float, 
                                                classe_carregamento: str, 
                                                classe_madeira: str, 
                                                classe_umidade: int, 
                                                gamma_g: float, 
                                                gamma_q: float, 
                                                gamma_w: float,
                                                f_mk: float,
                                            ) -> tuple[dict, dict]:
    """Verifica o tabuleiro de madeira nas condição de flexão conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gtabk: Carga permanente característica, uniformemente distribuída [kN/m] no tabuleiro
    :param p_rodak: carga variável característica por roda [kN]
    :param esp: Espaçamento entre longarinas [m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_mk: Resistência caracteristica à flexão [kPa]
    """

    # Geometria, Propriedades da seção transversal e coeficiente de correção para impacto vertical
    area, w_x, w_y, i_x, i_y, s_x, s_y, r_x, r_y, k_m = prop_madeiras(geo)
    ci = coef_impacto_vertical(esp)
    aux_ci = (1 + 0.75 * (ci - 1))

    # Momentos fletores devido a carga permanente e variável
    m_gk = momento_max_carga_permanente(p_gtabk, esp)
    m_qk = momento_max_carga_variavel_tabuleiro(p_rodak, esp)
    m_qk *= aux_ci
    
    # Verificação da flexão pura
    res_flex = checagem_momento_fletor_viga(
                                                w_x, k_m, 
                                                m_gk, m_qk, 
                                                classe_carregamento, 
                                                classe_madeira, classe_umidade, 
                                                gamma_g, gamma_q, gamma_w, f_mk
                                            )

    # Relatório
    relat =  {
                    "area [m2]": area,
                    "w_x [m3]": w_x,
                    "i_x [m4]": i_x,
                    "s_x [m3]": s_x,
                    "coeficiente_impacto_vertical": ci,
                    "m_gk [kN.m]": m_gk,
                    "aux_ci": aux_ci,
                    "m_qk [kN.m]": m_qk,
                    "m_sd [kN.m]": res_flex["m_sd [kN.m]"],
                    "k_mod1": res_flex["k_mod1"],
                    "k_mod2": res_flex["k_mod2"],
                    "k_mod": res_flex["k_mod"],
                    "sigma_x [kPa]": res_flex["sigma_x [kPa]"],
                    "f_md [kPa]": res_flex["f_md [kPa]"],
                    "g_flexao [-]": res_flex["g_confia [kPa]"],
                    "analise_flexao": res_flex["analise"],
                }

    return res_flex, relat


def textos_design() -> dict:
    textos = {
                "pt": {
                        "titulo": "Projeto estrutural de uma ponte de madeira",
                        "pre": "Verificação dos elementos estruturais",
                        "dados_pre": "Dados para dimensionamento",
                        "entrada_tipo_secao_longarina": "Tipo de seção",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_longarina": "Diâmetro da longarina (cm)",
                        "espaçamento_entre_longarinas": "Espaçamento entre longarinas (cm)",
                        "tipo_secao_tabuleiro": "Tipo de seção do tabuleiro",
                        "tipo_secao_tabuleiro_opcoes": ["Retangular"],
                        "largura_viga_tabuleiro": "Largura viga (cm) seção do tabuleiro",
                        "altura_viga_tabuleiro": "Altura viga (cm) seção do tabuleiro",
                        "planilha_head": "Upload da planilha de dados",
                        "texto_up": "Faça upload do arquivo gerado no pré-dimensionamento (.xlsx)",
                        "aguardando_upload": "Aguardando upload da planilha de pré-dimensionamento.",
                        "planilha_sucesso": "Planilha carregada com sucesso.",
                        "planilha_preview": "**Pré-visualização dos dados:**",
                        "gerador_projeto": "Gerar verificação estrutural do projeto",
                        "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                        "classe_madeira": "Classe de madeira",
                        "classe_madeira_opcoes": ["Madeira natural", "Madeira recomposta"],
                        "classe_umidade": "Classe de umidade",
                        "gamma_g": "γg",
                        "gamma_q": "γq",
                        "gamma_w": "γw",
                        "f_mk": "Resistência característica à flexão (MPa)",
                        "f_vk": "Resistência característica ao cisalhamento (MPa)",
                        "e_modflex": "Módulo de elasticidade à flexão (GPa)",
                        "gerador_desempenho": "Gerar desempenho estrutural para pré-dimensionamento",
                    },
                "en": {

                    },
            }
    return textos


def textos_pre_sizing_l() -> dict:
    textos = {
                "pt": {
                        "titulo": "Projeto paramétrico de uma ponte de madeira",
                        "pre": "Pré-dimensionamento",
                        "entrada_comprimento": "Comprimento das longarinas (cm)",
                        "pista": "Largura da pista disponível para longarinas (cm)",
                        "entrada_tipo_secao_longarina": "Tipo de seção",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_minimo": "Diâmetro mínimo (cm)",
                        "diametro_maximo": "Diâmetro máximo (cm)",
                        "tipo_secao_tabuleiro": "Tipo de seção do tabuleiro",
                        "tipo_secao_tabuleiro_opcoes": ["Retangular"],
                        "espaçamento_entre_longarinas_min": "Espaçamento mínimo entre longarinas (cm)",
                        "espaçamento_entre_longarinas_max": "Espaçamento máximo entre longarinas (cm)",
                        "largura_viga_tabuleiro_min": "Largura mínima da viga do tabuleiro (cm)",
                        "largura_viga_tabuleiro_max": "Largura máxima da viga do tabuleiro (cm)",
                        "altura_viga_tabuleiro_min": "Altura mínima da viga do tabuleiro (cm)",
                        "altura_viga_tabuleiro_max": "Altura máxima da viga do tabuleiro (cm)",
                        "carga_permanente": "Carga permanente atuante no tabuleiro (kPa) excluso peso próprio",
                        "carga_roda": "Carga por roda (kN)",
                        "carga_multidao": "Carga de multidão (kPa)",
                        "distancia_eixos": "Distância entre eixos (m) do veículo tipo",
                        "classe_carregamento": "Classe de carregamento",
                        "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                        "classe_madeira": "Classe de madeira",
                        "classe_madeira_opcoes": ["Madeira natural", "Madeira recomposta"],
                        "classe_umidade": "Classe de umidade",
                        "gamma_g": "γg",
                        "gamma_q": "γq",
                        "gamma_w": "γw",
                        "psi2": "ψ2",
                        "considerar_fluencia": "Coeficiente para fluência Tabela 20 NBR 7190",
                        "densidade_long": "Densidade da madeira (kg/m³) da longarina",
                        "f_mk": "Resistência característica à flexão (MPa) da longarina",
                        "f_vk": "Resistência característica ao cisalhamento (MPa) da longarina",
                        "e_modflex": "Módulo de elasticidade à flexão (GPa) da longarina",
                        "densidade_tab": "Densidade da madeira (kg/m³) do tabuleiro",
                        "f_mk_tab": "Resistência característica à flexão (MPa) do tabuleiro",
                        "gerador_desempenho": "Gerar desempenho estrutural via NSGA-II para pré-dimensionamento",
                        "botao_dados_down": "Baixar dados do pré-dimensionamento",
                        "tag_y_fig": r'$\frac{\delta_{\text{total}}}{L/250}$',
                        "tag_x_fig": "Área de madeira ($m^2$)",
                    },
                "en": {
                        "titulo": "Parametric design of a wooden bridge",
                        "pre": "Pre-sizing",
                        "entrada_comprimento": "Beam length (m)",
                        "pista": "Track width (m)",
                        "entrada_tipo_secao": "Section type",
                        "tipo_secao": ["Circular"],
                        "diametro_minimo": "Minimum diameter (cm)",
                        "diametro_maximo": "Maximum diameter (cm)",
                        "carga_permanente": "Dead load (kPa) excluding self-weight",
                        "carga_roda": "Load per wheel (kN)",
                        "carga_multidao": "Crowd load (kPa)",
                        "distancia_eixos": "Distance between axles (m)",
                        "classe_carregamento": "Load duration class",
                        "classe_carregamento_opcoes": ["Dead", "Long-term", "Medium-term", "Short-term", "Instantaneous"],
                        "classe_madeira": "Wood class",
                        "classe_madeira_opcoes": ["Natural wood", "Engineered wood"],
                        "classe_umidade": "Moisture class",
                        "gamma_g": "γg",
                        "gamma_q": "γq",
                        "gamma_w": "γw",
                        "psi2": "ψ2",
                        "considerar_fluencia": "Coefficient for creep Table 20 NBR 7190",
                        "densidade_long": "Wood density (kg/m³) of the beam",
                        "f_mk": "Characteristic bending strength (MPa)",
                        "f_vk": "Characteristic shear strength (MPa)",
                        "e_modflex": "Modulus of elasticity in bending (GPa)",
                        "gerador_desempenho": "Generate structural performance via NSGA-II for pre-sizing",
                        "botao_dados_down": "Download data from pre-sizing",
                        "tag_y_fig": "Total deflection ($m$)",
                        "tag_x_fig": "Wood area ($m^2$)",
                    },
            }
    return textos


def momento_max_carga_variavel_tabuleiro(p_rodak: float, esp: float, a_r: float = 0.45) -> float:
    """Momento fletor máximo devido à carga acidental concentrada (por roda) no tabuleiro.

    :param p_rodak: Carga por roda [kN]
    :param esp: Vão do tabuleiro (distância entre longarinas) [m]
    :param a_r: Comprimento efetivo associado à roda/classe [m]
    """

    return (p_rodak / 4.0) * (esp - a_r)


# Otimização estrutural
class ProjetoOtimo(ElementwiseProblem):
    def __init__(
                    self,
                    l: float,
                    p_gk: float,
                    p_rodak: float,
                    p_qk: float,
                    a: float,
                    classe_carregamento: str,
                    classe_madeira: str,
                    classe_umidade: int,
                    gamma_g: float,
                    gamma_q: float,
                    gamma_w: float,
                    psi2: float,
                    phi: float,
                    densidade_long: float,
                    densidade_tab: float,
                    f_mk_long: float,
                    f_vk_long: float,
                    e_modflex_long: float,
                    d_min: float,
                    d_max: float,
                    esp_min: float,
                    esp_max: float, 
                    bw_min: float,
                    bw_max: float,
                    h_min: float,
                    h_max: float,
                    f_mk_tab: float
                ):
        """Inicialização das variáveis do problema de otimização/confiabilidade estrutural
        """

        self.l = float(l)
        self.p_gk = float(p_gk)
        self.p_rodak = float(p_rodak)
        self.p_qk = float(p_qk)
        self.a = float(a)
        self.classe_carregamento = classe_carregamento
        self.classe_madeira = classe_madeira
        self.classe_umidade = classe_umidade
        self.gamma_g = float(gamma_g)
        self.gamma_q = float(gamma_q)
        self.gamma_w = float(gamma_w)
        self.psi2 = float(psi2)
        self.phi = float(phi)
        self.densidade_long = float(densidade_long)
        self.densidade_tab = float(densidade_tab)
        self.f_mk_long = float(f_mk_long)
        self.f_vk_long = float(f_vk_long)
        self.e_modflex_long = float(e_modflex_long)
        self.f_mk_tab = float(f_mk_tab)
        self.d_min = float(d_min)
        self.d_max = float(d_max)
        self.esp_min = float(esp_min)
        self.esp_max = float(esp_max)
        self.bw_min = float(bw_min)
        self.bw_max = float(bw_max)
        self.h_min = float(h_min)
        self.h_max = float(h_max)
        xl = np.array([d_min, esp_min, bw_min, h_min], dtype=float)
        xu = np.array([d_max, esp_max, bw_max, h_max], dtype=float)

        super().__init__(
                            n_var=4,
                            n_obj=2,
                            n_ieq_constr=4,
                            xl=xl,
                            xu=xu,
                            elementwise_evaluation=True
                        )

    def calcular_objetivos_restricoes_otimizacao(
                                                    self, 
                                                    d: float, 
                                                    esp: float, 
                                                    bw: float, 
                                                    h: float
                                                ) -> tuple[list, list, dict, dict, dict, dict, dict, dict, dict]:
        """Determina os objetivos e restrições do problema de otimização.
        """

        # Conversão unidades e cálculo de cargas
        l = self.l / 100.0                          # [m]
        d /= 100.0                                  # [m]
        esp /= 100.0                                # [m]
        bw /= 100.0                                 # [m]
        h /= 100.0                                  # [m]
        f_mk_long = self.f_mk_long *1E3             # [kPa]
        f_vk_long = self.f_vk_long * 1E3            # [kPa]
        e_modflex_long = self.e_modflex_long * 1E6  # [kPa]
        f_mk_tab = self.f_mk_tab * 1E3              # [kPa]

        # Armazena o geometria
        geo_tab = {"b_w": bw, "h": h}
        geo_long = {"d": d}

        # Carga permanente do tabuleiro que atua na longarina
        carga_area_tab = (self.densidade_tab * 9.81) * h / 1E3                      # [kPa]
        p_gk_long = (self.p_gk + carga_area_tab) * esp                              # [kN/m]
        props_long = prop_madeiras(geo_long)
        area_long = props_long[0]
        pp_gk_long = peso_proprio_longarina(self.densidade_long, area_long)         # [kN/m]
        p_gk_long += pp_gk_long                                                     # [kN/m]

        # Avaliação flexão, cisalhamento e flecha da longarina
        res_m, res_v, res_f_total, relat_l = checagem_completa_longarina_madeira_flexao(
                                                                                            geo_long,
                                                                                            p_gk_long,
                                                                                            self.p_qk,
                                                                                            self.p_rodak,
                                                                                            self.a,
                                                                                            l,
                                                                                            self.classe_carregamento.lower(),
                                                                                            self.classe_madeira.lower(),
                                                                                            self.classe_umidade,
                                                                                            self.gamma_g,
                                                                                            self.gamma_q,
                                                                                            self.gamma_w,
                                                                                            self.psi2,
                                                                                            self.phi,
                                                                                            f_mk_long,
                                                                                            f_vk_long,
                                                                                            e_modflex_long,
                                                                                        )

        # Carga permanente do tabuleiro que atua no tabuleiro
        p_gtabk = (carga_area_tab + self.p_gk) * bw
        relat_carga = {
                        "carga_area_tab [kPa]": carga_area_tab,
                        "p_gtabk [kN/m]": p_gtabk,
                        "pp_gk_long [kN/m]": pp_gk_long,
                        "p_glongk [kN/m]": p_gk_long,
                      }

        # Avaliação do flexão tabuleiro
        res_m_tab, relat_t = checagem_completa_tabuleiro_madeira_flexao(
                                                                            geo_tab,
                                                                            p_gtabk,
                                                                            self.p_rodak,
                                                                            esp,
                                                                            self.classe_carregamento.lower(),
                                                                            self.classe_madeira.lower(),
                                                                            self.classe_umidade,
                                                                            self.gamma_g,
                                                                            self.gamma_q,
                                                                            self.gamma_w,
                                                                            f_mk_tab,
                                                                        )
        
        # Área de materiais empregados
        props_tab = prop_madeiras(geo_tab)
        area_tab = props_tab[0]
        f1 = area_long + area_tab
        f2 = -res_f_total["of [-]"]         # Invertendo o sinal para garantir um processo de maximização
        g1 = res_m["g_otimiz [-]"]
        g2 = res_v["g_otimiz [-]"]
        g3 = res_f_total["g_otimiz [-]"]
        g4 = res_m_tab["g_otimiz [-]"]

        return [f1, f2], [g1, g2, g3, g4], res_m, res_v, res_f_total, relat_l, res_m_tab, relat_t, relat_carga
    
    def _evaluate(self, x, out, *args, **kwargs):
        
        # Geometria da longarina e espaçamento entre longarinas
        d = float(x[0])
        esp = float(x[1])

        # Geometria do tabuleiro
        bw = float(x[2])
        h = float(x[3])

        # Cálculo dos objetivos e restrições
        f, g, _, _, _, _, _, _, _ = self.calcular_objetivos_restricoes_otimizacao(d, esp, bw, h)
        out["F"] = np.array(f, dtype=float)
        out["G"] = np.array(g, dtype=float)


def chamando_nsga2(
                        dados: dict,
                        ds: list,
                        esps: list,
                        bws: list,
                        hs: list
                    ) -> pd.DataFrame:
    """Função para chamar o algoritmo NSGA-II para otimização do projeto estrutural.
    """

    # Instanciando o problema de otimização, construindo a estrutura exemplo
    problem = ProjetoOtimo(
                            l=dados["l (cm)"],
                            p_gk=dados["p_gk (kPa)"],
                            p_rodak=dados["p_rodak (kN)"],
                            p_qk=dados["p_qk (kPa)"],
                            a=dados["a (m)"],
                            classe_carregamento=dados["classe_carregamento"],
                            classe_madeira=dados["classe_madeira"],
                            classe_umidade=dados["classe_umidade"],
                            gamma_g=dados["gamma_g"],
                            gamma_q=dados["gamma_q"],
                            gamma_w=dados["gamma_w"],
                            psi2=dados["psi_2"],
                            phi=dados["phi"],

                            densidade_long=dados["densidade longarina (kg/m³)"],
                            densidade_tab=dados["densidade tabuleiro (kg/m³)"],

                            f_mk_long=dados["resistência característica à flexão longarina (MPa)"],
                            f_vk_long=dados["resistência característica ao cisalhamento longarina (MPa)"],
                            e_modflex_long=dados["módulo de elasticidade à flexão longarina (GPa)"],

                            f_mk_tab=dados["resistência característica à flexão tabuleiro (MPa)"],

                            d_min=ds[0],
                            d_max=ds[1],
                            esp_min=esps[0],
                            esp_max=esps[1],
                            bw_min=bws[0],
                            bw_max=bws[1],
                            h_min=hs[0],
                            h_max=hs[1],
                        )

    algorithm = NSGA2(
                        pop_size=500, sampling=FloatRandomSampling(),
                        crossover=SBX(prob=0.9, eta=15),
                        mutation=PM(eta=20),
                        eliminate_duplicates=True
                     )
    termination = get_termination("n_gen", 400)

    res = minimize(
                        problem, algorithm, 
                        termination, seed=1, 
                        save_history=False, verbose=False
                  )

    F_nsga = res.F
    G_nsga = res.G
    X_nsga = res.X
    
    return pd.DataFrame(
                            {
                                "d [cm]": X_nsga[:, 0],
                                "esp [cm]": X_nsga[:, 1],
                                "bw [cm]": X_nsga[:, 2],
                                "h [cm]": X_nsga[:, 3],
                                "area [m²]": F_nsga[:, 0],
                                "delta [-]": -F_nsga[:, 1], 
                                "flex lim beam [(Ms-Mr)/Mr]": G_nsga[:, 0], 
                                "cis lim beam [(Vs-Vr)/Vr]": G_nsga[:, 1], 
                                "delta lim beam [(ps-pr)/pr]": G_nsga[:, 2],
                                "flex lim deck [(Ms-Mr)/Mr]": G_nsga[:, 3],
                            }
                        )


# # Confiabilidade estrutural
# def smooth_max(a, b, k=50.0):
#     m = np.maximum(a, b)
#     return m + np.log(np.exp(k*(a-m)) + np.exp(k*(b-m))) / k


# def obj_confia(samples, params):

#     g = np.zeros((samples.shape[0]))
#     for i in range(samples.shape[0]):
#         # Extrair amostras 
#         p_gk = samples[i, 0]
#         p_rodak = samples[i, 1]
#         p_qk  = samples[i, 2]
#         f_mk = samples[i, 3]
#         f_vk = samples[i, 4]
#         e_modflex = samples[i, 5]
#         f_mktab = samples[i, 6]
#         densidade_long = samples[i, 7]
#         densidade_tab = samples[i, 8]
#         # print(p_gk, p_rodak, p_qk, f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab)
        
#         # Parâmetros fixos
#         a = params[0]
#         l = params[1]
#         classe_carregamento = params[2]
#         classe_madeira = params[3]
#         classe_umidade = params[4]
#         d_cm = params[5]
#         esp = params[6]
#         bw_cm = params[7]
#         h_cm = params[8]
#         tipo_g = params[9]  # 'flexao', 'cisalhamento' ou 'flecha'

#         # Função Estado Limite
#         projeto = ProjetoEstrutural(
#                                         l=l,
#                                         p_gk=p_gk,
#                                         p_rodak=p_rodak,
#                                         p_qk=p_qk,
#                                         a=a,
#                                         classe_carregamento=classe_carregamento,
#                                         classe_madeira=classe_madeira,
#                                         classe_umidade=classe_umidade,
#                                         gamma_g=1.0,
#                                         gamma_q=1.0,
#                                         gamma_w=1.0,
#                                         psi2=1.0,
#                                         phi=1.0,
#                                         densidade_long=densidade_long,
#                                         densidade_tab=densidade_tab,
#                                         f_mk_long=f_mk,
#                                         f_vk_long=f_vk,
#                                         e_modflex_long=e_modflex,
#                                         f_mk_tab=f_mktab,
#                                     )
#         res = projeto.calcular(d_cm=d_cm, esp_cm=esp, bw_cm=bw_cm, h_cm=h_cm)
#         if tipo_g == 'flexao':
#             g[i] = -res["flexao_longarina"]["g [kPa]"]
#         elif tipo_g == 'cisalhamento':
#             g[i] = -res["cisalhamento_longarina"]["g [kPa]"]
#         elif tipo_g == 'flecha':
#             delta_sd_1 = res["flecha_total_longarina"]["delta_fluencia [m]"]
#             delta_rd_1 = res["flecha_total_longarina"]["delta_lim_total [m]"]
#             delta_sd_2 = res["flecha_total_longarina"]["delta_qk [m]"]
#             delta_rd_2 = res["flecha_total_longarina"]["delta_lim_variavel [m]"]
#             g_fluencia = delta_rd_1 - delta_sd_1
#             g_variavel = delta_rd_2 - delta_sd_2
#             g[i] = smooth_max(g_fluencia, g_variavel)

#     return g


def gev_loc_scale_from_mean_std(mean: float, std: float) -> tuple[float, float]:
    EULER_GAMMA = 0.5772156649015329
    scale = std * np.sqrt(6) / np.pi
    loc = mean - EULER_GAMMA * scale
    return loc, scale


def chamando_form(p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab, d_cm, esp_cm, bw_cm, h_cm, tipo_g):
    p_gk = float(p_gk)
    p_rodak = float(p_rodak)
    p_qk = float(p_qk)
    a = float(a)
    l = float(l)
    f_mk = float(f_mk)
    f_vk = float(f_vk)
    e_modflex = float(e_modflex)
    f_mktab = float(f_mktab)
    densidade_long = float(densidade_long)
    densidade_tab = float(densidade_tab)
    d_cm = float(d_cm)
    esp_cm = float(esp_cm)
    bw_cm = float(bw_cm)
    h_cm = float(h_cm)
    # Parámetros GEV
    loc_rodak, scale_rodak = gev_loc_scale_from_mean_std(p_rodak, p_rodak*0.2)
    loc_qk, scale_qk = gev_loc_scale_from_mean_std(p_qk, p_qk*0.2)
    
    # Distribuições
    p_gk_aux = TruncatedNormal(a=(-p_gk/(p_gk*0.1)), b=np.inf, loc=p_gk, scale=p_gk*0.1)
    p_rodak_aux = GeneralizedExtreme(c=0.0, loc=loc_rodak, scale=scale_rodak)
    p_qk_aux = GeneralizedExtreme(c=0.0, loc=loc_qk, scale=scale_qk)
    f_mk_aux = TruncatedNormal(a=(-f_mk/(f_mk*0.1)), b=np.inf, loc=f_mk, scale=f_mk*0.1)
    f_vk_aux = TruncatedNormal(a=(-f_vk/(f_vk*0.1)), b=np.inf, loc=f_vk, scale=f_vk*0.1)     
    e_modflex_aux = TruncatedNormal(a=(-e_modflex/(e_modflex*0.1)), b=np.inf, loc=e_modflex, scale=e_modflex*0.1)
    f_mktab_aux = TruncatedNormal(a=(-f_mktab/(f_mktab*0.1)), b=np.inf, loc=f_mktab, scale=f_mktab*0.1)
    densidade_long_aux = TruncatedNormal(a=(-densidade_long/(densidade_long*0.1)), b=np.inf, loc=densidade_long, scale=densidade_long*0.1)
    densidade_tab_aux = TruncatedNormal(a=(-densidade_tab/(densidade_tab*0.1)), b=np.inf, loc=densidade_tab, scale=densidade_tab*0.1)

    # Variáveis fixas da viga
    paramss = [a, l, classe_carregamento, classe_madeira, classe_umidade, d_cm, esp_cm, bw_cm, h_cm, tipo_g]

    # Confiabilidade
    varss = [p_gk_aux, p_rodak_aux, p_qk_aux, f_mk_aux, f_vk_aux, e_modflex_aux, f_mktab_aux, densidade_long_aux, densidade_tab_aux]
    model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
    runmodel_nlc = RunModel(model=model)
    form = FORM(distributions=varss, runmodel_object=runmodel_nlc, tolerance_u=1e-3, tolerance_beta=1e-3)
    form.run()
    beta = form.beta[0]
    pf = form.failure_probability[0]

    return beta, pf


import numpy as np

from UQpy.sampling import MonteCarloSampling, LatinHypercubeSampling
from UQpy.sampling.ImportanceSampling import ImportanceSampling
from UQpy.distributions import TruncatedNormal, GeneralizedExtreme, JointIndependent
from UQpy.run_model.RunModel import RunModel
from UQpy.run_model.model_execution.PythonModel import PythonModel


def chamando_sampling(
                        p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade,
                        f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab,
                        d_cm, esp_cm, bw_cm, h_cm, tipo_g,
                        method: str = "LHS",          # "MC", "LHS" ou "IS"
                        nsamples: int = 100000,
                        random_state: int = 123
                    ):
    # casts
    p_gk = float(p_gk); p_rodak = float(p_rodak); p_qk = float(p_qk)
    a = float(a); l = float(l)
    f_mk = float(f_mk); f_vk = float(f_vk); e_modflex = float(e_modflex)
    f_mktab = float(f_mktab)
    densidade_long = float(densidade_long); densidade_tab = float(densidade_tab)
    d_cm = float(d_cm); esp_cm = float(esp_cm); bw_cm = float(bw_cm); h_cm = float(h_cm)

    # helper truncnorm X>=0 (a,b no domínio padrão)
    def tn_pos(mean, cov):
        mu = float(mean)
        sig = float(abs(mean) * cov)
        a_std = (0.0 - mu) / sig
        return TruncatedNormal(a=a_std, b=np.inf, loc=mu, scale=sig)

    # -------------------------
    # TARGET (como você já faz)
    # -------------------------
    loc_rodak, scale_rodak = gev_loc_scale_from_mean_std(p_rodak, p_rodak * 0.2)
    loc_qk, scale_qk       = gev_loc_scale_from_mean_std(p_qk,   p_qk   * 0.2)

    p_gk_aux           = tn_pos(p_gk, 0.10)
    p_rodak_aux        = GeneralizedExtreme(c=0.0, loc=loc_rodak, scale=scale_rodak)
    p_qk_aux           = GeneralizedExtreme(c=0.0, loc=loc_qk, scale=scale_qk)
    f_mk_aux           = tn_pos(f_mk, 0.10)
    f_vk_aux           = tn_pos(f_vk, 0.10)
    e_modflex_aux      = tn_pos(e_modflex, 0.10)
    f_mktab_aux        = tn_pos(f_mktab, 0.10)
    densidade_long_aux = tn_pos(densidade_long, 0.10)
    densidade_tab_aux  = tn_pos(densidade_tab, 0.10)

    varss = [
                p_gk_aux, p_rodak_aux, p_qk_aux, f_mk_aux, f_vk_aux,
                e_modflex_aux, f_mktab_aux, densidade_long_aux, densidade_tab_aux
            ]

    # params fixos
    paramss = [a, l, classe_carregamento, classe_madeira, classe_umidade, d_cm, esp_cm, bw_cm, h_cm, tipo_g]

    # -------------------------
    # SAMPLER UQpy
    # -------------------------
    method = method.upper()

    if method == "MC":
        sampler = MonteCarloSampling(distributions=varss, nsamples=nsamples, random_state=random_state)
        samples = sampler.samples
        weights = None

    elif method == "LHS":
        sampler = LatinHypercubeSampling(distributions=varss, nsamples=nsamples, random_state=random_state)
        samples = sampler.samples
        weights = None

    elif method == "IS":
        # 1) joint target (independente)
        target_joint = JointIndependent(marginals=varss)

        # 2) proposal: "puxar" para falha (heurística simples e editável)
        #    - ações ↑ (médias maiores)
        #    - resistências/rigidez ↓ (médias menores)
        m_load = 1.20
        m_res  = 0.85
        m_E    = 0.90
        m_rho  = 1.10

        # GEV proposal (mantém COV ~ 0.2 via std = mean*0.2, só desloca a média)
        p_rodak_p = p_rodak * m_load
        p_qk_p    = p_qk    * m_load
        loc_rodak_p, scale_rodak_p = gev_loc_scale_from_mean_std(p_rodak_p, p_rodak_p * 0.2)
        loc_qk_p, scale_qk_p       = gev_loc_scale_from_mean_std(p_qk_p,    p_qk_p    * 0.2)

        proposal_marginals = [
            tn_pos(p_gk * m_load, 0.10),                                        # p_gk
            GeneralizedExtreme(c=0.0, loc=loc_rodak_p, scale=scale_rodak_p),     # p_rodak
            GeneralizedExtreme(c=0.0, loc=loc_qk_p,    scale=scale_qk_p),        # p_qk
            tn_pos(f_mk * m_res, 0.10),                                          # f_mk
            tn_pos(f_vk * m_res, 0.10),                                          # f_vk
            tn_pos(e_modflex * m_E, 0.10),                                       # E
            tn_pos(f_mktab * m_res, 0.10),                                       # f_mktab
            tn_pos(densidade_long * m_rho, 0.10),                                # rho_long
            tn_pos(densidade_tab  * m_rho, 0.10),                                # rho_tab
        ]

        proposal_joint = JointIndependent(marginals=proposal_marginals)

        # 3) ImportanceSampling: gera amostras pela proposta e calcula pesos (normalizados)
        sampler = ImportanceSampling(
            log_pdf_target=target_joint.log_pdf,
            proposal=proposal_joint,
            random_state=random_state,
            nsamples=nsamples,
        )
        samples = sampler.samples
        weights = np.asarray(sampler.weights, dtype=float).reshape(-1)

    else:
        raise ValueError("method deve ser 'MC', 'LHS' ou 'IS'")

    # -------------------------
    # rodar modelo UQpy
    # -------------------------
    model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
    rmodel = RunModel(model=model)
    rmodel.run(samples=samples)

    g = np.asarray(rmodel.qoi_list, dtype=float).reshape(-1)

    # Convenção: falha quando g <= 0
    if weights is None:
        pf = float(np.mean(g <= 0.0))
    else:
        # pesos do IS já vêm normalizados para somar 1 no UQpy
        pf = float(np.sum((g <= 0.0).astype(float) * weights))

    beta = beta_from_pf(pf)

    return sampler, beta, pf


if __name__ == "__main__":
    df = pd.read_excel("beam_data.xlsx")
    df = df.to_dict(orient="records")
    df = df[0] 
    ds = [30, 150]
    esps = [30, 200]
    bws = [12, 60]
    hs = [12, 60]
    problem = ProjetoOtimo(
                        l=df["l (cm)"],
                        p_gk=df["p_gk (kPa)"],
                        p_rodak=df["p_rodak (kN)"],
                        p_qk=df["p_qk (kPa)"],
                        a=df["a (m)"],
                        classe_carregamento=df["classe_carregamento"],
                        classe_madeira=df["classe_madeira"],
                        classe_umidade=df["classe_umidade"],
                        gamma_g=df["gamma_g"],
                        gamma_q=df["gamma_q"],
                        gamma_w=df["gamma_w"],
                        psi2=df["psi_2"],
                        phi=df["phi"],
                        densidade_long=df["densidade longarina (kg/m³)"],
                        densidade_tab=df["densidade tabuleiro (kg/m³)"],
                        f_mk_long=df["resistência característica à flexão longarina (MPa)"],
                        f_vk_long=df["resistência característica ao cisalhamento longarina (MPa)"],
                        e_modflex_long=df["módulo de elasticidade à flexão longarina (GPa)"],
                        f_mk_tab=df["resistência característica à flexão tabuleiro (MPa)"],
                        d_min=ds[0],
                        d_max=ds[1],
                        esp_min=esps[0],
                        esp_max=esps[1],
                        bw_min=bws[0],
                        bw_max=bws[1],
                        h_min=hs[0],
                        h_max=hs[1],
                    )

    # 2) Define uma solução manual
    x_manual = np.array([[50., 120.0, 10., 30.]])   # d, esp, bw, h

    # 3) Avalia
    out = problem.evaluate(x_manual, return_values_of=["F", "G"])

    # 4) Imprime resultados
    f = out[0]
    g = out[1]
    print(f, g)