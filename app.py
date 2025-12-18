import streamlit as st

# st.title("ReliaBridge App")
# st.write("This framework checks and designs simple supported bridges using reliability analysis and design principles.")
# -------------------------------------------------
# CONFIGURAÇÃO GLOBAL (primeira instrução executável)
# -------------------------------------------------
st.set_page_config(
    page_title="App de Continhas",
    layout="centered",
)

# -------------------------------------------------
# INICIALIZAÇÃO DO ESTADO DE SESSÃO
# -------------------------------------------------
if "pagina" not in st.session_state:
    st.session_state.pagina = "Home"

if "a" not in st.session_state:
    st.session_state.a = 0.0

if "b" not in st.session_state:
    st.session_state.b = 0.0

if "x" not in st.session_state:
    st.session_state.x = 0.0

if "y" not in st.session_state:
    st.session_state.y = 0.0

# -------------------------------------------------
# SIDEBAR — NAVEGAÇÃO CONTROLADA
# -------------------------------------------------
st.sidebar.title("Navegação")

opcoes_paginas = ["Home", "Soma", "Multiplicação"]

st.session_state.pagina = st.sidebar.radio(
    "Selecione a página",
    opcoes_paginas,
    index=opcoes_paginas.index(st.session_state.pagina),
)

# -------------------------------------------------
# ROTEAMENTO DE PÁGINAS
# -------------------------------------------------
def pagina_home():
    st.title("Home — App de Continhas")
    st.write(
        "Este aplicativo demonstra navegação com gerenciamento de sessão. "
        "Cada usuário possui estado isolado, mesmo com acessos simultâneos."
    )

def pagina_soma():
    st.title("Página — Soma")

    st.session_state.a = st.number_input(
        "Valor A",
        value=st.session_state.a,
        step=1.0,
        key="input_a",
    )

    st.session_state.b = st.number_input(
        "Valor B",
        value=st.session_state.b,
        step=1.0,
        key="input_b",
    )

    if st.button("Calcular soma", type="primary"):
        resultado = st.session_state.a + st.session_state.b
        st.success(f"Resultado: {st.session_state.a} + {st.session_state.b} = {resultado}")

def pagina_multiplicacao():
    st.title("Página — Multiplicação")

    st.session_state.x = st.number_input(
        "Valor X",
        value=st.session_state.x,
        step=1.0,
        key="input_x",
    )

    st.session_state.y = st.number_input(
        "Valor Y",
        value=st.session_state.y,
        step=1.0,
        key="input_y",
    )

    if st.button("Calcular multiplicação", type="primary"):
        resultado = st.session_state.x * st.session_state.y
        st.success(f"Resultado: {st.session_state.x} × {st.session_state.y} = {resultado}")

# -------------------------------------------------
# EXECUÇÃO CONFORME ESTADO ATUAL
# -------------------------------------------------
if st.session_state.pagina == "Home":
    pagina_home()
elif st.session_state.pagina == "Soma":
    pagina_soma()
elif st.session_state.pagina == "Multiplicação":
    pagina_multiplicacao()

