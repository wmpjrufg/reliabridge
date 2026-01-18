"""Contém funções para cálculo e verificação de estruturas de madeira."""
import numpy as np
import pandas as pd
import io

from UQpy.distributions import Normal, Gamma, GeneralizedExtreme, JointIndependent
from UQpy.run_model.model_execution.PythonModel import PythonModel
from UQpy.run_model import RunModel
from UQpy.reliability import FORM
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
    dpi = 600                                                   # Change as you wish
    name = 'scatter'           # Change as you wish

    ### Chart dimensions (in centimeters)
    b_cm = 10                                                   # Change as you wish
    h_cm = 10                                                    # Change as you wish
    inches_to_cm = 1 / 2.54
    b_input = b_cm * inches_to_cm
    h_input = h_cm * inches_to_cm

    ### Axis and labels (For LateX font format use the dollar sign $)
    size_label = 10                                             # Change as you wish
    color_label = 'black'                                        # or hexadecimal. Change as you wish
    size_axis = 10                                              # Change as you wish
    color_axis = 'black'                                          # or hexadecimal. Change as you wish

    ### Scatter
    alpha_scatter = 1.0                                             # Change as you wish
    color_scatter = 'blue'                                          # Change as you wish
    size_scatter = 10                                               # Change as you wish

    ### Grid
    on_or_off = True
    line_width_grid = 0.5                                       # Change as you wish
    alpha_grid = 0.3                                            # Change as you wish
    style_grid = '-'                                            # Change as you wish
    color_grid = 'gray'                                         # or hexadecimal. Change as you wish

    ### Figure
    fig, ax = plt.subplots(figsize=(b_input, h_input))
    ax.tick_params(axis='both', which='major', labelsize=size_axis, colors=color_axis)
    ax.set_xlabel(label_x, fontsize=size_label, color=color_label)
    ax.set_ylabel(label_y, fontsize=size_label, color=color_label)

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
    :param p_qk: carga variável característica de multidão [kN/m²]
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
    :param e_modflex: módulo de elasticidade da madeira [kN/m²]
    :param i_x: momento de inércia da seção transversal [m⁴]

    :return: flecha máxima devido à carga permanente [m]
    """

    return (5 * p_gk * l**4) / (384 * e_modflex * i_x)


def flecha_max_carga_variavel(l: float, e_modflex: float, i_x: float, p_rodak: float, a: float) -> float:
    """Calcula a flecha máxima devido à carga variável.
    
    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kN/m²]
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
    :param p_qk: carga variável característica de multidão [kN/m²]
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

    :return: [0] Tensão de flexão em relação ao eixo x [kN/m²], 
             [1] Tensão de flexão em relação ao eixo y [kN/m²],  
             [2] Tensão normal devido à força axial [kN/m²]
    """

    f_md_x = m_x / w_x
    f_md_y = m_y / w_y
    f_p = p / area

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


def checagem_tensoes_normais(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> tuple[float, str]:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param sigma_x: Tensão normal em relação ao eixo x [kN/m²]
    :param sigma_y: Tensão normal em relação ao eixo y [kN/m²]
    :param f_md: Resistência de cálculo da madeira na flexão [kN/m²]

    :return: [0] Equação Estado Limite, [1] Descrição do Fator de utilização
    """

    verif_1 = (sigma_x + k_m * sigma_y) - f_md
    verif_2 = (sigma_y + k_m * sigma_x) - f_md
    g = max(verif_1, verif_2)
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
    """Verifica a função estado limite para momento fletor de uma viga de madeira conforme NBR 7190.

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
    :param f_mk: Resistência característica à flexão da madeira [kN/m²]

    :return:  Analise da verificação de tensões para momento fletor com as seguintes chaves: 
             "m_sd [kN.m]": Momento fletor de cálculo, 
             "k_mod1": Coeficiente de modificação 1, 
             "k_mod2": Coeficiente de modificação 2, 
             "k_mod": Coeficiente de modificação, 
             "sigma_x [kN/m²]": Tensão normal em relação ao eixo x, 
             "f_md [kN/m²]": Resistência de cálculo da madeira, 
             "g [kN/m²]": Equação Estado Limite no formato R - S,
             "sigma_sd/f_md": Fator de utilização da peça, 
             "analise": descrição se a viga passa ou não passa na verificação de tensões     
    """

    # Ações de cálculo
    m_sd = m_gk * gamma_g + m_qk * gamma_q

    # k_mod
    k_mod1, k_mod2, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões
    s_x, _, _ = flexao_obliqua(w_x, m_sd)

    # Resistência de cálculo
    f_md = resistencia_calculo(f_mk, gamma_w, k_mod)                
    
    # Verificação
    g, analise = checagem_tensoes_normais(k_m, s_x, 0.00, f_md)

    return {
                "m_sd [kN.m]": m_sd,
                "k_mod1": k_mod1,
                "k_mod2": k_mod2,
                "k_mod": k_mod,
                "sigma_x [kN/m²]": s_x,
                "f_md [kN/m²]": f_md,
                "g [kN/m²]": g,
                "sigma_sd/f_md": s_x / f_md,
                "analise": analise,
            }


def checagem_cisalhamento_viga(
                                    s_x: float, 
                                    b_medio: float, 
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
    """Verifica a função estado limite para cisalhamento de uma viga de madeira conforme NBR 7190.

    :param s_x: Momento estático da seção em relação a x [m³]
    :param b_medio: Largura ou somatória das larguras no ponto da seção em estudo [m]
    :param i_x: Momento de inércia em relação ao eixo x [m4]
    :param area: Área da seção transversal da viga [m²]
    :param tipo_secao: 'Retangular' ou 'Circular'
    :param v_gk: Esforço cortante característico devido às cargas permanentes [kN]
    :param v_qk: Esforço cortante característico devido às cargas variáveis [kN]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param f_vk: Resistência característica ao cisalhamento da madeira [kN/m²]

    :return:  Analise da verificação de tensões para cisalhamento com as seguintes chaves:
             "v_sd [kN]": Cortante de cálculo,
             "f_vd [kN/m²]": Resistência de cálculo ao cisalhamento,
             "tau_sd [kN/m²]": Tensão de cisalhamento solicitante de cálculo,
             "g [kN]": diferença entre resistência e solicitação,
             "tau_sd/f_vd": tau_sd / f_vd,
             "analise": descrição se a viga passa ou não passa na verificação de tensões     
    """

    # Ações de cálculo
    v_sd = v_gk * gamma_g + v_qk * gamma_q

    # k_mod
    _, _, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Resistência de cálculo
    f_vd = resistencia_calculo(f_vk, gamma_w, k_mod)     

    # Tensão de cálculo
    if tipo_secao == "Circular":
        tau_sd = (v_sd * s_x) / (b_medio * i_x)
    else:
        tau_sd = (1.5 * v_sd) / area

    # Verificação
    g =  tau_sd - f_vd

    return {
                "v_sd [kN]": v_sd,
                "f_vd [kN/m²]": f_vd,
                "tau_sd [kN/m²]": tau_sd,
                "g [kN/m²]": g,
                "tau_sd/f_vd": tau_sd / f_vd,
                "analise": 'OK' if g <= 0 else 'N OK',
            }


def checagem_flecha_viga(l: float, delta_gk: float, delta_qk: float, psi2: float, phi: float) -> dict:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param l: vão teórico da viga [m]
    :param delta_gk: flecha devido a carga permanente [m]
    :param delta_qk: flecha devido a carga variável [m]
    :param psi2: Coeficiente de combinação para carga variável
    :param phi: Coeficiente de fluencia para carga variável

    :return:  Analise da verificação de flecha com as seguintes chaves:
             "delta_lim [m]": limite de flecha, 
             "delta_qk [m]": flecha máxima devido à carga variável, 
             "g [m]": Equação Estado Limite, 
             "delta_qk/delta_lim": Fator de utilização da peça,
             "analise": descrição se a viga passa ou não passa na verificação de flecha     
    """

    # Verificação flecha total
    delta_sd_1 = delta_gk + psi2 * phi * delta_qk
    g_sd1 = delta_sd_1 - l / 250

    # Verificação flecha variável
    delta_sd_2 = delta_qk
    g_sd2 = delta_sd_2 - l / 350
    g_sd = max(g_sd1, g_sd2)

    return {
                "delta_lim_total [m]": l/250,
                "delta_lim_variavel [m]": l/350,
                "delta_fluencia [m]": delta_sd_1,
                "delta_qk [m]": delta_sd_2,
                "g [m]": g_sd,
                "delta_phi/delta_lim": delta_sd_1 / (l/250),
                "delta_qk/delta_lim": delta_sd_2 / (l/350),
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
                                                densidade: float, 
                                                f_mk: float,
                                                f_vk: float,
                                                e_modflex: float, 

                                            ) -> tuple[dict, dict, dict, dict, str]:
    """Verifica a longarina de madeira submetida à flexão simples conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gk: Carga permanente característica, uniformemente distribuída [kN/m]
    :param p_qk: Carga variável característica de multidão [kN/m²]
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
    :param densidade: densidade da madeira [kg/m³]
    :param f_mk: Resistência caracteristica à flexão [kN/m²]
    :param f_vk: Resistência caracteristica ao cisalhamento [kN/m²]
    :param e_modflex: Módulo de elasticidade à flexão [kN/m²]
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
        b_medio = geo['d']
        tipo_secao = "Circular"
    else:
        v_qk = cortante_max_carga_variavel(l, p_rodak, p_qk, a, geo['h'])    
        b_medio = geo['b_w']
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
                                            s_x, b_medio, i_x, area, tipo_secao, 
                                            v_gk, v_qk, 
                                            classe_carregamento,
                                            classe_madeira, classe_umidade,
                                            gamma_g, gamma_q, gamma_w, f_vk
                                        )

    # Verificação de deslocamento carga variável e total com fluência
    res_flecha = checagem_flecha_viga(l, delta_gk, delta_qk, psi2, phi)

    # Relatório
    # relat = relatorio()

    return res_flex, res_cis, res_flecha, "relat"


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
                                                densidade: float, 
                                                f_mk: float,
                                            ) -> tuple[dict, str]:
    """Verifica a longarina de madeira submetida à flexão simples conforme NBR 7190.

    :param geo: Parâmetros geométricos da seção transversal. Se retangular: Chaves: 'b_w': Largura da seção transversal [m] e 'h': Altura da seção transversal [m]. Se circular: Chaves: 'd': Diâmetro da seção transversal [m]
    :param p_gtabk: Carga permanente característica no tabuleiro excluso peso próprio [kN/m²]
    :param p_rodak: carga variável característica por roda [kN]
    :param esp: Espaçamento entre longarinas [m]
    :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
    :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
    :param classe_umidade: 1, 2, 3, 4
    :param gamma_g: Coeficiente parcial de segurança para carga permanente
    :param gamma_q: Coeficiente parcial de segurança para carga variável
    :param gamma_w: Coeficiente parcial de segurança para madeira
    :param densidade: densidade da madeira [kg/m³]
    :param f_mk: Resistência caracteristica à flexão [kN/m²]
    """

    # Geometria, Propriedades da seção transversal e coeficiente de correção para impacto vertical
    area, w_x, w_y, i_x, i_y, s_x, s_y, r_x, r_y, k_m = prop_madeiras(geo)
    ci = coef_impacto_vertical(esp)
    aux_ci = (1 + 0.75 * (ci - 1))

    # Momentos fletores devido a carga permanente e variável
    p_gk = p_gtabk * geo['b_w']
    m_gk = momento_max_carga_permanente(p_gk, esp)
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
    # relat = relatorio()

    return res_flex, "relat"


def textos_design() -> dict:
    textos = {
                "pt": {
                        "titulo": "Projeto estrutural de uma ponte de madeira",
                        "pre": "Verificação dos elementos estruturais",
                        "entrada_tipo_secao_longarina": "Tipo de seção",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_longarina": "Diâmetro da longarina (cm)",
                        "espaçamento_entre_longarinas": "Espaçamento entre longarinas (cm)",
                        "tipo_secao_tabuleiro": "Tipo de seção do tabuleiro",
                        "tipo_secao_tabuleiro_opcoes": ["Retangular"],
                        "largura_viga_tabuleiro": "Largura (m) seção do tabuleiro",
                        "altura_viga_tabuleiro": "Altura (m) seção do tabuleiro",
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
                        "carga_permanente": "Carga permanente atuante no tabuleiro (kN/m²) excluso peso próprio",
                        "carga_roda": "Carga por roda (kN)",
                        "carga_multidao": "Carga de multidão (kN/m²)",
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
                        "tag_y_fig": "Flecha total ($m$)",
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
                        "carga_permanente": "Dead load (kN/m²) excluding self-weight",
                        "carga_roda": "Load per wheel (kN)",
                        "carga_multidao": "Crowd load (kN/m²)",
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


# Otimização
class ProjetoOtimo(ElementwiseProblem):
    def __init__(
                    self,
                    l,
                    p_gk, p_rodak, p_qk, a,
                    classe_carregamento, classe_madeira, classe_umidade,
                    gamma_g, gamma_q, gamma_w, psi2, phi,
                    densidade_long, densidade_tab, f_mk_long, f_vk_long, e_modflex_long,
                    d_min, d_max, esp_min, esp_max, 
                    bw_min, bw_max, h_min, h_max, f_mk_tab
                ):
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
        self.d_min = float(d_min)
        self.d_max = float(d_max)
        self.esp_min = float(esp_min)
        self.esp_max = float(esp_max)
        self.bw_min = float(bw_min)
        self.bw_max = float(bw_max)
        self.h_min = float(h_min)
        self.h_max = float(h_max)
        self.f_mk_tab = float(f_mk_tab)
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

    def _evaluate(self, x, out, *args, **kwargs):
        
        # Geometria da longarina e espaçamento entre longarinas
        d = float(x[0])
        esp = float(x[1])
        geo_long = {"d": d}

        # Geometria do tabuleiro
        bw = float(x[2])
        h = float(x[3])

        # Conversão unidades e cálculo de cargas
        l = self.l / 100.0                          # [m]
        d /= 100.0                                  # [m]
        esp /= 100.0                                # [m]
        bw /= 100.0                                 # [m]
        h /= 100.0                                  # [m]
        f_mk_long = self.f_mk_long *1E3             # [kN/m²]
        f_vk_long = self.f_vk_long * 1E3            # [kN/m²]
        e_modflex_long = self.e_modflex_long * 1E6  # [kN/m²]
        f_mk_tab = self.f_mk_tab * 1E3              # [kN/m²]

        # Armazena o geometria
        geo_tab = {"b_w": bw, "h": h}
        geo_long = {"d": d}

        # Correção da carga permanente do tabuleiro
        carga_area_tab = self.densidade_tab * h * 9.81 / 1E3                        # [kN/m²]
        p_gk_long = (self.p_gk + carga_area_tab) * esp                              # [kN/m]
        props_long = prop_madeiras(geo_long)
        area_long = props_long[0]
        p_gk_long += peso_proprio_longarina(self.densidade_long, area_long) * esp   # [kN/m]

        # Avaliação da longarina
        res_m, res_v, res_f_total, relat = checagem_completa_longarina_madeira_flexao(
                                                                                        geo_long,
                                                                                        p_gk_long,
                                                                                        self.p_rodak,
                                                                                        self.p_qk,
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
                                                                                        self.densidade_long,
                                                                                        f_mk_long,
                                                                                        f_vk_long,
                                                                                        e_modflex_long,
                                                                                    )
        # Avaliação do tabuleiro
        res_m_tab, relat = checagem_completa_tabuleiro_madeira_flexao(
                                                                        geo_tab,
                                                                        self.p_gk + carga_area_tab,
                                                                        self.p_rodak,
                                                                        esp,
                                                                        self.classe_carregamento.lower(),
                                                                        self.classe_madeira.lower(),
                                                                        self.classe_umidade,
                                                                        self.gamma_g,
                                                                        self.gamma_q,
                                                                        self.gamma_w,
                                                                        self.densidade_tab,
                                                                        f_mk_tab,
                                                                    )
        
        # Área de materiais eempregados
        props_tab = prop_madeiras(geo_tab)
        area_tab = props_tab[0]
        area_total = area_long + area_tab
        flecha_total = res_f_total["delta_fluencia [m]"]
        out["F"] = np.array([area_total, -flecha_total], dtype=float)
        out["G"] = np.array([res_m["g [kN/m²]"], res_v["g [kN/m²]"], res_f_total["g [m]"], res_m_tab["g [kN/m²]"]], dtype=float)


def chamando_nsga2(dados: dict, ds: list, esps: list, bws: list, hs: list): # -> pd.DataFrame:
    problem = ProjetoOtimo(
                            l=dados["l (cm)"],
                            p_gk=dados["p_gk (kN/m²)"],
                            p_rodak=dados["p_rodak (kN)"],
                            p_qk=dados["p_qk (kN/m²)"],
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
                                "delta [m]": -F_nsga[:, 1], 
                                "flex lim beam [kPa]": G_nsga[:, 0], 
                                "cis lim beam [kPa]": G_nsga[:, 1], 
                                "delta lim beam [m]": G_nsga[:, 2],
                                "flex lim deck [kPa]": G_nsga[:, 3],
                            }
                        )


class ProjetoEstrutural:
    def __init__(
                    self,
                    l,
                    p_gk, p_rodak, p_qk, a,
                    classe_carregamento, classe_madeira, classe_umidade,
                    gamma_g, gamma_q, gamma_w, psi2, phi,
                    densidade_long, densidade_tab,
                    f_mk_long, f_vk_long, e_modflex_long,
                    f_mk_tab,
                ):
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

    def calcular(self, d_cm, esp_cm, bw_cm, h_cm):
        """Executa o dimensionamento completo para uma solução definida.
        """

        # Conversões
        l = self.l / 100.0
        d = d_cm / 100.0
        esp = esp_cm / 100.0
        bw = bw_cm / 100.0
        h = h_cm / 100.0
        f_mk_long = self.f_mk_long * 1E3
        f_vk_long = self.f_vk_long * 1E3
        e_modflex_long = self.e_modflex_long * 1E6
        f_mk_tab = self.f_mk_tab * 1E3

        # Armazena geometria
        geo_long = {"d": d}
        geo_tab = {"b_w": bw, "h": h}

        # Correção da carga permanente do tabuleiro
        carga_area_tab = self.densidade_tab * h * 9.81 / 1E3                        # [kN/m²]
        p_gk_long = (self.p_gk + carga_area_tab) * esp                              # [kN/m]
        props_long = prop_madeiras(geo_long)
        area_long = props_long[0]
        p_gk_long += peso_proprio_longarina(self.densidade_long, area_long) * esp   # [kN/m]

        # Avaliação da longarina
        res_m, res_v, res_f_total, relat_long = checagem_completa_longarina_madeira_flexao(
                                                                                                geo_long,
                                                                                                p_gk_long,
                                                                                                self.p_rodak,
                                                                                                self.p_qk,
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
                                                                                                self.densidade_long,
                                                                                                f_mk_long,
                                                                                                f_vk_long,
                                                                                                e_modflex_long,
                                                                                            )
        # Avaliação do tabuleiro
        res_m_tab, relat_tab = checagem_completa_tabuleiro_madeira_flexao(
                                                                            geo_tab,
                                                                            self.p_gk + carga_area_tab,
                                                                            self.p_rodak,
                                                                            esp,
                                                                            self.classe_carregamento.lower(),
                                                                            self.classe_madeira.lower(),
                                                                            self.classe_umidade,
                                                                            self.gamma_g,
                                                                            self.gamma_q,
                                                                            self.gamma_w,
                                                                            self.densidade_tab,
                                                                            f_mk_tab,
                                                                        )

        # Área de materiais eempregados
        props_tab = prop_madeiras(geo_tab)
        area_tab = props_tab[0]

        return {
                    "geometria": {
                                    "d_cm": d_cm,
                                    "esp_cm": esp_cm,
                                    "bw_cm": bw_cm,
                                    "h_cm": h_cm,
                                },
                    "areas": {
                                "longarina_m2": area_long,
                                "tabuleiro_m2": area_tab,
                                "total_m2": area_long + area_tab,
                            },
                    "flexao_longarina": res_m,
                    "cisalhamento_longarina": res_v,
                    "flecha_total_longarina": res_f_total,
                    "flexao_tabuleiro": res_m_tab,
                    "relatorios": {
                                        "longarina": relat_long,
                                        "tabuleiro": relat_tab,
                                    },
                }

# if __name__ == "__main__":
#     problem = ProjetoOtimo(
#                             l=6.0,
#                             p_gk=10.0,
#                             p_rodak=40.0,
#                             p_qk=4.0,
#                             a=1.5,
#                             classe_carregamento="permanente",
#                             classe_madeira="madeira recomposta",
#                             classe_umidade=1,
#                             gamma_g=1.35,
#                             gamma_q=1.5,
#                             gamma_w=1.0,
#                             densidade=650.0,
#                             f_mk=30.0,
#                             f_vk=20.0,
#                             e_modflex=12.,
#                             d_min=30.0,
#                             d_max=100.0,
#                         )

#     # 2) Define uma solução manual (d em cm)
#     x_manual = np.array([[100.0]])   # shape (1, n_var) -> aqui n_var=1

#     # 3) Avalia
#     out = problem.evaluate(x_manual, return_values_of=["F", "G"])

#     f = out[0]
#     g = out[1]
#     print(f, g)

# def flecha_max_carga_variavel_tabuleiro(p_rodak: float, e_modflex: float, i_x: float, esp: float, a_r: float = 0.45) -> float:
#     """Flecha máxima devido à carga variável (por roda) no tabuleiro.

#     :param p_rodak: Carga por roda [kN]
#     :param e_modflex: Módulo de elasticidade da madeira [kN/m²]
#     :param i_x: Momento de inércia da seção transversal do tabuleiro [m⁴]
#     :param esp: Vão do tabuleiro (distância entre longarinas) [m]
#     :param a_r: Comprimento efetivo associado à roda/classe [m]

#     :return: Flecha máxima devido à carga variável [m]
#     """

#     termo = 0.5 * a_r * (esp ** 3) - (a_r ** 2) * (esp ** 2) + (a_r ** 4) / 24.0
#     return (p_rodak / (16.0 * e_modflex * i_x * a_r)) * termo


# def relatorio():
#     var = "# Cabeçalho"
#     var += "\n"
#     return var
    
# def obj_confia(samples, params):

#     # Extrair amostras  
#     n = samples.shape[0] #cada linha de samples gera um valor próprio de g, o vetor g passa a representar corretamente o estado limite, o FORM passa a enxergar a superfície de falha correta
#     g = np.zeros(n)
#     #g = np.zeros((samples.shape[0]))  g tinha tamanho n,apenas a posição g[0] era preenchida, todas as outras ficavam em zero, só a primeira amostra era avaliada, as demais eram tratadas como g = 0 (estado limite ativo), o resultado de β e pf ficava fisicamente errado
#     p_gk = samples[:, 0]
#     p_rodak = samples[:, 1]
#     p_qk  = samples[:, 2]
#     f_ck = samples[:, 3]
#     f_tk = samples[:, 4]
#     e_modflex = samples[:, 5]

    
#     # Parâmetros fixos
#     geo = params[0]
#     a = params[1]
#     l = params[2]
#     classe_carregamento = params[3]
#     classe_madeira = params[4]
#     classe_umidade = params[5]
#     gamma_g = params[6]
#     gamma_q = params[7]
#     gamma_w = params[8]

#     # Função Estado Limite
#     for i in range(n): res_m, _, _ = checagem_longarina_madeira_flexao(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)
#     #g[0] = res_m["g [kN/m²]"]
#     g[i] = res_m["g [kN/m²]"]

#     return g


# def confia_flexao_pura(geo: dict, p_gk: float, p_rodak: float, p_qk: float, a: float, l: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_ck: float, f_tk: float, e_modflex: float) -> tuple[float, float]:

#     # Distribuições
#     p_gk_aux = Normal(loc=p_gk, scale=p_gk*0.1)
#     p_rodak_aux = Normal(loc=p_rodak, scale=p_rodak*0.1)
#     p_qk_aux = Normal(loc=p_qk, scale=p_qk*0.1)
#     f_tk_aux = Normal(loc=f_tk, scale=f_tk*0.1)
#     f_ck_aux = Normal(loc=f_ck, scale=f_ck*0.1)     
#     e_modflex_aux = Normal(loc=e_modflex, scale=e_modflex*0.1)
#     varss = [p_gk_aux, p_rodak_aux, p_qk_aux, f_ck_aux, f_tk_aux, e_modflex_aux]

#     # Variáveis fixas da viga
#     paramss = [geo, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex]

#     # Reliability analysis Normal Loading Condition
#     model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
#     runmodel_nlc = RunModel(model=model)
#     form = FORM(distributions=varss, runmodel_object=runmodel_nlc, tolerance_u=1e-5, tolerance_beta=1e-5)
#     form.run()
#     beta = form.beta[0]
#     pf = form.failure_probability[0]

#     return beta, pf


# if __name__ == "__main__":
#     # Teste das funções
#     geo = {'d': 0.49}
#     p_gk = 1.7177
#     p_rodak = 40.0
#     p_qk = 4.0
#     a = 1.5
#     l = 13.4
#     classe_carregamento = 'permanente'
#     classe_madeira = 'madeira natural'
#     classe_umidade = 1
#     gamma_g = 1.3
#     gamma_q = 1.5
#     gamma_w = 1.4
#     f_c0k = 40E3
#     f_t0k = 40E3
#     e_modflex = 14.5E6

#     # samples = np.array([[10.0, 40.0, 4.0, 20E3, 15E3, 12E6]])
#     # params = [geo, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w]
#     # g = obj_confia(samples, params)
#     # res_flex, res_flecha, res_cis = checagem_longarina_madeira_flexao(geo, p_gk, p_qk, p_rodak, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k, e_modflex)
#     # print("g: ", g)
#     # print("Flexão: ", res_flex)
#     # print("Flecha: ", res_flecha)
#     # print("Cisalhamento: ", res_cis)

#     beta, pf = confia_flexao_pura(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k, e_modflex)
#     print("Beta: ", beta)
#     print("Pf: ", pf)
