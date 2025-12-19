import streamlit as st

st.set_page_config(page_title="ReliaBridge", layout="wide")
home_page = st.Page("pages/home.py", title="Início", icon="🏠", default=True)
longarina_page = st.Page("pages/longarina_projeto.py", title="Projeto Longarina", icon="🏗️")
pg = st.navigation([home_page, longarina_page])
pg.run()
