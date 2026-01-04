"""Contém funções para cálculo e verificação de estruturas de madeira."""
import numpy as np
from UQpy.distributions import Normal, Gamma, GeneralizedExtreme, JointIndependent
from UQpy.run_model.model_execution.PythonModel import PythonModel
from UQpy.run_model import RunModel
from UQpy.reliability import FORM


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


def coef_impacto_vertical(liv: float) -> float:
    """Cálculo do Coeficiente de Impacto Vertical (CIV) conforme NBR 7188:2024 item 5.1.3.1. CIV = Coeficiente que majora os esforços para considerar efeitos dinâmicos e vibrações do tráfego.

    :param liv: Vão teórico da estrutura [m] - distância entre apoios para cálculo do impacto
    
    :return: Valor do coeficiente de impacto vertical (CIV)
    """

    if liv < 10.0:
        return 1.35  
    elif 10.0 <= liv <= 200.0:
        return 1 + 1.06 * (20 / (liv + 50))  
    else:
        return 1.0   


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


def checagem_tensoes(k_m: float, sigma_x: float, sigma_y: float, f_md: float) -> tuple[float, str]:
    """Verifica as tensões na madeira conforme NBR 7190.
    
    :param k_m: Coeficiente de correção do tipo da seção transversal
    :param sigma_x: Tensão normal em relação ao eixo x [kN/m²]
    :param sigma_y: Tensão normal em relação ao eixo y [kN/m²]
    :param f_md: Resistência de cálculo da madeira [kN/m²]

    :return: [0] Equação Estado Limite, [1] Descrição do Fator de utilização
    """

    verif_1 = f_md - sigma_x + k_m * sigma_y
    verif_2 = f_md - sigma_y + k_m * sigma_x
    g = max(verif_1, verif_2)
    analise = 'OK' if g <= 1 else 'N OK'

    return g, analise


def checagem_flexao_pura_viga(w_x: float, k_m: float, m_gk: float, m_qk: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k:float) -> dict:
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

    return:  Analise da verificação de tensões: {"m_sd [kN.m]": Momento fletor de cálculo, "k_mod1": Coeficiente de modificação 1, "k_mod2": Coeficiente de modificação 2, "k_mod": Coeficiente de modificação, "sigma_x [kN/m²]": Tensão normal em relação ao eixo x, "f_md [kN/m²]": Resistência de cálculo da madeira, "g [kN/m²]": Equação Estado Limite, "analise": descrição se a viga passa ou não passa na verificação de tensões}     
    """

    # Ações de cálculo
    m_sd = m_gk * gamma_g + m_qk * gamma_q

    # k_mod
    k_mod1, k_mod2, k_mod = k_mod_madeira(classe_carregamento, classe_madeira, classe_umidade)

    # Tensões
    s_x, _, _ = flexao_obliqua(w_x, m_sd)

    # Resistência de cálculo (caso mais desfavorável)
    f_md = min(resistencia_calculo(f_c0k, gamma_w, k_mod), resistencia_calculo(f_t0k, gamma_w, k_mod))                
    
    # Verificação
    g, analise = checagem_tensoes(k_m, s_x, _, f_md)

    return {
                "m_sd [kN.m]": m_sd,
                "k_mod1": k_mod1,
                "k_mod2": k_mod2,
                "k_mod": k_mod,
                "sigma_x [kN/m²]": s_x,
                "f_md [kN/m²]": f_md,
                "g [kN/m²]": g,
                "analise": analise,
            }


def checagem_flecha_viga(l: float, e_modflex: float, i_x: float, p_rodak: float, a: float) -> dict:
    """Verifica a resistência à flexão oblíqua da madeira conforme NBR 7190.

    :param l: vão teórico da viga [m]
    :param e_modflex: módulo de elasticidade da madeira [kN/m²]
    :param i_x: momento de inércia da seção transversal [m⁴]
    :param p_rodak: carga variável característica por roda [kN]
    :param a: distância entre eixos [m]

    return:  Analise da verificação de flecha: {"delta_lim [m]": limite de flecha, "delta_qk [m]": flecha máxima devido à carga variável, "g [m]": Equação Estado Limite, "analise": descrição se a viga passa ou não passa na verificação de flecha}     
    """

    # limite de flecha
    delta_lim = l / 360

    # k_mod
    delta_qk = flecha_max_carga_variavel(l, e_modflex, i_x, p_rodak, a)

    # Função Estado Limite
    g = delta_lim - delta_qk

    return {
                "delta_lim [m]": delta_lim,
                "delta_qk [m]": delta_qk,
                "g [m]": g,
                "analise": 'OK' if g >= 0 else 'N OK',
            }


def checagem_longarina_madeira_flexao(geo: dict, p_gk: float, p_qk: float, p_rodak: float, a: float, l: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_c0k: float, f_t0k: float, e_modflex: float) -> tuple[dict, dict, dict]:
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
    :param f_c0k: Resistência característica à compressão paralela às fibras [kN/m²]
    :param f_t0k: Resistência característica à tração paralela às fibras [kN/m²]
    :param e_modflex: Módulo de elasticidade à flexão [kN/m²]

    """

    # Geometria, Propriedades da seção transversal
    area, w_x, w_y, i_x, i_y, r_x, r_y, k_m = prop_madeiras(geo)

    # Momentos fletores de cálculo carga permanente e variável
    m_gk = momento_max_carga_permanente(p_gk, l)
    m_qkaux = momento_max_carga_variavel(l, p_rodak, p_qk, a)

    # Coeficiente de Impacto Vertical
    ci = coef_impacto_vertical(l)

    # Combinação de ações
    m_qk =  (m_qkaux + 0.75 * (ci - 1) * m_qkaux)

    # Verificação da flexão pura
    res_flex = checagem_flexao_pura_viga(w_x, k_m, m_gk, m_qk, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k)

    # Verificação de deslocamento (a implementar)
    res_flecha = checagem_flecha_viga(l, e_modflex, i_x, p_rodak, a)

    # Verificação do cisalhamento
    res_cis = {}

    return res_flex, res_flecha, res_cis


def obj_confia(samples, params):
    
    # Extrair amostras
    g = np.zeros((samples.shape[0]))
    p_gk = samples[:, 0]
    p_rodak = samples[:, 1]
    p_qk  = samples[:, 2]
    f_ck = samples[:, 3]
    f_tk = samples[:, 4]
    e_modflex = samples[:, 5]

    # Parâmetros fixos
    geo = params[0]
    a = params[1]
    l = params[2]
    classe_carregamento = params[3]
    classe_madeira = params[4]
    classe_umidade = params[5]
    gamma_g = params[6]
    gamma_q = params[7]
    gamma_w = params[8]

    # Função Estado Limite
    res_m, _, _ = checagem_longarina_madeira_flexao(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex)
    g[0] = res_m["g [kN/m²]"]

    return g


def confia_flexao_pura(geo: dict, p_gk: float, p_rodak: float, p_qk: float, a: float, l: float, classe_carregamento: str, classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_w: float, f_ck: float, f_tk: float, e_modflex: float) -> tuple[float, float]:

    # Distribuições
    p_gk_aux = Normal(loc=p_gk, scale=p_gk*0.1)
    p_rodak_aux = Normal(loc=p_rodak, scale=p_rodak*0.1)
    p_qk_aux = Normal(loc=p_qk, scale=p_qk*0.1)
    f_tk_aux = Normal(loc=f_tk, scale=f_tk*0.1)
    f_ck_aux = Normal(loc=f_ck, scale=f_ck*0.1)     
    e_modflex_aux = Normal(loc=e_modflex, scale=e_modflex*0.1)
    varss = [p_gk_aux, p_rodak_aux, p_qk_aux, f_ck_aux, f_tk_aux, e_modflex_aux]

    # Variáveis fixas da viga
    paramss = [geo, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_ck, f_tk, e_modflex]

    # Reliability analysis Normal Loading Condition
    model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
    runmodel_nlc = RunModel(model=model)
    form = FORM(distributions=varss, runmodel_object=runmodel_nlc, tolerance_u=1e-5, tolerance_beta=1e-5)
    form.run()
    beta = form.beta[0]
    pf = form.failure_probability[0]

    return beta, pf


if __name__ == "__main__":
    # Teste das funções
    geo = {'d': 0.3}
    p_gk = 10.0
    p_rodak = 40.0
    p_qk = 4.0
    a = 1.5
    l = 6.0
    classe_carregamento = 'permanente'
    classe_madeira = 'madeira natural'
    classe_umidade = 2
    gamma_g = 1.0
    gamma_q = 1.0
    gamma_w = 1.0
    f_c0k = 20E3
    f_t0k = 20E3
    e_modflex = 12E6

    # samples = np.array([[10.0, 40.0, 4.0, 20E3, 15E3, 12E6]])
    # params = [geo, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w]
    # g = obj_confia(samples, params)
    # res_flex, res_flecha, res_cis = checagem_longarina_madeira_flexao(geo, p_gk, p_qk, p_rodak, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k, e_modflex)
    # print("g: ", g)
    # print("Flexão: ", res_flex)
    # print("Flecha: ", res_flecha)
    # print("Cisalhamento: ", res_cis)

    beta, pf = confia_flexao_pura(geo, p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k, e_modflex)
    print("Beta: ", beta)
    print("Pf: ", pf)