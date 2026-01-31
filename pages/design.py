# Tela de dimensionamento
import io
import json
import hashlib
from datetime import datetime

import streamlit as st
import pandas as pd

from madeiras import textos_design, ProjetoOtimo, gerar_relatorio_final


# -----------------------------
# Helpers: assinatura + invalidação (pronto p/ evoluir depois)
# -----------------------------
def make_signature(d: dict) -> str:
    payload = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def invalidate_results():
    st.session_state["has_results"] = False
    for k in ["res_design", "sig_last"]:
        st.session_state.pop(k, None)


def status_global(prefixo: str, *blocos: dict) -> tuple[str, bool]:
    lang = st.session_state.get("lang", "pt")
    
    textos = textos_design()
    t_local = textos.get(lang, textos["pt"])
    passou = all(
        isinstance(b, dict) and str(b.get("analise", "")).upper() == "OK"
        for b in blocos
        if b is not None
    )

    status_texto = t_local["status_ok"] if passou else t_local["status_falha"]
    emoji = "✅" if passou else "❌"

    return f"{emoji} {prefixo} — {status_texto}", passou


# -----------------------------
# UI text
# -----------------------------
lang = st.session_state.get("lang", "pt")
textos = textos_design()
t = textos.get(lang, textos["pt"])

st.header(t["titulo"])
st.subheader(t["pre"])


# ============================================================
# 1) form para dados do dimensionamento
# ============================================================
with st.form("form_design", clear_on_submit=False):

    # -------------------------
    # Inputs de geometria escolhida (projeto final)
    # -------------------------
    st.subheader(t["dados_pre"])

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
        if str(tipo_secao_tabuleiro).lower() == "retangular" or str(tipo_secao_tabuleiro).lower() == "rectangular":
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
        st.error(t["erro_geo"])
        st.stop()

    # Se df veio como DataFrame com 1 linha, garantimos série/escalares
    # (muitas vezes o Excel vem com 1 linha e você quer acessar como scalar)
    # Regra: se df tem 1 linha, usamos df.iloc[0] (Series)
    if isinstance(df, pd.DataFrame) and len(df) == 1:
        df0 = df.iloc[0]
    else:
        # Se vier mais de uma linha, você decide depois qual usar.
        # Por ora, vamos usar a primeira para não te travar.
        df0 = df.iloc[0]

    # Instancia o dimensionamento determinístico
    projeto = ProjetoOtimo(
                                l=df0["l (cm)"],
                                p_gk=df0["p_gk (kPa)"],
                                p_rodak=df0["p_rodak (kN)"],
                                p_qk=df0["p_qk (kPa)"],
                                a=df0["a (m)"],
                                classe_carregamento=df0["classe_carregamento"],
                                classe_madeira=df0["classe_madeira"],
                                classe_umidade=df0["classe_umidade"],
                                gamma_g=df0["gamma_g"],
                                gamma_q=df0["gamma_q"],
                                gamma_wc=df0["gamma_wc"],
                                gamma_wf=df0["gamma_wf"],
                                psi2=df0["psi_2"],
                                phi=df0["phi"],
                                densidade_long=df0["densidade longarina (kg/m³)"],
                                densidade_tab=df0["densidade tabuleiro (kg/m³)"],
                                f_mk_long=df0["resistência característica à flexão longarina (MPa)"],
                                f_vk_long=df0["resistência característica ao cisalhamento longarina (MPa)"],
                                e_modflex_long=df0["módulo de elasticidade à flexão longarina (GPa)"],
                                f_mk_tab=df0["resistência característica à flexão tabuleiro (MPa)"],
                                d_min=0,
                                d_max=0,
                                esp_min=0,
                                esp_max=0,
                                bw_min=0,
                                bw_max=0,
                                h_min=0,
                                h_max=0
                            )

    # Calcula (uma vez só)
    res = projeto.calcular_objetivos_restricoes_otimizacao(d=float(d_cm), esp=float(esp_cm), bw=float(bw_cm), h=float(h_cm))

    # (Opcional) guarda na sessão para você evoluir depois sem recalcular
    st.session_state["res_design"] = res
    st.session_state["has_results"] = True


# ============================================================
# 3) DISPLAY (se existir resultado em sessão)
# ============================================================
if st.session_state.get("has_results", False):

    res = st.session_state["res_design"]

    st.subheader(t["resultado_head"])

    # 3) Verificações — Longarina
    titulo_longarina, longarina_ok = status_global(
                                                    t["verif_longarina_titulo"],
                                                    res[2],
                                                    res[3],
                                                    res[4]
                                                )
    with st.expander(titulo_longarina, expanded=not longarina_ok):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"**{t['label_flexao']}**")
            st.json(res[2])

        with col2:
            st.markdown(f"**{t['label_cisalhamento']}**")
            st.json(res[3])
        with col3:
            st.markdown(f"**{t['label_flecha']}**")
            st.json(res[4])

    # 4) Verificações — Tabuleiro (status no título)
    titulo_tabuleiro, tabuleiro_ok = status_global(
                                                    t["verif_tabuleiro_titulo"],
                                                    res[6]
                                                )

    with st.expander(titulo_tabuleiro, expanded=not tabuleiro_ok):
        st.markdown(f"**{t['label_flexao']}**")
        st.json(res[6])

    # 5) Relatórios completos (auditoria)
    with st.expander(t["resultado_relatorios"], expanded=False):
        rel_carga = res[-1]
        rel_l = res[-2]
        rel_t = res[-3]
        st.markdown(f"**{t['label_cargas']}**")
        st.json(rel_carga)
        st.markdown(f"**{t['label_longarina']}**")
        st.json(rel_l)
        st.markdown(f"**{t['label_tabuleiro']}**")
        st.json(rel_t)
    
    # 2. Converte esse texto para os bytes do PDF
    pdf_bytes = markdown_para_pdf(md_text)

    # 3. Configura o botão para baixar os bytes do PDF
    st.download_button(
        label="📄 Baixar Relatório em PDF",
        data=pdf_bytes,
        file_name=f"{t['nome_arquivo']}.pdf",
        mime="application/pdf",
    )
else:
    st.warning(t["aviso_gerar_primeiro"]) ##teste
    