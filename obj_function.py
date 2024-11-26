import numpy as np

def momento_resistente_sem_corrosao(d_barras, n_barras, f_ck, f_yk, b_w, d, gamma_c, gamma_s):
    """
    Determina o momento resistente de uma viga de concreto armado sem corrosão.

    Args: 
        d_barras (Float): Diâmetro da barra de aço (m)
        n_barras (int): Número de barras de aço
        f_ck (Float): Resistência característica do concreto (kPa)
        f_yk (Float): Resistência característica do aço (kPa)
        b_w (Float): Largura da seção (m)
        d (Float): Altura útil da seção (m)
        gamma_c (Float): Coeficiente de ponderação do concreto
        gamma_s (Float): Coeficiente de ponderação do aço
            
    Returns:
        m_rd (Float): Momento resistente da viga (kN.m)
    """

    # Resistência de cálculo
    f_cd = f_ck / gamma_c
    f_yd = f_yk / gamma_s

    # Propriedades do dimensionamento
    f_ck /= 1E3
    if f_ck >  50:
        lambda_c = 0.80 - ((f_ck - 50) / 400)
        alpha_c = (1.00 - ((f_ck - 50) / 200)) * 0.85
        beta = 0.35
    else:
        lambda_c = 0.80
        alpha_c = 0.85
        beta = 0.45
    f_ck *= 1E3

    # Momento resistente
    area_aco = n_barras * ((np.pi * d_barras ** 2) / 4)
    x_iii = (area_aco * f_yd) / (alpha_c * f_cd * b_w * lambda_c)
    m_rd = area_aco * f_yd * (d - 0.50 * lambda_c * x_iii)

    return m_rd


def pontes(x, none_variable):
    """Objective function for the Nowak example (tutorial).
    """

    # Random variables and fixed variables
    f_ck = x[0]
    w = x[1]
    pho_a_s = x[2]
    b_w = x[3]
    h = x[4]
    f_y_aux = x[5]
    df = none_variable['dataset']
    l = none_variable['l (cm)']
    d = 0.90 * h
    res = []
    load = []
    g = []
    # Internal load
    m_w = (w * l ** 2) / 8
    for i, row in df.iterrows():
        load.append(m_w)
        n_barras = row['positive bending moment - number of longitudinal bars']
        d_barras = row['positive bending moment - diameter longitudinal bars (mm)'] * 1E-3
        f_yk = 500 * 1E3 * f_y_aux #####
        gamma_c = 1.00
        gamma_s = 1.00
        res.append(momento_resistente_sem_corrosao(d_barras, n_barras * pho_a_s, f_ck, f_yk, b_w, d, gamma_c, gamma_s))
        g.append(res[-1] - load[-1])

    return res, load, g


if __name__ == '__main__':
    # Test
    x = [50E3, 20, 0.01, 30, 50, 500]
    none_variable = {'dataset': pd.DataFrame({'positive bending moment - number of longitudinal bars': [4, 4], 'positive bending moment - diameter longitudinal bars (mm)': [16, 16]}), 'l (cm)': 500}
    res, load, g = pontes(x, none_variable)
    print(res)
    print(load)
    print(g)