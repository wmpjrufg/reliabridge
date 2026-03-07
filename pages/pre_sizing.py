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
with st.container():
    st.markdown(t["pre"])


# ============================================================
# 1) FORM PARA ENTRADA DE DADOS
# ============================================================
with st.form("form_geometria", clear_on_submit=False):

    st.subheader(t["geometria_t"])
    col1, col2 = st.columns(2)
    with col1:
        l = st.number_input(t["entrada_comprimento"], min_value=300.0, key="l")
    with col2:
        larg = st.number_input(t["pista"], min_value=200.0, key="larg")

    st.divider()

    st.subheader(t["variaveis_otimizacao"])
    col1, col2 = st.columns(2)
    with col1:
        tipo_secao_longarina = st.selectbox(t["entrada_tipo_secao_longarina"], t["tipo_secao_longarina"], key="tipo_secao_longarina")
        if tipo_secao_longarina.lower() == "circular":
            d_cm_min = st.number_input(t["diametro_minimo"], min_value=1.0, key="d_cm_min")
            d_cm_max = st.number_input(t["diametro_maximo"], min_value=1.0, key="d_cm_max")
        else:
            d_cm_min, d_cm_max, n_max = None
        n_min_long = st.number_input(t["espaço_min_longarinas"], value=0.0, min_value=0.0, key="n_min_long")
        n_max_long = st.number_input(t["espaço_max_longarinas"], value=0.0, min_value=0.0, key="n_max_long")

    with col2:
        tipo_secao_tabuleiro = st.selectbox(t["tipo_secao_tabuleiro"], t["tipo_secao_tabuleiro_opcoes"], key="tipo_secao_tabuleiro")
        if tipo_secao_tabuleiro.lower() == "retangular":
            bw_min  = st.number_input(t["largura_viga_tabuleiro_min"], key="bw_min")
            bw_max  = st.number_input(t["largura_viga_tabuleiro_max"], key="bw_max")
            h_min   = st.number_input(t["altura_viga_tabuleiro_min"], key="h_min")
            h_max   = st.number_input(t["altura_viga_tabuleiro_max"], key="h_max")
        else:
            bw_min = bw_max = h_min = h_max = None
        n_min_tab = st.number_input(t["espaço_min_tabuleiros"], value=0.0, min_value=0.0, key="n_min_tab")
        n_max_tab = st.number_input(t["espaço_max_tabuleiros"], value=0.0, min_value=0.0, key="n_max_tab")

    st.divider()

    st.subheader(t["cargas_projeto"])
    col1, col2 = st.columns(2)
    with col1:
        p_gk    = st.number_input(t["carga_permanente"], key="p_gk")
        p_rodak = st.number_input(t["carga_roda"], key="p_rodak")
    with col2:
        p_qk = st.number_input(t["carga_multidao"], key="p_qk")
        a    = st.number_input(t["distancia_eixos"], key="a")

    st.divider()

    st.subheader(t["classes_mad_carga"])
    col1, col2, col3 = st.columns(3)
    with col1:
        classe_carregamento_raw = st.selectbox(
            t["classe_carregamento"],
            t["classe_carregamento_opcoes"],
            key="classe_carregamento"
        )
    with col2:
        classe_madeira_raw = st.selectbox(
            t["classe_madeira"],
            t["classe_madeira_opcoes"],
            key="classe_madeira"
        )
    with col3:
        classe_umidade = st.selectbox(
            t["classe_umidade"],
            [1, 2, 3, 4],
            key="classe_umidade"
        )

    st.divider()

    st.subheader(t["coeficientes_seguranca"])
    col1, col2, col3 = st.columns(3)
    with col1:
        gamma_g = st.number_input(t["gamma_g"], step=0.1, key="gamma_g")
        gamma_q = st.number_input(t["gamma_q"], step=0.1, key="gamma_q")
    with col2:
        gamma_wf = st.number_input(t["gamma_wf"], step=0.1, key="gamma_wf")
        gamma_wc = st.number_input(t["gamma_wc"], step=0.1, key="gamma_wc")
    with col3:
        psi_2 = st.number_input(t["psi2"], step=0.1, key="psi_2")
        fluencia = st.number_input(t["considerar_fluencia"], step=0.1, key="phi")

    st.divider()

    st.subheader(t["prop_madeira"])

    st.markdown(f"**{t['longarina_t']}**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        densidade_long = st.number_input(t["densidade_long"], step=1.0, key="densidade_long")
    with col2:
        f_mk_mpa = st.number_input(t["f_mk"], step=0.1, key="f_mk_mpa")
    with col3:
        f_vk_mpa = st.number_input(t["f_vk"], step=0.1, key="f_vk_mpa")
    with col4:
        e_modflex_gpa = st.number_input(t["e_modflex"], step=0.1, key="e_modflex_gpa")

    st.markdown(f"**{t['tabuleiro_t']}**")
    col1, col2 = st.columns(2)
    with col1:
        densidade_tab = st.number_input(t["densidade_tab"], step=1.0, key="densidade_tab")
    with col2:
        f_mk_mpa_tab = st.number_input(t["f_mk_tab"], step=0.1, key="f_mk_mpa_tab")

    st.divider()

    submitted_design = st.form_submit_button(t["gerador_desempenho"])


# ============================================================
# 2) DADOS DO PROJETO (sempre disponíveis)
# ============================================================
dados_projeto = {
                    f"{t['entrada_comprimento']}": l,
                    f"{t['pista']}": larg,
                    f"{t['tipo_secao_longarina']}": tipo_secao_longarina,
                    f"{t['tipo_secao_tabuleiro']}": tipo_secao_tabuleiro,
                    f"{t['carga_permanente']} (kPa)": p_gk,
                    f"{t['carga_roda']} (kN)": p_rodak,
                    f"{t['carga_multidao']} (kPa)": p_qk,
                    f"{t['distancia_eixos']} (m)": a,
                    f"{t['classe_carregamento']}": classe_carregamento_raw.lower(),
                    f"{t['classe_madeira']}": classe_madeira_raw.lower(),
                    f"{t['classe_umidade']}": classe_umidade,
                    f"{t['gamma_g']}": gamma_g,
                    f"{t['gamma_q']}": gamma_q,
                    f"{t['gamma_wc']}": gamma_wc,
                    f"{t['gamma_wf']}": gamma_wf,
                    f"{t['psi2']}": psi_2,
                    f"{t['considerar_fluencia']}": fluencia,
                    f"{t['densidade_long']} (kg/m³)": densidade_long,
                    f"{t['f_mk']} (MPa)": f_mk_mpa,
                    f"{t['f_vk']} (MPa)": f_vk_mpa,
                    f"{t['e_modflex']} (GPa)": e_modflex_gpa,
                    f"{t['densidade_tab']} (kg/m³)": densidade_tab,
                    f"{t['f_mk_tab']} (MPa)": f_mk_mpa_tab,
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
    erros = []

    # ------------------------------------------------------------
    # Geometria geral
    # ------------------------------------------------------------
    if l <= 0:
        erros.append(f"- {t['entrada_comprimento']}")
    if larg <= 0:
        erros.append(f"- {t['pista']}")

    # ------------------------------------------------------------
    # Variáveis de otimização - Longarinas
    # ------------------------------------------------------------
    if tipo_secao_longarina.lower() == "circular":
        if d_cm_min is None or d_cm_min <= 0:
            erros.append(f"- {t['diametro_minimo']}")
        if d_cm_max is None or d_cm_max <= 0:
            erros.append(f"- {t['diametro_maximo']}")
        if d_cm_min is not None and d_cm_max is not None and d_cm_min > d_cm_max:
            erros.append(f"- {t['diametro_minimo']} > {t['diametro_maximo']}")
        if n_max_long is None or n_max_long <= 0:
            erros.append(f"- {t['espaço_max_longarinas']}")

    # ------------------------------------------------------------
    # Variáveis de otimização - Tabuleiro
    # ------------------------------------------------------------
    if tipo_secao_tabuleiro.lower() == "retangular":
        if bw_min is None or bw_min <= 0:
            erros.append(f"- {t['largura_viga_tabuleiro_min']}")
        if bw_max is None or bw_max <= 0:
            erros.append(f"- {t['largura_viga_tabuleiro_max']}")
        if h_min is None or h_min <= 0:
            erros.append(f"- {t['altura_viga_tabuleiro_min']}")
        if h_max is None or h_max <= 0:
            erros.append(f"- {t['altura_viga_tabuleiro_max']}")
        if bw_min is not None and bw_max is not None and bw_min > bw_max:
            erros.append(f"- {t['largura_viga_tabuleiro_min']} > {t['largura_viga_tabuleiro_max']}")
        if h_min is not None and h_max is not None and h_min > h_max:
            erros.append(f"- {t['altura_viga_tabuleiro_min']} > {t['altura_viga_tabuleiro_max']}")
        if n_max_tab is None or n_max_tab <= 0:
            erros.append(f"- {t['espaço_max_tabuleiros']}")

    # ------------------------------------------------------------
    # Cargas
    # ------------------------------------------------------------
    if p_gk <= 0:
        erros.append(f"- {t['carga_permanente']}")
    if p_rodak <= 0:
        erros.append(f"- {t['carga_roda']}")
    if p_qk <= 0:
        erros.append(f"- {t['carga_multidao']}")
    if a <= 0:
        erros.append(f"- {t['distancia_eixos']}")

    # ------------------------------------------------------------
    # Coeficientes de segurança
    # ------------------------------------------------------------
    if gamma_g <= 0:
        erros.append(f"- {t['gamma_g']}")
    if gamma_q <= 0:
        erros.append(f"- {t['gamma_q']}")
    if gamma_wf <= 0:
        erros.append(f"- {t['gamma_wf']}")
    if gamma_wc <= 0:
        erros.append(f"- {t['gamma_wc']}")
    if psi_2 <= 0:
        erros.append(f"- {t['psi2']}")
    if fluencia <= 0:
        erros.append(f"- {t['considerar_fluencia']}")

    # ------------------------------------------------------------
    # Propriedades da madeira
    # ------------------------------------------------------------
    if densidade_long <= 0:
        erros.append(f"- {t['densidade_long']}")
    if f_mk_mpa <= 0:
        erros.append(f"- {t['f_mk']}")
    if f_vk_mpa <= 0:
        erros.append(f"- {t['f_vk']}")
    if e_modflex_gpa <= 0:
        erros.append(f"- {t['e_modflex']}")

    if densidade_tab <= 0:
        erros.append(f"- {t['densidade_tab']}")
    if f_mk_mpa_tab <= 0:
        erros.append(f"- {t['f_mk_tab']}")

    # ------------------------------------------------------------
    # Resultado da validação
    # ------------------------------------------------------------
    if erros:
        st.error("Os seguintes campos devem ser preenchidos com valores maiores que zero:\n\n" + "\n".join(erros))
        st.stop()

    # Se passou na validação, segue o processamento
    st.success("Dados validados com sucesso.")
    st.session_state["sig_last"] = sig_now

    ds       = [float(d_cm_min), float(d_cm_max)]
    bws      = [float(bw_min),   float(bw_max)]
    hs       = [float(h_min),    float(h_max)]
    n_p_long = [float(n_min_long), float(n_max_long)]
    n_p_tab  = [float(n_min_tab),  float(n_max_tab)]

    # NSGA-II
    res_nsga = chamando_nsga2(dados_projeto, ds, bws, hs, n_p_long, n_p_tab, t)

    # padroniza DataFrame final (PT/EN)
    if lang == "pt":
        df_resultados = pd.DataFrame({
                                        "d_cm": res_nsga["d [cm]"].tolist(),
                                        "esp_cm": res_nsga["esp [cm]"].tolist(),
                                        "bw_cm": res_nsga["bw [cm]"].tolist(),
                                        "h_cm": res_nsga["h [cm]"].tolist(),
                                        "area_m2": res_nsga["area [m²]"].tolist(),
                                        "deflecção": res_nsga["delta [-]"].tolist(),
                                        "longarina_g_m": res_nsga["flex lim beam [(Ms-Mr)/Mr]"].tolist(),
                                        "longarina_g_v": res_nsga["cis lim beam [(Vs-Vr)/Vr]"].tolist(),
                                        "longarina_g_f": res_nsga["delta lim beam [(ps-pr)/pr]"].tolist(),
                                        "tabuleiro_g_m": res_nsga["flex lim deck [(Ms-Mr)/Mr]"].tolist(),
                                    })
        x = df_resultados["area_m2"].to_numpy()
        y = df_resultados["deflecção"].to_numpy()
    else:
        df_resultados = pd.DataFrame({
                                        "d_cm": res_nsga["d [cm]"].tolist(),
                                        "esp_cm": res_nsga["esp [cm]"].tolist(),
                                        "bw_cm": res_nsga["bw [cm]"].tolist(),
                                        "h_cm": res_nsga["h [cm]"].tolist(),
                                        "area_m2": res_nsga["area [m²]"].tolist(),
                                        "deflection": res_nsga["delta [-]"].tolist(),
                                        "beam_g_m": res_nsga["flex lim beam [(Ms-Mr)/Mr]"].tolist(),
                                        "beam_g_v": res_nsga["cis lim beam [(Vs-Vr)/Vr]"].tolist(),
                                        "beam_g_f": res_nsga["delta lim beam [(ps-pr)/pr]"].tolist(),
                                        "deck_g_m": res_nsga["flex lim deck [(Ms-Mr)/Mr]"].tolist(),
                                    })
        x = df_resultados["area_m2"].to_numpy()
        y = df_resultados["deflection_m"].to_numpy()

    # Excel dos resultados
    excel_bytes_resultados = montar_excel_df(df_resultados)

    # Figura (salva como bytes PNG para re-render sem sumir)
    fig = fronteira_pareto(x.tolist(), y.tolist(), t["tag_x_fig"], t["tag_y_fig"])
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
