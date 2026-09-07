"""Pipeline headless de pré-dimensionamento.

Reproduz o mesmo caminho de cálculo da página Streamlit `pages/pre_sizing.py`, sem
runtime de UI, para que um notebook possa processar em lote uma planilha com uma linha
por simulação e gravar os mesmos artefatos, inclusive o `pre_sizing_package.zip`.

É viável porque `madeiras.py` não importa Streamlit: todo o cálculo já é puro. O que
estava preso à interface era apenas a cola — montar o dicionário de entrada, renomear
colunas, serializar figuras e montar o pacote. É essa cola que vive aqui.

Este módulo é uma transcrição fiel, função a função e na mesma ordem, do bloco
`if submitted_design:` de `pages/pre_sizing.py` (linhas 453-672) e do bloco de Sobol
(linhas 739-762). Qualquer divergência de resultado entre os dois é bug daqui.
"""

from __future__ import annotations

import hashlib
import io
import time
import traceback
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from madeiras import (
    chamando_nsga2,
    chamar_sobol,
    estatistica_descritiva_variaveis,
    fronteira_pareto,
    geracao_estabilizacao_hipervolume,
    historico_hipervolume,
    montar_excel,
    montar_excel_df,
    normalizar_dados_pre_sizing,
    plot_boxplot_variaveis_fronteira,
    plot_convergencia_hipervolume,
    plot_sobol_total_indices,
    textos_pre_sizing_l,
)

# --------------------------------------------------------------------------------------
# Constantes
# --------------------------------------------------------------------------------------

PREFIXO_CONFIG = "cfg_"
COLUNA_ID = "id"

# Transcrição do bloco de renomeação de pages/pre_sizing.py:583-616. A ordem das chaves
# define a ordem das colunas do XLSX de resultados, e é esse invariante que mantém a
# compatibilidade de schema com as saídas já geradas pela interface.
MAPA_COLUNAS_RESULTADO = {
    "pt": {
        "d_cm": "d [cm]",
        "esp_cm": "esp [cm]",
        "bw_cm": "bw [cm]",
        "h_cm": "h [cm]",
        "esp_tab_cm": "esp tab [cm]",
        "of_volume_m3": "volume [m³]",
        "of_fator_flecha": "delta [-]",
        "longarina_g_m": "flex lim beam [(Ms-Mr)/Mr]",
        "longarina_g_v": "cis lim beam [(Vs-Vr)/Vr]",
        "longarina_g_f": "delta lim beam [(ps-pr)/pr]",
        "tabuleiro_g_m": "flex lim deck [(Ms-Mr)/Mr]",
        "longarina_g_esp": "spacing beam",
        "tabuleiro_g_esp": "spacing deck",
    },
    "en": {
        "d_cm": "d [cm]",
        "esp_cm": "esp [cm]",
        "bw_cm": "bw [cm]",
        "h_cm": "h [cm]",
        "deck_spacing_cm": "esp tab [cm]",
        "of_volume_m3": "volume [m³]",
        "of_deflection_factor": "delta [-]",
        "beam_g_m": "flex lim beam [(Ms-Mr)/Mr]",
        "beam_g_v": "cis lim beam [(Vs-Vr)/Vr]",
        "beam_g_f": "delta lim beam [(ps-pr)/pr]",
        "deck_g_m": "flex lim deck [(Ms-Mr)/Mr]",
        "beam_g_spacing": "spacing beam",
        "deck_g_spacing": "spacing deck",
    },
}

# Coluna do segundo objetivo e do espaçamento do tabuleiro, por idioma.
COLUNA_OBJ_Y = {"pt": "of_fator_flecha", "en": "of_deflection_factor"}
COLUNA_ESP_TAB = {"pt": "esp_tab_cm", "en": "deck_spacing_cm"}

# Ordem do boxplot e da estatística descritiva (pages/pre_sizing.py:626). Atenção: NÃO é a
# ordem das colunas do DataFrame de resultados acima, que é d, esp, bw, h, esp_tab. Esta
# aqui tem de casar com t["fronteira_variaveis_labels"] = [d, bw, h, Esp. long., Esp. tab.];
# trocar uma pela outra rotularia errado todos os boxplots e tabelas de estatística.
def colunas_variaveis(idioma: str = "pt") -> list[str]:
    return ["d_cm", "bw_cm", "h_cm", "esp_cm", COLUNA_ESP_TAB[idioma]]


# Os 9 membros do pacote, na ordem em que montar_zip_pacote() os insere.
NOMES_MEMBROS_ZIP = (
    "beam_data.xlsx",
    "pre_sizing_results_optimized.xlsx",
    "pareto_frontier.png",
    "design_variables_boxplot.png",
    "hypervolume_convergence.png",
    "sobol_total_indices.png",
    "design_variables_statistics.xlsx",
    "hypervolume_convergence.csv",
    "sobol_total_indices.xlsx",
)

NOME_ZIP = "pre_sizing_package.zip"

# Vocabulário aceito por k_mod_madeira (madeiras.py:652-664), em minúsculas.
CLASSES_CARREGAMENTO = {
    "permanente",
    "longa duração",
    "média duração",
    "curta duração",
    "instantânea",
}
CLASSES_MADEIRA = {"madeira natural", "madeira recomposta"}
CLASSES_UMIDADE = {1, 2, 3, 4}


# --------------------------------------------------------------------------------------
# Configuração
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class LimitesBusca:
    """Intervalos de busca das cinco variáveis de projeto, em cm.

    Não vêm do `beam_data.xlsx`: na interface são widgets, passados como argumentos
    separados a `chamando_nsga2` e `chamar_sobol`. Os padrões abaixo são os valores das
    execuções já publicadas.

    `esp_long` e `esp_tab` são ESPAÇAMENTOS em cm, não contagens de peças, apesar de
    `madeiras` chamá-los de `n_long` e `n_tab`.
    """

    d: tuple[float, float] = (30.0, 150.0)
    bw: tuple[float, float] = (5.0, 60.0)
    h: tuple[float, float] = (5.0, 60.0)
    esp_long: tuple[float, float] = (30.0, 200.0)
    esp_tab: tuple[float, float] = (2.0, 5.0)

    def como_listas(self) -> tuple[list, list, list, list, list]:
        """Devolve (ds, bws, hs, n_long, n_tab) no formato que `madeiras` espera."""
        return (
            [float(self.d[0]), float(self.d[1])],
            [float(self.bw[0]), float(self.bw[1])],
            [float(self.h[0]), float(self.h[1])],
            [float(self.esp_long[0]), float(self.esp_long[1])],
            [float(self.esp_tab[0]), float(self.esp_tab[1])],
        )


@dataclass(frozen=True)
class ParametrosAlgoritmo:
    """Parâmetros do NSGA-II. Padrões iguais aos de `chamando_nsga2`."""

    pop_size: int = 50
    n_gen: int = 150
    n_checagens: int = 30
    verbose: bool = False


@dataclass(frozen=True)
class ConfigSobol:
    """Sobol por caso. Com `ativo=False` o pacote sai sem os dois membros de Sobol."""

    ativo: bool = True
    n_samples: int = 20000


@dataclass(frozen=True)
class CasoBatch:
    """Uma linha da planilha de lote, já separada em dados e configuração.

    `percentual_robustez` não tem campo aqui de propósito: `chamando_nsga2` lê o valor de
    dentro de `dados` (madeiras.py:2609). Para varrer robustez, varie a coluna
    "Percentual de robustez" da planilha.
    """

    id: str
    dados: dict
    limites: LimitesBusca = LimitesBusca()
    algoritmo: ParametrosAlgoritmo = ParametrosAlgoritmo()
    sobol: ConfigSobol = ConfigSobol()
    subdiretorio: str | None = None
    ativo: bool = True

    def destino(self, raiz: Path) -> Path:
        return Path(raiz) / (self.subdiretorio or f"simulacao_{self.id}")


# --------------------------------------------------------------------------------------
# Artefatos
# --------------------------------------------------------------------------------------


@dataclass
class ArtefatosCaso:
    """Tudo que uma execução produz: o análogo puro do `st.session_state` da interface."""

    id: str
    dados: dict
    status: str = "ok"  # "ok" | "erro_nsga" | "erro"
    erro: str | None = None
    traceback: str | None = None
    avisos: list[str] = field(default_factory=list)
    tempos: dict[str, float] = field(default_factory=dict)

    df_resultados: pd.DataFrame | None = None
    df_estatistica: pd.DataFrame | None = None
    hist_hv: pd.DataFrame | None = None
    gen_estab: int | None = None
    sobol_result: dict | None = None

    excel_bytes_entrada: bytes | None = None
    excel_bytes_resultados: bytes | None = None
    fig_png: bytes | None = None
    boxplot_png: bytes | None = None
    convergencia_png: bytes | None = None
    sobol_png: bytes | None = None

    def membros(self) -> list[tuple[str, bytes | None]]:
        """Réplica da lista `itens` de montar_zip_pacote (pages/pre_sizing.py:114-135):
        mesma ordem e mesmas condições de inclusão."""
        itens: list[tuple[str, bytes | None]] = [
            ("beam_data.xlsx", self.excel_bytes_entrada),
            ("pre_sizing_results_optimized.xlsx", self.excel_bytes_resultados),
            ("pareto_frontier.png", self.fig_png),
            ("design_variables_boxplot.png", self.boxplot_png),
            ("hypervolume_convergence.png", self.convergencia_png),
            ("sobol_total_indices.png", self.sobol_png),
        ]

        if self.df_estatistica is not None and not self.df_estatistica.empty:
            itens.append(
                ("design_variables_statistics.xlsx", montar_excel_df(self.df_estatistica))
            )

        if self.hist_hv is not None and not self.hist_hv.empty:
            itens.append(
                ("hypervolume_convergence.csv", self.hist_hv.to_csv(index=False).encode("utf-8"))
            )

        if self.sobol_result is not None:
            itens.append(
                ("sobol_total_indices.xlsx", montar_excel_df(self.sobol_result["total_order"]))
            )

        return itens


# --------------------------------------------------------------------------------------
# Núcleo
# --------------------------------------------------------------------------------------


def textos(idioma: str = "pt") -> dict:
    """Atalho para `textos_pre_sizing_l()[idioma]`."""
    return textos_pre_sizing_l()[idioma]


def figura_para_png(fig, dpi: int = 200) -> bytes:
    """Serializa uma figura matplotlib em PNG e libera a memória associada.

    Cópia de pages/pre_sizing.py:97-103. O `plt.close` é essencial em lote: sem ele as
    figuras se acumulam e o matplotlib passa a avisar de excesso de figuras abertas.
    """
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()


def montar_zip(artefatos: ArtefatosCaso) -> bytes:
    """Monta o pacote com planilhas e figuras disponíveis, como o download da interface."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for nome, conteudo in artefatos.membros():
            if conteudo:
                zf.writestr(nome, conteudo)
    buffer.seek(0)
    return buffer.getvalue()


def rodar_caso(
    caso: CasoBatch,
    *,
    t: dict | None = None,
    idioma: str = "pt",
    capturar_erros: bool = True,
) -> ArtefatosCaso:
    """Executa um caso pelo mesmo caminho de cálculo da interface.

    Ordem replicada de pages/pre_sizing.py:558-672 e 739-762.

    Uma célula sem solução viável devolve `status="erro_nsga"` com artefatos parciais.
    Isso é resultado legítimo de célula difícil, não quebra do lote. Falha de hipervolume
    ou de Sobol vira aviso, e o pacote sai com menos membros.
    """
    t = t or textos(idioma)
    art = ArtefatosCaso(id=caso.id, dados=dict(caso.dados))
    ds, bws, hs, n_long, n_tab = caso.limites.como_listas()
    t0_total = time.perf_counter()

    try:
        art.excel_bytes_entrada = montar_excel(caso.dados)

        t0 = time.perf_counter()
        try:
            res_nsga, callback_hist = chamando_nsga2(
                caso.dados,
                ds,
                bws,
                hs,
                n_long,
                n_tab,
                t,
                verbose=caso.algoritmo.verbose,
                salvar_historico=True,
                pop_size=caso.algoritmo.pop_size,
                n_gen=caso.algoritmo.n_gen,
                n_checagens=caso.algoritmo.n_checagens,
            )
        except ValueError as exc:
            art.status = "erro_nsga"
            art.erro = str(exc)
            art.tempos["nsga2"] = time.perf_counter() - t0
            art.tempos["total"] = time.perf_counter() - t0_total
            return art
        art.tempos["nsga2"] = time.perf_counter() - t0

        # Falha de convergência não derruba o caso, exatamente como na interface.
        try:
            art.hist_hv = historico_hipervolume(callback_hist)
            art.gen_estab = geracao_estabilizacao_hipervolume(art.hist_hv)
        except Exception as exc:
            art.avisos.append(f"Convergência não pôde ser calculada: {exc}")

        mapa = MAPA_COLUNAS_RESULTADO[idioma]
        art.df_resultados = pd.DataFrame(
            {destino: res_nsga[origem].tolist() for destino, origem in mapa.items()}
        )
        art.excel_bytes_resultados = montar_excel_df(art.df_resultados)

        cols = colunas_variaveis(idioma)
        x = art.df_resultados["of_volume_m3"].to_numpy()
        y = art.df_resultados[COLUNA_OBJ_Y[idioma]].to_numpy()

        try:
            art.fig_png = figura_para_png(
                fronteira_pareto(x.tolist(), y.tolist(), t["tag_x_fig"], t["tag_y_fig"])
            )
            art.boxplot_png = figura_para_png(
                plot_boxplot_variaveis_fronteira(
                    art.df_resultados,
                    cols,
                    t["fronteira_variaveis_labels"],
                    t["fronteira_variaveis_y"],
                )
            )
            if art.hist_hv is not None:
                art.convergencia_png = figura_para_png(
                    plot_convergencia_hipervolume(
                        {t["convergencia_serie"]: art.hist_hv},
                        label_x=t["convergencia_x"],
                        label_y=t["convergencia_y"],
                    )
                )
        finally:
            plt.close("all")

        art.df_estatistica = estatistica_descritiva_variaveis(
            art.df_resultados,
            cols,
            t["fronteira_variaveis_labels"],
            t["estatistica_colunas"],
        )

        if caso.sobol.ativo:
            t0 = time.perf_counter()
            try:
                art.sobol_result = chamar_sobol(
                    caso.dados,
                    ds,
                    bws,
                    hs,
                    n_long,
                    n_tab,
                    t,
                    n_samples=caso.sobol.n_samples,
                    verbose=caso.algoritmo.verbose,
                )
                art.sobol_png = figura_para_png(
                    plot_sobol_total_indices(
                        art.sobol_result["total_order"],
                        label_x=t["sobol_axis_constraints"],
                        label_y=t["sobol_axis_variables"],
                        x_labels=t["sobol_constraint_labels"],
                        y_labels=t["sobol_variable_labels"],
                    )
                )
            except Exception as exc:
                art.sobol_result = None
                art.sobol_png = None
                art.avisos.append(f"Sobol não pôde ser calculado: {exc}")
            finally:
                plt.close("all")
                art.tempos["sobol"] = time.perf_counter() - t0

    except Exception as exc:
        if not capturar_erros:
            raise
        art.status = "erro"
        art.erro = str(exc)
        art.traceback = traceback.format_exc()

    art.tempos["total"] = time.perf_counter() - t0_total
    return art


# --------------------------------------------------------------------------------------
# Gravação
# --------------------------------------------------------------------------------------


def salvar_caso(
    art: ArtefatosCaso,
    destino: Path,
    *,
    escrever_soltos: bool = True,
    escrever_zip: bool = True,
    sobrescrever: bool = False,
) -> list[Path]:
    """Grava os artefatos soltos e o `pre_sizing_package.zip` em `destino`.

    Espelha o layout de `simulacaoes_/simulacao_C_XX/`.

    Com `sobrescrever=False` recusa gravar num diretório que já contenha algum dos
    arquivos de saída. É proteção deliberada: as pastas das simulações publicadas contêm
    planilhas editadas à mão para o artigo e não estão versionadas no git.
    """
    destino = Path(destino)
    alvos = list(NOMES_MEMBROS_ZIP) + [NOME_ZIP]

    if not sobrescrever and destino.exists():
        existentes = [n for n in alvos if (destino / n).exists()]
        if existentes:
            raise FileExistsError(
                f"{destino} já contém {len(existentes)} arquivo(s) de saída "
                f"(ex.: {existentes[0]}). Use sobrescrever=True se for mesmo a intenção."
            )

    destino.mkdir(parents=True, exist_ok=True)
    escritos: list[Path] = []

    if escrever_soltos:
        for nome, conteudo in art.membros():
            if conteudo:
                caminho = destino / nome
                caminho.write_bytes(conteudo)
                escritos.append(caminho)

    if escrever_zip and any(c for _, c in art.membros()):
        caminho = destino / NOME_ZIP
        caminho.write_bytes(montar_zip(art))
        escritos.append(caminho)

    if art.erro:
        caminho = destino / "_erro.txt"
        caminho.write_text(art.traceback or art.erro, encoding="utf-8")
        escritos.append(caminho)

    return escritos


def resumo_lote(artefatos: list[ArtefatosCaso]) -> pd.DataFrame:
    """Tabela de status, indicadores e tempos por caso.

    A média de `t_total_s` entre os casos com status "ok" é o tempo médio de
    processamento por célula.
    """
    linhas = []
    for a in artefatos:
        df = a.df_resultados
        linhas.append(
            {
                "id": a.id,
                "status": a.status,
                "n_solucoes": None if df is None else len(df),
                "volume_min": None if df is None else float(df["of_volume_m3"].min()),
                "volume_max": None if df is None else float(df["of_volume_m3"].max()),
                "hv_final": None
                if a.hist_hv is None or a.hist_hv.empty
                else float(a.hist_hv["hipervolume"].iloc[-1]),
                "gen_estab": a.gen_estab,
                "sobol_ok": a.sobol_result is not None,
                "t_nsga2_s": a.tempos.get("nsga2"),
                "t_sobol_s": a.tempos.get("sobol"),
                "t_total_s": a.tempos.get("total"),
                "avisos": " | ".join(a.avisos) if a.avisos else None,
                "erro": a.erro,
            }
        )
    return pd.DataFrame(linhas)


def rodar_lote(
    casos: list[CasoBatch],
    destino_raiz: Path,
    *,
    t: dict | None = None,
    idioma: str = "pt",
    callback=None,
    pular_existentes: bool = False,
    sobrescrever: bool = False,
) -> tuple[list[ArtefatosCaso], pd.DataFrame]:
    """Roda os casos em série, cronometrando e gravando cada um assim que termina.

    Série e não paralelo: NSGA-II e Sobol já saturam a CPU, e a ordem estável preserva o
    determinismo. Gravar por caso dentro do laço faz um lote longo sobreviver a uma queda
    no meio; `pular_existentes=True` retoma de onde parou.

    `callback(i, n, artefatos)` é chamado após cada caso, para progresso.
    """
    t = t or textos(idioma)
    destino_raiz = Path(destino_raiz)
    destino_raiz.mkdir(parents=True, exist_ok=True)

    ativos = [c for c in casos if c.ativo]
    artefatos: list[ArtefatosCaso] = []

    for i, caso in enumerate(ativos, start=1):
        destino = caso.destino(destino_raiz)
        if pular_existentes and (destino / NOME_ZIP).exists():
            continue

        art = rodar_caso(caso, t=t, idioma=idioma)
        salvar_caso(art, destino, sobrescrever=sobrescrever or pular_existentes)
        artefatos.append(art)

        resumo = resumo_lote(artefatos)
        resumo.to_excel(destino_raiz / "_lote_resumo.xlsx", index=False)

        if callback is not None:
            callback(i, len(ativos), art)

    return artefatos, resumo_lote(artefatos)


# --------------------------------------------------------------------------------------
# Planilha de casos
# --------------------------------------------------------------------------------------


def _para_bool(valor, padrao: bool = True) -> bool:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return padrao
    if isinstance(valor, (bool, int)):
        return bool(valor)
    return str(valor).strip().lower() in {"1", "true", "verdadeiro", "sim", "yes", "x", "s"}


def _cfg(linha: dict, nome: str, padrao):
    valor = linha.get(PREFIXO_CONFIG + nome)
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return padrao
    return valor


def _validar_dados(dados: dict, t: dict, id_caso: str) -> None:
    try:
        normalizados = normalizar_dados_pre_sizing(dados, t)
    except KeyError as exc:
        raise ValueError(f"Caso {id_caso}: campo de entrada ausente. {exc}") from exc

    faltando = [k for k, v in normalizados.items() if v is None or pd.isna(v)]
    if faltando:
        raise ValueError(f"Caso {id_caso}: campos vazios na planilha: {faltando}")

    carregamento = str(normalizados[t["classe_carregamento"]]).strip().lower()
    if carregamento not in CLASSES_CARREGAMENTO:
        raise ValueError(
            f"Caso {id_caso}: classe de carregamento {carregamento!r} fora do vocabulário "
            f"aceito {sorted(CLASSES_CARREGAMENTO)}."
        )

    madeira = str(normalizados[t["classe_madeira"]]).strip().lower()
    if madeira not in CLASSES_MADEIRA:
        raise ValueError(
            f"Caso {id_caso}: classe de madeira {madeira!r} fora do vocabulário aceito "
            f"{sorted(CLASSES_MADEIRA)}."
        )

    umidade = int(normalizados[t["classe_umidade"]])
    if umidade not in CLASSES_UMIDADE:
        raise ValueError(f"Caso {id_caso}: classe de umidade {umidade} fora de {{1,2,3,4}}.")


def ler_planilha_casos(caminho, *, idioma: str = "pt", aba: str = "Casos") -> list[CasoBatch]:
    """Lê a planilha de lote e devolve um `CasoBatch` por linha.

    Separação de dados e configuração pelo prefixo: toda coluna cujo nome começa com
    `cfg_`, mais a coluna `id`, é configuração; todas as demais compõem `dados`, na ordem
    original. É robusto porque os cabeçalhos de entrada são frases longas em português e
    nenhum deles começa com `cfg_` — configuração nunca vaza para o `beam_data.xlsx`.

    Valida antes de gastar CPU: campos obrigatórios presentes e não vazios, vocabulário
    das classes, limites com mínimo menor ou igual ao máximo, e ids únicos.
    """
    t = textos(idioma)
    df = pd.read_excel(caminho, sheet_name=aba, dtype={COLUNA_ID: str})

    casos: list[CasoBatch] = []
    vistos: set[str] = set()

    for _, serie in df.iterrows():
        linha = serie.to_dict()
        id_caso = str(linha.get(COLUNA_ID, "")).strip()
        if not id_caso or id_caso.lower() == "nan":
            raise ValueError("Há linha sem 'id' na planilha de casos.")
        if id_caso in vistos:
            raise ValueError(f"Id duplicado na planilha de casos: {id_caso!r}.")
        vistos.add(id_caso)

        dados = {
            k: v
            for k, v in linha.items()
            if k != COLUNA_ID and not str(k).startswith(PREFIXO_CONFIG)
        }
        _validar_dados(dados, t, id_caso)

        limites = LimitesBusca(
            d=(float(_cfg(linha, "d_min", 30.0)), float(_cfg(linha, "d_max", 150.0))),
            bw=(float(_cfg(linha, "bw_min", 5.0)), float(_cfg(linha, "bw_max", 60.0))),
            h=(float(_cfg(linha, "h_min", 5.0)), float(_cfg(linha, "h_max", 60.0))),
            esp_long=(
                float(_cfg(linha, "esp_long_min", 30.0)),
                float(_cfg(linha, "esp_long_max", 200.0)),
            ),
            esp_tab=(
                float(_cfg(linha, "esp_tab_min", 2.0)),
                float(_cfg(linha, "esp_tab_max", 5.0)),
            ),
        )
        for nome, (minimo, maximo) in {
            "d": limites.d,
            "bw": limites.bw,
            "h": limites.h,
            "esp_long": limites.esp_long,
            "esp_tab": limites.esp_tab,
        }.items():
            if minimo > maximo:
                raise ValueError(
                    f"Caso {id_caso}: limite {nome} invertido ({minimo} > {maximo})."
                )

        subdir = _cfg(linha, "subdiretorio", None)
        casos.append(
            CasoBatch(
                id=id_caso,
                dados=dados,
                limites=limites,
                algoritmo=ParametrosAlgoritmo(
                    pop_size=int(_cfg(linha, "pop_size", 50)),
                    n_gen=int(_cfg(linha, "n_gen", 150)),
                    n_checagens=int(_cfg(linha, "n_checagens", 30)),
                ),
                sobol=ConfigSobol(
                    ativo=_para_bool(linha.get(PREFIXO_CONFIG + "sobol"), True),
                    n_samples=int(_cfg(linha, "sobol_n_samples", 20000)),
                ),
                subdiretorio=None if subdir is None else str(subdir),
                ativo=_para_bool(linha.get(PREFIXO_CONFIG + "ativo"), True),
            )
        )

    return casos


def montar_planilha_casos(casos: list[CasoBatch]) -> pd.DataFrame:
    """Serializa uma lista de `CasoBatch` de volta para o layout da planilha."""
    linhas = []
    for c in casos:
        linha = {COLUNA_ID: c.id}
        linha.update(c.dados)
        linha.update(
            {
                f"{PREFIXO_CONFIG}d_min": c.limites.d[0],
                f"{PREFIXO_CONFIG}d_max": c.limites.d[1],
                f"{PREFIXO_CONFIG}bw_min": c.limites.bw[0],
                f"{PREFIXO_CONFIG}bw_max": c.limites.bw[1],
                f"{PREFIXO_CONFIG}h_min": c.limites.h[0],
                f"{PREFIXO_CONFIG}h_max": c.limites.h[1],
                f"{PREFIXO_CONFIG}esp_long_min": c.limites.esp_long[0],
                f"{PREFIXO_CONFIG}esp_long_max": c.limites.esp_long[1],
                f"{PREFIXO_CONFIG}esp_tab_min": c.limites.esp_tab[0],
                f"{PREFIXO_CONFIG}esp_tab_max": c.limites.esp_tab[1],
                f"{PREFIXO_CONFIG}pop_size": c.algoritmo.pop_size,
                f"{PREFIXO_CONFIG}n_gen": c.algoritmo.n_gen,
                f"{PREFIXO_CONFIG}n_checagens": c.algoritmo.n_checagens,
                f"{PREFIXO_CONFIG}sobol": c.sobol.ativo,
                f"{PREFIXO_CONFIG}sobol_n_samples": c.sobol.n_samples,
                f"{PREFIXO_CONFIG}ativo": c.ativo,
                f"{PREFIXO_CONFIG}subdiretorio": c.subdiretorio,
            }
        )
        linhas.append(linha)
    return pd.DataFrame(linhas)


def ler_beam_data(origem) -> dict:
    """Lê um `beam_data.xlsx`, seja um arquivo solto ou um `pre_sizing_package.zip`.

    Preferir sempre o zip: os arquivos soltos das simulações publicadas podem ter sido
    reabertos e re-salvos no Excel.
    """
    origem = Path(origem)
    if origem.suffix == ".zip":
        with zipfile.ZipFile(origem) as z:
            conteudo = z.read("beam_data.xlsx")
        return pd.read_excel(io.BytesIO(conteudo)).to_dict("records")[0]
    return pd.read_excel(origem).to_dict("records")[0]


def coletar_casos_de_diretorios(
    diretorios,
    *,
    prefixo_remover: str = "simulacao_",
    sobrescrever_dados: dict | None = None,
    **config,
) -> list[CasoBatch]:
    """Reconstrói `CasoBatch` a partir de diretórios de simulação já existentes.

    Lê o `beam_data.xlsx` de dentro do `pre_sizing_package.zip` quando ele existe.
    `sobrescrever_dados` é aplicado a todas as linhas, para corrigir um campo de uma vez.
    Argumentos extras (`limites`, `algoritmo`, `sobol`) vão para todos os casos.
    """
    casos = []
    for d in diretorios:
        d = Path(d)
        pacote = d / NOME_ZIP
        dados = ler_beam_data(pacote if pacote.exists() else d / "beam_data.xlsx")
        if sobrescrever_dados:
            dados.update(sobrescrever_dados)
        nome = d.name
        casos.append(
            CasoBatch(
                id=nome[len(prefixo_remover) :] if nome.startswith(prefixo_remover) else nome,
                dados=dados,
                **config,
            )
        )
    return casos


# --------------------------------------------------------------------------------------
# Verificação
# --------------------------------------------------------------------------------------


def _ler_membros_referencia(referencia) -> dict[str, bytes]:
    referencia = Path(referencia)
    if referencia.suffix == ".zip":
        with zipfile.ZipFile(referencia) as z:
            return {n: z.read(n) for n in z.namelist()}
    return {
        n: (referencia / n).read_bytes()
        for n in NOMES_MEMBROS_ZIP
        if (referencia / n).exists()
    }


def _comparar_conteudo(nome: str, a: bytes, b: bytes) -> tuple[bool, float | None, str]:
    """Compara dois membros: estrutura igual? maior diferença numérica? descrição."""
    if a == b:
        return True, 0.0, "bytes idênticos"

    if nome.endswith((".xlsx", ".csv")):
        ler = pd.read_excel if nome.endswith(".xlsx") else pd.read_csv
        da, db = ler(io.BytesIO(a)), ler(io.BytesIO(b))
        if list(da.columns) != list(db.columns) or da.shape != db.shape:
            return False, None, f"estrutura difere: {da.shape} {list(da.columns)[:3]}… vs {db.shape}"
        num = da.select_dtypes("number")
        dif = (num - db[num.columns]).abs().to_numpy().max() if not num.empty else 0.0
        return True, float(dif), f"estrutura igual, maior diferença numérica {dif:.3g}"

    if nome.endswith(".png"):
        try:
            from PIL import Image, ImageChops
            import numpy as np

            ia = Image.open(io.BytesIO(a)).convert("RGB")
            ib = Image.open(io.BytesIO(b)).convert("RGB")
            if ia.size != ib.size:
                return False, None, f"tamanhos diferentes: {ia.size} vs {ib.size}"
            diff = np.asarray(ImageChops.difference(ia, ib), dtype=float)
            return True, float(diff.mean()), f"mesmo tamanho, erro médio {diff.mean():.4f}/canal"
        except ImportError:
            return True, None, "png difere (PIL ausente para medir)"

    return False, None, "conteúdo difere"


def comparar_com_referencia(artefatos: ArtefatosCaso, referencia) -> pd.DataFrame:
    """Compara os membros produzidos contra um pacote de referência.

    `referencia` é o caminho de um `pre_sizing_package.zip` ou de um diretório. Prefira
    sempre o zip: os arquivos soltos das simulações publicadas foram editados à mão para o
    artigo e não são mais a saída original.

    Atenção ao que esta função pode e não pode provar. Igualdade byte a byte não é
    alcançável: XLSX e ZIP carregam carimbo de data, e a fronteira em si depende do
    caminho que o NSGA-II percorre, que é sensível a diferenças de último bit no
    ponto flutuante entre máquinas. Duas execuções da mesma matriz em computadores
    diferentes divergem legitimamente. Para aferir fidelidade do cálculo use
    `verificar_modelo`, que é o teste que de fato vale.

    Aqui, `estrutura_igual` é o que se deve exigir: mesmo conjunto de membros, mesmas
    colunas, mesmo formato. `dif_max` é informativo.
    """
    ref = _ler_membros_referencia(referencia)
    novos = {nome: conteudo for nome, conteudo in artefatos.membros() if conteudo}

    linhas = []
    for nome in NOMES_MEMBROS_ZIP:
        a, b = novos.get(nome), ref.get(nome)
        if a is None and b is None:
            continue
        if a is None or b is None:
            linhas.append(
                {
                    "membro": nome,
                    "nos_dois": False,
                    "md5_igual": False,
                    "estrutura_igual": False,
                    "dif_max": None,
                    "detalhe": f"ausente em {'novo' if a is None else 'referência'}",
                }
            )
            continue
        estrutura, dif, detalhe = _comparar_conteudo(nome, a, b)
        linhas.append(
            {
                "membro": nome,
                "nos_dois": True,
                "md5_igual": hashlib.md5(a).hexdigest() == hashlib.md5(b).hexdigest(),
                "estrutura_igual": estrutura,
                "dif_max": dif,
                "detalhe": detalhe,
            }
        )
    return pd.DataFrame(linhas)


def verificar_modelo(referencia, limites: LimitesBusca | None = None, *, idioma: str = "pt") -> dict:
    """Confere se o modelo mecânico ainda reproduz os valores de um pacote de referência.

    Este é o teste de fidelidade que importa, e o único que é robusto: pega as soluções
    já gravadas na fronteira de referência, reavalia cada uma pelo mesmo protocolo robusto
    da otimização e compara objetivos e restrições.

    Diferente de comparar fronteiras inteiras, aqui não há busca envolvida, então o
    resultado não depende do caminho do NSGA-II. Se a maior diferença ficar na ordem da
    precisão de máquina, o cálculo é o mesmo.

    Devolve um dicionário com `dif_max_F`, `dif_max_G`, `n_solucoes` e `identico`.
    """
    import numpy as np
    from madeiras import _criar_projeto_otimo_pre_sizing

    limites = limites or LimitesBusca()
    t = textos(idioma)
    ref = _ler_membros_referencia(referencia)

    dados = normalizar_dados_pre_sizing(ler_beam_data(referencia), t)
    df = pd.read_excel(io.BytesIO(ref["pre_sizing_results_optimized.xlsx"]))
    ds, bws, hs, n_long, n_tab = limites.como_listas()

    perc = float(dados.get(t["percentual_robustez"], 5.0))
    projeto = _criar_projeto_otimo_pre_sizing(
        dados, ds, bws, hs, n_long, n_tab, t, n_checagens=30, perc_robustez=perc
    )

    F, G = [], []
    for _, r in df.iterrows():
        saida: dict = {}
        projeto._evaluate(
            np.array([r.d_cm, r.bw_cm, r.h_cm, r.esp_cm, r.esp_tab_cm], dtype=float), saida
        )
        F.append(saida["F"])
        G.append(saida["G"])

    F, G = np.array(F), np.array(G)
    ref_F = df[["of_volume_m3", "of_fator_flecha"]].to_numpy()
    ref_G = df[
        [
            "longarina_g_m",
            "longarina_g_v",
            "longarina_g_f",
            "tabuleiro_g_m",
            "longarina_g_esp",
            "tabuleiro_g_esp",
        ]
    ].to_numpy()

    dif_f = float(np.abs(F - ref_F).max())
    dif_g = float(np.abs(G - ref_G).max())
    return {
        "n_solucoes": len(df),
        "dif_max_F": dif_f,
        "dif_max_G": dif_g,
        "identico": bool(np.array_equal(F, ref_F) and np.array_equal(G, ref_G)),
        "dentro_precisao_maquina": dif_f < 1e-9 and dif_g < 1e-9,
    }
