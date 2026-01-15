import streamlit as st

# Configuração da página (Sempre a primeira linha)
st.set_page_config(page_title="ReliaBridge", layout="wide")

# Inicializa o estado do idioma se não existir
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

# Cria o seletor na barra lateral (Aparecerá em todas as páginas)
idioma_selecionado = st.sidebar.selectbox("Language / Idioma", ["Português", "English"], index=0 if st.session_state["lang"] == "pt" else 1)
if idioma_selecionado == "Português":
    st.session_state["lang"] = "pt"
else:
    st.session_state["lang"] = "en"
lang = st.session_state["lang"]

# Dicionário com os Títulos do Menu
titulos_menu = {
                    "pt": {
                            "home": "Início",
                            "longarina": "Pré-dimensionamento da Longarina",
                            "design": "Projeto da Longarina"
                          },
                    "en": {
                            "home": "Home",
                            "longarina": "Pre-sizing of Stringer",
                            "design": "Stringer Design"
                          }
                }

# Definição das páginas usando os títulos dinâmicos
home_page = st.Page("pages/home.py", title=titulos_menu[lang]["home"], icon="🏠", default=True)
longarina_page = st.Page("pages/pre_sizing.py", title=titulos_menu[lang]["longarina"], icon="🏗️")
design_page = st.Page("pages/design.py", title=titulos_menu[lang]["design"], icon="🛠️")

# Executa a navegação
pg = st.navigation([home_page, longarina_page, design_page])
pg.run()
