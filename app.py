import streamlit as st

st.set_page_config(page_title="ReliaBridge", layout="wide")

# Idioma global: default pt, mas quem muda é a Home
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]

titulos_menu = {
                    "pt": {
                        "home": "Início",
                        "longarina": "Pré-dimensionamento",
                        # "design": "Projeto da Longarina",
                        # "confiabilidade": "Confiabilidade"
                    },
                    "en": {
                        "home": "Home",
                        "longarina": "Pre-sizing",
                        # "design": "Stringer Design",
                        # "confiabilidade": "Reliability"
                    },
                }

home_page = st.Page("pages/home.py", title=titulos_menu[lang]["home"], icon="🏠", default=True)
longarina_page = st.Page("pages/pre_sizing.py", title=titulos_menu[lang]["longarina"], icon="🏗️")
# design_page = st.Page("pages/design.py", title=titulos_menu[lang]["design"], icon="🛠️")
# reliability_page = st.Page("pages/reliability.py", title=titulos_menu[lang]["confiabilidade"], icon="📊")

pg = st.navigation([home_page, longarina_page])
pg.run()
