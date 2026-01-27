# # Confiabilidade estrutural
# def smooth_max(a, b, k=50.0):
#     m = np.maximum(a, b)
#     return m + np.log(np.exp(k*(a-m)) + np.exp(k*(b-m))) / k


# def obj_confia(samples, params):

#     g = np.zeros((samples.shape[0]))
#     for i in range(samples.shape[0]):
#         # Extrair amostras 
#         p_gk = samples[i, 0]
#         p_rodak = samples[i, 1]
#         p_qk  = samples[i, 2]
#         f_mk = samples[i, 3]
#         f_vk = samples[i, 4]
#         e_modflex = samples[i, 5]
#         f_mktab = samples[i, 6]
#         densidade_long = samples[i, 7]
#         densidade_tab = samples[i, 8]
#         # print(p_gk, p_rodak, p_qk, f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab)
        
#         # Parâmetros fixos
#         a = params[0]
#         l = params[1]
#         classe_carregamento = params[2]
#         classe_madeira = params[3]
#         classe_umidade = params[4]
#         d_cm = params[5]
#         esp = params[6]
#         bw_cm = params[7]
#         h_cm = params[8]
#         tipo_g = params[9]  # 'flexao', 'cisalhamento' ou 'flecha'

#         # Função Estado Limite
#         projeto = ProjetoEstrutural(
#                                         l=l,
#                                         p_gk=p_gk,
#                                         p_rodak=p_rodak,
#                                         p_qk=p_qk,
#                                         a=a,
#                                         classe_carregamento=classe_carregamento,
#                                         classe_madeira=classe_madeira,
#                                         classe_umidade=classe_umidade,
#                                         gamma_g=1.0,
#                                         gamma_q=1.0,
#                                         gamma_w=1.0,
#                                         psi2=1.0,
#                                         phi=1.0,
#                                         densidade_long=densidade_long,
#                                         densidade_tab=densidade_tab,
#                                         f_mk_long=f_mk,
#                                         f_vk_long=f_vk,
#                                         e_modflex_long=e_modflex,
#                                         f_mk_tab=f_mktab,
#                                     )
#         res = projeto.calcular(d_cm=d_cm, esp_cm=esp, bw_cm=bw_cm, h_cm=h_cm)
#         if tipo_g == 'flexao':
#             g[i] = -res["flexao_longarina"]["g [kPa]"]
#         elif tipo_g == 'cisalhamento':
#             g[i] = -res["cisalhamento_longarina"]["g [kPa]"]
#         elif tipo_g == 'flecha':
#             delta_sd_1 = res["flecha_total_longarina"]["delta_fluencia [m]"]
#             delta_rd_1 = res["flecha_total_longarina"]["delta_lim_total [m]"]
#             delta_sd_2 = res["flecha_total_longarina"]["delta_qk [m]"]
#             delta_rd_2 = res["flecha_total_longarina"]["delta_lim_variavel [m]"]
#             g_fluencia = delta_rd_1 - delta_sd_1
#             g_variavel = delta_rd_2 - delta_sd_2
#             g[i] = smooth_max(g_fluencia, g_variavel)

#     return g

def gev_loc_scale_from_mean_std(mean: float, std: float) -> tuple[float, float]:
    EULER_GAMMA = 0.5772156649015329
    scale = std * np.sqrt(6) / np.pi
    loc = mean - EULER_GAMMA * scale
    return loc, scale


def chamando_form(p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade, f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab, d_cm, esp_cm, bw_cm, h_cm, tipo_g):
    p_gk = float(p_gk)
    p_rodak = float(p_rodak)
    p_qk = float(p_qk)
    a = float(a)
    l = float(l)
    f_mk = float(f_mk)
    f_vk = float(f_vk)
    e_modflex = float(e_modflex)
    f_mktab = float(f_mktab)
    densidade_long = float(densidade_long)
    densidade_tab = float(densidade_tab)
    d_cm = float(d_cm)
    esp_cm = float(esp_cm)
    bw_cm = float(bw_cm)
    h_cm = float(h_cm)
    # Parámetros GEV
    loc_rodak, scale_rodak = gev_loc_scale_from_mean_std(p_rodak, p_rodak*0.2)
    loc_qk, scale_qk = gev_loc_scale_from_mean_std(p_qk, p_qk*0.2)
    
    # Distribuições
    p_gk_aux = TruncatedNormal(a=(-p_gk/(p_gk*0.1)), b=np.inf, loc=p_gk, scale=p_gk*0.1)
    p_rodak_aux = GeneralizedExtreme(c=0.0, loc=loc_rodak, scale=scale_rodak)
    p_qk_aux = GeneralizedExtreme(c=0.0, loc=loc_qk, scale=scale_qk)
    f_mk_aux = TruncatedNormal(a=(-f_mk/(f_mk*0.1)), b=np.inf, loc=f_mk, scale=f_mk*0.1)
    f_vk_aux = TruncatedNormal(a=(-f_vk/(f_vk*0.1)), b=np.inf, loc=f_vk, scale=f_vk*0.1)     
    e_modflex_aux = TruncatedNormal(a=(-e_modflex/(e_modflex*0.1)), b=np.inf, loc=e_modflex, scale=e_modflex*0.1)
    f_mktab_aux = TruncatedNormal(a=(-f_mktab/(f_mktab*0.1)), b=np.inf, loc=f_mktab, scale=f_mktab*0.1)
    densidade_long_aux = TruncatedNormal(a=(-densidade_long/(densidade_long*0.1)), b=np.inf, loc=densidade_long, scale=densidade_long*0.1)
    densidade_tab_aux = TruncatedNormal(a=(-densidade_tab/(densidade_tab*0.1)), b=np.inf, loc=densidade_tab, scale=densidade_tab*0.1)

    # Variáveis fixas da viga
    paramss = [a, l, classe_carregamento, classe_madeira, classe_umidade, d_cm, esp_cm, bw_cm, h_cm, tipo_g]

    # Confiabilidade
    varss = [p_gk_aux, p_rodak_aux, p_qk_aux, f_mk_aux, f_vk_aux, e_modflex_aux, f_mktab_aux, densidade_long_aux, densidade_tab_aux]
    model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
    runmodel_nlc = RunModel(model=model)
    form = FORM(distributions=varss, runmodel_object=runmodel_nlc, tolerance_u=1e-3, tolerance_beta=1e-3)
    form.run()
    beta = form.beta[0]
    pf = form.failure_probability[0]

    return beta, pf


import numpy as np

from UQpy.sampling import MonteCarloSampling, LatinHypercubeSampling
from UQpy.sampling.ImportanceSampling import ImportanceSampling
from UQpy.distributions import TruncatedNormal, GeneralizedExtreme, JointIndependent
from UQpy.run_model.RunModel import RunModel
from UQpy.run_model.model_execution.PythonModel import PythonModel


def chamando_sampling(
                        p_gk, p_rodak, p_qk, a, l, classe_carregamento, classe_madeira, classe_umidade,
                        f_mk, f_vk, e_modflex, f_mktab, densidade_long, densidade_tab,
                        d_cm, esp_cm, bw_cm, h_cm, tipo_g,
                        method: str = "LHS",          # "MC", "LHS" ou "IS"
                        nsamples: int = 100000,
                        random_state: int = 123
                    ):
    # casts
    p_gk = float(p_gk); p_rodak = float(p_rodak); p_qk = float(p_qk)
    a = float(a); l = float(l)
    f_mk = float(f_mk); f_vk = float(f_vk); e_modflex = float(e_modflex)
    f_mktab = float(f_mktab)
    densidade_long = float(densidade_long); densidade_tab = float(densidade_tab)
    d_cm = float(d_cm); esp_cm = float(esp_cm); bw_cm = float(bw_cm); h_cm = float(h_cm)

    # helper truncnorm X>=0 (a,b no domínio padrão)
    def tn_pos(mean, cov):
        mu = float(mean)
        sig = float(abs(mean) * cov)
        a_std = (0.0 - mu) / sig
        return TruncatedNormal(a=a_std, b=np.inf, loc=mu, scale=sig)

    # -------------------------
    # TARGET (como você já faz)
    # -------------------------
    loc_rodak, scale_rodak = gev_loc_scale_from_mean_std(p_rodak, p_rodak * 0.2)
    loc_qk, scale_qk       = gev_loc_scale_from_mean_std(p_qk,   p_qk   * 0.2)

    p_gk_aux           = tn_pos(p_gk, 0.10)
    p_rodak_aux        = GeneralizedExtreme(c=0.0, loc=loc_rodak, scale=scale_rodak)
    p_qk_aux           = GeneralizedExtreme(c=0.0, loc=loc_qk, scale=scale_qk)
    f_mk_aux           = tn_pos(f_mk, 0.10)
    f_vk_aux           = tn_pos(f_vk, 0.10)
    e_modflex_aux      = tn_pos(e_modflex, 0.10)
    f_mktab_aux        = tn_pos(f_mktab, 0.10)
    densidade_long_aux = tn_pos(densidade_long, 0.10)
    densidade_tab_aux  = tn_pos(densidade_tab, 0.10)

    varss = [
                p_gk_aux, p_rodak_aux, p_qk_aux, f_mk_aux, f_vk_aux,
                e_modflex_aux, f_mktab_aux, densidade_long_aux, densidade_tab_aux
            ]

    # params fixos
    paramss = [a, l, classe_carregamento, classe_madeira, classe_umidade, d_cm, esp_cm, bw_cm, h_cm, tipo_g]

    # -------------------------
    # SAMPLER UQpy
    # -------------------------
    method = method.upper()

    if method == "MC":
        sampler = MonteCarloSampling(distributions=varss, nsamples=nsamples, random_state=random_state)
        samples = sampler.samples
        weights = None

    elif method == "LHS":
        sampler = LatinHypercubeSampling(distributions=varss, nsamples=nsamples, random_state=random_state)
        samples = sampler.samples
        weights = None

    elif method == "IS":
        # 1) joint target (independente)
        target_joint = JointIndependent(marginals=varss)

        # 2) proposal: "puxar" para falha (heurística simples e editável)
        #    - ações ↑ (médias maiores)
        #    - resistências/rigidez ↓ (médias menores)
        m_load = 1.20
        m_res  = 0.85
        m_E    = 0.90
        m_rho  = 1.10

        # GEV proposal (mantém COV ~ 0.2 via std = mean*0.2, só desloca a média)
        p_rodak_p = p_rodak * m_load
        p_qk_p    = p_qk    * m_load
        loc_rodak_p, scale_rodak_p = gev_loc_scale_from_mean_std(p_rodak_p, p_rodak_p * 0.2)
        loc_qk_p, scale_qk_p       = gev_loc_scale_from_mean_std(p_qk_p,    p_qk_p    * 0.2)

        proposal_marginals = [
            tn_pos(p_gk * m_load, 0.10),                                        # p_gk
            GeneralizedExtreme(c=0.0, loc=loc_rodak_p, scale=scale_rodak_p),     # p_rodak
            GeneralizedExtreme(c=0.0, loc=loc_qk_p,    scale=scale_qk_p),        # p_qk
            tn_pos(f_mk * m_res, 0.10),                                          # f_mk
            tn_pos(f_vk * m_res, 0.10),                                          # f_vk
            tn_pos(e_modflex * m_E, 0.10),                                       # E
            tn_pos(f_mktab * m_res, 0.10),                                       # f_mktab
            tn_pos(densidade_long * m_rho, 0.10),                                # rho_long
            tn_pos(densidade_tab  * m_rho, 0.10),                                # rho_tab
        ]

        proposal_joint = JointIndependent(marginals=proposal_marginals)

        # 3) ImportanceSampling: gera amostras pela proposta e calcula pesos (normalizados)
        sampler = ImportanceSampling(
            log_pdf_target=target_joint.log_pdf,
            proposal=proposal_joint,
            random_state=random_state,
            nsamples=nsamples,
        )
        samples = sampler.samples
        weights = np.asarray(sampler.weights, dtype=float).reshape(-1)

    else:
        raise ValueError("method deve ser 'MC', 'LHS' ou 'IS'")

    # -------------------------
    # rodar modelo UQpy
    # -------------------------
    model = PythonModel(model_script='madeiras.py', model_object_name='obj_confia', params=paramss)
    rmodel = RunModel(model=model)
    rmodel.run(samples=samples)

    g = np.asarray(rmodel.qoi_list, dtype=float).reshape(-1)

    # Convenção: falha quando g <= 0
    if weights is None:
        pf = float(np.mean(g <= 0.0))
    else:
        # pesos do IS já vêm normalizados para somar 1 no UQpy
        pf = float(np.sum((g <= 0.0).astype(float) * weights))

    beta = beta_from_pf(pf)

    return sampler, beta, pf