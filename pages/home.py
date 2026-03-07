import streamlit as st

# -----------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------
st.set_page_config(
                        page_title="ReliaBridge",
                        page_icon="🌉",
                        layout="wide"
                    )

# -----------------------------------------------------------
# ESTADO DA LINGUAGEM
# -----------------------------------------------------------
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

# -----------------------------------------------------------
# TEXTOS
# -----------------------------------------------------------
textos = {

    "pt": {

        "lang_label": "Idioma / Language",
        "lang_opts": ["Português", "English"],

        "title": "Bem-vindo",
        "subtitle": "Plataforma para análise estrutural de pontes de madeira",

        "logo_ufcat": "imgs/ufcat.png",
        "logo_ufscar": "imgs/ufscar.png",
        "logo_pucgo": "imgs/pucgo.png",

        "erro_imagem": "Arquivo de imagem não encontrado.",

        "body": """
        <div style="text-align: justify; font-size:17px; line-height:1.8">

        <p>
        Esta plataforma realiza análises estruturais em <b>pontes de madeira</b>,
        seguindo rigorosamente as especificações da
        <b>NBR 7190:2022 – Projeto de Estruturas de Madeira</b>.
        </p>

        <p>
        A ferramenta foi desenvolvida por uma equipe de pesquisadores composta por
        <b>Prof. Wanderlei M. Pereira Junior</b>, <b>Priscilla Silva Teotônio</b>,
        <b>Pedro Henrique Gomes Duarte</b>, <b>Prof. Wellington A. da Silva</b>,
        <b>Prof. André Luís Christoforo</b>, <b>Matheus Henrique Morato de Moraes</b>,
        <b>João Paulo M. Lopes</b>, <b>Enzo Moura Rezende</b> e <b>Profa. Maria José Pereira Dantas</b>.
        </p>

        <p>
        O sistema permite avaliar a <b>segurança</b> e o <b>desempenho estrutural</b> de longarinas de madeira, 
        realizando o cálculo das propriedades geométricas de seções retangulares e circulares e a determinação dos esforços solicitantes, 
        como <b>momentos fletores, esforços cortantes e reações de apoio</b>, considerando <b>cargas permanentes e variáveis</b>. 
        Além disso, a plataforma incorpora o coeficiente de impacto vertical conforme a <b>NBR 7188:2024</b> e executa verificações de 
        <b>Estado Limite Último (ELU)</b> e <b>Estado Limite de Serviço (ELS)</b>.
        </p>

        <p>
        O software permite a seleção das seções estruturais mais adequadas para a ponte por meio de uma análise de <b>otimização multiobjetivo</b>, 
        cujo propósito é <b>minimizar o volume de madeira</b> utilizado e, simultaneamente, <b>maximizar o desempenho estrutural</b> em termos de flecha, 
        respeitando os limites estabelecidos pelas normas técnicas. O processo de otimização é conduzido pelo <b>algoritmo NSGA-II</b>, um método evolutivo 
        amplamente empregado para a resolução de problemas de otimização multiobjetivo, capaz de gerar um conjunto de soluções ótimas conhecidas como 
        <b>fronteira de Pareto</b>. Para a execução da análise, o usuário deve fornecer as propriedades geométricas e mecânicas da madeira 
        empregada nas longarinas e no tabuleiro, as cargas atuantes na estrutura, bem como os limites admissíveis das variáveis de projeto.
        </p>
        
        <p>
        Dessa forma, a plataforma se consolida como uma ferramenta
        computacional relevante para o <b>projeto, análise e verificação
        de pontes de madeira</b>, alinhada às normas técnicas brasileiras
        e voltada ao suporte de decisões em engenharia estrutural.
        </p>

        </div>
        """
    },

    "en": {

        "lang_label": "Language / Idioma",
        "lang_opts": ["Português", "English"],

        "title": "Welcome",
        "subtitle": "Platform for structural analysis of timber bridges",

        "logo_ufcat": "imgs/ufcat.png",
        "logo_ufscar": "imgs/ufscar.png",
        "logo_pucgo": "imgs/pucgo.png",

        "erro_imagem": "Image file not found.",

        "body": """
        <div style="text-align: justify; font-size:17px; line-height:1.8">

        <p>
        This platform performs structural analyses of <b>timber bridges</b>,
        rigorously following the requirements of
        <b>NBR 7190:2022 – Design of Timber Structures</b>.
        </p>

        <p>
        The platform was developed by a research team composed of
        <b>Prof. Wanderlei M. Pereira Junior</b>, <b>Priscilla Silva Teotônio</b>,
        <b>Pedro Henrique Gomes Duarte</b>, <b>Prof. Wellington A. da Silva</b>,
        <b>Prof. André Luís Christoforo</b>, <b>Matheus Henrique Morato de Moraes</b>,
        <b>João Paulo M. Lopes</b>, <b>Enzo Moura Rezende</b> and <b>Profa. Maria José Pereira Dantas</b>.
        </p>

        <p>
        The system enables the evaluation of the <b>safety</b> and <b>structural performance</b> of timber stringers by calculating the geometric properties of rectangular and circular cross-sections and determining internal forces such as <b>bending moments, shear forces, and support reactions</b>, while considering <b>permanent and variable loads</b>. In addition, the platform incorporates the vertical impact coefficient according to <b>NBR 7188:2024</b> and performs <b>Ultimate Limit State (ULS)</b> and <b>Serviceability Limit State (SLS)</b> verifications.
        </p>

        <p>
        The software enables the selection of the most suitable structural cross-sections for the bridge through a <b>multi-objective optimization analysis</b>, 
        whose goal is to <b>minimize the volume of timber used</b> while <b>maximizing structural performance</b> in terms of deflection, within the limits established by technical standards. 
        The optimization process is performed using the <b>NSGA-II algorithm</b>, an evolutionary method widely applied to solve multi-objective 
        optimization problems, capable of generating a set of optimal solutions known as the <b>Pareto frontier</b>. 
        To perform the analysis, the user must provide the geometric and mechanical properties of the timber used in the stringers and deck, the applied loads, and the admissible bounds of the design variables.
        </p>

        <p>
        Therefore, the platform represents a relevant computational
        tool for the <b>design, analysis and verification of timber
        bridges</b> aligned with Brazilian technical standards.
        </p>

        </div>
        """
    }
}

# -----------------------------------------------------------
# IDIOMA ATUAL
# -----------------------------------------------------------
lang = st.session_state["lang"]
t = textos.get(lang, textos["pt"])
idx = 0 if lang == "pt" else 1

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:

    escolha = st.selectbox(
        t["lang_label"],
        t["lang_opts"],
        index=idx
    )

    novo_lang = "pt" if escolha == "Português" else "en"

    if novo_lang != st.session_state["lang"]:
        st.session_state["lang"] = novo_lang
        st.rerun()

# -----------------------------------------------------------
# LOGOS
# -----------------------------------------------------------
try:

    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        st.image(t["logo_ufcat"], width=160)

    with col2:
        st.image(t["logo_ufscar"], width=160)

    with col3:
        st.image(t["logo_pucgo"], width=160)

except Exception:
    st.warning(t["erro_imagem"])

# -----------------------------------------------------------
# TÍTULO
# -----------------------------------------------------------
st.markdown(
    f"""
    <h1 style="text-align:center;margin-bottom:0">
    {t["title"]}
    </h1>

    <h4 style="text-align:center;color:gray;margin-top:0">
    {t["subtitle"]}
    </h4>
    """,
    unsafe_allow_html=True
)

st.divider()

# -----------------------------------------------------------
# TEXTO PRINCIPAL
# -----------------------------------------------------------
st.markdown(t["body"], unsafe_allow_html=True)