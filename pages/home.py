import streamlit as st
    
if "lang" not in st.session_state:
    st.session_state["lang"] = "pt"

# Textos (pt/en) centralizados
textos = {
            "pt": {
                        "lang_label": "Idioma/Language",
                        "lang_opts": ["Português", "English"],
                        "title": "Bem-vindo",
                        "logo_ufcat": "imgs/ufcat.jpeg",
                        "logo_ufscar": "imgs/ufscar.jpeg",
                        "body": (   
                                    "Esta plataforma realiza análises estruturais em pontes de madeira, seguindo rigorosamente as "
                                    "especificações da **NBR 7190:2022 - Projeto de Estruturas de Madeira**. "
                                    "Esta plataforma foi realizada pela equipe composta por: Wanderlei M. Pereira Junior, "
                                    "Priscilla Silva Teotônio, Pedro Henrique Gomes Duarte, Wellington A. da Silva, André Luís Christoforo, "
                                    "Matheus Henrique Morato de Moraes, João Paulo M. Lopes, Enzo e Maria José. "
                                    "Ela permite avaliar a segurança e o desempenho de longarinas e vigas de madeira, calculando propriedades "
                                    "geométricas de seções retangulares e circulares, determinando esforços solicitantes (momentos fletores, "
                                    "cortantes e reações) considerando cargas permanentes e variáveis, e aplicando o coeficiente de impacto "
                                    "vertical conforme a NBR 7188:2024. O software realiza verificações de estado limite último, incluindo "
                                    "flexão oblíqua e cisalhamento, e de estado limite de serviço, como flechas máximas. Além disso, incorpora "
                                    "uma análise de confiabilidade através do Método FORM para estimar o índice de confiabilidade e a "
                                    "probabilidade de falha, considerando as incertezas inerentes aos materiais e cargas, sendo uma ferramenta "
                                    "essencial para o projeto e verificação de pontes em madeira no contexto das normas técnicas brasileiras."
                                ),
                    },
            "en": {
                        "lang_label": "Language/Idioma",
                        "lang_opts": ["Português", "English"],
                        "title": "Welcome",
                        "logo_ufcat": "imgs/ufcat.jpeg",
                        "logo_ufscar": "imgs/ufscar.jpeg",
                        "body": (
                                    "This platform performs structural analyses of timber bridges, rigorously following the specifications of "
                                    "**NBR 7190:2022 - Design of Timber Structures**. This platform was developed by the team: "
                                    "Wanderlei M. Pereira Junior, Priscilla Silva Teotônio, Pedro Henrique Gomes Duarte, Wellington A. da Silva, "
                                    "André Luís Christoforo, Matheus Henrique Morato de Moraes, João Paulo M. Lopes, Enzo, and Maria José. "
                                    "It enables the assessment of safety and performance of stringers and beams by calculating geometric properties"
                                    "of rectangular and circular cross-sections, determining internal forces (bending moments, shear forces, "
                                    "and reactions) considering permanent and variable loads, and applying the vertical impact coefficient in "
                                    "accordance with NBR 7188:2024. The software performs ultimate limit state verifications, including oblique "
                                    "bending and shear, and serviceability limit state checks, such as maximum deflections. Furthermore, "
                                    "it incorporates a reliability analysis using the FORM method to estimate the reliability index and probability "
                                    "of failure, accounting for inherent uncertainties in materials and loads, making it an essential tool for "
                                    "the design and verification of timber bridges within the context of Brazilian technical standards."
                                ),
                    },
        }

lang = st.session_state["lang"]
t = textos.get(lang, textos["pt"])
idx = 0 if lang == "pt" else 1

with st.sidebar:
    escolha = st.selectbox(t["lang_label"], t["lang_opts"], index=idx)
    novo_lang = "pt" if escolha == "Português" else "en"
    if novo_lang != st.session_state["lang"]:
        st.session_state["lang"] = novo_lang
        st.rerun()

    


# --- Conteúdo ---
try:
    col_logo1, col_logo2 = st.columns([1, 1])

    with col_logo1:
        st.image(t["logo_ufcat"], width=200)

    with col_logo2:
        st.image(t["logo_ufscar"], width=200)
except:
    st.warning("Arquivo de imagem não encontrado. Verifique a pasta 'images/'.")
    
st.title(t["title"])
st.write(t["body"])