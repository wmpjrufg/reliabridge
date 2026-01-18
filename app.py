import streamlit as st

st.set_page_config(page_title="ReliaBridge", layout="wide")
st.markdown(
                """
                <style>
                /* ==============================
                SCROLLBARS (WebKit/Chromium)
                ============================== */

                /* Global (quando houver) */
                ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }
                ::-webkit-scrollbar-track { background: #f0f0f0 !important; border-radius: 10px !important; }
                ::-webkit-scrollbar-thumb {
                    background-color: #9e9e9e !important;
                    border-radius: 10px !important;
                    border: 3px solid #f0f0f0 !important;
                }
                ::-webkit-scrollbar-thumb:hover { background-color: #616161 !important; }

                /* Main containers do Streamlit (onde costuma rolar) */
                .stApp ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }
                section.main ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }
                [data-testid="stAppViewContainer"] ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }
                [data-testid="stMain"] ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }

                /* Dataframes / tabelas (quase sempre o “culpado”) */
                [data-testid="stDataFrame"] ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }
                [data-testid="stTable"] ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }

                /* Expanders e outros containers roláveis */
                [data-testid="stExpander"] ::-webkit-scrollbar { width: 20px !important; height: 20px !important; }

                /* Firefox (fallback) */
                * { scrollbar-width: auto; scrollbar-color: #9e9e9e #f0f0f0; }

                </style>
                """,
                unsafe_allow_html=True
            )



# Idioma global: default pt, mas quem muda é a Home
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"
lang = st.session_state["lang"]

titulos_menu = {
                    "pt": {
                        "home": "Início",
                        "longarina": "Pré-dimensionamento",
                        "design": "Projeto dos Elementos",
                        # "confiabilidade": "Confiabilidade"
                    },
                    "en": {
                        "home": "Home",
                        "longarina": "Pre-sizing",
                        "design": "Elements Design",
                        # "confiabilidade": "Reliability"
                    },
                }

home_page = st.Page("pages/home.py", title=titulos_menu[lang]["home"], icon="🏠", default=True)
longarina_page = st.Page("pages/pre_sizing.py", title=titulos_menu[lang]["longarina"], icon="🏗️")
design_page = st.Page("pages/design.py", title=titulos_menu[lang]["design"], icon="🛠️")
# reliability_page = st.Page("pages/reliability.py", title=titulos_menu[lang]["confiabilidade"], icon="📊")

pg = st.navigation([home_page, longarina_page, design_page])
pg.run()
