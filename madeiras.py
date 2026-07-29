"""Contém funções para cálculo e verificação de estruturas de madeira."""
import markdown
from xhtml2pdf import pisa
import pypandoc
import tempfile
from datetime import datetime
import numpy as np
import pandas as pd
import os
import io
import unicodedata
from io import BytesIO
from scipy import stats as st

from UQpy.run_model.RunModel import RunModel
from UQpy.run_model.model_execution.PythonModel import PythonModel
from UQpy.distributions import Uniform
from UQpy.distributions.collection.JointIndependent import JointIndependent
import matplotlib as mpl
mpl.use("Agg")
from UQpy.sensitivity.SobolSensitivity import SobolSensitivity
import matplotlib.pyplot as plt
mpl.rcParams.update({
                        'font.family': 'serif',
                        'mathtext.fontset': 'cm',
                        'axes.unicode_minus': False
                    })

# -----------------------------------------------------------------------------
# Padrão visual único das figuras
# -----------------------------------------------------------------------------
# Todas as figuras da plataforma compartilham cor, tipografia e tamanhos, de modo
# que possam ser usadas lado a lado em relatório e em artigo sem retrabalho.

COR_PRIMARIA   = '#1f4e79'   # azul escuro, usado em linhas, pontos e contornos
COR_SECUNDARIA = '#c00000'   # vermelho, reservado para destaque (ex.: média)
COR_PREENCHE   = '#dbeafe'   # azul claro, preenchimento de caixas
COR_TEXTO      = 'black'
COR_GRADE      = 'gray'

TAM_ROTULO = 10              # rótulos de eixo
TAM_EIXO   = 10              # números dos eixos
CM_POL     = 1 / 2.54

# Dois formatos apenas: figuras de par de objetivos (quadradas) e figuras que
# comparam variáveis lado a lado (largas).
FIG_PADRAO = (11.0, 9.0)     # fronteira eficiente, convergência do hipervolume
FIG_LARGA  = (18.0, 8.0)     # boxplot das variáveis, mapa de Sobol


def _limites_arredondados(v_min: float, v_max: float, n_intervalos: int = 5) -> tuple[float, float, np.ndarray]:
    """Calcula limites e marcações de eixo em valores redondos.

    Garante que os dados fiquem integralmente dentro do intervalo e que a primeira
    e a última marcação coincidam com as extremidades do eixo, evitando que a curva
    ultrapasse o último número rotulado.

    :param v_min: Menor valor dos dados
    :param v_max: Maior valor dos dados
    :param n_intervalos: Número desejado de intervalos entre marcações

    :return: [0] limite inferior, [1] limite superior, [2] posições das marcações
    """

    v_min, v_max = float(v_min), float(v_max)
    if not np.isfinite(v_min) or not np.isfinite(v_max):
        return 0.0, 1.0, np.linspace(0.0, 1.0, n_intervalos + 1)

    if np.isclose(v_max, v_min):
        delta = abs(v_min) * 0.1 if abs(v_min) > 1e-12 else 0.5
        v_min, v_max = v_min - delta, v_max + delta

    bruto = (v_max - v_min) / max(int(n_intervalos), 1)
    magnitude = 10.0 ** np.floor(np.log10(bruto))
    for passo_norm in (1.0, 2.0, 2.5, 5.0, 10.0):
        passo = passo_norm * magnitude
        if passo >= bruto:
            break

    inferior = np.floor(v_min / passo) * passo
    superior = np.ceil(v_max / passo) * passo
    marcacoes = np.arange(inferior, superior + passo * 0.5, passo)

    return float(inferior), float(superior), marcacoes


def _aplicar_estilo_eixos(
    ax,
    label_x: str = "",
    label_y: str = "",
    arredondar_x: bool = True,
    arredondar_y: bool = True,
    n_intervalos: int = 5,
) -> None:
    """Aplica o padrão visual comum a um eixo: tipografia, grade e marcações redondas."""

    ax.set_xlabel(label_x, fontsize=TAM_ROTULO, color=COR_TEXTO)
    ax.set_ylabel(label_y, fontsize=TAM_ROTULO, color=COR_TEXTO)
    ax.tick_params(axis='both', which='major', labelsize=TAM_EIXO, colors=COR_TEXTO)

    # Zera as margens automáticas antes de ler os limites: interessa a extensão
    # real dos dados, e não o intervalo já expandido em 5% pelo matplotlib, que
    # produziria limites arredondados para fora do domínio físico da grandeza.
    ax.margins(x=0, y=0)
    ax.autoscale_view()

    for eixo, arredondar in (('x', arredondar_x), ('y', arredondar_y)):
        if not arredondar:
            continue
        v_min, v_max = (ax.get_xlim() if eixo == 'x' else ax.get_ylim())
        inferior, superior, marcacoes = _limites_arredondados(v_min, v_max, n_intervalos)
        if eixo == 'x':
            ax.set_xlim(inferior, superior)
            ax.set_xticks(marcacoes)
        else:
            ax.set_ylim(inferior, superior)
            ax.set_yticks(marcacoes)

    ax.grid(True, which='major', linestyle='-', linewidth=0.5, color=COR_GRADE, alpha=0.3)
    ax.set_axisbelow(True)
from matplotlib.figure import Figure
from matplotlib.patches import Circle
from pymoo.core.problem import ElementwiseProblem
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.indicators.hv import HV


def restringir_espaco(esp: float, esp_min: float, esp_max: float, comp: float, largura_peca: float):
    """Verifica se existe uma disposição uniforme de peças ao longo de um comprimento/largura disponível tal que o espaçamento final corrigido entre peças fique dentro dos limites admissíveis.

    Geometria adotada:
        comp = n * largura_peca + (n - 1) * esp_corr

    Parâmetros
    ----------
    esp : float
        Espaçamento proposto pela heurística [m].
    esp_min : float
        Espaçamento mínimo permitido [m].
    esp_max : float
        Espaçamento máximo permitido [m].
    comp : float
        Comprimento/largura total disponível [m].
    largura_peca : float
        Largura (ou diâmetro) de cada peça [m].

    Retorno
    -------
    g : float
        Violação da restrição. Se g <= 0, a solução é viável.
    n_escolhido : int | None
        Número inteiro de peças adotado.
    esp_corr : float | None
        Espaçamento uniforme corrigido resultante.
    """
   
    if esp < 0 or esp_max <= 0 or comp <= 0 or largura_peca <= 0:
        return np.inf, 0, np.nan

    n_cont = (comp + esp) / (largura_peca + esp)
    candidatos = sorted(set([int(np.floor(n_cont)), int(np.ceil(n_cont))]))
    melhor_g = np.inf
    melhor_n = None
    melhor_esp_corr = None
    melhor_chave = (True, np.inf, np.inf)

    for n in candidatos:
        if n < 2:
            continue
        sobra = comp - n * largura_peca
        if sobra < 0:
            continue

        esp_corr = sobra / (n - 1)
        # restrições normalizadas
        g_min = (esp_min - esp_corr) / esp_min if esp_min > 0 else -np.inf
        g_max = (esp_corr - esp_max) / esp_max
        g = max(g_min, g_max)

        chave = (g > 0.0, max(g, 0.0), abs(esp_corr - esp))
        if chave < melhor_chave:
            melhor_chave = chave
            melhor_g = g
            melhor_n = n
            melhor_esp_corr = esp_corr

    if melhor_n is None:
        return np.inf, 0, np.nan

    return melhor_g, melhor_n, melhor_esp_corr


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
    """Plota a fronteira eficiente no espaço dos objetivos.

    Segue o padrão visual comum (ver constantes no topo do módulo) e compartilha
    o tamanho com a figura de convergência do hipervolume.

    :param x: Valores do primeiro objetivo (volume de madeira)
    :param y: Valores do segundo objetivo (utilização do limite de serviço)
    :param label_x: Rótulo do eixo horizontal
    :param label_y: Rótulo do eixo vertical
    """

    fig, ax = plt.subplots(figsize=(FIG_PADRAO[0] * CM_POL, FIG_PADRAO[1] * CM_POL))
    ax.scatter(x, y, alpha=1.0, color=COR_PRIMARIA, s=14, edgecolors='none')
    _aplicar_estilo_eixos(ax, label_x, label_y)
    fig.tight_layout()

    return fig


def plot_sobol_total_indices(
    total_order: pd.DataFrame,
    label_x: str = "Constraints",
    label_y: str = "Variables",
    x_labels: list[str] | None = None,
    y_labels: list[str] | None = None,
) -> Figure:
    """Plota os índices totais de Sobol em mapa de calor.

    Compartilha o tamanho com o boxplot das variáveis de projeto.

    :param total_order: DataFrame com coluna 'variavel' e uma coluna por restrição
    :param label_x: Rótulo do eixo horizontal
    :param label_y: Rótulo do eixo vertical
    :param x_labels: Rótulos das restrições
    :param y_labels: Rótulos das variáveis
    """

    df = total_order.set_index("variavel")
    valores = np.clip(df.to_numpy(dtype=float), 0.0, None)

    fig, ax = plt.subplots(figsize=(FIG_LARGA[0] * CM_POL, FIG_LARGA[1] * CM_POL))
    vmax = max(1.0, float(np.nanmax(valores))) if valores.size else 1.0
    cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "sobol_azul",
        ["#ffffff", "#dbeafe", "#93b8d8", "#4a7fb0", COR_PRIMARIA],
    )
    im = ax.imshow(valores, aspect="auto", cmap=cmap, vmin=0.0, vmax=vmax)

    nomes_x = x_labels if x_labels is not None and len(x_labels) == df.shape[1] else df.columns
    nomes_y = y_labels if y_labels is not None and len(y_labels) == df.shape[0] else df.index

    ax.set_xticks(np.arange(df.shape[1]))
    ax.set_xticklabels(nomes_x, rotation=30, ha="right", fontsize=TAM_EIXO - 1)
    ax.set_yticks(np.arange(df.shape[0]))
    ax.set_yticklabels(nomes_y, fontsize=TAM_EIXO - 1)
    ax.set_xlabel(label_x, fontsize=TAM_ROTULO, color=COR_TEXTO)
    ax.set_ylabel(label_y, fontsize=TAM_ROTULO, color=COR_TEXTO)
    ax.tick_params(axis='both', which='major', colors=COR_TEXTO, length=0)

    # Texto claro sobre célula escura, escuro sobre clara, para manter legibilidade
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            valor = valores[i, j]
            cor_texto = 'white' if valor > 0.6 * vmax else COR_TEXTO
            ax.text(j, i, f"{valor:.2f}", ha="center", va="center", color=cor_texto, fontsize=TAM_EIXO - 1)

    cbar = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("$S_T$", fontsize=TAM_ROTULO, color=COR_TEXTO)
    cbar.ax.tick_params(labelsize=TAM_EIXO - 1, colors=COR_TEXTO)

    fig.tight_layout()
    return fig


def plot_boxplot_variaveis_fronteira(
    df_resultados: pd.DataFrame,
    colunas: list[str],
    labels: list[str],
    label_y: str = "cm",
) -> Figure:
    """Plota a dispersão das variáveis de projeto presentes na fronteira.

    Compartilha o tamanho com o mapa de Sobol.

    :param df_resultados: DataFrame com as soluções da fronteira
    :param colunas: Colunas do DataFrame a representar
    :param labels: Rótulos legíveis, na mesma ordem de `colunas`
    :param label_y: Rótulo do eixo vertical
    """

    dados = [df_resultados[coluna].dropna().to_numpy(dtype=float) for coluna in colunas]

    fig, ax = plt.subplots(figsize=(FIG_LARGA[0] * CM_POL, FIG_LARGA[1] * CM_POL))
    box = ax.boxplot(
        dados,
        labels=labels,
        patch_artist=True,
        showmeans=True,
        meanline=False,
        widths=0.55,
        medianprops={"color": COR_PRIMARIA, "linewidth": 1.6},
        meanprops={"marker": "o", "markerfacecolor": COR_SECUNDARIA, "markeredgecolor": COR_SECUNDARIA, "markersize": 4},
        boxprops={"linewidth": 1.1, "color": COR_PRIMARIA},
        whiskerprops={"linewidth": 1.0, "color": COR_PRIMARIA},
        capprops={"linewidth": 1.0, "color": COR_PRIMARIA},
        flierprops={"marker": "o", "markerfacecolor": COR_PREENCHE, "markeredgecolor": COR_PRIMARIA, "markersize": 4, "alpha": 0.8},
    )

    for patch in box["boxes"]:
        patch.set_facecolor(COR_PREENCHE)

    # O eixo x é categórico: arredondar apenas o eixo y
    _aplicar_estilo_eixos(ax, "", label_y, arredondar_x=False)
    ax.grid(False, axis='x')

    fig.tight_layout()
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


def prop_madeiras(geo: dict) -> tuple[float, float, float, float, float, float, float, float, float, float]:
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


def peso_proprio_longarina(densidade: float, area_secao: float) -> float:
    """Calcula o peso próprio (PP) da longarina.

    :param densidade: densidade da madeira [kg/m³]
    :param area_secao: área da seção transversal da longarina [m²]

    :return: peso próprio por metro linear [kN/m]
    """

    return densidade * area_secao


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
    :param gamma_w: Coeficiente parcial de segurança para madeira na flexão
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
    :param gamma_w: Coeficiente parcial de segurança para madeira no cisalhamento
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
        tau_sd = (4/3) * (v_sd / area)
    else:
        tau_sd = (3/2) * (v_sd / area)

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
    delta_qk_aux_cor = psi2 * (1 + phi) * delta_qk
    delta_sd_1 = delta_gk + delta_qk_aux_cor
    lim_1 = l / 250
    g_sd1 = (delta_sd_1 - lim_1) / lim_1

    # Verificação flecha variável
    delta_sd_2 = delta_qk
    lim_2 = l / 360
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


def checagem_completa_longarina_madeira_flexao(geo: dict, p_gk: float, p_qk: float, p_rodak: float, a: float, l: float, classe_carregamento: str, 
                                                classe_madeira: str, classe_umidade: int, gamma_g: float, gamma_q: float, gamma_wf: float,
                                                gamma_wc: float, psi2: float, phi: float, f_mk: float, f_vk: float, e_modflex: float) -> tuple[dict, dict, dict, dict]:
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
    :param gamma_wf: Coeficiente parcial de segurança para madeira na flexão
    :param gamma_wc: Coeficiente parcial de segurança para madeira no cisalhamento
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
                                                gamma_g, gamma_q, gamma_wf, f_mk
                                            )
    
    # Verificação do cisalhamento
    res_cis = checagem_cisalhamento_viga(
                                            i_x, area, tipo_secao, 
                                            v_gk, v_qk, 
                                            classe_carregamento,
                                            classe_madeira, classe_umidade,
                                            gamma_g, gamma_q, gamma_wc, f_vk
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
                        "titulo": "Projeto estrutural paramétrico de uma ponte de madeira",
                        "pre": """
                                ### Instruções

                                Nesta seção, o usuário deve carregar a planilha `beam_data.xlsx` gerada no **pré-dimensionamento** e informar a geometria da solução que deseja verificar:

                                - diâmetro da longarina (`d`);
                                - largura do tabuleiro (`bw`);
                                - altura do tabuleiro (`h`);
                                - espaçamento entre longarinas;
                                - espaçamento entre peças do tabuleiro.

                                A partir desses dados, o sistema verifica se a longarina e o tabuleiro atendem às funções de verificação de flexão, cisalhamento e flecha.

                                O principal indicador exibido é `g_otimiz`. A interpretação é direta:

                                - `g_otimiz <= 0`: a verificação atende;
                                - `g_otimiz > 0`: a verificação não atende.

                                Quanto mais próximo de zero e negativo, mais próximo a peça está do limite sem ultrapassá-lo. Valores positivos indicam violação da restrição.
                                """,
                        "dados_pre": "Dados para dimensionamento",
                        "entrada_tipo_secao_longarina": "Tipo de seção",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_longarina": "Diâmetro equivalente da longarina (cm) conforme item 9.7 da NBR 7190",
                        "espaçamento_entre_longarinas": "Espaçamento entre longarinas (cm)",
                        "tipo_secao_tabuleiro": "Tipo de seção do tabuleiro",
                        "tipo_secao_tabuleiro_opcoes": ["Retangular"],
                        "largura_viga_tabuleiro": "Largura viga (cm) seção do tabuleiro",
                        "altura_viga_tabuleiro": "Altura viga (cm) seção do tabuleiro",
                        "espaçamento_entre_tabuleiros": "Espaçamento entre peças do tabuleiro (cm)",
                        "planilha_head": "Planilha de dados do projeto",
                        "texto_up": "Faça upload do arquivo gerado no pré-dimensionamento (.xlsx)",
                        "aguardando_upload": "Aguardando upload da planilha de pré-dimensionamento.",
                        "planilha_sucesso": "Planilha carregada com sucesso.",
                        "planilha_preview": "*Pré-visualização dos dados:*",
                        "gerador_projeto": "Gerar verificação estrutural do projeto",
                        "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                        "classe_madeira": "Classe de madeira",
                        "classe_madeira_opcoes": ["Madeira natural", "Madeira recomposta"],
                        "classe_umidade": "Classe de umidade",
                        "f_mk": "Resistência característica à flexão (MPa)",
                        "f_vk": "Resistência característica ao cisalhamento (MPa)",
                        "e_modflex": "Módulo de elasticidade à flexão (GPa)",
                        "gerador_desempenho": "Gerar desempenho estrutural para pré-dimensionamento",
                        "resultado_relatorios": "Relatórios completos de cálculo",
                        "resultado_head": "Relatórios de dimensionamento",
                        "resultado_intro": "Resumo das funções de verificação. O relatório em PDF apresenta as contas detalhadas.",
                        "verif_longarina_titulo": "Verificações da longarina",
                        "label_flexao": "Flexão",
                        "label_cisalhamento": "Cisalhamento",
                        "label_flecha": "Flecha",
                        "verif_tabuleiro_titulo": "Verificações do tabuleiro",
                        "label_flexao": "Flexão",
                        "label_cargas": "Cargas",
                        "label_longarina": "Longarina",
                        "label_tabuleiro": "Tabuleiro",
                        "botao_baixar_relatorio": "📄 Baixar relatório (Markdown)",
                        "nome_arquivo": "Relatorio_Ponte",
                        "aviso_gerar_primeiro": "Sem resultados atuais. Clique em “Gerar” para processar.",
                        "erro_sem_planilha": "Envie a planilha .xlsx para continuar.",
                        "erro_geo": "Preencha a geometria (longarina e tabuleiro) para continuar.",
                        "status_ok": "OK",
                        "status_falha": "NÃO ATENDE",
                        "indicador_g": "Indicador g_otimiz",
                        "g_atende": "Atende: g_otimiz <= 0.",
                        "g_nao_atende": "Não atende: g_otimiz > 0.",
                        "g_interpretacao": "Valores negativos indicam folga na verificação; valores positivos indicam violação da restrição.",
                    },
                "en": {
                        "titulo": "Parametric structural design of a wooden bridge",
                        "pre": """
                                ### Instructions

                                In this section, the user must upload the `beam_data.xlsx` spreadsheet generated in **pre-sizing** and enter the geometry of the solution to be checked:

                                - girder diameter (`d`);
                                - deck width (`bw`);
                                - deck height (`h`);
                                - spacing between girders;
                                - spacing between deck elements.

                                Based on these data, the system checks whether the girder and deck satisfy the bending, shear, and deflection verification functions.

                                The main indicator displayed is `g_otimiz`. Its interpretation is direct:

                                - `g_otimiz <= 0`: the verification passes;
                                - `g_otimiz > 0`: the verification fails.

                                The closer the value is to zero on the negative side, the closer the member is to its limit without exceeding it. Positive values indicate constraint violation.
                                """,
                        "dados_pre": "Data for sizing",
                        "entrada_tipo_secao_longarina": "Section type",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_longarina": "Equivalent girder diameter (cm) according to item 9.7 of NBR 7190",
                        "espaçamento_entre_longarinas": "Spacing between girders (cm)",
                        "tipo_secao_tabuleiro": "Deck section type",
                        "tipo_secao_tabuleiro_opcoes": ["Rectangular"],
                        "largura_viga_tabuleiro": "Deck plank width (cm)",
                        "altura_viga_tabuleiro": "Deck plank height (cm)",
                        "espaçamento_entre_tabuleiros": "Spacing between deck elements (cm)",
                        "planilha_head": "Upload data spreadsheet",
                        "texto_up": "Upload the file generated in the pre-sizing (.xlsx)",
                        "aguardando_upload": "Waiting for pre-sizing spreadsheet upload.",
                        "planilha_sucesso": "Spreadsheet successfully loaded.",
                        "planilha_preview": "*Data preview:*",
                        "gerador_projeto": "Generate structural verification of the project",
                        "classe_carregamento_opcoes": ["Dead", "Long-term", "Medium-term", "Short-term", "Instantaneous"],
                        "classe_madeira": "Wood class",
                        "classe_madeira_opcoes": ["Natural wood", "Engineered wood"],
                        "classe_umidade": "Moisture class",
                        "f_mk": "Characteristic bending strength (MPa)",
                        "f_vk": "Characteristic shear strength (MPa)",
                        "e_modflex": "Modulus of elasticity in bending (GPa)",
                        "gerador_desempenho": "Generate structural performance for pre-sizing",
                        "resultado_relatorios":  "Complete calculation reports",
                        "resultado_head": "Full design report",
                        "resultado_intro": "Summary of the verification functions. The PDF report presents the detailed calculations.",
                        "verif_longarina_titulo": "Girder checks",
                        "label_flexao": "Bending",
                        "label_cisalhamento": "Shear",
                        "label_flecha": "Deflection",
                        "verif_tabuleiro_titulo": "Deck checks",
                        "label_cargas": "Loads",
                        "label_longarina": "Girder",
                        "label_tabuleiro": "Deck",
                        "botao_baixar_relatorio": "📄 Download Report (Markdown)",
                        "nome_arquivo": "Bridge_Report",
                        "aviso_gerar_primeiro": "No current results. Click “Generate” to process.",
                        "erro_sem_planilha": "Send the .xlsx spreadsheet to continue.",
                        "erro_geo": "Fill in the geometry (beam and deck) to continue.",
                        "status_ok": "OK",
                        "status_falha": "NOT OK",
                        "indicador_g": "g_otimiz indicator",
                        "g_atende": "Passes: g_otimiz <= 0.",
                        "g_nao_atende": "Fails: g_otimiz > 0.",
                        "g_interpretacao": "Negative values indicate reserve in the verification; positive values indicate constraint violation.",
                    },
            }
    return textos


def textos_pre_sizing_l() -> dict:
    textos = {
                "pt": {
                        "titulo": "Projeto paramétrico de uma ponte de madeira",
                        "pre": """
                                    ### Informações

                                    Nesta seção, o usuário poderá estabelecer os critérios necessários para a construção da **fronteira eficiente** utilizando um algoritmo de **otimização robusta e multiobjetivo**.

                                    O usuário deverá informar:

                                    - **critérios geométricos** do projeto da ponte;
                                    - **propriedades mecânicas da madeira** utilizada nas **longarinas** e no **tabuleiro**;
                                    - **carregamentos atuantes** na estrutura.

                                    Nesta ferramenta paramétrica, as principais **variáveis de projeto** consideradas no processo de otimização são:

                                    - **diâmetro das longarinas**;
                                    - **espaçamento entre longarinas**;
                                    - **dimensões das pranchas do tabuleiro**;
                                    - **espaçamento entre peças do tabuleiro**.

                                    O **percentual de robustez** representa a variação considerada nas variáveis de projeto durante a otimização. Por exemplo, ao informar **5%**, cada solução candidata é avaliada também com pequenas perturbações de até ±5% nas variáveis, permitindo buscar geometrias menos sensíveis a variações dimensionais e incertezas de execução. O valor **0%** corresponde a uma otimização determinística, sem perturbações.

                                    Os **intervalos das variáveis de projeto** informados no formulário definem o espaço de busca utilizado pelo algoritmo. A partir desses limites, o processo de otimização explora diferentes combinações de dimensões e espaçamentos para encontrar soluções viáveis.

                                    Além disso, o usuário poderá definir:

                                    - o **espaçamento mínimo e máximo entre longarinas**;
                                    - o **espaçamento mínimo e máximo entre peças do tabuleiro**.

                                    Ao final do processo de otimização, será obtida uma **fronteira eficiente (fronteira de Pareto)** contendo as soluções estruturalmente viáveis encontradas pelo algoritmo. O usuário poderá então **baixar uma planilha** contendo todas as configurações que apresentaram desempenho satisfatório durante o processo de otimização.

                                    Caso nenhuma solução viável seja encontrada, os **parâmetros de entrada poderão ser ajustados** e o processo de otimização poderá ser executado novamente. Os dados informados permanecem **armazenados em cache**, permitindo a continuidade das análises sem necessidade de reinserção das informações. Vale salientar que o tempo de processamento pode variar conforme os limites informados, o percentual de robustez e o desempenho do computador. Testes em máquinas comuns de escritório indicam que o processo pode levar de 1 a 5 minutos.
                                    """,
                        "entrada_comprimento": "Comprimento das longarinas (cm)",
                        "pista": "Largura da pista disponível para longarinas (cm)",
                        "entrada_tipo_secao_longarina": "Tipo de seção",
                        "tipo_secao_longarina": ["Circular"],
                        "diametro_minimo": "Diâmetro mínimo equivalente (cm)",
                        "diametro_maximo": "Diâmetro máximo equivalente (cm)",
                        "espaço_min_longarinas": "Espaçamento mínimo entre longarinas (cm)",
                        "espaço_max_longarinas": "Espaçamento máximo entre longarinas (cm)",
                        "tipo_secao_tabuleiro": "Tipo de seção do tabuleiro",
                        "tipo_secao_tabuleiro_opcoes": ["Retangular"],
                        "largura_viga_tabuleiro_min": "Largura mínima da viga do tabuleiro (cm)",
                        "largura_viga_tabuleiro_max": "Largura máxima da viga do tabuleiro (cm)",
                        "altura_viga_tabuleiro_min": "Altura mínima da viga do tabuleiro (cm)",
                        "altura_viga_tabuleiro_max": "Altura máxima da viga do tabuleiro (cm)",
                        "espaço_min_tabuleiros": "Espaçamento mínimo entre peças do tabuleiro (cm)",
                        "espaço_max_tabuleiros": "Espaçamento máximo entre peças do tabuleiro (cm)",
                        "carga_permanente": "Carga permanente atuante no tabuleiro (kN/m²) excluso peso próprio",
                        "carga_roda": "Carga por roda (kN)",
                        "carga_multidao": "Carga de multidão (kN/m²)",
                        "distancia_eixos": "Distância entre eixos (m) do veículo tipo",
                        "classe_carregamento": "Classe de carregamento",
                        "classe_carregamento_opcoes": ["Permanente", "Longa duração", "Média duração", "Curta duração", "Instantânea"],
                        "classe_madeira": "Classe de madeira",
                        "classe_madeira_opcoes": ["Madeira natural", "Madeira recomposta"],
                        "classe_umidade": "Classe de umidade",
                        "gamma_g": "γg - Carga permanente",
                        "gamma_q": "γq - Carga variável",
                        "gamma_wc": "γwc - Cisalhamento",
                        "gamma_wf": "γwf - Flexão",
                        "psi2": "ψ2",
                        "considerar_fluencia": "Coeficiente para fluência Tabela 20 NBR 7190",
                        "robustez_t": "Robustez da otimização",
                        "percentual_robustez": "Percentual de robustez",
                        "densidade_long": "Densidade da madeira (kg/m³) da longarina",
                        "f_mk": "Resistência característica à flexão (MPa) da longarina",
                        "f_vk": "Resistência característica ao cisalhamento (MPa) da longarina",
                        "e_modflex": "Módulo de elasticidade à flexão (GPa) da longarina",
                        "densidade_tab": "Densidade da madeira (kg/m³) do tabuleiro",
                        "f_mk_tab": "Resistência característica à flexão (MPa) do tabuleiro",
                        "gerador_desempenho": "Gerar desempenho estrutural via NSGA-II para pré-dimensionamento",
                        "fronteira_head": "Fronteira eficiente – Pré-dimensionamento",
                        "fronteira_variaveis_head": "Variação das variáveis de projeto na fronteira",
                        "fronteira_variaveis_info": "O boxplot resume como as variáveis de projeto aparecem nas soluções da fronteira eficiente.",
                        "fronteira_variaveis_y": "Valor (cm)",
                        "fronteira_variaveis_labels": ["d", "bw", "h", "Esp. long.", "Esp. tab."],
                        "estatistica_head": "Estatística descritiva das variáveis de projeto",
                        "estatistica_info": "Resumo numérico do boxplot acima. Amplitude pequena indica que a fronteira converge para um valor praticamente fixo daquela variável; amplitude grande indica que é por ela que se obtém o compromisso entre os objetivos.",
                        "estatistica_colunas": {
                                                "variavel": "Variável",
                                                "n": "N",
                                                "media": "Média",
                                                "desvio": "Desvio padrão",
                                                "cv": "CV (%)",
                                                "minimo": "Mínimo",
                                                "q1": "1º quartil",
                                                "mediana": "Mediana",
                                                "q3": "3º quartil",
                                                "maximo": "Máximo",
                                                "amplitude": "Amplitude",
                                            },
                        "convergencia_head": "Convergência do NSGA-II – Hipervolume",
                        "convergencia_info": "O hipervolume mede a região do espaço de objetivos dominada pela fronteira. O crescimento indica que o algoritmo está de fato melhorando as soluções; a estabilização indica que o número de gerações adotado é suficiente.",
                        "convergencia_x": "Geração",
                        "convergencia_y": "Hipervolume normalizado [-]",
                        "convergencia_serie": "Pré-dimensionamento",
                        "convergencia_estabiliza": "Hipervolume final de {hv:.4f}, estabilizado (dentro de 1%) a partir da geração {gen} de {total}.",
                        "sobol_head": "Sensibilidade global das restrições - Índice total de Sobol",
                        "sobol_info": "Use esta análise para identificar quais variáveis de entrada mais influenciam cada restrição no intervalo informado. A análise roda com 10.000 amostras base; valores maiores indicam maior contribuição para a variação da restrição.",
                        "sobol_n_samples": "Número base de amostras Sobol",
                        "sobol_button": "Executar análise de Sobol",
                        "sobol_spinner": "Executando análise de Sobol com UQpy...",
                        "sobol_total_order": "Índice total de Sobol (ST)",
                        "sobol_axis_constraints": "Restrições",
                        "sobol_axis_variables": "Variáveis",
                        "sobol_constraint_labels": ["Flexão long.", "Cisalh. long.", "Flecha long.", "Flexão tab.", "Esp. long.", "Esp. tab."],
                        "sobol_variable_labels": ["d", "bw", "h", "Esp. long.", "Esp. tab."],
                        "sobol_download": "Baixar índices totais de Sobol",
                        "sobol_next_step": "Sugestão: depois desta leitura das restrições, a próxima etapa natural é fazer uma ciência de dados básica da fronteira eficiente, observando correlações, agrupamentos e soluções mais equilibradas.",
                        "geometria_t": "Dados de geometria",
                        "variaveis_otimizacao": "Variáveis de otimização",
                        "cargas_projeto": "Cargas atuantes no projeto",
                        "classes_mad_carga": "Classes de madeira, carregamento e umidade",
                        "coeficientes_seguranca": "Coeficientes de segurança",
                        "prop_madeira": "Propriedades da madeira",
                        "longarina_t": "Longarina",
                        "tabuleiro_t": "Tabuleiro",
                        "restricoes_packing": "Restrições de espaçamento das peças",
                        "botao_dados_down": "Baixar dados do pré-dimensionamento",
                        "tag_y_fig": r'$\frac{\delta_{\text{total}}}{L/250}$',
                        "tag_x_fig": "Volume de madeira ($m^3$)",
                    },
                "en": {
                    "titulo": "Parametric design of a timber bridge",
                    "pre": """
                            ### Information

                            In this section, the user can define the criteria required to construct the **efficient frontier** using a **robust multi-objective optimization** algorithm.

                            The user must provide:

                            - **geometric criteria** for the bridge design;
                            - **mechanical properties of the timber** used in the **girders** and **deck**;
                            - **loads acting** on the structure.

                            In this parametric tool, the main **design variables** considered in the optimization process are:

                            - **girder diameter**;
                            - **spacing between girders**;
                            - **deck plank dimensions**;
                            - **spacing between deck elements**.

                            The **robustness percentage** represents the variation considered in the design variables during optimization. For example, when **5%** is entered, each candidate solution is also evaluated with small perturbations of up to ±5% in the variables, helping identify geometries that are less sensitive to dimensional variation and construction uncertainty. A value of **0%** corresponds to deterministic optimization, without perturbations.

                            The **design-variable intervals** provided in the form define the search space used by the algorithm. Based on these limits, the optimization process explores different combinations of dimensions and spacing values to identify feasible solutions.

                            In addition, the user may define:

                            - the **minimum and maximum spacing between girders**;
                            - the **minimum and maximum spacing between deck elements**.

                            At the end of the optimization process, an **efficient frontier (Pareto frontier)** will be obtained, containing the structurally feasible solutions identified by the algorithm. The user will then be able to **download a spreadsheet** containing all configurations that successfully met the optimization criteria.

                            If no feasible solution is found, the **input parameters can be adjusted**, and the optimization process can be executed again. The input data remain **stored in cache**, allowing the analysis to continue without the need to re-enter the information. It is worth noting that the processing time may vary depending on the specified bounds, the robustness percentage, and the computer performance. Tests on common office machines indicate that the process can take from 1 to 5 minutes.
                            """,
                    "entrada_comprimento": "Girder length (cm)",
                    "pista": "Available roadway width for girders (cm)",
                    "entrada_tipo_secao_longarina": "Section type",
                    "tipo_secao_longarina": ["Circular"],
                    "diametro_minimo": "Minimum equivalent diameter (cm)",
                    "diametro_maximo": "Maximum equivalent diameter (cm)",
                    "espaço_min_longarinas": "Minimum spacing between girders (cm)",
                    "espaço_max_longarinas": "Maximum spacing between girders (cm)",
                    "tipo_secao_tabuleiro": "Deck section type",
                    "tipo_secao_tabuleiro_opcoes": ["Rectangular"],
                    "largura_viga_tabuleiro_min": "Minimum deck plank width (cm)",
                    "largura_viga_tabuleiro_max": "Maximum deck plank width (cm)",
                    "altura_viga_tabuleiro_min": "Minimum deck plank height (cm)",
                    "altura_viga_tabuleiro_max": "Maximum deck plank height (cm)",
                    "espaço_min_tabuleiros": "Minimum spacing between deck elements (cm)",
                    "espaço_max_tabuleiros": "Maximum spacing between deck elements (cm)",
                    "carga_permanente": "Permanent load acting on the deck (kN/m²), excluding self-weight",
                    "carga_roda": "Wheel load (kN)",
                    "carga_multidao": "Crowd load (kN/m²)",
                    "distancia_eixos": "Axle spacing (m) of the standard vehicle",
                    "classe_carregamento": "Load duration class",
                    "classe_carregamento_opcoes": ["Permanent", "Long-term", "Medium-term", "Short-term", "Instantaneous"],
                    "classe_madeira": "Timber class",
                    "classe_madeira_opcoes": ["Solid timber", "Engineered timber"],
                    "classe_umidade": "Moisture class",
                    "gamma_g": "γg - Permanent load",
                    "gamma_q": "γq - Variable load",
                    "gamma_wc": "γwc - Shear",
                    "gamma_wf": "γwf - Bending",
                    "psi2": "ψ2",
                    "considerar_fluencia": "Creep coefficient - Table 20 of NBR 7190",
                    "robustez_t": "Optimization robustness",
                    "percentual_robustez": "Robustness percentage",
                    "densidade_long": "Timber density (kg/m³) of the girder",
                    "f_mk": "Characteristic bending strength (MPa) of the girder",
                    "f_vk": "Characteristic shear strength (MPa) of the girder",
                    "e_modflex": "Modulus of elasticity in bending (GPa) of the girder",
                    "densidade_tab": "Timber density (kg/m³) of the deck",
                    "f_mk_tab": "Characteristic bending strength (MPa) of the deck",
                    "gerador_desempenho": "Generate structural performance via NSGA-II for preliminary design",
                    "fronteira_head": "Efficient frontier – Preliminary design",
                    "fronteira_variaveis_head": "Design-variable variation along the frontier",
                    "fronteira_variaveis_info": "The boxplot summarizes how the design variables appear across the efficient-frontier solutions.",
                    "fronteira_variaveis_y": "Value (cm)",
                    "fronteira_variaveis_labels": ["d", "bw", "h", "Girder spacing", "Deck spacing"],
                    "estatistica_head": "Descriptive statistics of the design variables",
                    "estatistica_info": "Numerical summary of the boxplot above. A small range means the frontier converges to a nearly fixed value of that variable; a large range means it is the variable through which the trade-off between objectives is obtained.",
                    "estatistica_colunas": {
                                                "variavel": "Variable",
                                                "n": "N",
                                                "media": "Mean",
                                                "desvio": "Std. deviation",
                                                "cv": "CV (%)",
                                                "minimo": "Minimum",
                                                "q1": "1st quartile",
                                                "mediana": "Median",
                                                "q3": "3rd quartile",
                                                "maximo": "Maximum",
                                                "amplitude": "Range",
                                            },
                    "convergencia_head": "NSGA-II convergence – Hypervolume",
                    "convergencia_info": "The hypervolume measures the region of the objective space dominated by the frontier. Its growth shows that the algorithm is effectively improving the solutions; its stabilization shows that the adopted number of generations is sufficient.",
                    "convergencia_x": "Generation",
                    "convergencia_y": "Normalized hypervolume [-]",
                    "convergencia_serie": "Preliminary design",
                    "convergencia_estabiliza": "Final hypervolume of {hv:.4f}, stabilized (within 1%) from generation {gen} of {total}.",
                    "sobol_head": "Global sensitivity of constraints - Total Sobol index",
                    "sobol_info": "Use this analysis to identify which input variables most influence each constraint within the interval provided. The analysis runs with 10,000 base samples; larger values indicate a stronger contribution to the variation of the constraint.",
                    "sobol_n_samples": "Sobol base sample size",
                    "sobol_button": "Run Sobol analysis",
                    "sobol_spinner": "Running Sobol analysis with UQpy...",
                    "sobol_total_order": "Total Sobol index (ST)",
                    "sobol_axis_constraints": "Constraints",
                    "sobol_axis_variables": "Variables",
                    "sobol_constraint_labels": ["Girder bending", "Girder shear", "Girder defl.", "Deck bending", "Girder spacing", "Deck spacing"],
                    "sobol_variable_labels": ["d", "bw", "h", "Girder spacing", "Deck spacing"],
                    "sobol_download": "Download total Sobol indices",
                    "sobol_next_step": "Suggestion: after reading the constraints, the natural next step is a basic data-science analysis of the efficient frontier, looking at correlations, clusters, and the most balanced solutions.",
                    "geometria_t": "Geometry data",
                    "variaveis_otimizacao": "Optimization variables",
                    "cargas_projeto": "Design loads",
                    "classes_mad_carga": "Timber, load duration, and moisture classes",
                    "coeficientes_seguranca": "Safety factors",
                    "prop_madeira": "Timber properties",
                    "longarina_t": "Girder",
                    "tabuleiro_t": "Deck",
                    "restricoes_packing": "Element spacing constraints",
                    "botao_dados_down": "Download preliminary design data",
                    "tag_y_fig": r'$\frac{\delta_{\text{total}}}{L/250}$',
                    "tag_x_fig": "Timber volume ($m^3$)",
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


def gerar_relatorio_final(projeto, res, geo_real):
    """Gera o relatório de dimensionamento em Markdown.

    A memória de cálculo (Seção 3) é emitida em LaTeX (display math), apresentando
    para cada grandeza a fórmula simbólica, a substituição numérica e o resultado,
    de modo a permitir a conferência manual passo a passo.
    """

    # Separando os Dados

    # A variável 'res' é um pacotão que veio do cálculo. Aqui "desembrulhamos"
    # ela item por item para pegar só o que interessa para escrever o relatório.
    res_m = res[2]         # Tudo sobre a Flexão da Longarina
    res_v = res[3]         # Tudo sobre o Cisalhamento
    res_f = res[4]         # Tudo sobre a Flecha (deformação)
    relat_l = res[5]       # Detalhes técnicos da longarina (Inércia, Área, etc.)
    res_m_tab = res[6]     # Resultados do Tabuleiro
    relat_t = res[7]       # Detalhes técnicos do tabuleiro
    relat_carga = res[-1]  # Memória de cálculo das cargas (peso próprio, etc.)


    # Arredonda as casas decimais e converte unidades (dividir por 1000 para virar MPa).
    # Se o valor vier vazio, coloca um tracinho "-" para não quebrar o relatório.
    def fmt(val, div=1.0, decimals=2):
        try:
            if val is None: return "-"
            return f"{float(val)/div:.{decimals}f}"
        except:
            return str(val)

    # Verifica se a análise deu "OK".
    def status_icon(dicio):
        return "**APROVADO**" if dicio.get("analise") == "OK" else "**REPROVADO**"

    def f(val, decimals=4):
        return fmt(val, 1.0, decimals)

    def fmpa(val_kpa, decimals=3):
        return fmt(val_kpa, 1000.0, decimals)

    def eq(*linhas: str) -> str:
        """Monta um bloco de equação LaTeX (display) com as linhas alinhadas pelo '='.

        As linhas devem ser passadas como raw strings de LaTeX, já contendo o '&='
        a partir da segunda. Ex.: eq(r"A &= \\frac{\\pi d^2}{4}", r"&= 0.28").
        """
        return "$$\n\\begin{aligned}\n" + " \\\\\n".join(linhas) + "\n\\end{aligned}\n$$\n"

    l_m = projeto.l / 100.0
    bw_pista_m = projeto.bw_pista / 100.0
    d_m = float(geo_real["d"]) / 100.0
    bw_m = float(geo_real["bw"]) / 100.0
    h_m = float(geo_real["h"]) / 100.0
    esp_long_m = float(geo_real["esp"]) / 100.0
    esp_tab_m = float(geo_real.get("esp_tab", 0.0)) / 100.0
    esp_long_corr = relat_carga.get("esp_long_corr [m]", esp_long_m)
    esp_tab_corr = relat_carga.get("esp_tab_corr [m]", esp_tab_m)
    dens_long_kn = projeto.densidade_long * 9.81 / 1000.0
    dens_tab_kn = projeto.densidade_tab * 9.81 / 1000.0
    m_qk_long_sem_impacto = relat_l.get("m_qk [kN.m]", 0.0) / relat_l.get("aux_ci", 1.0)
    v_qk_long_sem_impacto = relat_l.get("v_qk [kN]", 0.0) / relat_l.get("aux_ci", 1.0)
    c_momento = (l_m - 4.0 * projeto.a) / 2.0 if l_m > 6.0 else 0.0
    e_cortante = l_m - 3.0 * projeto.a - 2.0 * d_m
    b_flecha = (l_m - 2.0 * projeto.a) / 2.0
    aux_flecha = l_m**3 + 2.0 * b_flecha * (3.0 * l_m**2 - 4.0 * b_flecha**2)
    delta_total = res_f.get("delta_fluencia [m]")
    delta_q = res_f.get("delta_qk [m]")
    delta_g = relat_l.get("delta_gk [m]")
    delta_lim_total = res_f.get("delta_lim_total [m]")
    delta_lim_variavel = res_f.get("delta_lim_variavel [m]")

    # ------------------------------------------------------------------
    # Seção 3 — memória de cálculo (equações em LaTeX)
    # ------------------------------------------------------------------
    # As equações são montadas com raw strings concatenadas (e não f-strings)
    # para evitar a duplicação de chaves que o LaTeX exigiria dentro de f-string.

    memoria_detalhada = (
        "\n# 3. Memória de Cálculo Detalhada\n\n"
        "Para cada grandeza são apresentadas a fórmula simbólica, a substituição "
        "numérica e o resultado, permitindo a conferência manual passo a passo.\n\n"

        "## 3.1 Conversão de unidades\n\n"
        "As dimensões são informadas em centímetros e convertidas para metros.\n\n"
        + eq(
            r"L &= \frac{" + fmt(projeto.l) + r"}{100} = " + f(l_m) + r"\ \text{m}",
            r"B_{pista} &= \frac{" + fmt(projeto.bw_pista) + r"}{100} = " + f(bw_pista_m) + r"\ \text{m}",
            r"d &= \frac{" + fmt(geo_real['d']) + r"}{100} = " + f(d_m) + r"\ \text{m}",
            r"b_{w} &= \frac{" + fmt(geo_real['bw']) + r"}{100} = " + f(bw_m) + r"\ \text{m}",
            r"h &= \frac{" + fmt(geo_real['h']) + r"}{100} = " + f(h_m) + r"\ \text{m}",
            r"esp_{long} &= \frac{" + fmt(geo_real['esp']) + r"}{100} = " + f(esp_long_m) + r"\ \text{m}",
            r"esp_{tab} &= \frac{" + fmt(geo_real.get('esp_tab', 0.0)) + r"}{100} = " + f(esp_tab_m) + r"\ \text{m}",
        )

        + "\n## 3.2 Propriedades geométricas da longarina (seção circular)\n\n"
        + eq(
            r"A &= \frac{\pi\,d^{2}}{4}",
            r"&= \frac{\pi \cdot (" + f(d_m) + r")^{2}}{4}",
            r"&= " + f(relat_l.get('area [m2]'), 6) + r"\ \text{m}^{2}",
        )
        + eq(
            r"I_{x} &= \frac{\pi\,d^{4}}{64}",
            r"&= \frac{\pi \cdot (" + f(d_m) + r")^{4}}{64}",
            r"&= " + f(relat_l.get('i_x [m4]'), 8) + r"\ \text{m}^{4}",
        )
        + eq(
            r"W_{x} &= \frac{I_{x}}{d/2}",
            r"&= \frac{" + f(relat_l.get('i_x [m4]'), 8) + r"}{" + f(d_m) + r"/2}",
            r"&= " + f(relat_l.get('w_x [m3]'), 8) + r"\ \text{m}^{3}",
        )
        + eq(
            r"S_{x} &= A \cdot \frac{d}{2}",
            r"&= " + f(relat_l.get('area [m2]'), 6) + r" \cdot \frac{" + f(d_m) + r"}{2}",
            r"&= " + f(relat_l.get('s_x [m3]'), 8) + r"\ \text{m}^{3}",
        )

        + "\n## 3.3 Propriedades geométricas do tabuleiro (seção retangular)\n\n"
        + eq(
            r"A_{tab} &= b_{w} \cdot h",
            r"&= " + f(bw_m) + r" \cdot " + f(h_m),
            r"&= " + f(relat_t.get('area [m2]'), 6) + r"\ \text{m}^{2}",
        )
        + eq(
            r"I_{x,tab} &= \frac{b_{w}\,h^{3}}{12}",
            r"&= \frac{" + f(bw_m) + r" \cdot (" + f(h_m) + r")^{3}}{12}",
            r"&= " + f(relat_t.get('i_x [m4]'), 8) + r"\ \text{m}^{4}",
        )
        + eq(
            r"W_{x,tab} &= \frac{I_{x,tab}}{h/2}",
            r"&= \frac{" + f(relat_t.get('i_x [m4]'), 8) + r"}{" + f(h_m) + r"/2}",
            r"&= " + f(relat_t.get('w_x [m3]'), 8) + r"\ \text{m}^{3}",
        )

        + "\n## 3.4 Ajuste geométrico dos espaçamentos\n\n"
        + "O número de peças é inteiro, de modo que o espaçamento informado é ajustado "
        + "para preencher exatamente o espaço disponível.\n\n"
        + eq(
            r"n_{long} &= " + str(relat_carga.get('num_longs')) + r"\ \text{peças}",
            r"esp_{long,corr} &= " + f(esp_long_corr) + r"\ \text{m} = " + fmt(esp_long_corr * 100.0) + r"\ \text{cm}",
            r"n_{tab} &= " + str(relat_carga.get('num_tabs')) + r"\ \text{peças}",
            r"esp_{tab,corr} &= " + f(esp_tab_corr) + r"\ \text{m} = " + fmt(esp_tab_corr * 100.0) + r"\ \text{cm}",
        )

        + "\n## 3.5 Cargas permanentes\n\n"
        + "Conversão da densidade (kg/m³) em peso específico (kN/m³):\n\n"
        + eq(
            r"\gamma_{long} &= \frac{\rho_{long} \cdot 9{,}81}{1000}"
            r" = \frac{" + fmt(projeto.densidade_long) + r" \cdot 9{,}81}{1000}"
            r" = " + f(dens_long_kn) + r"\ \text{kN/m}^{3}",
            r"\gamma_{tab} &= \frac{\rho_{tab} \cdot 9{,}81}{1000}"
            r" = \frac{" + fmt(projeto.densidade_tab) + r" \cdot 9{,}81}{1000}"
            r" = " + f(dens_tab_kn) + r"\ \text{kN/m}^{3}",
        )
        + "Peso próprio da longarina:\n\n"
        + eq(
            r"pp_{long} &= \gamma_{long} \cdot A",
            r"&= " + f(dens_long_kn) + r" \cdot " + f(relat_l.get('area [m2]'), 6),
            r"&= " + f(relat_carga.get('pp_gk_long [kN/m]')) + r"\ \text{kN/m}",
        )
        + "Peso próprio do tabuleiro, distribuído por área de pista:\n\n"
        + eq(
            r"pp_{tab} &= \frac{\gamma_{tab} \cdot n_{tab} \cdot (h \cdot b_{w} \cdot B_{pista})}{B_{pista} \cdot L}",
            r"&= \frac{" + f(dens_tab_kn) + r" \cdot " + str(relat_carga.get('num_tabs'))
            + r" \cdot (" + f(h_m) + r" \cdot " + f(bw_m) + r" \cdot " + f(bw_pista_m) + r")}"
            + r"{" + f(bw_pista_m) + r" \cdot " + f(l_m) + r"}",
            r"&= " + f(relat_carga.get('pp_tab [kPa]')) + r"\ \text{kPa}",
        )
        + "Carga permanente total sobre a longarina:\n\n"
        + eq(
            r"p_{g,long} &= (p_{gk} + pp_{tab}) \cdot esp_{long,corr} + pp_{long}",
            r"&= (" + f(projeto.p_gk) + r" + " + f(relat_carga.get('pp_tab [kPa]')) + r") \cdot "
            + f(esp_long_corr) + r" + " + f(relat_carga.get('pp_gk_long [kN/m]')),
            r"&= " + f(relat_carga.get('p_glongk [kN/m]')) + r"\ \text{kN/m}",
        )
        + "Carga permanente sobre a peça do tabuleiro:\n\n"
        + eq(
            r"p_{g,tab} &= (p_{gk} + pp_{tab}) \cdot b_{w}",
            r"&= (" + f(projeto.p_gk) + r" + " + f(relat_carga.get('pp_tab [kPa]')) + r") \cdot " + f(bw_m),
            r"&= " + f(relat_carga.get('p_gtabk [kN/m]')) + r"\ \text{kN/m}",
        )

        + "\n## 3.6 Esforços solicitantes na longarina\n\n"
        + "Coeficiente de impacto vertical (NBR 7188) e coeficiente auxiliar:\n\n"
        + eq(
            r"C_{i} &= " + f(relat_l.get('coeficiente_impacto_vertical'), 3),
            r"aux_{ci} &= 1 + 0{,}75\,(C_{i} - 1)"
            r" = 1 + 0{,}75 \cdot (" + f(relat_l.get('coeficiente_impacto_vertical'), 3) + r" - 1)"
            r" = " + f(relat_l.get('aux_ci'), 3),
        )
        + "Momento fletor devido à carga permanente:\n\n"
        + eq(
            r"M_{gk} &= \frac{p_{g,long} \cdot L^{2}}{8}",
            r"&= \frac{" + f(relat_carga.get('p_glongk [kN/m]')) + r" \cdot (" + f(l_m) + r")^{2}}{8}",
            r"&= " + f(relat_l.get('m_gk [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + "Momento fletor devido à carga móvel:\n\n"
        + eq(
            r"c &= \frac{L - 4a}{2} = \frac{" + f(l_m) + r" - 4 \cdot " + f(projeto.a) + r"}{2} = " + f(c_momento) + r"\ \text{m}",
        )
        + eq(
            r"M_{qk,0} &= \frac{3\,P_{roda}\,L}{4} - P_{roda}\,a + \frac{p_{qk}\,c^{2}}{2}",
            r"&= \frac{3 \cdot " + f(projeto.p_rodak) + r" \cdot " + f(l_m) + r"}{4}"
            r" - " + f(projeto.p_rodak) + r" \cdot " + f(projeto.a)
            + r" + \frac{" + f(projeto.p_qk) + r" \cdot (" + f(c_momento) + r")^{2}}{2}",
            r"&= " + f(m_qk_long_sem_impacto) + r"\ \text{kN}\cdot\text{m}",
        )
        + eq(
            r"M_{qk} &= M_{qk,0} \cdot aux_{ci}",
            r"&= " + f(m_qk_long_sem_impacto) + r" \cdot " + f(relat_l.get('aux_ci'), 3),
            r"&= " + f(relat_l.get('m_qk [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + "Momento fletor de cálculo:\n\n"
        + eq(
            r"M_{sd} &= \gamma_{g}\,M_{gk} + \gamma_{q}\,M_{qk}",
            r"&= " + f(projeto.gamma_g) + r" \cdot " + f(relat_l.get('m_gk [kN.m]'))
            + r" + " + f(projeto.gamma_q) + r" \cdot " + f(relat_l.get('m_qk [kN.m]')),
            r"&= " + f(res_m.get('m_sd [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + "Esforço cortante devido à carga permanente:\n\n"
        + eq(
            r"V_{gk} &= \frac{p_{g,long} \cdot L}{2}",
            r"&= \frac{" + f(relat_carga.get('p_glongk [kN/m]')) + r" \cdot " + f(l_m) + r"}{2}",
            r"&= " + f(relat_l.get('v_gk [kN]')) + r"\ \text{kN}",
        )
        + "Esforço cortante devido à carga móvel:\n\n"
        + eq(
            r"e &= L - 3a - 2d = " + f(l_m) + r" - 3 \cdot " + f(projeto.a)
            + r" - 2 \cdot " + f(d_m) + r" = " + f(e_cortante) + r"\ \text{m}",
        )
        + eq(
            r"V_{qk,0} &= \frac{P_{roda}}{L}\,(6a + 3e) + \frac{p_{qk}\,e^{2}}{2L}",
            r"&= \frac{" + f(projeto.p_rodak) + r"}{" + f(l_m) + r"} \cdot (6 \cdot " + f(projeto.a)
            + r" + 3 \cdot " + f(e_cortante) + r")"
            + r" + \frac{" + f(projeto.p_qk) + r" \cdot (" + f(e_cortante) + r")^{2}}{2 \cdot " + f(l_m) + r"}",
            r"&= " + f(v_qk_long_sem_impacto) + r"\ \text{kN}",
        )
        + eq(
            r"V_{qk} &= V_{qk,0} \cdot aux_{ci}",
            r"&= " + f(v_qk_long_sem_impacto) + r" \cdot " + f(relat_l.get('aux_ci'), 3),
            r"&= " + f(relat_l.get('v_qk [kN]')) + r"\ \text{kN}",
        )
        + "Esforço cortante de cálculo:\n\n"
        + eq(
            r"V_{sd} &= \gamma_{g}\,V_{gk} + \gamma_{q}\,V_{qk}",
            r"&= " + f(projeto.gamma_g) + r" \cdot " + f(relat_l.get('v_gk [kN]'))
            + r" + " + f(projeto.gamma_q) + r" \cdot " + f(relat_l.get('v_qk [kN]')),
            r"&= " + f(res_v.get('v_sd [kN]')) + r"\ \text{kN}",
        )

        + "\n## 3.7 Verificação à flexão da longarina\n\n"
        + "Coeficiente de modificação, resultado do produto entre o fator de duração do "
        + "carregamento e o fator de classe de umidade:\n\n"
        + eq(
            r"k_{mod} &= k_{mod,1} \cdot k_{mod,2}",
            r"&= " + f(res_m.get('k_mod1'), 3) + r" \cdot " + f(res_m.get('k_mod2'), 3),
            r"&= " + f(res_m.get('k_mod'), 3),
        )
        + eq(
            r"f_{md} &= \frac{k_{mod} \cdot f_{mk}}{\gamma_{wf}}",
            r"&= \frac{" + f(res_m.get('k_mod'), 3) + r" \cdot " + f(projeto.f_mk_long * 1000.0) + r"}{" + f(projeto.gamma_wf) + r"}",
            r"&= " + f(res_m.get('f_md [kPa]')) + r"\ \text{kPa} = " + fmpa(res_m.get('f_md [kPa]')) + r"\ \text{MPa}",
        )
        + eq(
            r"\sigma_{x,d} &= \frac{M_{sd}}{W_{x}}",
            r"&= \frac{" + f(res_m.get('m_sd [kN.m]')) + r"}{" + f(relat_l.get('w_x [m3]'), 8) + r"}",
            r"&= " + f(res_m.get('sigma_x [kPa]')) + r"\ \text{kPa} = " + fmpa(res_m.get('sigma_x [kPa]')) + r"\ \text{MPa}",
        )
        + eq(
            r"g &= \frac{\sigma_{x,d} - f_{md}}{f_{md}}",
            r"&= \frac{" + f(res_m.get('sigma_x [kPa]')) + r" - " + f(res_m.get('f_md [kPa]')) + r"}{" + f(res_m.get('f_md [kPa]')) + r"}",
            r"&= " + f(res_m.get('g_otimiz [-]'), 4),
        )
        + "Resultado: " + status_icon(res_m) + " ($g \\leq 0$ indica segurança).\n"

        + "\n## 3.8 Verificação ao cisalhamento da longarina\n\n"
        + eq(
            r"f_{vd} &= \frac{k_{mod} \cdot f_{vk}}{\gamma_{wc}}",
            r"&= \frac{" + f(res_m.get('k_mod'), 3) + r" \cdot " + f(projeto.f_vk_long * 1000.0) + r"}{" + f(projeto.gamma_wc) + r"}",
            r"&= " + f(res_v.get('f_vd [kPa]')) + r"\ \text{kPa} = " + fmpa(res_v.get('f_vd [kPa]')) + r"\ \text{MPa}",
        )
        + "Para a seção circular, a tensão tangencial máxima ocorre no centro da seção:\n\n"
        + eq(
            r"\tau_{sd} &= \frac{4}{3} \cdot \frac{V_{sd}}{A}",
            r"&= \frac{4}{3} \cdot \frac{" + f(res_v.get('v_sd [kN]')) + r"}{" + f(relat_l.get('area [m2]'), 6) + r"}",
            r"&= " + f(res_v.get('tau_sd [kPa]')) + r"\ \text{kPa} = " + fmpa(res_v.get('tau_sd [kPa]')) + r"\ \text{MPa}",
        )
        + eq(
            r"g &= \frac{\tau_{sd} - f_{vd}}{f_{vd}}",
            r"&= \frac{" + f(res_v.get('tau_sd [kPa]')) + r" - " + f(res_v.get('f_vd [kPa]')) + r"}{" + f(res_v.get('f_vd [kPa]')) + r"}",
            r"&= " + f(res_v.get('g_otimiz [-]'), 4),
        )
        + "Resultado: " + status_icon(res_v) + ".\n"

        + "\n## 3.9 Verificação de flecha da longarina\n\n"
        + "Flecha devida à carga permanente (viga biapoiada, carga uniformemente distribuída):\n\n"
        + eq(
            r"\delta_{gk} &= \frac{5\,p_{g,long}\,L^{4}}{384\,E\,I_{x}}",
            r"&= \frac{5 \cdot " + f(relat_carga.get('p_glongk [kN/m]')) + r" \cdot (" + f(l_m) + r")^{4}}"
            + r"{384 \cdot " + f(projeto.e_modflex_long * 1000000.0) + r" \cdot " + f(relat_l.get('i_x [m4]'), 8) + r"}",
            r"&= " + f(delta_g, 6) + r"\ \text{m}",
        )
        + "Flecha devida à carga móvel concentrada:\n\n"
        + eq(
            r"b &= \frac{L - 2a}{2} = \frac{" + f(l_m) + r" - 2 \cdot " + f(projeto.a) + r"}{2} = " + f(b_flecha) + r"\ \text{m}",
        )
        + eq(
            r"aux &= L^{3} + 2b\,(3L^{2} - 4b^{2})",
            r"&= (" + f(l_m) + r")^{3} + 2 \cdot " + f(b_flecha)
            + r" \cdot \left(3 \cdot (" + f(l_m) + r")^{2} - 4 \cdot (" + f(b_flecha) + r")^{2}\right)",
            r"&= " + f(aux_flecha) + r"\ \text{m}^{3}",
        )
        + eq(
            r"\delta_{qk} &= \frac{P_{roda} \cdot aux}{48\,E\,I_{x}}",
            r"&= \frac{" + f(projeto.p_rodak) + r" \cdot " + f(aux_flecha) + r"}"
            + r"{48 \cdot " + f(projeto.e_modflex_long * 1000000.0) + r" \cdot " + f(relat_l.get('i_x [m4]'), 8) + r"}",
            r"&= " + f(delta_q, 6) + r"\ \text{m}",
        )
        + "Flecha total, considerando a fluência:\n\n"
        + eq(
            r"\delta_{total} &= \delta_{gk} + \psi_{2}\,(1 + \varphi)\,\delta_{qk}",
            r"&= " + f(delta_g, 6) + r" + " + f(projeto.psi2) + r" \cdot (1 + " + f(projeto.phi) + r") \cdot " + f(delta_q, 6),
            r"&= " + f(delta_total, 6) + r"\ \text{m}",
        )
        + "Limites normativos e funções de estado limite:\n\n"
        + eq(
            r"\delta_{lim,total} &= \frac{L}{250} = \frac{" + f(l_m) + r"}{250} = " + f(delta_lim_total, 6) + r"\ \text{m}",
            r"\delta_{lim,var} &= \frac{L}{360} = \frac{" + f(l_m) + r"}{360} = " + f(delta_lim_variavel, 6) + r"\ \text{m}",
        )
        + eq(
            r"g_{total} &= \frac{\delta_{total} - \delta_{lim,total}}{\delta_{lim,total}}"
            r" = \frac{" + f(delta_total, 6) + r" - " + f(delta_lim_total, 6) + r"}{" + f(delta_lim_total, 6) + r"}",
            r"g_{var} &= \frac{\delta_{qk} - \delta_{lim,var}}{\delta_{lim,var}}"
            r" = \frac{" + f(delta_q, 6) + r" - " + f(delta_lim_variavel, 6) + r"}{" + f(delta_lim_variavel, 6) + r"}",
            r"g &= \max(g_{total},\ g_{var}) = " + f(res_f.get('g_otimiz [-]'), 4),
        )
        + "Resultado: " + status_icon(res_f) + ".\n"

        + "\n## 3.10 Esforços e verificação à flexão do tabuleiro\n\n"
        + "A peça do tabuleiro é verificada como viga biapoiada, vencendo o vão entre longarinas.\n\n"
        + eq(
            r"C_{i,tab} &= " + f(relat_t.get('coeficiente_impacto_vertical'), 3),
            r"aux_{ci,tab} &= 1 + 0{,}75\,(C_{i,tab} - 1) = " + f(relat_t.get('aux_ci'), 3),
        )
        + eq(
            r"M_{gk,tab} &= \frac{p_{g,tab} \cdot esp_{long,corr}^{2}}{8}",
            r"&= \frac{" + f(relat_carga.get('p_gtabk [kN/m]')) + r" \cdot (" + f(esp_long_corr) + r")^{2}}{8}",
            r"&= " + f(relat_t.get('m_gk [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + eq(
            r"M_{qk,tab} &= \frac{P_{roda}}{4}\,(esp_{long,corr} - 0{,}45) \cdot aux_{ci,tab}",
            r"&= \frac{" + f(projeto.p_rodak) + r"}{4} \cdot (" + f(esp_long_corr) + r" - 0{,}45) \cdot " + f(relat_t.get('aux_ci'), 3),
            r"&= " + f(relat_t.get('m_qk [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + eq(
            r"M_{sd,tab} &= \gamma_{g}\,M_{gk,tab} + \gamma_{q}\,M_{qk,tab}",
            r"&= " + f(projeto.gamma_g) + r" \cdot " + f(relat_t.get('m_gk [kN.m]'))
            + r" + " + f(projeto.gamma_q) + r" \cdot " + f(relat_t.get('m_qk [kN.m]')),
            r"&= " + f(res_m_tab.get('m_sd [kN.m]')) + r"\ \text{kN}\cdot\text{m}",
        )
        + eq(
            r"f_{md,tab} &= \frac{k_{mod} \cdot f_{mk,tab}}{\gamma_{wf}}",
            r"&= \frac{" + f(res_m_tab.get('k_mod'), 3) + r" \cdot " + f(projeto.f_mk_tab * 1000.0) + r"}{" + f(projeto.gamma_wf) + r"}",
            r"&= " + f(res_m_tab.get('f_md [kPa]')) + r"\ \text{kPa} = " + fmpa(res_m_tab.get('f_md [kPa]')) + r"\ \text{MPa}",
        )
        + eq(
            r"\sigma_{x,d,tab} &= \frac{M_{sd,tab}}{W_{x,tab}}",
            r"&= \frac{" + f(res_m_tab.get('m_sd [kN.m]')) + r"}{" + f(relat_t.get('w_x [m3]'), 8) + r"}",
            r"&= " + f(res_m_tab.get('sigma_x [kPa]')) + r"\ \text{kPa} = " + fmpa(res_m_tab.get('sigma_x [kPa]')) + r"\ \text{MPa}",
        )
        + eq(
            r"g_{tab} &= \frac{\sigma_{x,d,tab} - f_{md,tab}}{f_{md,tab}}",
            r"&= \frac{" + f(res_m_tab.get('sigma_x [kPa]')) + r" - " + f(res_m_tab.get('f_md [kPa]')) + r"}{" + f(res_m_tab.get('f_md [kPa]')) + r"}",
            r"&= " + f(res_m_tab.get('g_otimiz [-]'), 4),
        )
        + "Resultado: " + status_icon(res_m_tab) + ".\n"
    )

    # Escrevendo o Relatório

    # Montagem do texto final. Usa f-strings (o f na frente das aspas)
    # para injetar os valores das variáveis direto no meio do texto.

    md = f"""
# RELIABRIDGE — Memorial de Cálculo

**Grupo de Pesquisa e Estudos em Engenharia — GPEE**

Data de emissão: {datetime.now().strftime('%d/%m/%Y')}

---

*Disclaimer:* Este software é parte de um projeto de pesquisa, desenvolvido para fins educacionais. Não nos responsabilizamos por quaisquer danos diretos ou indiretos decorrentes do uso deste software.

---

# 1. Dados de Entrada

Os valores abaixo reproduzem integralmente a planilha `beam_data.xlsx` gerada no pré-dimensionamento.

## 1.1 Geometria geral

| Parâmetro | Símbolo | Valor | Unidade |
| :--- | :---: | :---: | :---: |
| Vão teórico das longarinas | $L$ | {fmt(projeto.l)} | cm |
| Largura da pista disponível | $B_{{pista}}$ | {fmt(projeto.bw_pista)} | cm |

## 1.2 Ações

| Parâmetro | Símbolo | Valor | Unidade |
| :--- | :---: | :---: | :---: |
| Carga permanente no tabuleiro (excluso peso próprio) | $p_{{gk}}$ | {fmt(projeto.p_gk)} | kPa |
| Carga concentrada por roda | $P_{{rodak}}$ | {fmt(projeto.p_rodak)} | kN |
| Carga de multidão | $p_{{qk}}$ | {fmt(projeto.p_qk)} | kPa |
| Distância entre eixos do trem tipo | $a$ | {fmt(projeto.a)} | m |

## 1.3 Classes normativas

| Parâmetro | Valor |
| :--- | :---: |
| Classe de carregamento | {str(projeto.classe_carregamento).title()} |
| Classe da madeira | {str(projeto.classe_madeira).title()} |
| Classe de umidade | {projeto.classe_umidade} |

## 1.4 Coeficientes parciais de segurança e de combinação

| Parâmetro | Símbolo | Valor |
| :--- | :---: | :---: |
| Majoração das ações permanentes | $\\gamma_g$ | {fmt(projeto.gamma_g)} |
| Majoração das ações variáveis | $\\gamma_q$ | {fmt(projeto.gamma_q)} |
| Minoração da resistência à flexão | $\\gamma_{{wf}}$ | {fmt(projeto.gamma_wf)} |
| Minoração da resistência ao cisalhamento | $\\gamma_{{wc}}$ | {fmt(projeto.gamma_wc)} |
| Fator de combinação quase permanente | $\\psi_2$ | {fmt(projeto.psi2)} |
| Coeficiente de fluência (Tabela 20, NBR 7190) | $\\varphi$ | {fmt(projeto.phi)} |

## 1.5 Propriedades dos materiais

| Elemento | Parâmetro | Símbolo | Valor | Unidade |
| :--- | :--- | :---: | :---: | :---: |
| Longarina | Densidade | $\\rho_{{long}}$ | {fmt(projeto.densidade_long)} | kg/m$^3$ |
| Longarina | Resistência caract. à flexão | $f_{{mk}}$ | {fmt(projeto.f_mk_long)} | MPa |
| Longarina | Resistência caract. ao cisalhamento | $f_{{vk}}$ | {fmt(projeto.f_vk_long)} | MPa |
| Longarina | Módulo de elasticidade à flexão | $E_{{0,ef}}$ | {fmt(projeto.e_modflex_long)} | GPa |
| Tabuleiro | Densidade | $\\rho_{{tab}}$ | {fmt(projeto.densidade_tab)} | kg/m$^3$ |
| Tabuleiro | Resistência caract. à flexão | $f_{{mk,tab}}$ | {fmt(projeto.f_mk_tab)} | MPa |


# 2. Geometria e Propriedades da Seção

## 2.1 Dimensões adotadas

| Elemento | Parâmetro | Valor | Unidade |
| :--- | :--- | :---: | :---: |
| Longarina | Diâmetro ($d$) | {fmt(geo_real['d'])} | cm |
| Longarina | Espaçamento informado | {fmt(geo_real['esp'])} | cm |
| Longarina | Espaçamento ajustado | {fmt(esp_long_corr * 100.0)} | cm |
| Longarina | Número de peças | {relat_carga.get('num_longs')} | - |
| Tabuleiro | Largura ($b_w$) | {fmt(geo_real['bw'])} | cm |
| Tabuleiro | Altura ($h$) | {fmt(geo_real['h'])} | cm |
| Tabuleiro | Espaçamento informado | {fmt(geo_real.get('esp_tab', 0.0))} | cm |
| Tabuleiro | Espaçamento ajustado | {fmt(esp_tab_corr * 100.0)} | cm |
| Tabuleiro | Número de peças | {relat_carga.get('num_tabs')} | - |

## 2.2 Propriedades geométricas da longarina

| Propriedade | Símbolo | Valor | Unidade |
| :--- | :---: | :---: | :---: |
| Área da seção | $A$ | {fmt(relat_l.get('area [m2]'), 0.0001)} | cm$^2$ |
| Módulo resistente | $W_x$ | {fmt(relat_l.get('w_x [m3]'), 0.000001)} | cm$^3$ |
| Momento de inércia | $I_x$ | {fmt(relat_l.get('i_x [m4]'), 0.00000001)} | cm$^4$ |
| Momento estático | $S_x$ | {fmt(relat_l.get('s_x [m3]'), 0.000001)} | cm$^3$ |

## 2.3 Propriedades geométricas do tabuleiro

| Propriedade | Símbolo | Valor | Unidade |
| :--- | :---: | :---: | :---: |
| Área da seção | $A_{{tab}}$ | {fmt(relat_t.get('area [m2]'), 0.0001)} | cm$^2$ |
| Módulo resistente | $W_{{x,tab}}$ | {fmt(relat_t.get('w_x [m3]'), 0.000001)} | cm$^3$ |
| Momento de inércia | $I_{{x,tab}}$ | {fmt(relat_t.get('i_x [m4]'), 0.00000001)} | cm$^4$ |

{memoria_detalhada}

---

Relatório gerado automaticamente pelo sistema RELIABRIDGE em {datetime.now().strftime('%d/%m/%Y às %H:%M')}.
"""
    return md


def markdown_para_pdf(conteudo_md, output_filename=None):
    extra_args = [
        '--pdf-engine=xelatex',
        '-V', 'geometry:margin=2cm',
    ]

    try:
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp_path = tmp.name

        # Tenta converter
        pypandoc.convert_text(
            conteudo_md,
            'pdf',
            format='md',
            outputfile=tmp_path,
            extra_args=extra_args
        )

        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 0:
            with open(tmp_path, "rb") as f:
                pdf_bytes = f.read()
            os.unlink(tmp_path) # Deleta o temp
            return pdf_bytes
        else:
            print("ERRO: O arquivo PDF foi criado mas está vazio (0 bytes).")
            return None

    except Exception as e:
        print(f"ERRO CRÍTICO NO PANDOC: {e}")
        return None


# Otimização estrutural
class ProjetoOtimo(ElementwiseProblem):
    def __init__(
                    self,
                    bw_pista: float,
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
                    gamma_wf: float,
                    gamma_wc: float,
                    psi2: float,
                    phi: float,
                    densidade_long: float,
                    densidade_tab: float,
                    f_mk_long: float,
                    f_vk_long: float,
                    e_modflex_long: float,
                    f_mk_tab: float,
                    d_min: float,
                    d_max: float,
                    bw_min: float,
                    bw_max: float,
                    h_min: float,
                    h_max: float,
                    n_min_long: float,
                    n_max_long: float,
                    n_min_tab: float,
                    n_max_tab: float,
                    n_checagens: int = 30,
                    perc_robustez: float = 5.0
                ):
        """Inicialização das variáveis do problema de otimização/confiabilidade estrutural.

        :param bw_pista: Largura da pista disponível para longarinas [cm]
        :param l: Comprimento do vão [cm]
        :param p_gk: Carga permanente característica atuante no tabuleiro [kPa]
        :param p_rodak: carga variável característica por roda [kN]
        :param p_qk: Carga variável característica de multidão [kPa]
        :param a: distância entre eixos [m]
        :param classe_carregamento: 'permanente', 'longa duração', 'média duração', 'curta duração' ou 'instantânea'
        :param classe_madeira: 'madeira natural' ou 'madeira recomposta'
        :param classe_umidade: 1, 2, 3, 4
        :param gamma_g: Coeficiente parcial de segurança para carga permanente
        :param gamma_q: Coeficiente parcial de segurança para carga variável
        :param gamma_wf: Coeficiente parcial de segurança para madeira na flexão
        :param gamma_wc: Coeficiente parcial de segurança para madeira no cisalhamento
        :param psi2: Coeficiente de combinação para carga variável
        :param phi: Coeficiente de fluência para carga variável
        :param densidade_long: Densidade da madeira (kg/m³) da longarina
        :param densidade_tab: Densidade da madeira (kg/m³) do tabuleiro
        :param f_mk_long: Resistência característica à flexão (MPa) da longarina
        :param f_vk_long: Resistência característica ao cisalhamento (MPa) da longarina
        :param e_modflex_long: Módulo de elasticidade à flexão (GPa) da longarina
        :param f_mk_tab: Resistência característica à flexão (MPa) do tabuleiro
        :param d_min: Diâmetro mínimo da longarina [cm]
        :param d_max: Diâmetro máximo da longarina [cm]
        :param bw_min: Largura mínima da viga do tabuleiro [cm]
        :param bw_max: Largura máxima da viga do tabuleiro [cm]
        :param h_min: Altura mínima da viga do tabuleiro [cm]
        :param h_max: Altura máxima da viga do tabuleiro [cm]
        :param n_min_long: Espaço mínimo de longarinas
        :param n_max_long: Espaço máximo de longarinas
        :param n_min_tab: Espaço mínimo de peças do tabuleiro
        :param n_max_tab: Espaço máximo de peças do tabuleiro
        :param n_checagens: Número de checagens para avaliação robusta na otimização
        :param perc_robustez: Percentual de robustez para considerar na otimização [5 igual a 5%]
        """

        self.bw_pista               = float(bw_pista)
        self.l                      = float(l)
        self.p_gk                   = float(p_gk)
        self.p_rodak                = float(p_rodak)
        self.p_qk                   = float(p_qk)
        self.a                      = float(a)
        self.classe_carregamento    = classe_carregamento
        self.classe_madeira         = classe_madeira
        self.classe_umidade         = classe_umidade
        self.gamma_g                = float(gamma_g)
        self.gamma_q                = float(gamma_q)
        self.gamma_wf               = float(gamma_wf)
        self.gamma_wc               = float(gamma_wc)
        self.psi2                   = float(psi2)
        self.phi                    = float(phi)
        self.densidade_long         = float(densidade_long)
        self.densidade_tab          = float(densidade_tab)
        self.f_mk_long              = float(f_mk_long)
        self.f_vk_long              = float(f_vk_long)
        self.e_modflex_long         = float(e_modflex_long)
        self.f_mk_tab               = float(f_mk_tab)
        self.d_min                  = float(d_min)
        self.d_max                  = float(d_max)
        self.bw_min                 = float(bw_min)
        self.bw_max                 = float(bw_max)
        self.h_min                  = float(h_min)
        self.h_max                  = float(h_max)
        self.n_min_long             = int(n_min_long)
        self.n_max_long             = int(n_max_long)
        self.n_min_tab              = int(n_min_tab)
        self.n_max_tab              = int(n_max_tab)
        self.n_checagens            = int(n_checagens)
        self.perc_robustez          = float(perc_robustez)
        self.multiplicadores_robustez = self._criar_multiplicadores_robustez()
        xl = np.array([d_min, bw_min, h_min, n_min_long, n_min_tab], dtype=float)
        xu = np.array([d_max, bw_max, h_max, n_max_long, n_max_tab], dtype=float)

        super().__init__(
                            n_var        = 5,
                            n_obj        = 2,
                            n_ieq_constr = 6,
                            xl           = xl,
                            xu           = xu,
                            elementwise_evaluation=True
                        )

    def _criar_multiplicadores_robustez(self) -> np.ndarray:
        rho = self.perc_robustez / 100.0
        if rho <= 0.0 or self.n_checagens <= 1:
            return np.ones((1, 5), dtype=float)

        rng = np.random.default_rng(1)
        xi = rng.uniform(-1.0, 1.0, size=(self.n_checagens, 5))
        return 1.0 + rho * xi

    def calcular_objetivos_restricoes_otimizacao(self, d: float, bw: float, h: float, n_long: float, n_tab: float) -> tuple[list, list, dict, dict, dict, dict, dict, dict, dict]:
        """Determina os objetivos e restrições do problema de otimização.

        :param d: Diâmetro da longarina [cm]
        :param bw: Largura da viga do tabuleiro [cm]
        :param h: Altura da viga do tabuleiro [cm]
        :param n_long: Espaçamento entre longarinas
        :param n_tab: Espaçamento entre peças do tabuleiro

        :return:    [0] Lista com os objetivos, ambos de minimização. f1 volume total de madeira [m³], f2 utilização do limite de serviço da longarina (delta_total / delta_lim), adimensional
                    [1] Lista com as restrições
                    [2] Dicionário com resultados da verificação de flexão da longarina
                    [3] Dicionário com resultados da verificação de cisalhamento da longarina
                    [4] Dicionário com resultados da verificação de flecha da longarina
                    [5] Dicionário com o relatório da longarina
                    [6] Dicionário com resultados da verificação de flexão do tabuleiro
                    [7] Dicionário com o relatório do tabuleiro
                    [8] Dicionário com o relatório das cargas atuantes
        """

        # Conversão unidades e cálculo de cargas
        l               = self.l / 100.0                         # [m]
        bw_pista        = self.bw_pista / 100.0                  # [m]
        d               /= 100.0                                 # [m]
        bw              /= 100.0                                 # [m]
        h               /= 100.0                                 # [m]
        esp_min_long    = self.n_min_long / 100.0                # [m]
        esp_max_long    = self.n_max_long / 100.0                # [m]
        esp_min_tab     = self.n_min_tab / 100.0                 # [m]
        esp_max_tab     = self.n_max_tab / 100.0                 # [m]
        esp_long        = float(n_long) / 100.0                  # [m]
        esp_tab         = float(n_tab) / 100.0                   # [m]
        f_mk_long       = self.f_mk_long *1E3                    # [kPa]
        f_vk_long       = self.f_vk_long * 1E3                   # [kPa]
        e_modflex_long  = self.e_modflex_long * 1E6              # [kPa]
        f_mk_tab        = self.f_mk_tab * 1E3                    # [kPa]
        densidade_long  = self.densidade_long * 9.81 / 1000.0    # [kN/m3]
        densidade_tab   = self.densidade_tab * 9.81 / 1000.0     # [kN/m3]

        # Armazena o geometria
        geo_tab  = {"b_w": bw, "h": h}
        geo_long = {"d": d}

        # Restrição de preenchimento do espaço disponível para longarina e tabuleiro
        g5, num_longs, esp_long_corr = restringir_espaco(esp_long, esp_min_long, esp_max_long, bw_pista, d)
        g6, num_tabss, esp_tab_corr  = restringir_espaco(esp_tab, esp_min_tab, esp_max_tab, l, bw)

        # Carga permanente do tabuleiro que atua na longarina
        carga_area_tab = (densidade_tab * num_tabss * (h * bw * bw_pista)) / (bw_pista * l)  # [kPa]            
        p_gk_long      = (self.p_gk + carga_area_tab) * esp_long_corr                        # [kN/m]
        props_long     = prop_madeiras(geo_long)
        area_long      = props_long[0]
        pp_gk_long     = peso_proprio_longarina(densidade_long, area_long)                   # [kN/m]
        p_gk_long      += pp_gk_long                                                         # [kN/m]

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
                                                                                            self.gamma_wf,
                                                                                            self.gamma_wc,
                                                                                            self.psi2,
                                                                                            self.phi,
                                                                                            f_mk_long,
                                                                                            f_vk_long,
                                                                                            e_modflex_long,
                                                                                        )

        # Carga permanente do tabuleiro que atua no tabuleiro
        p_gtabk = (carga_area_tab + self.p_gk) * bw
        relat_carga = {
                            "pp_tab [kPa]": carga_area_tab,
                            "p_gtabk [kN/m]": p_gtabk,
                            "pp_gk_long [kN/m]": pp_gk_long,
                            "p_glongk [kN/m]": p_gk_long,
                            "num_longs": num_longs,
                            "num_tabs": num_tabss,
                            "esp_long_corr [m]": esp_long_corr,
                            "esp_tab_corr [m]": esp_tab_corr,
                        }

        # Avaliação do flexão tabuleiro
        res_m_tab, relat_t = checagem_completa_tabuleiro_madeira_flexao(
                                                                            geo_tab,
                                                                            p_gtabk,
                                                                            self.p_rodak,
                                                                            esp_long_corr,
                                                                            self.classe_carregamento.lower(),
                                                                            self.classe_madeira.lower(),
                                                                            self.classe_umidade,
                                                                            self.gamma_g,
                                                                            self.gamma_q,
                                                                            self.gamma_wf,
                                                                            f_mk_tab,
                                                                        )
        
        # Área de materiais empregados
        props_tab = prop_madeiras(geo_tab)
        area_tab = props_tab[0]
        f1 = num_longs * area_long * l + num_tabss * area_tab * bw_pista
        f2 = res_f_total["of [-]"]
        g1 = res_m["g_otimiz [-]"]
        g2 = res_v["g_otimiz [-]"]
        g3 = res_f_total["g_otimiz [-]"]
        g4 = res_m_tab["g_otimiz [-]"]

        return [f1, f2], [g1, g2, g3, g4, g5, g6], res_m, res_v, res_f_total, relat_l, res_m_tab, relat_t, relat_carga
    
    def _evaluate(self, x, out, *args, **kwargs):
        
        # Geometria da longarina, tabuleiro e espaçamentos
        d        = float(x[0])
        bw       = float(x[1])
        h        = float(x[2])
        esp_long = float(x[3])
        esp_tab  = float(x[4])

        # Cálculo dos objetivos e restrições para avaliação robusta (média de várias checagens para cada indivíduo)
        dados = []
        x_nominal = np.array([d, bw, h, esp_long, esp_tab], dtype=float)
        for multiplicador in self.multiplicadores_robustez:
            x_perturbado = x_nominal * multiplicador
            f, g, *_ = self.calcular_objetivos_restricoes_otimizacao(*x_perturbado)
            resultado = {'f1': f[0], 'f2': f[1], 'g1': g[0], 'g2': g[1], 'g3': g[2], 'g4': g[3], 'g5': g[4], 'g6': g[5]}
            dados.append(resultado)
        df = pd.DataFrame(dados)
        f = df[['f1', 'f2']].mean().tolist()
        g = df[['g1', 'g2', 'g3', 'g4', 'g5', 'g6']].mean().tolist()

        out["F"] = np.array(f, dtype=float)
        out["G"] = np.array(g, dtype=float)


def _normalizar_chave_excel(chave: str) -> str:
    chave = unicodedata.normalize("NFKC", str(chave))
    return " ".join(chave.lower().split())


def valor_dados_pre_sizing(dados: dict, *nomes: str, default=None):
    for nome in nomes:
        if nome in dados and pd.notna(dados[nome]):
            return dados[nome]

    dados_normalizados = {
        _normalizar_chave_excel(chave): valor
        for chave, valor in dados.items()
        if pd.notna(valor)
    }
    for nome in nomes:
        nome_normalizado = _normalizar_chave_excel(nome)
        if nome_normalizado in dados_normalizados:
            return dados_normalizados[nome_normalizado]

    if default is not None:
        return default
    raise KeyError(f"Nenhuma destas chaves foi encontrada nos dados: {nomes}")


_valor_dados = valor_dados_pre_sizing


def normalizar_dados_pre_sizing(dados: dict, t: dict) -> dict:
    """Converte uma linha do Excel para as chaves esperadas pelo pré-dimensionamento atual."""

    return {
        t["entrada_comprimento"]: _valor_dados(dados, t["entrada_comprimento"], "l (cm)", "Comprimento das longarinas (cm)"),
        t["pista"]: _valor_dados(dados, t["pista"], "Largura da pista disponível para longarinas (cm)"),
        f"{t['carga_permanente']} (kPa)": _valor_dados(
            dados,
            f"{t['carga_permanente']} (kPa)",
            t["carga_permanente"],
            "Carga permanente atuante no tabuleiro (kPa) excluso peso próprio",
            "p_gk (kPa)",
        ),
        f"{t['carga_roda']} (kN)": _valor_dados(dados, f"{t['carga_roda']} (kN)", t["carga_roda"], "p_rodak (kN)"),
        f"{t['carga_multidao']} (kPa)": _valor_dados(dados, f"{t['carga_multidao']} (kPa)", t["carga_multidao"], "Carga de multidão (kPa)", "p_qk (kPa)"),
        f"{t['distancia_eixos']} (m)": _valor_dados(dados, f"{t['distancia_eixos']} (m)", t["distancia_eixos"], "a (m)"),
        t["classe_carregamento"]: _valor_dados(dados, t["classe_carregamento"], "classe_carregamento"),
        t["classe_madeira"]: _valor_dados(dados, t["classe_madeira"], "classe_madeira"),
        t["classe_umidade"]: _valor_dados(dados, t["classe_umidade"], "classe_umidade"),
        t["gamma_g"]: _valor_dados(dados, t["gamma_g"], "gamma_g"),
        t["gamma_q"]: _valor_dados(dados, t["gamma_q"], "gamma_q"),
        t["gamma_wf"]: _valor_dados(dados, t["gamma_wf"], "gamma_wf"),
        t["gamma_wc"]: _valor_dados(dados, t["gamma_wc"], "gamma_wc"),
        t["psi2"]: _valor_dados(dados, t["psi2"], "psi_2"),
        t["considerar_fluencia"]: _valor_dados(dados, t["considerar_fluencia"], "phi"),
        t["percentual_robustez"]: _valor_dados(dados, t["percentual_robustez"], default=5.0),
        f"{t['densidade_long']} (kg/m³)": _valor_dados(dados, f"{t['densidade_long']} (kg/m³)", t["densidade_long"], "densidade longarina (kg/m³)"),
        f"{t['densidade_tab']} (kg/m³)": _valor_dados(dados, f"{t['densidade_tab']} (kg/m³)", t["densidade_tab"], "densidade tabuleiro (kg/m³)"),
        f"{t['f_mk']} (MPa)": _valor_dados(dados, f"{t['f_mk']} (MPa)", t["f_mk"], "resistência característica à flexão longarina (MPa)"),
        f"{t['f_vk']} (MPa)": _valor_dados(dados, f"{t['f_vk']} (MPa)", t["f_vk"], "resistência característica ao cisalhamento longarina (MPa)"),
        f"{t['e_modflex']} (GPa)": _valor_dados(dados, f"{t['e_modflex']} (GPa)", t["e_modflex"], "módulo de elasticidade à flexão longarina (GPa)"),
        f"{t['f_mk_tab']} (MPa)": _valor_dados(dados, f"{t['f_mk_tab']} (MPa)", t["f_mk_tab"], "resistência característica à flexão tabuleiro (MPa)"),
    }


def _criar_projeto_otimo_pre_sizing(
    dados: dict,
    ds: list,
    bws: list,
    hs: list,
    n_long: list,
    n_tab: list,
    t: dict,
    n_checagens: int,
    perc_robustez: float,
) -> ProjetoOtimo:
    return ProjetoOtimo(
                            bw_pista            = dados[f"{t['pista']}"],
                            l                   = dados[f"{t['entrada_comprimento']}"],
                            p_gk                = dados[f"{t['carga_permanente']} (kPa)"],
                            p_rodak             = dados[f"{t['carga_roda']} (kN)"],
                            p_qk                = dados[f"{t['carga_multidao']} (kPa)"],
                            a                   = dados[f"{t['distancia_eixos']} (m)"],
                            classe_carregamento = dados[f"{t['classe_carregamento']}"],
                            classe_madeira      = dados[f"{t['classe_madeira']}"],
                            classe_umidade      = dados[f"{t['classe_umidade']}"],
                            gamma_g             = dados[f"{t['gamma_g']}"],
                            gamma_q             = dados[f"{t['gamma_q']}"],
                            gamma_wf            = dados[f"{t['gamma_wf']}"],
                            gamma_wc            = dados[f"{t['gamma_wc']}"],
                            psi2                = dados[f"{t['psi2']}"],
                            phi                 = dados[f"{t['considerar_fluencia']}"],
                            densidade_long      = _valor_dados(dados, f"{t['densidade_long']} (kg/m³)", f"{t['densidade_long']} (kg/mÂ³)"),
                            densidade_tab       = _valor_dados(dados, f"{t['densidade_tab']} (kg/m³)", f"{t['densidade_tab']} (kg/mÂ³)"),
                            f_mk_long           = dados[f"{t['f_mk']} (MPa)"],
                            f_vk_long           = dados[f"{t['f_vk']} (MPa)"],
                            e_modflex_long      = dados[f"{t['e_modflex']} (GPa)"],
                            f_mk_tab            = dados[f"{t['f_mk_tab']} (MPa)"],
                            d_min               = ds[0],
                            d_max               = ds[1],
                            bw_min              = bws[0],
                            bw_max              = bws[1],
                            h_min               = hs[0],
                            h_max               = hs[1],
                            n_min_long          = n_long[0],
                            n_max_long          = n_long[1],
                            n_min_tab           = n_tab[0],
                            n_max_tab           = n_tab[1],
                            n_checagens         = n_checagens,
                            perc_robustez       = perc_robustez,
                    )


def chamando_nsga2(
                        dados: dict,
                        ds: list,
                        bws: list,
                        hs: list,
                        n_long: list,
                        n_tab: list,
                        t: dict,
                        verbose: bool = True,
                        salvar_historico: bool = False,
                        pop_size: int = 75,
                        n_gen: int = 100,
                        n_checagens: int = 30,
                    ):
    """Função para chamar o algoritmo NSGA-II para otimização do projeto estrutural.

    :param dados: Dados de entrada do projeto
    :param ds: Diâmetro mínimo e máximo da longarina [cm]
    :param bws: Largura mínima e máxima da viga do tabuleiro [cm]
    :param hs: Altura mínima e máxima da viga do tabuleiro [cm]
    :param n_long: Espaço mínimo e máximo de longarinas
    :param n_tab: Espaço mínimo e máximo de vigas do tabuleiro
    :param t: Dicionário de textos para nomenclatura dos dados de entrada
    :param verbose: Imprime o progresso da otimização
    :param salvar_historico: Armazena a população de cada geração, permitindo o
                             cálculo da curva de hipervolume. Aumenta o consumo de
                             memória, por isso é desligado por padrão na aplicação.
    :param pop_size: Tamanho da população do NSGA-II
    :param n_gen: Número de gerações
    :param n_checagens: Número de checagens da avaliação robusta por indivíduo

    :return: DataFrame com a fronteira eficiente. Se salvar_historico for True,
             retorna a tupla (DataFrame, objeto de resultado do pymoo).
    """

    dados = normalizar_dados_pre_sizing(dados, t)
    label_percentual_robustez = t.get("percentual_robustez")
    perc_robustez             = float(dados.get(label_percentual_robustez, 5.0))

    pop_size    = int(pop_size)
    n_gen       = int(n_gen)
    n_checagens = int(n_checagens)

    if verbose:
        print("[ReliaBridge][NSGA-II] Iniciando otimização de pré-dimensionamento.", flush=True)
        print(
                    "[ReliaBridge][NSGA-II] "
                    f"pop={pop_size}, gerações={n_gen}, robustez={perc_robustez:g}%, "
                    f"checagens={n_checagens}",
                    flush=True,
                )
        print(
                    "[ReliaBridge][NSGA-II] Limites: "
                    f"d={ds} cm, bw={bws} cm, h={hs} cm, esp_long={n_long} cm, esp_tab={n_tab} cm.",
                    flush=True,
                )

    # Instanciando o problema de otimização, construindo a estrutura exemplo
    problem_b = ProjetoOtimo(
                                bw_pista            = dados[f"{t['pista']}"],
                                l                   = dados[f"{t['entrada_comprimento']}"],
                                p_gk                = dados[f"{t['carga_permanente']} (kPa)"],
                                p_rodak             = dados[f"{t['carga_roda']} (kN)"],
                                p_qk                = dados[f"{t['carga_multidao']} (kPa)"],
                                a                   = dados[f"{t['distancia_eixos']} (m)"],
                                classe_carregamento = dados[f"{t['classe_carregamento']}"],
                                classe_madeira      = dados[f"{t['classe_madeira']}"],
                                classe_umidade      = dados[f"{t['classe_umidade']}"],
                                gamma_g             = dados[f"{t['gamma_g']}"],
                                gamma_q             = dados[f"{t['gamma_q']}"],
                                gamma_wf            = dados[f"{t['gamma_wf']}"],
                                gamma_wc            = dados[f"{t['gamma_wc']}"],
                                psi2                = dados[f"{t['psi2']}"],
                                phi                 = dados[f"{t['considerar_fluencia']}"],
                                densidade_long      = dados[f"{t['densidade_long']} (kg/m³)"],
                                densidade_tab       = dados[f"{t['densidade_tab']} (kg/m³)"],
                                f_mk_long           = dados[f"{t['f_mk']} (MPa)"],
                                f_vk_long           = dados[f"{t['f_vk']} (MPa)"],
                                e_modflex_long      = dados[f"{t['e_modflex']} (GPa)"],
                                f_mk_tab            = dados[f"{t['f_mk_tab']} (MPa)"],
                                d_min               = ds[0],
                                d_max               = ds[1],
                                bw_min              = bws[0],
                                bw_max              = bws[1],
                                h_min               = hs[0],
                                h_max               = hs[1],
                                n_min_long          = n_long[0],
                                n_max_long          = n_long[1],
                                n_min_tab           = n_tab[0],
                                n_max_tab           = n_tab[1],
                                n_checagens         = n_checagens,
                                perc_robustez       = perc_robustez,
                        )

    algorithm   = NSGA2(pop_size=pop_size, sampling=FloatRandomSampling(), crossover=SBX(prob=0.9, eta=15), mutation=PM(eta=20), eliminate_duplicates=True)
    termination = get_termination("n_gen", n_gen)
    res         = minimize(problem_b, algorithm, termination, seed=1, save_history=salvar_historico, verbose=verbose)
    F_nsga      = res.F
    G_nsga      = res.G
    X_nsga      = res.X

    if X_nsga is None or F_nsga is None or G_nsga is None:
        if verbose:
            print("[ReliaBridge][NSGA-II] Finalizado sem solução viável.", flush=True)
        raise ValueError(
            "Nenhuma solução viável foi encontrada pelo NSGA-II. "
            "Revise os limites geométricos, espaçamentos, carregamentos ou reduza o percentual de robustez."
        )

    if verbose:
        print(f"[ReliaBridge][NSGA-II] Finalizado com {len(X_nsga)} soluções retornadas.", flush=True)
    
    df_fronteira = pd.DataFrame(
                            {
                                "d [cm]": X_nsga[:, 0],
                                "bw [cm]": X_nsga[:, 1],
                                "h [cm]": X_nsga[:, 2],
                                "esp [cm]": X_nsga[:, 3],
                                "esp tab [cm]": X_nsga[:, 4],
                                "volume [m³]": F_nsga[:, 0],
                                "delta [-]": F_nsga[:, 1],
                                "flex lim beam [(Ms-Mr)/Mr]": G_nsga[:, 0],
                                "cis lim beam [(Vs-Vr)/Vr]": G_nsga[:, 1],
                                "delta lim beam [(ps-pr)/pr]": G_nsga[:, 2],
                                "flex lim deck [(Ms-Mr)/Mr]": G_nsga[:, 3],
                                "spacing beam": G_nsga[:, 4],
                                "spacing deck": G_nsga[:, 5],
                            }
                        )

    if salvar_historico:
        return df_fronteira, res

    return df_fronteira


def historico_hipervolume(res, ponto_referencia: np.ndarray | None = None) -> pd.DataFrame:
    """Calcula a evolução do hipervolume ao longo das gerações do NSGA-II.

    Exige que a otimização tenha sido executada com ``save_history=True``.

    Os objetivos são normalizados pelo ponto ideal e pelo nadir observados ao longo
    de toda a execução, de modo que o hipervolume resulte adimensional e comparável
    entre execuções de escalas diferentes. O ponto de referência padrão é
    (1,1; 1,1) no espaço normalizado, prática usual para problemas biobjetivo.

    :param res: Objeto de resultado retornado por ``pymoo.optimize.minimize``
    :param ponto_referencia: Ponto de referência no espaço normalizado. Se None, usa [1.1, 1.1]

    :return: DataFrame com colunas 'geracao', 'hipervolume', 'n_solucoes' e
             'n_avaliacoes'. Gerações sem nenhuma solução viável recebem
             hipervolume igual a zero.
    """

    if not getattr(res, "history", None):
        raise ValueError(
            "O resultado não possui histórico. Execute a otimização com save_history=True."
        )

    # Frente não dominada (apenas soluções viáveis) de cada geração
    frentes = []
    for algoritmo in res.history:
        opt = algoritmo.opt
        f_geracao = None
        if opt is not None and len(opt) > 0:
            viaveis = opt.get("feasible")
            f_todas = np.atleast_2d(np.asarray(opt.get("F"), dtype=float))
            if viaveis is not None:
                mascara = np.asarray(viaveis, dtype=bool).reshape(-1)
                f_todas = f_todas[mascara]
            if f_todas.size > 0:
                f_geracao = f_todas
        frentes.append(f_geracao)

    validas = [f for f in frentes if f is not None]
    if not validas:
        raise ValueError("Nenhuma geração apresentou solução viável; hipervolume indefinido.")

    empilhado = np.vstack(validas)
    ideal = empilhado.min(axis=0)
    nadir = empilhado.max(axis=0)
    amplitude = np.where(nadir - ideal > 0.0, nadir - ideal, 1.0)

    ref = np.array([1.1, 1.1]) if ponto_referencia is None else np.asarray(ponto_referencia, dtype=float)
    indicador = HV(ref_point=ref)

    linhas = []
    for i, (algoritmo, f_geracao) in enumerate(zip(res.history, frentes), start=1):
        if f_geracao is None:
            hv, n_sol = 0.0, 0
        else:
            f_norm = (f_geracao - ideal) / amplitude
            hv, n_sol = float(indicador(f_norm)), int(f_geracao.shape[0])
        linhas.append(
            {
                "geracao": i,
                "hipervolume": hv,
                "n_solucoes": n_sol,
                "n_avaliacoes": int(getattr(algoritmo.evaluator, "n_eval", 0)),
            }
        )

    return pd.DataFrame(linhas)


def geracao_estabilizacao_hipervolume(historico: pd.DataFrame, tolerancia: float = 0.01) -> int:
    """Primeira geração a partir da qual o hipervolume permanece dentro de `tolerancia` do valor final.

    Leitura objetiva de "a partir daqui o algoritmo não melhora mais". Se o valor
    resultante for próximo do total de gerações, o número de gerações adotado está
    curto; se for muito baixo, há esforço computacional sobrando.

    :param historico: DataFrame retornado por historico_hipervolume
    :param tolerancia: Tolerância relativa ao hipervolume final (0.01 = 1%)
    """

    hv = historico["hipervolume"].to_numpy(dtype=float)
    if hv.size == 0 or hv[-1] <= 0.0:
        return -1

    acima = hv >= hv[-1] * (1.0 - tolerancia)
    for i in range(acima.size):
        if acima[i:].all():
            return int(historico["geracao"].iloc[i])

    return int(historico["geracao"].iloc[-1])


def estatistica_descritiva_variaveis(
    df_resultados: pd.DataFrame,
    colunas: list[str],
    labels: list[str],
    nomes_colunas: dict | None = None,
) -> pd.DataFrame:
    """Resume as variáveis de projeto presentes na fronteira eficiente.

    Complementa o boxplot com os valores numéricos correspondentes.

    :param df_resultados: DataFrame com as soluções da fronteira
    :param colunas: Colunas do DataFrame a resumir
    :param labels: Rótulos legíveis, na mesma ordem de `colunas`
    :param nomes_colunas: Tradução dos cabeçalhos da tabela de saída
    """

    padrao = {
        "variavel": "Variável", "n": "N", "media": "Média", "desvio": "Desvio padrão",
        "cv": "CV (%)", "minimo": "Mínimo", "q1": "1º quartil", "mediana": "Mediana",
        "q3": "3º quartil", "maximo": "Máximo", "amplitude": "Amplitude",
    }
    nomes = {**padrao, **(nomes_colunas or {})}

    linhas = []
    for coluna, label in zip(colunas, labels):
        if coluna not in df_resultados.columns:
            continue
        serie = pd.to_numeric(df_resultados[coluna], errors="coerce").dropna()
        if serie.empty:
            continue
        media = float(serie.mean())
        desvio = float(serie.std(ddof=1)) if serie.size > 1 else 0.0
        linhas.append(
            {
                nomes["variavel"]: label,
                nomes["n"]: int(serie.size),
                nomes["media"]: round(media, 2),
                nomes["desvio"]: round(desvio, 2),
                nomes["cv"]: round(100.0 * desvio / media, 2) if abs(media) > 1e-12 else float("nan"),
                nomes["minimo"]: round(float(serie.min()), 2),
                nomes["q1"]: round(float(serie.quantile(0.25)), 2),
                nomes["mediana"]: round(float(serie.median()), 2),
                nomes["q3"]: round(float(serie.quantile(0.75)), 2),
                nomes["maximo"]: round(float(serie.max()), 2),
                nomes["amplitude"]: round(float(serie.max() - serie.min()), 2),
            }
        )

    return pd.DataFrame(linhas)


def plot_convergencia_hipervolume(
    historicos: dict[str, pd.DataFrame],
    label_x: str = "Geração",
    label_y: str = "Hipervolume normalizado [-]",
) -> Figure:
    """Plota a evolução do hipervolume ao longo das gerações.

    :param historicos: Dicionário {rótulo da série: DataFrame de historico_hipervolume}.
                       Permite sobrepor várias execuções (ex.: Ponte 01 e Ponte 02,
                       ou diferentes níveis de robustez) na mesma figura.
    :param label_x: Rótulo do eixo horizontal
    :param label_y: Rótulo do eixo vertical
    """

    # Série única usa a cor primária; múltiplas séries se distinguem pelo traço,
    # mantendo a mesma cor, conforme o padrão visual do conjunto de figuras.
    estilos = ['-', '--', '-.', ':', (0, (3, 1, 1, 1))]

    fig, ax = plt.subplots(figsize=(FIG_PADRAO[0] * CM_POL, FIG_PADRAO[1] * CM_POL))

    for i, (rotulo, df) in enumerate(historicos.items()):
        ax.plot(
            df["geracao"].to_numpy(),
            df["hipervolume"].to_numpy(),
            linestyle=estilos[i % len(estilos)],
            color=COR_PRIMARIA,
            linewidth=1.4,
            label=rotulo,
        )

    _aplicar_estilo_eixos(ax, label_x, label_y)

    if len(historicos) > 1:
        ax.legend(fontsize=TAM_EIXO - 1, frameon=False)

    fig.tight_layout()
    return fig


def funcoes_sobol(entrada, params) -> np.ndarray:
    """Modelo chamado pela UQpy para estimar Sobol das restricoes."""

    d, bw, h, n_long, n_tab = np.asarray(entrada, dtype=float).reshape(-1)[:5]
    projeto = params["projeto"]

    try:
        _, g, *_ = projeto.calcular_objetivos_restricoes_otimizacao(d, bw, h, n_long, n_tab)
        return np.nan_to_num(np.array(g, dtype=float), nan=1.0e6, posinf=1.0e6, neginf=-1.0e6)
    except Exception:
        return np.full(6, 1.0e6, dtype=float)


def chamar_sobol(
                    dados: dict,
                    ds: list,
                    bws: list,
                    hs: list,
                    n_long: list,
                    n_tab: list,
                    t: dict,
                    n_samples: int = 64,
                    verbose: bool = True,
                ) -> dict:
    """Executa analise de sensibilidade Sobol das restricoes do pre-dimensionamento."""

    dados = normalizar_dados_pre_sizing(dados, t)
    n_samples = max(int(n_samples), 2)
    params = {
                    "dados": dados,
                    "ds": [float(ds[0]), float(ds[1])],
                    "bws": [float(bws[0]), float(bws[1])],
                    "hs": [float(hs[0]), float(hs[1])],
                    "n_long": [float(n_long[0]), float(n_long[1])],
                    "n_tab": [float(n_tab[0]), float(n_tab[1])],
                    "t": t,
                }
    params["projeto"] = _criar_projeto_otimo_pre_sizing(
                                                            dados,
                                                            params["ds"],
                                                            params["bws"],
                                                            params["hs"],
                                                            params["n_long"],
                                                            params["n_tab"],
                                                            t,
                                                            n_checagens=1,
                                                            perc_robustez=0.0,
                                                        )

    if verbose:
        print("[ReliaBridge][Sobol] Iniciando analise de sensibilidade.", flush=True)
        print(
            "[ReliaBridge][Sobol] "
            f"amostras={n_samples}, variaveis=5, saidas=6 restricoes.",
            flush=True,
        )

    model = PythonModel(
                            model_script="madeiras.py",
                            model_object_name="funcoes_sobol",
                            var_names=["d_cm", "bw_cm", "h_cm", "esp_long_cm", "esp_tab_cm"],
                            delete_files=True,
                            params=params,
                        )

    runmodel_obj = RunModel(model=model)
    dist_object = JointIndependent(
        [
            Uniform(params["ds"][0], params["ds"][1] - params["ds"][0]),
            Uniform(params["bws"][0], params["bws"][1] - params["bws"][0]),
            Uniform(params["hs"][0], params["hs"][1] - params["hs"][0]),
            Uniform(params["n_long"][0], params["n_long"][1] - params["n_long"][0]),
            Uniform(params["n_tab"][0], params["n_tab"][1] - params["n_tab"][0]),
        ]
    )

    sobol = SobolSensitivity(runmodel_obj, dist_object, random_state=1)
    sobol.run(n_samples=n_samples, estimate_second_order=False)

    variaveis = ["d_cm", "bw_cm", "h_cm", "esp_long_cm", "esp_tab_cm"]
    restricoes = [
        "g_flexao_longarina",
        "g_cisalhamento_longarina",
        "g_flecha_longarina",
        "g_flexao_tabuleiro",
        "g_esp_longarina",
        "g_esp_tabuleiro",
    ]

    def indices_para_df(indices: np.ndarray) -> pd.DataFrame:
        valores = np.nan_to_num(np.asarray(indices, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
        df = pd.DataFrame(valores, columns=restricoes)
        df.insert(0, "variavel", variaveis)
        return df

    resultado = {
        "total_order": indices_para_df(sobol.total_order_indices),
        "n_samples": n_samples,
    }

    if verbose:
        print("[ReliaBridge][Sobol] Analise finalizada.", flush=True)

    return resultado
    
if __name__ == "__main__":
    df = pd.read_excel("beam_data_01.xlsx")
    df = df.to_dict(orient="records")
    df = df[0]

    t = textos_pre_sizing_l()["pt"]
    dados = normalizar_dados_pre_sizing(df, t)
    ds       = [30, 150]
    bws      = [5, 60]
    hs       = [5, 60]
    n_p_long = [30, 200]
    n_p_tab  = [5, 60]

    problem_b = ProjetoOtimo(
                                bw_pista=dados[t["pista"]],
                                l=dados[t["entrada_comprimento"]],
                                p_gk=dados[f"{t['carga_permanente']} (kPa)"],
                                p_rodak=dados[f"{t['carga_roda']} (kN)"],
                                p_qk=dados[f"{t['carga_multidao']} (kPa)"],
                                a=dados[f"{t['distancia_eixos']} (m)"],
                                classe_carregamento=dados[t["classe_carregamento"]],
                                classe_madeira=dados[t["classe_madeira"]],
                                classe_umidade=dados[t["classe_umidade"]],
                                gamma_g=dados[t["gamma_g"]],
                                gamma_q=dados[t["gamma_q"]],
                                gamma_wf=dados[t["gamma_wf"]],
                                gamma_wc=dados[t["gamma_wc"]],
                                psi2=dados[t["psi2"]],
                                phi=dados[t["considerar_fluencia"]],
                                densidade_long=dados[f"{t['densidade_long']} (kg/m³)"],
                                densidade_tab=dados[f"{t['densidade_tab']} (kg/m³)"],
                                f_mk_long=dados[f"{t['f_mk']} (MPa)"],
                                f_vk_long=dados[f"{t['f_vk']} (MPa)"],
                                e_modflex_long=dados[f"{t['e_modflex']} (GPa)"],
                                f_mk_tab=dados[f"{t['f_mk_tab']} (MPa)"],
                                d_min=ds[0],
                                d_max=ds[1],
                                bw_min=bws[0],
                                bw_max=bws[1],
                                h_min=hs[0],
                                h_max=hs[1],
                                n_min_long=n_p_long[0],
                                n_max_long=n_p_long[1],
                                n_min_tab=n_p_tab[0],
                                n_max_tab=n_p_tab[1],
                                perc_robustez=dados[t["percentual_robustez"]],
                            )

    # 2) Define uma solução manual
    x_manual = np.array([[55., 15., 30., 120.0, 10.]])   # d, bw, h, n_long, n_tab

    # 3) Avalia
    out = problem_b.evaluate(x_manual, return_values_of=["F", "G"])

    # 4) Imprime resultados
    f = out[0]
    g = out[1]
    print(f, g)
