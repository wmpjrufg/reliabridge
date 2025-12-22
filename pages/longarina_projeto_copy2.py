
# from madeiras import *

import numpy as np
import streamlit as st
import math




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
    


# Tela ###############################################################################################################################################

# Obtém o idioma da sessão (já configurado na página principal)
lang = st.session_state.get("lang", "pt")

# Dicionário com todas as traduções
textos = {
    "pt": {
        "titulo": "Cálculo de Longarina",
        "geometria": "Geometria da seção",
        "tipo_secao": "Tipo de seção",
        "opcoes_secao": ["Retangular", "Circular"],
        "largura_b": "Largura b (m)",
        "altura_h": "Altura h (m)",
        "diametro_d": "Diâmetro d (m)",
        "esforcos": "Esforços solicitantes",
        "momento_permanente_x": "Momento permanente M_gk,x (kN·m)",
        "momento_variavel_x": "Momento variável M_qk,x (kN·m)",
        "momento_permanente_y": "Momento permanente M_gk,y (kN·m)",
        "momento_variavel_y": "Momento variável M_qk,y (kN·m)",
        "forca_normal": "Força normal P_k (kN)",
        "propriedades": "Propriedades da madeira",
        "classe_carregamento": "Classe de carregamento",
        "opcoes_carregamento": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
        "classe_madeira": "Tipo de madeira",
        "opcoes_madeira": ["Madeira natural", "Madeira recomposta"],
        "classe_umidade": "Classe de umidade",
        "opcoes_umidade": ["1", "2", "3", "4"],
        "gamma_g": "γ_g (coeficiente permanente)",
        "gamma_q": "γ_q (coeficiente variável)",
        "gamma_w": "γ_w (coeficiente madeira)",
        "resistencias": "Resistências características",
        "f_c0k": "f_c0k - Compressão paralela (kN/m²)",
        "f_t0k": "f_t0k - Tração paralela (kN/m²)",
        "botao": "Calcular Resistência",
        "resultado_analise": "Análise:",
        "fator_utilizacao": "Fator de utilização:",
        "raio_minimo": "Raio mínimo de giração (m):",
        "calculando": "Calculando...",
        "sucesso": "Cálculo realizado com sucesso!",
        "erro_geometria": "Erro: Defina a geometria da seção",
        "estrutura_adequada": "✓ Estrutura adequada",
        "estrutura_insuficiente": "⚠ Estrutura pode estar subdimensionada"
    },
    "en": {
        "titulo": "Stringer Calculation",
        "geometria": "Section Geometry",
        "tipo_secao": "Section type",
        "opcoes_secao": ["Rectangular", "Circular"],
        "largura_b": "Width b (m)",
        "altura_h": "Height h (m)",
        "diametro_d": "Diameter d (m)",
        "esforcos": "Applied Loads",
        "momento_permanente_x": "Permanent moment M_gk,x (kN·m)",
        "momento_variavel_x": "Variable moment M_qk,x (kN·m)",
        "momento_permanente_y": "Permanent moment M_gk,y (kN·m)",
        "momento_variavel_y": "Variable moment M_qk,y (kN·m)",
        "forca_normal": "Normal force P_k (kN)",
        "propriedades": "Wood Properties",
        "classe_carregamento": "Loading class",
        "opcoes_carregamento": ["Permanent", "Long duration", "Medium duration", "Short duration", "Instantaneous"],
        "classe_madeira": "Wood type",
        "opcoes_madeira": ["Natural wood", "Recomposed wood"],
        "classe_umidade": "Humidity class",
        "opcoes_umidade": ["1", "2", "3", "4"],
        "gamma_g": "γ_g (permanent coefficient)",
        "gamma_q": "γ_q (variable coefficient)",
        "gamma_w": "γ_w (wood coefficient)",
        "resistencias": "Characteristic Resistances",
        "f_c0k": "f_c0k - Parallel compression (kN/m²)",
        "f_t0k": "f_t0k - Parallel tension (kN/m²)",
        "botao": "Calculate Resistance",
        "resultado_analise": "Analysis:",
        "fator_utilizacao": "Utilization factor:",
        "raio_minimo": "Minimum radius of gyration (m):",
        "calculando": "Calculating...",
        "sucesso": "Calculation completed successfully!",
        "erro_geometria": "Error: Define section geometry",
        "estrutura_adequada": "✓ Structure adequate",
        "estrutura_insuficiente": "⚠ Structure may be underdimensioned"
    }
}

t = textos[lang]

# Função de cálculo integrada
def checagem_flexao_simples_ponte(geo, m_gkx, m_qkx, classe_carregamento, classe_madeira, 
                                 classe_umidade, gamma_g, gamma_q, gamma_w, f_c0k, f_t0k, 
                                 p_k=0, m_gky=0, m_qky=0, lang="pt"):
    """
    Função integrada de cálculo para verificação de longarina em madeira
    """
    
    # 1. Coeficientes de modificação (kmod) baseados na classe de carregamento e umidade
    kmod_valores = {
        "Permanente": {"1": 0.60, "2": 0.55, "3": 0.50, "4": 0.45},
        "Longa duração": {"1": 0.70, "2": 0.65, "3": 0.60, "4": 0.55},
        "Média duração": {"1": 0.80, "2": 0.75, "3": 0.70, "4": 0.65},
        "Curta duração": {"1": 0.90, "2": 0.85, "3": 0.80, "4": 0.75},
        "Instantânea": {"1": 1.10, "2": 1.10, "3": 1.10, "4": 1.10},
        "Permanent": {"1": 0.60, "2": 0.55, "3": 0.50, "4": 0.45},
        "Long duration": {"1": 0.70, "2": 0.65, "3": 0.60, "4": 0.55},
        "Medium duration": {"1": 0.80, "2": 0.75, "3": 0.70, "4": 0.65},
        "Short duration": {"1": 0.90, "2": 0.85, "3": 0.80, "4": 0.75},
        "Instantaneous": {"1": 1.10, "2": 1.10, "3": 1.10, "4": 1.10}
    }
    
    # 2. Coeficiente γm para madeira
    gamma_m = 1.40  # Valor padrão para madeira sólida
    
    # 3. Determinar kmod
    classe_umidade_str = str(classe_umidade)
    if classe_carregamento in kmod_valores and classe_umidade_str in kmod_valores[classe_carregamento]:
        kmod = kmod_valores[classe_carregamento][classe_umidade_str]
    else:
        kmod = 0.70  # Valor padrão
    
    # 4. Cálculo das resistências de cálculo
    f_c0d = (kmod * f_c0k) / gamma_m  # Resistência à compressão de cálculo
    f_t0d = (kmod * f_t0k) / gamma_m  # Resistência à tração de cálculo
    
    # 5. Cálculo das propriedades geométricas
    if "b_w" in geo and "h" in geo:  # Seção retangular
        b = geo["b_w"]
        h = geo["h"]
        A = b * h  # Área
        Wx = (b * h**2) / 6  # Módulo resistente em x
        Wy = (h * b**2) / 6  # Módulo resistente em y
        Ix = (b * h**3) / 12  # Momento de inércia em x
        Iy = (h * b**3) / 12  # Momento de inércia em y
        r_min = min(math.sqrt(Ix/A), math.sqrt(Iy/A))  # Raio mínimo de giração
        secao_tipo = "retangular"
    elif "d" in geo:  # Seção circular
        d = geo["d"]
        r = d / 2
        A = math.pi * r**2  # Área
        Wx = math.pi * r**3 / 4  # Módulo resistente
        Wy = Wx  # Para círculo, Wx = Wy
        Ix = math.pi * r**4 / 4  # Momento de inércia
        Iy = Ix  # Para círculo, Ix = Iy
        r_min = math.sqrt(Ix/A)  # Raio de giração
        secao_tipo = "circular"
    else:
        # Retornar erro se geometria não for definida
        return {
            "analise": t["erro_geometria"],
            "fator_utilizacao": 0,
            "r_min": 0
        }
    
    # 6. Cálculo dos esforços de cálculo (combinações)
    # Combinação ELU (Estados Limites Últimos)
    m_d_x = gamma_g * m_gkx + gamma_q * m_qkx  # Momento em x de cálculo
    m_d_y = gamma_g * m_gky + gamma_q * m_qky  # Momento em y de cálculo
    p_d = gamma_g * p_k  # Força normal de cálculo
    
    # 7. Tensões atuantes
    sigma_cd = abs(p_d * 1000 / A) if A > 0 else 0  # Tensão de compressão (kN/m²)
    sigma_mx_d = abs(m_d_x * 1000 / Wx) if Wx > 0 else 0  # Tensão de flexão em x (kN/m²)
    sigma_my_d = abs(m_d_y * 1000 / Wy) if Wy > 0 else 0  # Tensão de flexão em y (kN/m²)
    
    # 8. Verificação de flexão composta (combinação de tensões)
    # Para flexão em duas direções + força normal
    if f_c0d > 0:
        fator_util = (sigma_cd / f_c0d) + (sigma_mx_d / f_t0d) + (sigma_my_d / f_t0d)
    else:
        fator_util = 1.0
    
    # 9. Análise dos resultados
    if fator_util <= 1.0:
        if lang == "pt":
            analise = f"{t['estrutura_adequada']}. Fator de utilização: {fator_util:.3f} ≤ 1.0"
        else:
            analise = f"{t['estrutura_adequada']}. Utilization factor: {fator_util:.3f} ≤ 1.0"
    else:
        if lang == "pt":
            analise = f"{t['estrutura_insuficiente']}. Fator: {fator_util:.3f} > 1.0. Redimensionar."
        else:
            analise = f"{t['estrutura_insuficiente']}. Factor: {fator_util:.3f} > 1.0. Redimension."
    
    # 10. Informações adicionais
    if lang == "pt":
        analise += f"\n• kmod = {kmod:.2f}"
        analise += f"\n• f_c0d = {f_c0d:.0f} kN/m²"
        analise += f"\n• Área = {A:.4f} m²"
        analise += f"\n• Seção: {secao_tipo}"
    else:
        analise += f"\n• kmod = {kmod:.2f}"
        analise += f"\n• f_c0d = {f_c0d:.0f} kN/m²"
        analise += f"\n• Area = {A:.4f} m²"
        analise += f"\n• Section: {secao_tipo}"
    
    return {
        "analise": analise,
        "fator_utilizacao": fator_util,
        "r_min": r_min,
        "area": A,
        "kmod": kmod,
        "f_c0d": f_c0d,
        "tipo_secao": secao_tipo
    }

# -> INTERFACE PRINCIPAL
st.header(t["titulo"])

# Criar abas para organização
tab1, tab2, tab3 = st.tabs([
    "📐 " + t["geometria"],
    "⚡ " + t["esforcos"],
    "📊 " + t["propriedades"]
])

with tab1:
    # -> GEOMETRIA
    st.subheader(t["geometria"])
    tipo_secao = st.selectbox(
        t["tipo_secao"],
        t["opcoes_secao"],
        key="tipo_secao"
    )
    
    geo = {}
    col1, col2 = st.columns(2)
    
    if tipo_secao == t["opcoes_secao"][0]:  # Retangular / Rectangular
        with col1:
            geo["b_w"] = st.number_input(t["largura_b"], min_value=0.01, value=0.15, 
                                        step=0.01, format="%.3f", key="largura_b")
        with col2:
            geo["h"] = st.number_input(t["altura_h"], min_value=0.01, value=0.40, 
                                      step=0.01, format="%.3f", key="altura_h")
        
        # Mostrar visualização da seção retangular
        st.write("**Visualização da seção:**")
        col_v1, col_v2 = st.columns([1, 3])
        with col_v1:
            st.write(f"b = {geo.get('b_w', 0):.3f} m")
            st.write(f"h = {geo.get('h', 0):.3f} m")
            if 'b_w' in geo and 'h' in geo:
                area = geo['b_w'] * geo['h']
                st.write(f"Área = {area:.4f} m²")
                
    else:  # Circular
        geo["d"] = st.number_input(t["diametro_d"], min_value=0.01, value=0.30, 
                                  step=0.01, format="%.3f", key="diametro_d")
        
        # Mostrar visualização da seção circular
        st.write("**Visualização da seção:**")
        col_v1, col_v2 = st.columns([1, 3])
        with col_v1:
            st.write(f"d = {geo.get('d', 0):.3f} m")
            if 'd' in geo:
                area = math.pi * (geo['d']/2)**2
                st.write(f"Área = {area:.4f} m²")

with tab2:
    # -> ESFORÇOS / APPLIED LOADS
    st.subheader(t["esforcos"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Flexão em X**")
        m_gkx = st.number_input(t["momento_permanente_x"], value=10.0, 
                               step=1.0, format="%.2f", key="m_gkx")
        m_qkx = st.number_input(t["momento_variavel_x"], value=15.0, 
                               step=1.0, format="%.2f", key="m_qkx")
        
    with col2:
        st.write("**Flexão em Y**")
        m_gky = st.number_input(t["momento_permanente_y"], value=5.0, 
                               step=1.0, format="%.2f", key="m_gky")
        m_qky = st.number_input(t["momento_variavel_y"], value=8.0, 
                               step=1.0, format="%.2f", key="m_qky")
    
    st.divider()
    
    col3, col4 = st.columns(2)
    with col3:
        p_k = st.number_input(t["forca_normal"], value=50.0, 
                             step=5.0, format="%.2f", key="p_k")
    
    with col4:
        # Resumo dos esforços
        st.write("**Resumo dos esforços:**")
        st.write(f"• Mx total = {m_gkx + m_qkx:.1f} kN·m")
        st.write(f"• My total = {m_gky + m_qky:.1f} kN·m")
        st.write(f"• P = {p_k:.1f} kN")

with tab3:
    # -> MADEIRA E COEFICIENTES / WOOD PROPERTIES
    st.subheader(t["propriedades"])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        classe_carregamento = st.selectbox(
            t["classe_carregamento"],
            t["opcoes_carregamento"],
            key="classe_carregamento"
        )
    
    with col2:
        classe_madeira = st.selectbox(
            t["classe_madeira"],
            t["opcoes_madeira"],
            key="classe_madeira"
        )
    
    with col3:
        classe_umidade = st.selectbox(
            t["classe_umidade"],
            t["opcoes_umidade"],
            key="classe_umidade"
        )
    
    st.divider()
    
    st.write("**Coeficientes de ponderação:**")
    col_g1, col_g2, col_g3 = st.columns(3)
    
    with col_g1:
        gamma_g = st.number_input(t["gamma_g"], value=1.35, 
                                 min_value=1.0, max_value=2.0, 
                                 step=0.05, format="%.2f", key="gamma_g")
    with col_g2:
        gamma_q = st.number_input(t["gamma_q"], value=1.50, 
                                 min_value=1.0, max_value=2.0, 
                                 step=0.05, format="%.2f", key="gamma_q")
    with col_g3:
        gamma_w = st.number_input(t["gamma_w"], value=1.40, 
                                 min_value=1.0, max_value=2.0, 
                                 step=0.05, format="%.2f", key="gamma_w")
    
    st.divider()
    
    # -> RESISTÊNCIAS / CHARACTERISTIC RESISTANCES
    st.subheader(t["resistencias"])
    col_r1, col_r2 = st.columns(2)
    
    with col_r1:
        f_c0k = st.number_input(t["f_c0k"], value=20000.0, 
                               min_value=1000.0, max_value=100000.0,
                               step=1000.0, format="%.0f", key="f_c0k")
    with col_r2:
        f_t0k = st.number_input(t["f_t0k"], value=14000.0, 
                               min_value=1000.0, max_value=100000.0,
                               step=1000.0, format="%.0f", key="f_t0k")

# -> BOTÃO DE CÁLCULO
st.divider()

col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    calcular = st.button(f"🚀 {t['botao']}", type="primary", use_container_width=True)

if calcular:
    if not geo:
        st.error(t["erro_geometria"])
    else:
        with st.spinner(t["calculando"]):
            # Realizar cálculo
            resultado = checagem_flexao_simples_ponte(
                geo,
                m_gkx,
                m_qkx,
                classe_carregamento,
                classe_madeira,
                classe_umidade,
                gamma_g,
                gamma_q,
                gamma_w,
                f_c0k,
                f_t0k,
                p_k,
                m_gky,
                m_qky,
                lang
            )
            
            # Exibir resultados
            st.success(t["sucesso"])
            
            # Métricas principais
            col_res1, col_res2, col_res3 = st.columns(3)
            
            with col_res1:
                st.metric(t["fator_utilizacao"], f"{resultado['fator_utilizacao']:.3f}",
                         delta="Adequado" if resultado['fator_utilizacao'] <= 1.0 else "Crítico",
                         delta_color="normal" if resultado['fator_utilizacao'] <= 1.0 else "inverse")
            
            with col_res2:
                st.metric(t["raio_minimo"], f"{resultado['r_min']:.4f} m")
            
            with col_res3:
                st.metric("Área da seção", f"{resultado.get('area', 0):.4f} m²")
            
            # Detalhes da análise
            with st.expander("📋 Detalhes da análise", expanded=True):
                # Separar as linhas da análise
                linhas_analise = resultado["analise"].split('\n')
                for linha in linhas_analise:
                    if '✓' in linha or '⚠' in linha or '●' in linha or '•' in linha:
                        st.write(linha)
                    else:
                        st.write(f"• {linha}")
                
                # Informações adicionais
                st.divider()
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.write("**Parâmetros usados:**")
                    st.write(f"• kmod = {resultado.get('kmod', 0):.3f}")
                    st.write(f"• γm = 1.40")
                    st.write(f"• f_c0d = {resultado.get('f_c0d', 0):.0f} kN/m²")
                
                with col_info2:
                    st.write("**Recomendações:**")
                    if resultado['fator_utilizacao'] <= 0.8:
                        st.success("✓ Estrutura com boa margem de segurança")
                    elif resultado['fator_utilizacao'] <= 1.0:
                        st.warning("⚠ Estrutura no limite, monitorar")
                    else:
                        st.error("✗ Redimensionar a seção ou material")

# Informações de ajuda
with st.expander("❓ Ajuda / Informações"):
    if lang == "pt":
        st.markdown("""
        ### Como usar esta calculadora:
        
        1. **Geometria**: Selecione o tipo de seção e dimensões
        2. **Esforços**: Insira os momentos fletores e força normal
        3. **Propriedades**: Defina as características da madeira
        4. **Calcule**: Clique no botão para verificar a estrutura
        
        ### Valores típicos para madeira:
        - **f_c0k**: 18.000-24.000 kN/m² (Coníferas)
        - **f_t0k**: 12.000-18.000 kN/m² (Coníferas)
        
        ### Classes de carregamento:
        - **Permanente**: > 10 anos
        - **Longa duração**: 6 meses - 10 anos
        - **Média duração**: 1 semana - 6 meses
        - **Curta duração**: < 1 semana
        - **Instantânea**: Acidentes, ventos
        """)
    else:
        st.markdown("""
        ### How to use this calculator:
        
        1. **Geometry**: Select section type and dimensions
        2. **Loads**: Enter bending moments and normal force
        3. **Properties**: Define wood characteristics
        4. **Calculate**: Click button to verify structure
        
        ### Typical wood values:
        - **f_c0k**: 18,000-24,000 kN/m² (Conifers)
        - **f_t0k**: 12,000-18,000 kN/m² (Conifers)
        
        ### Loading classes:
        - **Permanent**: > 10 years
        - **Long duration**: 6 months - 10 years
        - **Medium duration**: 1 week - 6 months
        - **Short duration**: < 1 week
        - **Instantaneous**: Accidents, winds
        """)

# Rodapé
st.divider()
if lang == "pt":
    st.caption("📐 Calculadora de longarina em madeira • NBR 7190/1997 • ReliaBridge v1.0")
else:
    st.caption("📐 Wood stringer calculator • NBR 7190/1997 • ReliaBridge v1.0")