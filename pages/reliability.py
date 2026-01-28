# Tela de confiabilidade
import io
import json
import hashlib

import streamlit as st
import pandas as pd
import math

from madeiras import textos_design, chamando_form


# -----------------------------
# Helpers: assinatura + invalidação (pronto p/ evoluir depois)
# -----------------------------
def pct_change(new: float, ref: float) -> float:
    if ref is None or ref == 0 or (isinstance(ref, float) and math.isclose(ref, 0.0)):
        return float("nan")
    return (new - ref) / ref * 100.0


def make_signature(d: dict) -> str:
    payload = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def invalidate_results():
    st.session_state["has_results"] = False
    for k in ["res_design", "sig_last"]:
        st.session_state.pop(k, None)


def status_global(prefixo: str, *blocos: dict) -> tuple[str, bool]:
    passou = all(
        isinstance(b, dict) and str(b.get("analise", "")).upper() == "OK"
        for b in blocos
        if b is not None
    )

    if passou:
        return f"✅ {prefixo} — OK", True
    return f"❌ {prefixo} — NÃO ATENDE", False


if "has_results" not in st.session_state:
    st.session_state["has_results"] = False

# >>> MINIMO: inicializa chaves usadas no slider/recalc
for k in ["res_ref", "d_ref_cm", "df0_design", "esp_cm_ref", "bw_cm_ref", "h_cm_ref", "slider_d_cm"]:
    if k not in st.session_state:
        st.session_state[k] = None
# <<<


# -----------------------------
# UI text
# -----------------------------
lang = st.session_state.get("lang", "pt")
textos = textos_design()
t = textos.get(lang, textos["pt"])

st.header(t["titulo"])
st.subheader(t["pre"])


# ============================================================
# 1) FORM
# ============================================================
with st.form("form_design", clear_on_submit=False):

    # -------------------------
    # Inputs de geometria escolhida (projeto final)
    # -------------------------
    st.subheader(t["geo_head"])

    colA, colB = st.columns(2)

    with colA:
        tipo_secao_longarina = st.selectbox(
            t["entrada_tipo_secao_longarina"],
            t["tipo_secao_longarina"],
            key="tipo_secao_longarina",
        )

        d_cm = None
        if str(tipo_secao_longarina).lower() == "circular":
            d_cm = st.number_input(
                t["diametro_longarina"],
                step=1.0,
                key="d_cm",
            )

        esp_cm = st.number_input(
            t["espaçamento_entre_longarinas"], 
            step=1.0,
            key="esp_cm",
        )

    with colB:
        tipo_secao_tabuleiro = st.selectbox(
            t["tipo_secao_tabuleiro"],
            t["tipo_secao_tabuleiro_opcoes"],
            key="tipo_secao_tabuleiro",
        )

        bw_cm = h_cm = None
        if str(tipo_secao_tabuleiro).lower() == "retangular":
            bw_cm = st.number_input(
                t["largura_viga_tabuleiro"],
                step=1.0,
                key="bw_cm",
            )
            h_cm = st.number_input(
                t["altura_viga_tabuleiro"],
                step=1.0,
                key="h_cm",
            )

    # -------------------------
    # Upload da planilha do pré-dimensionamento (dados-base)
    # -------------------------
    st.subheader(t["planilha_head"])

    uploaded_file = st.file_uploader(
        t["texto_up"],
        type=["xlsx"],
        key="uploaded_design_xlsx",
    )

    # Preview da planilha
    df = None
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success(t["planilha_sucesso"])
        st.markdown(t["planilha_preview"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info(t["aguardando_upload"])

    # Botão de cálculo
    submitted_design = st.form_submit_button(t["gerador_projeto"])

# ============================================================
# 2) COMPUTE (somente no submit)
# ============================================================
if submitted_design:

    # Validações mínimas (sem travar seu fluxo)
    if uploaded_file is None or df is None:
        st.error(t["erro_sem_planilha"])
        st.stop()

    if d_cm is None or bw_cm is None or h_cm is None:
        st.error(t["erro_sem_geo"])
        st.stop()

    if isinstance(df, pd.DataFrame) and len(df) == 1:
        df0 = df.iloc[0]
    else:
        df0 = df.iloc[0]

    beta_m, pf_m = chamando_form(
        df0["p_gk (kN/m²)"], df0["p_rodak (kN)"], df0["p_qk (kN/m²)"], df0["a (m)"], df0["l (cm)"],
        df0["classe_carregamento"], df0["classe_madeira"], df0["classe_umidade"],
        df0["resistência característica à flexão longarina (MPa)"],
        df0["resistência característica ao cisalhamento longarina (MPa)"],
        df0["módulo de elasticidade à flexão longarina (GPa)"],
        df0["resistência característica à flexão tabuleiro (MPa)"],
        df0["densidade longarina (kg/m³)"], df0["densidade tabuleiro (kg/m³)"],
        d_cm, esp_cm, bw_cm, h_cm, "flexao"
    )

    beta_f, pf_f = chamando_form(
        df0["p_gk (kN/m²)"], df0["p_rodak (kN)"], df0["p_qk (kN/m²)"], df0["a (m)"], df0["l (cm)"],
        df0["classe_carregamento"], df0["classe_madeira"], df0["classe_umidade"],
        df0["resistência característica à flexão longarina (MPa)"],
        df0["resistência característica ao cisalhamento longarina (MPa)"],
        df0["módulo de elasticidade à flexão longarina (GPa)"],
        df0["resistência característica à flexão tabuleiro (MPa)"],
        df0["densidade longarina (kg/m³)"], df0["densidade tabuleiro (kg/m³)"],
        d_cm, esp_cm, bw_cm, h_cm, "flecha"
    )

    res = {
        "indice_confiabilidade_flexão": beta_m,
        "probabilidade_de_fratura_flexão": pf_m,
        "indice_confiabilidade_flecha": beta_f,
        "probabilidade_de_fratura_flecha": pf_f,
    }

    # >>> MINIMO: baseline p/ slider/comparação (sem conflitar com widgets)
    st.session_state["res_ref"] = res.copy()
    st.session_state["d_ref_cm"] = float(d_cm)
    st.session_state["df0_design"] = df0.to_dict()
    st.session_state["esp_cm_ref"] = float(esp_cm)
    st.session_state["bw_cm_ref"] = float(bw_cm)
    st.session_state["h_cm_ref"] = float(h_cm)
    st.session_state["slider_d_cm"] = float(d_cm)
    # <<<

    st.session_state["res_design"] = res
    st.session_state["has_results"] = True


# ============================================================
# 3) DISPLAY (igual você fez) + SLIDER + COMPARAÇÃO
# ============================================================
if st.session_state.get("has_results", False):

    res = st.session_state.get("res_design", {})
    res_ref = st.session_state.get("res_ref", res)

    st.subheader("Resultados de Confiabilidade")

    with st.expander("Resultado (referência)", expanded=True):
        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Flexão**")
            st.metric("β (flexão)", f"{res_ref.get('indice_confiabilidade_flexão', float('nan')):.4f}")
            st.metric("Probabilidade de falha (flexão)", f"{res_ref.get('probabilidade_de_fratura_flexão', float('nan')):.4e}")

        with c2:
            st.markdown("**Flecha**")
            st.metric("β (flecha)", f"{res_ref.get('indice_confiabilidade_flecha', float('nan')):.4f}")
            st.metric("Probabilidade de falha (flecha)", f"{res_ref.get('probabilidade_de_fratura_flecha', float('nan')):.4e}")

    st.divider()
    st.subheader("Análise de Sensibilidade — Diâmetro da Longarina")

    d_ref = float(st.session_state.get("d_ref_cm") or 0.0)
    if d_ref <= 0:
        st.warning("Diâmetro de referência não definido. Gere um resultado primeiro.")
        st.stop()

    d_min = 0.8 * d_ref
    d_max = 1.2 * d_ref

    d_new = st.slider(
        "Diâmetro (cm)",
        min_value=float(d_min),
        max_value=float(d_max),
        value=float(st.session_state.get("slider_d_cm") or d_ref),
        step=0.5,
        key="slider_d_cm",
    )

    colR1, colR2 = st.columns([1, 2])
    with colR1:
        recalc = st.button("Recalcular confiabilidade", use_container_width=True)

    if recalc:
        df0_dict = st.session_state.get("df0_design", {})
        esp_cm_ = float(st.session_state.get("esp_cm_ref") or 0.0)
        bw_cm_  = float(st.session_state.get("bw_cm_ref") or 0.0)
        h_cm_   = float(st.session_state.get("h_cm_ref") or 0.0)

        beta_m_new, pf_m_new = chamando_form(
            df0_dict["p_gk (kN/m²)"], df0_dict["p_rodak (kN)"], df0_dict["p_qk (kN/m²)"],
            df0_dict["a (m)"], df0_dict["l (cm)"], df0_dict["classe_carregamento"],
            df0_dict["classe_madeira"], df0_dict["classe_umidade"],
            df0_dict["resistência característica à flexão longarina (MPa)"],
            df0_dict["resistência característica ao cisalhamento longarina (MPa)"],
            df0_dict["módulo de elasticidade à flexão longarina (GPa)"],
            df0_dict["resistência característica à flexão tabuleiro (MPa)"],
            df0_dict["densidade longarina (kg/m³)"], df0_dict["densidade tabuleiro (kg/m³)"],
            float(d_new), esp_cm_, bw_cm_, h_cm_,
            "flexao"
        )

        beta_f_new, pf_f_new = chamando_form(
            df0_dict["p_gk (kN/m²)"], df0_dict["p_rodak (kN)"], df0_dict["p_qk (kN/m²)"],
            df0_dict["a (m)"], df0_dict["l (cm)"], df0_dict["classe_carregamento"],
            df0_dict["classe_madeira"], df0_dict["classe_umidade"],
            df0_dict["resistência característica à flexão longarina (MPa)"],
            df0_dict["resistência característica ao cisalhamento longarina (MPa)"],
            df0_dict["módulo de elasticidade à flexão longarina (GPa)"],
            df0_dict["resistência característica à flexão tabuleiro (MPa)"],
            df0_dict["densidade longarina (kg/m³)"], df0_dict["densidade tabuleiro (kg/m³)"],
            float(d_new), esp_cm_, bw_cm_, h_cm_,
            "flecha"
        )

        res_new = {
            "indice_confiabilidade_flexão": beta_m_new,
            "probabilidade_de_fratura_flexão": pf_m_new,
            "indice_confiabilidade_flecha": beta_f_new,
            "probabilidade_de_fratura_flecha": pf_f_new,
            "d_cm": float(d_new),
        }

        st.session_state["res_design"] = res_new
        res = res_new

    st.divider()
    with st.expander("Comparação — Referência vs Cenário do Slider", expanded=True):

        b_ref_m = float(res_ref.get("indice_confiabilidade_flexão", float("nan")))
        p_ref_m = float(res_ref.get("probabilidade_de_fratura_flexão", float("nan")))
        b_ref_f = float(res_ref.get("indice_confiabilidade_flecha", float("nan")))
        p_ref_f = float(res_ref.get("probabilidade_de_fratura_flecha", float("nan")))

        b_new_m = float(res.get("indice_confiabilidade_flexão", b_ref_m))
        p_new_m = float(res.get("probabilidade_de_fratura_flexão", p_ref_m))
        b_new_f = float(res.get("indice_confiabilidade_flecha", b_ref_f))
        p_new_f = float(res.get("probabilidade_de_fratura_flecha", p_ref_f))

        st.markdown(
            f"**Diâmetro de referência:** {d_ref:.2f} cm  \n"
            f"**Diâmetro do cenário:** {float(d_new):.2f} cm"
        )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### Flexão")
            st.metric("β (ref)", f"{b_ref_m:.4f}")
            st.metric("β (cenário)", f"{b_new_m:.4f}", delta=f"{pct_change(b_new_m, b_ref_m):+.2f}%")

            st.metric("Pf (ref)", f"{p_ref_m:.4e}")
            st.metric("Pf (cenário)", f"{p_new_m:.4e}", delta=f"{pct_change(p_new_m, p_ref_m):+.2f}%")

        with c2:
            st.markdown("### Flecha")
            st.metric("β (ref)", f"{b_ref_f:.4f}")
            st.metric("β (cenário)", f"{b_new_f:.4f}", delta=f"{pct_change(b_new_f, b_ref_f):+.2f}%")

            st.metric("Pf (ref)", f"{p_ref_f:.4e}")
            st.metric("Pf (cenário)", f"{p_new_f:.4e}", delta=f"{pct_change(p_new_f, p_ref_f):+.2f}%")

else:
    st.warning("Sem resultados atuais. Clique em “Gerar” para processar.")
