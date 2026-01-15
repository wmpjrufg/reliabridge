import streamlit as st

st.set_page_config(page_title="ReliaBridge", layout="wide")

# Idioma global: default pt, mas quem muda é a Home
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

lang = st.session_state["lang"]

titulos_menu = {
                    "pt": {
                        "home": "Início",
                        "longarina": "Pré-dimensionamento da Longarina",
                        "design": "Projeto da Longarina",
                    },
                    "en": {
                        "home": "Home",
                        "longarina": "Pre-sizing of Stringer",
                        "design": "Stringer Design",
                    },
                }

home_page = st.Page("pages/home.py", title=titulos_menu[lang]["home"], icon="🏠", default=True)
longarina_page = st.Page("pages/pre_sizing.py", title=titulos_menu[lang]["longarina"], icon="🏗️")
design_page = st.Page("pages/design.py", title=titulos_menu[lang]["design"], icon="🛠️")

pg = st.navigation([home_page, longarina_page, design_page])
pg.run()
