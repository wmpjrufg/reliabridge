# Tela de dimensionamento
import io
import json
import hashlib
from datetime import datetime

import streamlit as st
import pandas as pd

from madeiras import (
                            textos_design,
                            textos_pre_sizing_l,
                            normalizar_dados_pre_sizing,
                            valor_dados_pre_sizing,
                            ProjetoOtimo,
                            gerar_relatorio_final,
                            markdown_para_pdf,
                        )


# -----------------------------
# Helpers: assinatura + invalidação
# -----------------------------
def make_signature(d: dict) -> str:
    payload = json.dumps(d, sort_keys=True, default=str).encode("utf-8")
    return hashlib.md5(payload).hexdigest()


def invalidate_results():
    st.session_state["has_results"] = False
    for k in ["res_design", "projeto_obj", "geo_final", "sig_last"]:
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


def render_verificacao(nome: str, resultado: dict, t_local: dict):
    g = float(resultado.get("g_otimiz [-]", 0.0))
    atende = g <= 0.0
    status = t_local["status_ok"] if atende else t_local["status_falha"]
    interpretacao = t_local["g_atende"] if atende else t_local["g_nao_atende"]

    st.markdown(f"**{nome}**")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(t_local["indicador_g"], f"{g:.4f}")
    with col2:
        st.markdown(f"**{status}**")
        st.caption(interpretacao)
        st.caption(t_local["g_interpretacao"])


def normalizar_planilha_pre_sizing(row: pd.Series, lang_atual: str) -> tuple[dict, dict]:
    dados_raw = row.to_dict()
    textos_pre = textos_pre_sizing_l()
    idiomas = [lang_atual, "pt", "en"]
    idiomas = list(dict.fromkeys([idioma for idioma in idiomas if idioma in textos_pre]))
    ultimo_erro = None

    for idioma in idiomas:
        t_pre = textos_pre[idioma]
        try:
            return normalizar_dados_pre_sizing(dados_raw, t_pre), t_pre
        except KeyError as exc:
            ultimo_erro = exc

    raise KeyError(
        "Não foi possível reconhecer as chaves da planilha de pré-dimensionamento. "
        "Gere novamente o arquivo beam_data.xlsx no pre-sizing e tente carregar aqui."
    ) from ultimo_erro


# -----------------------------
# UI text
# -----------------------------
lang = st.session_state.get("lang", "pt")
textos = textos_design()
t = textos.get(lang, textos["pt"])

st.header(t["titulo"])
st.markdown(t["pre"])


# ============================================================
# 1) form para dados do dimensionamento
# ============================================================
with st.form("form_design", clear_on_submit=False):

    st.subheader(t["dados_pre"])
    colA, colB = st.columns(2)

    with colA:
        tipo_secao_longarina = st.selectbox(
            t["entrada_tipo_secao_longarina"],
            t["tipo_secao_longarina"],
            key="tipo_secao_longarina",
        )

        d_cm = st.number_input(t["diametro_longarina"], step=1.0, key="input_d_cm") if str(tipo_secao_longarina).lower() == "circular" else 0.0
        esp_cm = st.number_input(t["espaçamento_entre_longarinas"], step=1.0, key="input_esp_cm")

    with colB:
        tipo_secao_tabuleiro = st.selectbox(
            t["tipo_secao_tabuleiro"],
            t["tipo_secao_tabuleiro_opcoes"],
            key="tipo_secao_tabuleiro",
        )

        bw_cm = 0.0
        h_cm = 0.0
        if str(tipo_secao_tabuleiro).lower() in ["retangular", "rectangular"]:
            bw_cm = st.number_input(t["largura_viga_tabuleiro"], step=1.0, key="input_bw_cm")
            h_cm = st.number_input(t["altura_viga_tabuleiro"], step=1.0, key="input_h_cm")
            esp_tab_cm = st.number_input(t["espaçamento_entre_tabuleiros"], step=1.0, key="input_esp_tab_cm")
        else:
            esp_tab_cm = 0.0

    st.subheader(t["planilha_head"])
    uploaded_file = st.file_uploader(t["texto_up"], type=["xlsx"], key="uploaded_design_xlsx")

    df = None
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.success(t["planilha_sucesso"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info(t["aguardando_upload"])

    submitted_design = st.form_submit_button(t["gerador_projeto"])


# ============================================================
# 2) COMPUTE (Salva tudo no session_state)
# ============================================================
if submitted_design:
    if uploaded_file is None or df is None:
        st.error(t["erro_sem_planilha"])
        st.stop()

    # Se df tem 1 linha, usamos a primeira
    df0 = df.iloc[0]
    try:
        dados_pre, t_pre = normalizar_planilha_pre_sizing(df0, lang)
    except KeyError as exc:
        st.error(str(exc))
        st.stop()

    if any(float(valor) <= 0 for valor in [d_cm, esp_cm, bw_cm, h_cm, esp_tab_cm]):
        st.error(t["erro_geo"])
        st.stop()

    # Instancia o dimensionamento
    projeto_instancia = ProjetoOtimo(
        bw_pista=dados_pre[t_pre["pista"]],
        l=dados_pre[t_pre["entrada_comprimento"]],
        p_gk=dados_pre[f"{t_pre['carga_permanente']} (kPa)"],
        p_rodak=dados_pre[f"{t_pre['carga_roda']} (kN)"],
        p_qk=dados_pre[f"{t_pre['carga_multidao']} (kPa)"],
        a=dados_pre[f"{t_pre['distancia_eixos']} (m)"],
        classe_carregamento=dados_pre[t_pre["classe_carregamento"]],
        classe_madeira=dados_pre[t_pre["classe_madeira"]],
        classe_umidade=dados_pre[t_pre["classe_umidade"]],
        gamma_g=dados_pre[t_pre["gamma_g"]],
        gamma_q=dados_pre[t_pre["gamma_q"]],
        gamma_wc=dados_pre[t_pre["gamma_wc"]],
        gamma_wf=dados_pre[t_pre["gamma_wf"]],
        psi2=dados_pre[t_pre["psi2"]],
        phi=dados_pre[t_pre["considerar_fluencia"]],
        densidade_long=valor_dados_pre_sizing(dados_pre, f"{t_pre['densidade_long']} (kg/m³)", f"{t_pre['densidade_long']} (kg/mÂ³)"),
        densidade_tab=valor_dados_pre_sizing(dados_pre, f"{t_pre['densidade_tab']} (kg/m³)", f"{t_pre['densidade_tab']} (kg/mÂ³)"),
        f_mk_long=valor_dados_pre_sizing(dados_pre, f"{t_pre['f_mk']} (MPa)"),
        f_vk_long=valor_dados_pre_sizing(dados_pre, f"{t_pre['f_vk']} (MPa)"),
        e_modflex_long=valor_dados_pre_sizing(dados_pre, f"{t_pre['e_modflex']} (GPa)"),
        f_mk_tab=valor_dados_pre_sizing(dados_pre, f"{t_pre['f_mk_tab']} (MPa)"),
        d_min=float(d_cm),
        d_max=float(d_cm),
        bw_min=float(bw_cm),
        bw_max=float(bw_cm),
        h_min=float(h_cm),
        h_max=float(h_cm),
        n_min_long=float(esp_cm),
        n_max_long=float(esp_cm),
        n_min_tab=float(esp_tab_cm),
        n_max_tab=float(esp_tab_cm),
        n_checagens=1,
        perc_robustez=0.0,
    )

    # Calcula
    res_calculado = projeto_instancia.calcular_objetivos_restricoes_otimizacao(
        d=float(d_cm), bw=float(bw_cm), h=float(h_cm), n_long=float(esp_cm), n_tab=float(esp_tab_cm)
    )

    # Persistência total dos dados para evitar NameError
    st.session_state["projeto_obj"] = projeto_instancia
    st.session_state["res_design"] = res_calculado
    st.session_state["geo_final"] = {'d': d_cm, 'esp': esp_cm, 'bw': bw_cm, 'h': h_cm, 'esp_tab': esp_tab_cm}
    st.session_state["has_results"] = True


# ============================================================
# 3) DISPLAY & REPORT
# ============================================================
if st.session_state.get("has_results", False):
    # Recupera os dados da sessão
    res = st.session_state["res_design"]
    projeto_persistido = st.session_state["projeto_obj"]
    geo_final = st.session_state["geo_final"]

    st.subheader(t["resultado_head"])
    st.caption(t["resultado_intro"])

    # Verificações — Longarina
    titulo_longarina, longarina_ok = status_global(t["verif_longarina_titulo"], res[2], res[3], res[4])
    with st.expander(titulo_longarina, expanded=not longarina_ok):
        col1, col2, col3 = st.columns(3)
        with col1:
            render_verificacao(t["label_flexao"], res[2], t)
        with col2:
            render_verificacao(t["label_cisalhamento"], res[3], t)
        with col3:
            render_verificacao(t["label_flecha"], res[4], t)

    # Verificações — Tabuleiro
    titulo_tabuleiro, tabuleiro_ok = status_global(t["verif_tabuleiro_titulo"], res[6])
    with st.expander(titulo_tabuleiro, expanded=not tabuleiro_ok):
        render_verificacao(t["label_flexao"], res[6], t)

    # # Auditoria
    # with st.expander(t["resultado_relatorios"], expanded=False):
    #     st.markdown(f"**{t['label_cargas']}**")
    #     st.json(res[-1])
    #     st.markdown(f"**{t['label_longarina']}**")
    #     st.json(res[-2])
    #     st.markdown(f"**{t['label_tabuleiro']}**")
    #     st.json(res[-3])
    
    # Geração do Relatório PDF
    with st.spinner("Preparando PDF..."):
        md_text = gerar_relatorio_final(
            projeto=projeto_persistido, # <--- Usando o objeto da sessão
            res=res,
            geo_real=geo_final # <--- Usando a geometria da sessão
        )
        pdf_bytes = markdown_para_pdf(md_text)

    if pdf_bytes:
        st.download_button(
            label="📄 Baixar Relatório em PDF",
            data=pdf_bytes,
            file_name=f"{t['nome_arquivo']}.pdf",
            mime="application/pdf",
        )
    else:
        st.error("❌ Falha na geração do PDF. Verifique o terminal para ver o erro do LaTeX.")
else:
    st.warning(t["aviso_gerar_primeiro"])
    
