"""Conferência nominal SMath/Python, sem busca e sem modificar o modelo.

Lê expressões e resultados salvos no XML; não executa o SMath Studio.
O interpretador suporta somente a aritmética presente no memorial, com
verificação dimensional em SI. Operações desconhecidas provocam erro.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import hashlib
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent
ARQUIVO_SMATH = RAIZ / "Cálculo Manual - Ponte de Madeira - Longaria Roliça.sm"


@dataclass(frozen=True)
class Quantidade:
    valor: float
    dimensao: tuple[float, float, float] = (0, 0, 0)  # comprimento, massa, tempo


UNIDADES = {
    "m": Quantidade(1, (1, 0, 0)), "cm": Quantidade(0.01, (1, 0, 0)),
    "mm": Quantidade(0.001, (1, 0, 0)), "kg": Quantidade(1, (0, 1, 0)),
    "N": Quantidade(1, (1, 1, -2)), "kN": Quantidade(1000, (1, 1, -2)),
    "Pa": Quantidade(1, (-1, 1, -2)), "kPa": Quantidade(1000, (-1, 1, -2)),
    "MPa": Quantidade(1e6, (-1, 1, -2)),
    # Aceleração padrão; compatível com os resultados numéricos salvos de g.e.
    "g.e": Quantidade(9.80665, (1, 0, -2)),
}


def avaliar_rpn(elementos, ambiente):
    """Avalia tokens postfix do XML, sem eval/exec ou resolução externa."""
    pilha = []
    for e in elementos:
        texto, tipo = e.text, e.get("type")
        if tipo == "bracket":
            continue
        if tipo == "operand":
            if e.get("style") == "unit":
                q = UNIDADES[texto]
            elif texto == "π":
                q = Quantidade(math.pi)
            elif texto in ambiente:
                q = ambiente[texto]
            else:
                try:
                    q = Quantidade(float(texto))
                except ValueError as exc:
                    raise ValueError(f"Símbolo não definido no SMath: {texto}") from exc
            pilha.append((q, texto))
            continue
        if tipo != "operator":
            raise ValueError(f"Token não suportado: {ET.tostring(e, encoding='unicode')}")
        n = int(e.get("args", "0"))
        if n == 1 and texto == "-":
            a, expr = pilha.pop()
            pilha.append((Quantidade(-a.valor, a.dimensao), f"(-{expr})"))
            continue
        if n != 2 or texto not in {"+", "-", "*", "/", "^"}:
            raise ValueError(f"Operação não suportada: {texto}/{n}")
        b, eb = pilha.pop()
        a, ea = pilha.pop()
        if texto in {"+", "-"}:
            if a.dimensao != b.dimensao:
                raise ValueError(f"Dimensões incompatíveis: {ea} {texto} {eb}")
            q = Quantidade(a.valor + (1 if texto == "+" else -1) * b.valor, a.dimensao)
        elif texto in {"*", "/"}:
            sinal = 1 if texto == "*" else -1
            dim = tuple(x + sinal * y for x, y in zip(a.dimensao, b.dimensao))
            q = Quantidade(a.valor * b.valor if texto == "*" else a.valor / b.valor, dim)
        else:
            if b.dimensao != (0, 0, 0):
                raise ValueError("Expoente com dimensão física")
            q = Quantidade(a.valor ** b.valor, tuple(x * b.valor for x in a.dimensao))
        if not math.isfinite(q.valor):
            raise ValueError(f"Resultado não finito: {ea} {texto} {eb}")
        pilha.append((q, f"({ea} {texto} {eb})"))
    if len(pilha) != 1:
        raise ValueError(f"Expressão incompleta: {pilha}")
    return pilha[0]


def ler_smath(caminho=ARQUIVO_SMATH):
    """Retorna ambiente SI e registros com referência salva e tolerância de impressão.

    A tolerância é meia unidade do último algarismo efetivamente salvo no XML,
    não uma tolerância percentual escolhida para encobrir divergências.
    """
    caminho = Path(caminho)
    root = ET.fromstring(caminho.read_bytes())
    ns = {"s": "http://smath.info/schemas/worksheet/1.0"}
    ambiente, registros = {}, []
    regioes = sorted(root.findall("s:regions/s:region", ns),
                     key=lambda r: (float(r.get("top")), float(r.get("left"))))
    for reg in regioes:
        matematica = reg.find("s:math", ns)
        if matematica is None:
            continue
        elementos = list(matematica.find("s:input", ns))
        atribuicao = elementos[-1].text == ":"
        nome = elementos[0].text if atribuicao else None
        q, expr = avaliar_rpn(elementos[1:-1] if atribuicao else elementos, ambiente)
        if atribuicao:
            ambiente[nome] = q
        resultado = matematica.find("s:result", ns)
        contrato = matematica.find("s:contract", ns)
        salvo = tolerancia = None
        if resultado is not None:
            qs, _ = avaliar_rpn(list(resultado), {})
            fator = 1.0
            if contrato is not None:
                unidade, _ = avaliar_rpn(list(contrato), {})
                if qs.dimensao != (0, 0, 0):
                    raise ValueError("Resultado com unidade e contrato: revisar formato SMath")
                qs = Quantidade(qs.valor * unidade.valor, unidade.dimensao)
                fator = unidade.valor
            if qs.dimensao != q.dimensao:
                raise ValueError(f"Dimensão do resultado salvo diverge: {nome or expr}")
            salvo = qs.valor
            # Formato desta planilha: mantissa numérica seguida de unidades/potência de dez.
            mantissa = Decimal(list(resultado)[0].text)
            passo = float(Decimal(10) ** mantissa.as_tuple().exponent)
            escala = abs(salvo / float(mantissa)) if mantissa else fator
            tolerancia = 0.5 * passo * escala + 1e-12 * max(abs(q.valor), 1e-12)
        registros.append(dict(chave=nome or expr, expressao=expr, si=q.valor,
                              dimensao=q.dimensao, salvo_si=salvo, tolerancia_si=tolerancia,
                              confere_cache=None if salvo is None else abs(q.valor-salvo) <= tolerancia,
                              top=float(reg.get("top"))))
    return ambiente, pd.DataFrame(registros)


def entradas_smath(ambiente):
    """Entradas literais do memorial; unidades explicitadas nas chaves."""
    v = lambda nome: ambiente[nome].valor
    return dict(d_m=v("d"), bw_m=v("b.w"), h_m=v("h"), L_m=v("L"),
                pista_m=v("b.w.pista"), esp_long_m=v("esp.long.corr"),
                esp_tab_m=v("esp.tab.corr"), n_tab=int(v("n.tab")),
                rho_kg_m3=v("γ.D40"), gravidade=UNIDADES["g.e"].valor,
                p_gk_kpa=v("p.gk")/1000, p_qk_kpa=v("q.v")/1000,
                roda_kn=v("P.rv")/1000, a_m=v("a"), ar_m=v("a.r"),
                fmk_kpa=v("f.c0.k")/1000, fvk_kpa=v("f.v0.k")/1000,
                E_kpa=v("E.c0.med")/1000, gamma_g=v("γ.g"), gamma_q=v("γ.q"),
                gamma_wf=v("γ.w.c"), gamma_wc=v("γ.w.v"), psi2=v("ψ.2"), phi=v("ϕ"),
                classe_carregamento="curta duração", classe_madeira="madeira natural",
                classe_umidade=3)


def avaliar_python(p):
    """Executa as funções de produção com as MESMAS entradas fixas do SMath.

    Não corrige nem substitui CIV, ELS ou resistência dentro de madeiras.py.
    A montagem das cargas usa os espaçamentos literais e g.e do memorial;
    a acomodação geométrica do otimizador é conferida separadamente.
    """
    import madeiras as m
    pl = m.prop_madeiras({"d": p["d_m"]})
    pt = m.prop_madeiras({"b_w": p["bw_m"], "h": p["h_m"]})
    gamma = p["rho_kg_m3"] * p["gravidade"] / 1000
    peso_long = m.peso_proprio_longarina(gamma, pl[0])
    peso_tab = gamma * p["n_tab"] * pt[0] / p["L_m"]
    carga_long = (p["p_gk_kpa"] + peso_tab) * p["esp_long_m"] + peso_long
    carga_q = p["p_qk_kpa"] * p["esp_long_m"]
    carga_tab = (p["p_gk_kpa"] + peso_tab) * p["bw_m"]
    rm, rv, rf, rl = m.checagem_completa_longarina_madeira_flexao(
        {"d": p["d_m"]}, carga_long, carga_q, p["roda_kn"], p["a_m"], p["L_m"],
        p["classe_carregamento"], p["classe_madeira"], p["classe_umidade"],
        p["gamma_g"], p["gamma_q"], p["gamma_wf"], p["gamma_wc"], p["psi2"],
        p["phi"], p["fmk_kpa"], p["fvk_kpa"], p["E_kpa"])
    rt, rlt = m.checagem_completa_tabuleiro_madeira_flexao(
        {"b_w": p["bw_m"], "h": p["h_m"]}, carga_tab, p["roda_kn"], p["esp_long_m"],
        p["classe_carregamento"], p["classe_madeira"], p["classe_umidade"],
        p["gamma_g"], p["gamma_q"], p["gamma_wf"], p["fmk_kpa"])
    valores = {
        "A.long": pl[0], "I.long": pl[3], "W.long": pl[1],
        "A.tab": pt[0], "I.tab": pt[3], "W.tab": pt[1], "S": pl[5],
        "k.mod": rm["k_mod"], "f.c0.d": rm["f_md [kPa]"]/1000,
        "f.m.d": rm["f_md [kPa]"]/1000, "f.v0.d": rv["f_vd [kPa]"]/1000,
        "G.long": peso_long, "p.tab": peso_tab, "P.gk.long": carga_long, "q": carga_q,
        "M.g.k": rl["m_gk [kN.m]"], "M.q.k0": m.momento_max_carga_variavel(p["L_m"], p["roda_kn"], carga_q, p["a_m"]),
        "CIV": rl["coeficiente_impacto_vertical"], "M.q.k": rl["m_qk [kN.m]"],
        "Q.g.k": rl["v_gk [kN]"], "Q.q.k0": m.cortante_max_carga_variavel(p["L_m"], p["roda_kn"], carga_q, p["a_m"], p["d_m"]),
        "Q.q.k": rl["v_qk [kN]"], "δ.gk": rl["delta_gk [m]"]*1000,
        "δ.q.k": rl["delta_qk [m]"]*1000, "M.sd": rm["m_sd [kN.m]"],
        "Q.sd": rv["v_sd [kN]"], "σ.Mx.d": rm["sigma_x [kPa]"]/1000,
        "τ": rv["tau_sd [kPa]"]/1000,
        "(σ.Mx.d / f.m.d)": rm["g_otimiz [-]"]+1,
        "(τ / f.v0.d)": rv["g_otimiz [-]"]+1,
        "δ.inst": (rl["delta_gk [m]"]+rl["delta_qk [m]"])*1000,
        "δ.fin": rf["delta_fluencia [m]"]*1000,
        "(L / 500)": rf["delta_lim_variavel [m]"]*1000,
        "(L / 350)": rf["delta_lim_total [m]"]*1000,
        "p.gtab.k": carga_tab, "M.gk.tab": rlt["m_gk [kN.m]"],
        "M.qk.tab.0": m.momento_max_carga_variavel_tabuleiro(p["roda_kn"], p["esp_long_m"], p["ar_m"]),
        "M.q.tab": rlt["m_qk [kN.m]"], "M.sd.tab": rt["m_sd [kN.m]"],
        "σ.Mx.d.tab": rt["sigma_x [kPa]"]/1000,
        "(σ.Mx.d.tab / f.m.d)": rt["g_otimiz [-]"]+1,
    }
    return dict(valores=valores, propriedades_long=pl, propriedades_tab=pt,
                flexao=rm, cisalhamento=rv, flecha=rf, longarina=rl,
                flexao_tab=rt, tabuleiro=rlt)


ESCALAS = {
    "A.long": (1, "m²"), "I.long": (1, "m⁴"), "W.long": (1, "m³"),
    "A.tab": (1, "m²"), "I.tab": (1, "m⁴"), "W.tab": (1, "m³"), "S": (1, "m³"),
    **{k: (1e6, "MPa") for k in ["f.c0.d", "f.m.d", "f.v0.d", "σ.Mx.d", "τ", "σ.Mx.d.tab"]},
    **{k: (1000, "kN/m") for k in ["G.long", "P.gk.long", "q", "p.gtab.k"]},
    "p.tab": (1000, "kPa"),
    **{k: (1000, "kN.m") for k in ["M.g.k", "M.q.k0", "M.q.k", "M.sd", "M.gk.tab", "M.qk.tab.0", "M.q.tab", "M.sd.tab"]},
    **{k: (1000, "kN") for k in ["Q.g.k", "Q.q.k0", "Q.q.k", "Q.sd"]},
    **{k: (0.001, "mm") for k in ["δ.gk", "δ.q.k", "δ.inst", "δ.fin", "(L / 500)", "(L / 350)"]},
}


def comparar(registros, valores):
    linhas = []
    for chave, valor in valores.items():
        r = registros.loc[registros.chave == chave].iloc[0]
        escala, unidade = ESCALAS.get(chave, (1, "–"))
        ref = r.si / escala
        salvo = None if pd.isna(r.salvo_si) else r.salvo_si / escala
        tol = 1e-10 * max(abs(ref), 1e-9)
        if abs(valor-ref) <= tol:
            status = "COINCIDE"
        elif salvo is not None and abs(valor-salvo) <= r.tolerancia_si/escala:
            status = "COMPATÍVEL COM ARREDONDAMENTO"
        else:
            status = "DIVERGE"
        linhas.append(dict(grandeza=chave, unidade=unidade, smath_salvo=salvo,
                           smath_recalculado=ref, python=valor,
                           diferenca=valor-ref,
                           diferenca_pct=100*(valor-ref)/ref if ref else np.nan, status=status))
    return pd.DataFrame(linhas)


def avaliar_otimizador(p, *, rho=0, n_checagens=1):
    """Chama ProjetoOtimo, incluindo acomodação e conversões usadas pelo lote."""
    import madeiras as m
    projeto = m.ProjetoOtimo(
        bw_pista=p["pista_m"]*100, l=p["L_m"]*100, p_gk=p["p_gk_kpa"],
        p_rodak=p["roda_kn"], p_qk=p["p_qk_kpa"], a=p["a_m"],
        classe_carregamento=p["classe_carregamento"], classe_madeira=p["classe_madeira"],
        classe_umidade=p["classe_umidade"], gamma_g=p["gamma_g"], gamma_q=p["gamma_q"],
        gamma_wf=p["gamma_wf"], gamma_wc=p["gamma_wc"], psi2=p["psi2"], phi=p["phi"],
        densidade_long=p["rho_kg_m3"], densidade_tab=p["rho_kg_m3"],
        f_mk_long=p["fmk_kpa"]/1000, f_vk_long=p["fvk_kpa"]/1000,
        e_modflex_long=p["E_kpa"]/1e6, f_mk_tab=p["fmk_kpa"]/1000,
        d_min=30, d_max=150, bw_min=5, bw_max=60, h_min=5, h_max=60,
        n_min_long=30, n_max_long=200, n_min_tab=2, n_max_tab=5,
        n_checagens=n_checagens, perc_robustez=rho)
    x = np.array([p[k]*100 for k in ["d_m", "bw_m", "h_m", "esp_long_m", "esp_tab_m"]])
    # Espaçamentos corrigidos literais são usados como propostas; a rotina real
    # os acomoda novamente. Não são apresentados como variáveis ótimas novas.
    resultado = projeto.calcular_objetivos_restricoes_otimizacao(*x)
    out = {}
    projeto._evaluate(x, out)
    return projeto, x, resultado, out


def auditar_els():
    """Contraexemplo: ELS total passa, ELS variável falha no código corrente."""
    import madeiras as m
    r = m.checagem_flecha_viga(5, 0, 0.015, 0.3, 0.8)
    return dict(entradas=dict(l=5, delta_gk=0, delta_qk=0.015, psi2=0.3, phi=0.8),
                resultado=r,
                sinais_coerentes=(r["g_otimiz [-]"] <= 0) == (r["g_confia [m]"] >= 0))


def identidade(caminho):
    return hashlib.sha256(Path(caminho).read_bytes()).hexdigest()


if __name__ == "__main__":
    # Este módulo só definia funções; rodar o arquivo direto não imprimia nada.
    # Este bloco executa a conferência nominal completa e imprime a tabela
    # SMath x Python, com as divergências (fora da tolerância do SMath) primeiro.
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 160)
    pd.set_option("display.float_format", lambda x: f"{x:.6g}")

    print(f"Arquivo SMath: {ARQUIVO_SMATH.name}")
    print(f"SHA-256: {identidade(ARQUIVO_SMATH)[:16]}...\n")

    ambiente, registros = ler_smath()
    entradas = entradas_smath(ambiente)
    resultado_py = avaliar_python(entradas)
    tabela = comparar(registros, resultado_py["valores"])

    ordem = {"DIVERGE": 0, "COMPATÍVEL COM ARREDONDAMENTO": 1, "COINCIDE": 2}
    tabela = (tabela.assign(_ordem=tabela.status.map(ordem))
                     .sort_values(["_ordem", "grandeza"])
                     .drop(columns="_ordem"))

    print(tabela.to_string(index=False))

    n_diverge = int((tabela.status == "DIVERGE").sum())
    n_total = len(tabela)
    print(f"\n{n_diverge} de {n_total} grandezas DIVERGEM (fora da tolerância de "
          f"arredondamento do SMath). Veja a coluna 'diferenca_pct' para o tamanho "
          f"de cada divergência.")
