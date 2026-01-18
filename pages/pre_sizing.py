# Tela de pré-dimensionamento com NSGA-II
import io
import json
import hashlib
import zipfile

import streamlit as st
import numpy as np
import pandas as pd

from madeiras import textos_pre_sizing_l, montar_excel, montar_excel_df, chamando_nsga2, fronteira_pareto


# -----------------------------
# Helpers: assinatura + invalidação
# -----------------------------
def make_signature(d: dict) -> str:
    payload = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(payload).hexdigest()

def invalidate_results():
    st.session_state["has_results"] = False
    for k in ["df_resultados", "excel_bytes_resultados", "fig_png", "zip_bytes", "sig_last"]:
        st.session_state.pop(k, None)

if "has_results" not in st.session_state:
    st.session_state["has_results"] = False


# -----------------------------
# UI text
# -----------------------------
lang = st.session_state.get("lang", "pt")
textos = textos_pre_sizing_l()
t = textos.get(lang, textos["pt"])

st.header(t["titulo"])
st.subheader(t["pre"])


# ============================================================
# 1) FORM
# ============================================================
with st.form("form_geometria", clear_on_submit=False):

    l = st.number_input(t["entrada_comprimento"], min_value=3.0, key="l")
    larg = st.number_input(t["pista"], min_value=0.5, key="larg")

    tipo_secao_longarina = st.selectbox(
        t["entrada_tipo_secao_longarina"],
        t["tipo_secao_longarina"],
        key="tipo_secao_longarina"
    )
    if tipo_secao_longarina.lower() == "circular":
        d_cm_min = st.number_input(t["diametro_minimo"], key="d_cm_min")
        d_cm_max = st.number_input(t["diametro_maximo"], key="d_cm_max")
    else:
        d_cm_min, d_cm_max = None, None

    tipo_secao_tabuleiro = st.selectbox(
        t["tipo_secao_tabuleiro"],
        t["tipo_secao_tabuleiro_opcoes"],
        key="tipo_secao_tabuleiro"
    )
    if tipo_secao_tabuleiro.lower() == "retangular":
        esp_min = st.number_input(t["espaçamento_entre_longarinas_min"], key="esp_min")
        esp_max = st.number_input(t["espaçamento_entre_longarinas_max"], key="esp_max")
        bw_min  = st.number_input(t["largura_viga_tabuleiro_min"], key="bw_min")
        bw_max  = st.number_input(t["largura_viga_tabuleiro_max"], key="bw_max")
        h_min   = st.number_input(t["altura_viga_tabuleiro_min"], key="h_min")
        h_max   = st.number_input(t["altura_viga_tabuleiro_max"], key="h_max")
    else:
        esp_min = esp_max = bw_min = bw_max = h_min = h_max = None

    p_gk = st.number_input(t["carga_permanente"], key="p_gk")
    p_rodak = st.number_input(t["carga_roda"], key="p_rodak")
    p_qk = st.number_input(t["carga_multidao"], key="p_qk")
    a = st.number_input(t["distancia_eixos"], key="a")

    classe_carregamento_raw = st.selectbox(
        t["classe_carregamento"],
        t["classe_carregamento_opcoes"],
        key="classe_carregamento"
    )
    classe_madeira_raw = st.selectbox(
        t["classe_madeira"],
        t["classe_madeira_opcoes"],
        key="classe_madeira"
    )
    classe_umidade = st.selectbox(
        t["classe_umidade"],
        [1, 2, 3, 4],
        key="classe_umidade"
    )

    gamma_g = st.number_input(t["gamma_g"], step=0.1, key="gamma_g")
    gamma_q = st.number_input(t["gamma_q"], step=0.1, key="gamma_q")
    gamma_w = st.number_input(t["gamma_w"], step=0.1, key="gamma_w")
    psi_2   = st.number_input(t["psi2"], step=0.1, key="psi_2")
    fluencia = st.number_input(t["considerar_fluencia"], step=0.1, key="phi")

    densidade_long = st.number_input(t["densidade_long"], step=1.0, key="densidade_long")
    f_mk_mpa = st.number_input(t["f_mk"], step=0.1, key="f_mk_mpa")
    f_vk_mpa = st.number_input(t["f_vk"], step=0.1, key="f_vk_mpa")
    e_modflex_gpa = st.number_input(t["e_modflex"], step=0.1, key="e_modflex_gpa")

    densidade_tab = st.number_input(t["densidade_tab"], step=1.0, key="densidade_tab")
    f_mk_mpa_tab  = st.number_input(t["f_mk_tab"], step=0.1, key="f_mk_mpa_tab")

    submitted_design = st.form_submit_button(t["gerador_desempenho"])


# ============================================================
# 2) DADOS DO PROJETO (sempre disponíveis)
# ============================================================
if lang == "pt":
    dados_projeto = {
        "l (cm)": l,
        "b_wpista (cm)": larg,
        "tipo_secao_longarina": tipo_secao_longarina,
        "tipo_secao_tabuleiro": tipo_secao_tabuleiro,
        "p_gk (kN/m²)": p_gk,
        "p_rodak (kN)": p_rodak,
        "p_qk (kN/m²)": p_qk,
        "a (m)": a,
        "classe_carregamento": classe_carregamento_raw.lower(),
        "classe_madeira": classe_madeira_raw.lower(),
        "classe_umidade": classe_umidade,
        "gamma_g": gamma_g,
        "gamma_q": gamma_q,
        "gamma_w": gamma_w,
        "psi_2": psi_2,
        "phi": fluencia,
        "densidade longarina (kg/m³)": densidade_long,
        "resistência característica à flexão longarina (MPa)": f_mk_mpa,
        "resistência característica ao cisalhamento longarina (MPa)": f_vk_mpa,
        "módulo de elasticidade à flexão longarina (GPa)": e_modflex_gpa,
        "densidade tabuleiro (kg/m³)": densidade_tab,
        "resistência característica à flexão tabuleiro (MPa)": f_mk_mpa_tab,
    }
else:
    dados_projeto = {
        "l (cm)": l,
        "b_wpista (cm)": larg,
        "tipo_secao_longarina": tipo_secao_longarina,
        "tipo_secao_tabuleiro": tipo_secao_tabuleiro,
        "p_gk (kN/m²)": p_gk,
        "p_rodak (kN)": p_rodak,
        "p_qk (kN/m²)": p_qk,
        "a (m)": a,
        "classe_carregamento": classe_carregamento_raw.lower(),
        "classe_madeira": classe_madeira_raw.lower(),
        "classe_umidade": classe_umidade,
        "gamma_g": gamma_g,
        "gamma_q": gamma_q,
        "gamma_w": gamma_w,
        "psi_2": psi_2,
        "phi": fluencia,
        "densidade longarina (kg/m³)": densidade_long,
        "resistência característica à flexão longarina (MPa)": f_mk_mpa,
        "resistência característica ao cisalhamento longarina (MPa)": f_vk_mpa,
        "módulo de elasticidade à flexão longarina (GPa)": e_modflex_gpa,
        "densidade tabuleiro (kg/m³)": densidade_tab,
        "resistência característica à flexão tabuleiro (MPa)": f_mk_mpa_tab,
    }

excel_bytes = montar_excel(dados_projeto)


# ============================================================
# 3) INVALIDAÇÃO AUTOMÁTICA (se inputs mudarem)
# ============================================================
sig_now = make_signature(dados_projeto)
sig_last = st.session_state.get("sig_last")

if st.session_state.get("has_results", False) and (sig_last is not None) and (sig_now != sig_last):
    invalidate_results()


# ============================================================
# 4) COMPUTE (apenas quando clicar em Gerar)
# ============================================================
if submitted_design:
    # validações mínimas (para evitar rodar com None)
    if d_cm_min is None or d_cm_max is None:
        st.error("Defina os limites de diâmetro (d_min e d_max).")
        st.stop()
    if esp_min is None or esp_max is None or bw_min is None or bw_max is None or h_min is None or h_max is None:
        st.error("Defina os limites do tabuleiro (esp, bw, h).")
        st.stop()

    st.session_state["sig_last"] = sig_now

    ds   = [float(d_cm_min), float(d_cm_max)]
    esps = [float(esp_min),  float(esp_max)]
    bws  = [float(bw_min),   float(bw_max)]
    hs   = [float(h_min),    float(h_max)]

    # NSGA-II
    res_nsga = chamando_nsga2(dados_projeto, ds, esps, bws, hs)

    # padroniza DataFrame final (PT/EN)
    if lang == "pt":
        df_resultados = pd.DataFrame({
            "d_cm": res_nsga["d [cm]"].tolist(),
            "esp_cm": res_nsga["esp [cm]"].tolist(),
            "bw_cm": res_nsga["bw [cm]"].tolist(),
            "h_cm": res_nsga["h [cm]"].tolist(),
            "area_m2": res_nsga["area [m²]"].tolist(),
            "deflecção_m": res_nsga["delta [m]"].tolist(),
            "longarina_g_m": res_nsga["flex lim beam [kPa]"].tolist(),
            "longarina_g_v": res_nsga["cis lim beam [kPa]"].tolist(),
            "longarina_g_f": res_nsga["delta lim beam [m]"].tolist(),
            "tabuleiro_g_m": res_nsga["flex lim deck [kPa]"].tolist(),
        })
        x = df_resultados["area_m2"].to_numpy()
        y = df_resultados["deflecção_m"].to_numpy()
    else:
        df_resultados = pd.DataFrame({
            "d_cm": res_nsga["d [cm]"].tolist(),
            "esp_cm": res_nsga["esp [cm]"].tolist(),
            "bw_cm": res_nsga["bw [cm]"].tolist(),
            "h_cm": res_nsga["h [cm]"].tolist(),
            "area_m2": res_nsga["area [m²]"].tolist(),
            "deflection_m": res_nsga["delta [m]"].tolist(),
            "beam_g_m": res_nsga["flex lim beam [kPa]"].tolist(),
            "beam_g_v": res_nsga["cis lim beam [kPa]"].tolist(),
            "beam_g_f": res_nsga["delta lim beam [m]"].tolist(),
            "deck_g_m": res_nsga["flex lim deck [kPa]"].tolist(),
        })
        x = df_resultados["area_m2"].to_numpy()
        y = df_resultados["deflection_m"].to_numpy()

    # Excel dos resultados
    excel_bytes_resultados = montar_excel_df(df_resultados)

    # Figura (salva como bytes PNG para re-render sem sumir)
    fig = fronteira_pareto(x, y, t["tag_x_fig"], t["tag_y_fig"])
    fig_buf = io.BytesIO()
    fig.savefig(fig_buf, format="png", dpi=400, bbox_inches="tight")
    fig_buf.seek(0)
    fig_png = fig_buf.getvalue()

    # ZIP (bytes)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("beam_data.xlsx", excel_bytes)
        zf.writestr("pre_sizing_results_optimized.xlsx", excel_bytes_resultados)
        zf.writestr("pareto_frontier.png", fig_png)
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.getvalue()

    # Persistência (para sobreviver a reruns)
    st.session_state["df_resultados"] = df_resultados
    st.session_state["excel_bytes_resultados"] = excel_bytes_resultados
    st.session_state["fig_png"] = fig_png
    st.session_state["zip_bytes"] = zip_bytes
    st.session_state["has_results"] = True


# ============================================================
# 5) RENDER (sempre que houver resultados em cache)
# ============================================================
if st.session_state.get("has_results", False):
    st.subheader(t["gerador_desempenho"])
    st.dataframe(st.session_state["df_resultados"], use_container_width=True)

    st.subheader("Fronteira eficiente – Pré-dimensionamento")
    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        st.image(st.session_state["fig_png"])

    st.download_button(
        label=t["botao_dados_down"],
        data=st.session_state["zip_bytes"],
        file_name="pre_sizing_package.zip",
        mime="application/zip",
    )

else:
    st.warning(t.get("aviso_gerar_primeiro", "Sem resultados atuais. Clique em “Gerar” para processar."))
