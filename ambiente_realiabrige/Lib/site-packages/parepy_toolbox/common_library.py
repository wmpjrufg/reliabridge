"""Common library for PAREpy toolbox"""
from datetime import datetime
from typing import List, Dict, Union, Callable, Tuple
from distfit import distfit
from scipy.stats.distributions import norm, gumbel_r, gumbel_l, dweibull, gamma, beta, triang
from scipy.integrate import quad
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from numpy import sqrt, pi, exp
import random


def sampling(n_samples: int, d: int, model: Dict, variables_setup: List) -> np.ndarray:
    """
    This algorithm generates a set of random numbers according to a type of distribution.

    Args:
        n_samples (Integer): Number of samples
        d (Integer): Number of dimensions
        model (Dictionary): Model parameters
        variables_setup (List): Random variable parameters (list of dictionaries)
    
    Returns:
        random_sampling (np.array): Random samples
    """

    # Model settnigs
    model_sampling = model['model sampling'].upper()

    if model_sampling.upper() in ['MCS TIME', 'MCS-TIME', 'MCS_TIME']:
        # Time analysis
        time_analysis = model['time steps']

        # Generating n_samples samples
        random_sampling = np.empty((0, d))
        for _ in range(n_samples):

            # Generating a temporal sample
            temporal_sampling = np.zeros((time_analysis, d))
            for i in range(d):

                # Setup pdf
                type_dist = variables_setup[i]['type'].upper()
                seed_dist = variables_setup[i]['seed']
                n_samples_in_temporal_aux = variables_setup[i]['stochastic variable']
                if n_samples_in_temporal_aux:
                    n_samples_in_temporal = time_analysis
                else:
                    n_samples_in_temporal = 1
                
                # Normal or Gaussian
                if type_dist == 'GAUSSIAN' or type_dist == 'NORMAL':
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = norm.rvs(loc=mean_dist,
                                                       scale=stda_dist,
                                                       size=n_samples_in_temporal,
                                                       random_state=seed_dist)
                # Gumbel right or Gumbel maximum
                elif type_dist == 'GUMBEL MAX':
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = gumbel_r.rvs(loc=mean_dist,
                                                           scale=stda_dist,
                                                           size=n_samples_in_temporal,
                                                           random_state=seed_dist)
                # Gumbel left or Gumbel minimum
                elif type_dist == 'GUMBEL MIN':
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = gumbel_l.rvs(loc=mean_dist,
                                                           scale=stda_dist,
                                                           size=n_samples_in_temporal,
                                                           random_state=seed_dist)
                # Weibull
                elif type_dist == 'WEIBULL':
                    shape_dist = variables_setup[i]['shape']
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = dweibull.rvs(shape_dist,
                                                           loc=mean_dist,
                                                           scale=stda_dist,
                                                           size=n_samples_in_temporal,
                                                           random_state=seed_dist)
                # Lognormal
                elif type_dist == 'LOGNORMAL':
                    # https://shivamrana.me/2024/01/lognormal-to-normal/
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    rng = np.random.default_rng()
                    lognorm_samples = rng.lognormal(mean_dist, stda_dist, n_samples_in_temporal)
                    norm_samples = np.log(lognorm_samples)
                    temporal_sampling[:, i] = norm.rvs(loc=norm_samples.mean(),
                                                       scale=norm_samples.std(),
                                                       size=n_samples_in_temporal,
                                                       random_state=seed_dist)
                # Gamma
                elif type_dist == 'GAMMA':
                    shape_dist = variables_setup[i]['shape']
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = gamma.rvs(shape_dist,
                                                        loc=mean_dist,
                                                        scale=stda_dist,
                                                        size=n_samples_in_temporal,
                                                        random_state=seed_dist)
                # Beta
                elif type_dist == 'BETA':
                    a = variables_setup[i]['a']
                    b = variables_setup[i]['b']
                    mean_dist = variables_setup[i]['loc']
                    stda_dist = variables_setup[i]['scale']
                    temporal_sampling[:, i] = beta.rvs(a,
                                                        b,
                                                        loc=mean_dist,
                                                        scale=stda_dist,
                                                        size=n_samples_in_temporal,
                                                        random_state=seed_dist)
                # Triangular
                elif type_dist == 'TRIANGULAR':
                    loc = variables_setup[i]['loc']
                    a = variables_setup[i]['min']
                    b = variables_setup[i]['max']
                    std = b - a
                    c = (loc - a) / (b - a)
                    temporal_sampling[:, i] = triang.rvs(c=c,
                                                        loc=a,
                                                        scale=std,
                                                        size=n_samples_in_temporal,
                                                        random_state=seed_dist)
            random_sampling = np.concatenate((random_sampling, temporal_sampling), axis=0)

        # convert time dataset
        time_sampling = np.zeros((time_analysis * n_samples, 1))
        cont = 0
        for _ in range(n_samples):
            for m in range(time_analysis):
                time_sampling[cont, 0] = int(m)
                cont += 1
        random_sampling = np.concatenate((random_sampling, time_sampling), axis=1)

    elif model_sampling.upper() in ['MCS', 'CRUDE MONTE CARLO', 'MONTE CARLO', 'CRUDE MCS']:
        random_sampling = np.zeros((n_samples, d))

        for j in range(d):
            # Setup pdf
            type_dist = variables_setup[j]['type'].upper()
            seed_dist = variables_setup[j]['seed']

            # Normal or Gaussian
            if type_dist == 'GAUSSIAN' or type_dist == 'NORMAL':
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                random_sampling[:, j] = norm.rvs(loc=mean_dist,
                                                    scale=stda_dist,
                                                    size=n_samples,
                                                    random_state=seed_dist)
            # Gumbel right or Gumbel maximum
            elif type_dist == 'GUMBEL MAX' or type_dist == 'GUMBEL MAX.':
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                random_sampling[:, j] = gumbel_r.rvs(loc=mean_dist,
                                                        scale=stda_dist,
                                                        size=n_samples,
                                                        random_state=seed_dist)
            # Gumbel left or Gumbel minimum
            elif type_dist == 'GUMBEL MIN' or type_dist == 'GUMBEL MIN.':
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                random_sampling[:, j] = gumbel_l.rvs(loc=mean_dist,
                                                     scale=stda_dist,
                                                     size=n_samples,
                                                     random_state=seed_dist)
            # Weibull
            elif type_dist == 'WEIBULL':
                shape_dist = variables_setup[j]['shape']
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                random_sampling[:, j] = dweibull.rvs(shape_dist,
                                                        loc=mean_dist,
                                                        scale=stda_dist,
                                                        size=n_samples,
                                                        random_state=seed_dist)
            # Lognormal
            elif type_dist == 'LOGNORMAL':
                # https://shivamrana.me/2024/01/lognormal-to-normal/
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                rng = np.random.default_rng()
                lognorm_samples = rng.lognormal(mean_dist, stda_dist, n_samples)
                norm_samples = np.log(lognorm_samples)
                random_sampling[:, j] = norm.rvs(loc=norm_samples.mean(),
                                                scale=norm_samples.std(),
                                                size=n_samples,
                                                random_state=seed_dist)
            # Gamma
            elif type_dist == 'GAMMA':
                shape_dist = variables_setup[j]['shape']
                mean_dist = variables_setup[j]['loc']
                stda_dist = variables_setup[j]['scale']
                random_sampling[:, j] = gamma.rvs(shape_dist,
                                                    loc=mean_dist,
                                                    scale=stda_dist,
                                                    size=n_samples,
                                                    random_state=seed_dist)
            # Beta
            elif type_dist == 'BETA':
                mean_dist = variables_setup[i]['loc']
                stda_dist = variables_setup[i]['scale']
                a = variables_setup[i]['a']
                b = variables_setup[i]['b']
                random_sampling[:, j] = beta.rvs(a,
                                                    b,
                                                    loc=mean_dist,
                                                    scale=stda_dist,
                                                    size=n_samples,
                                                    random_state=seed_dist)
            # Triangular
            elif type_dist == 'TRIANGULAR':
                loc = variables_setup[j]['loc']
                a = variables_setup[j]['min']
                b = variables_setup[j]['max']
                std = b - a
                c = (loc - a) / (b - a)
                random_sampling[:, j] = triang.rvs(c=c,
                                                   loc=a,
                                                   scale=std,
                                                   size=n_samples,
                                                   random_state=seed_dist)

    return random_sampling


def simpling(n_samples: int, d: int, model: Dict, variables_setup: List) -> np.ndarray:
    """
    This algorithm generates a set of random numbers according to a type of distribution.

    Args:
        n_samples (int): Number of samples.
        d (int): Number of dimensions.
        model (Dict): Model parameters, including seed and method.
        variables_setup (List): List of dictionaries, each with parameters for each variable.

    Returns:
        np.ndarray: Random samples.
    """
    model_type = model['model sampling'].upper()
    samples = []

    for variable in variables_setup:
        type_dist = variable['type'].upper()
        seed = variable['seed']

        if model_type in ['MCS']:
            if type_dist == 'UNIFORM':
                samples.append(sampling_uniform_distribution(variable["min"], variable["max"], n_samples, seed))

            elif type_dist == "NORMAL":
                samples.append(inverse_normal_sampling(n_samples, variable["mean"], variable["std"], seed, "MCS"))

            elif type_dist == "GUMBEL_R":
                samples.append(inverse_gumbel_r(n_samples, variable["mu"], variable["beta"], seed, "MCS"))

            elif type_dist == "GUMBEL_L":
                samples.append(inverse_gumbel_l(n_samples,
                        variable["mu"], variable["beta"], seed, "MCS"))
                
            elif type_dist == "TRIANGULAR":
                samples.append(triangular_inverse_cdf(n_samples, variable["a_min"], variable["a_mean"], variable["a_max"], seed, "MCS"))

        elif model_type in ['LHS']:
            if type_dist == 'UNIFORM':
                samples.append(uniform_lhs(n_samples, d, seed))

            elif type_dist == "NORMAL":
                samples.append(inverse_normal_sampling(n_samples, variable["mean"], variable["std"], seed, "LHS"))
                
            elif type_dist == "GUMBEL_R":
                samples.append(inverse_gumbel_r(n_samples, variable["mu"], variable["beta"], seed, "LHS"))

            elif type_dist == "GUMBEL_L":
                samples.append(inverse_gumbel_l(n_samples, variable["mu"], variable["beta"], seed, "LHS"))

            elif type_dist == "TRIANGULAR":
                samples.append(triangular_inverse_cdf(n_samples, variable["a_min"], variable["a_mean"], variable["a_max"], seed, "LHS"))

            else:
                raise ValueError(f"Unknown distribution type: {type_dist}")

    return np.array(samples)


def newton_raphson(f: Callable[[float], float], df: Callable[[float], float], x0: float, tol: float) -> float:
    """
    This function calculates the root of a function using the Newton-Raphson method.

    Args:
        f (Python function [def]): Function
        df (Python function [def]): Derivative of the function
        x0 (Float): Initial value
        tol (Float): Tolerance
    
    Returns:
        x0 (Float): Root of the function
    """

    if abs(f(x0)) < tol:
        return x0
    else:
        return newton_raphson(f, df, x0 - f(x0)/df(x0), tol)


def pf_equation(beta: float) -> float:
    """
    This function calculates the probability of failure (pf) for a given reliability index (ϐ) using a standard normal cumulative distribution function. The calculation is performed by integrating the probability density function (PDF) of a standard normal distribution.

    Args:
        beta (Float): Reliability index
    
    Returns:
        pf_value (Float): Probability of failure
    """

    def integrand(x):
        return 1/sqrt(2*np.pi) * np.exp(-x**2/2) 

    def integral_x(x):
        integral, _ = quad(integrand, 0, x)
        return 1 - (0.5 + integral)

    return integral_x(beta)


def beta_equation(pf: float) -> Union[float, str]:
    """
    This function calculates the reliability index value for a given probability of failure (pf).

    Args:
        pf (Float): Probability of failure
    
    Returns:
        beta_value (Float or String): Beta value
    """

    if pf > 0.5:
        beta_value = "minus infinity"
    else:
        F = lambda BETA: BETA*(0.00569689925051199*sqrt(2)*exp(-0.497780952459929*BETA**2)/sqrt(pi) + 0.0131774933075162*sqrt(2)*exp(-0.488400032299965*BETA**2)/sqrt(pi) + 0.0204695783506533*sqrt(2)*exp(-0.471893773055302*BETA**2)/sqrt(pi) + 0.0274523479879179*sqrt(2)*exp(-0.448874334002837*BETA**2)/sqrt(pi) + 0.0340191669061785*sqrt(2)*exp(-0.42018898411968*BETA**2)/sqrt(pi) + 0.0400703501675005*sqrt(2)*exp(-0.386874144322843*BETA**2)/sqrt(pi) + 0.045514130991482*sqrt(2)*exp(-0.350103048710684*BETA**2)/sqrt(pi) + 0.0502679745335254*sqrt(2)*exp(-0.311127540182165*BETA**2)/sqrt(pi) + 0.0542598122371319*sqrt(2)*exp(-0.271217130855817*BETA**2)/sqrt(pi) + 0.0574291295728559*sqrt(2)*exp(-0.231598755762806*BETA**2)/sqrt(pi) + 0.0597278817678925*sqrt(2)*exp(-0.19340060305222*BETA**2)/sqrt(pi) + 0.0611212214951551*sqrt(2)*exp(-0.157603139738968*BETA**2)/sqrt(pi) + 0.0615880268633578*sqrt(2)*exp(-0.125*BETA**2)/sqrt(pi) + 0.0611212214951551*sqrt(2)*exp(-0.0961707934336129*BETA**2)/sqrt(pi) + 0.0597278817678925*sqrt(2)*exp(-0.0714671611917261*BETA**2)/sqrt(pi) + 0.0574291295728559*sqrt(2)*exp(-0.0510126028581118*BETA**2)/sqrt(pi) + 0.0542598122371319*sqrt(2)*exp(-0.0347157651329596*BETA**2)/sqrt(pi) + 0.0502679745335254*sqrt(2)*exp(-0.0222960750615538*BETA**2)/sqrt(pi) + 0.045514130991482*sqrt(2)*exp(-0.0133198644739499*BETA**2)/sqrt(pi) + 0.0400703501675005*sqrt(2)*exp(-0.00724451280416452*BETA**2)/sqrt(pi) + 0.0340191669061785*sqrt(2)*exp(-0.00346766973926267*BETA**2)/sqrt(pi) + 0.0274523479879179*sqrt(2)*exp(-0.00137833506369952*BETA**2)/sqrt(pi) + 0.0204695783506533*sqrt(2)*exp(-0.000406487440814915*BETA**2)/sqrt(pi) + 0.0131774933075162*sqrt(2)*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) + 0.00569689925051199*sqrt(2)*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi))/2 + pf - 0.5
        F_PRIME = lambda BETA: BETA*(-0.00567161586997623*sqrt(2)*BETA*exp(-0.497780952459929*BETA**2)/sqrt(pi) - 0.0128717763140469*sqrt(2)*BETA*exp(-0.488400032299965*BETA**2)/sqrt(pi) - 0.0193189331214818*sqrt(2)*BETA*exp(-0.471893773055302*BETA**2)/sqrt(pi) - 0.0246453088397815*sqrt(2)*BETA*exp(-0.448874334002837*BETA**2)/sqrt(pi) - 0.0285889583658099*sqrt(2)*BETA*exp(-0.42018898411968*BETA**2)/sqrt(pi) - 0.0310043648675369*sqrt(2)*BETA*exp(-0.386874144322843*BETA**2)/sqrt(pi) - 0.0318692720390705*sqrt(2)*BETA*exp(-0.350103048710684*BETA**2)/sqrt(pi) - 0.031279502533111*sqrt(2)*BETA*exp(-0.311127540182165*BETA**2)/sqrt(pi) - 0.0294323811914605*sqrt(2)*BETA*exp(-0.271217130855817*BETA**2)/sqrt(pi) - 0.0266010299072288*sqrt(2)*BETA*exp(-0.231598755762806*BETA**2)/sqrt(pi) - 0.0231028167058843*sqrt(2)*BETA*exp(-0.19340060305222*BETA**2)/sqrt(pi) - 0.0192657928246347*sqrt(2)*BETA*exp(-0.157603139738968*BETA**2)/sqrt(pi) - 0.0153970067158395*sqrt(2)*BETA*exp(-0.125*BETA**2)/sqrt(pi) - 0.0117561527336413*sqrt(2)*BETA*exp(-0.0961707934336129*BETA**2)/sqrt(pi) - 0.00853716430789267*sqrt(2)*BETA*exp(-0.0714671611917261*BETA**2)/sqrt(pi) - 0.00585921875877428*sqrt(2)*BETA*exp(-0.0510126028581118*BETA**2)/sqrt(pi) - 0.00376734179556552*sqrt(2)*BETA*exp(-0.0347157651329596*BETA**2)/sqrt(pi) - 0.00224155706678351*sqrt(2)*BETA*exp(-0.0222960750615538*BETA**2)/sqrt(pi) - 0.00121248411291229*sqrt(2)*BETA*exp(-0.0133198644739499*BETA**2)/sqrt(pi) - 0.000580580329711626*sqrt(2)*BETA*exp(-0.00724451280416452*BETA**2)/sqrt(pi) - 0.000235934471270962*sqrt(2)*BETA*exp(-0.00346766973926267*BETA**2)/sqrt(pi) - 7.56770676252561e-5*sqrt(2)*BETA*exp(-0.00137833506369952*BETA**2)/sqrt(pi) - 1.66412530366349e-5*sqrt(2)*BETA*exp(-0.000406487440814915*BETA**2)/sqrt(pi) - 1.79402532164194e-6*sqrt(2)*BETA*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) - 2.81149347557902e-8*sqrt(2)*BETA*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi))/2 + 0.002848449625256*sqrt(2)*exp(-0.497780952459929*BETA**2)/sqrt(pi) + 0.00658874665375808*sqrt(2)*exp(-0.488400032299965*BETA**2)/sqrt(pi) + 0.0102347891753266*sqrt(2)*exp(-0.471893773055302*BETA**2)/sqrt(pi) + 0.0137261739939589*sqrt(2)*exp(-0.448874334002837*BETA**2)/sqrt(pi) + 0.0170095834530893*sqrt(2)*exp(-0.42018898411968*BETA**2)/sqrt(pi) + 0.0200351750837502*sqrt(2)*exp(-0.386874144322843*BETA**2)/sqrt(pi) + 0.022757065495741*sqrt(2)*exp(-0.350103048710684*BETA**2)/sqrt(pi) + 0.0251339872667627*sqrt(2)*exp(-0.311127540182165*BETA**2)/sqrt(pi) + 0.027129906118566*sqrt(2)*exp(-0.271217130855817*BETA**2)/sqrt(pi) + 0.028714564786428*sqrt(2)*exp(-0.231598755762806*BETA**2)/sqrt(pi) + 0.0298639408839463*sqrt(2)*exp(-0.19340060305222*BETA**2)/sqrt(pi) + 0.0305606107475775*sqrt(2)*exp(-0.157603139738968*BETA**2)/sqrt(pi) + 0.0307940134316789*sqrt(2)*exp(-0.125*BETA**2)/sqrt(pi) + 0.0305606107475775*sqrt(2)*exp(-0.0961707934336129*BETA**2)/sqrt(pi) + 0.0298639408839463*sqrt(2)*exp(-0.0714671611917261*BETA**2)/sqrt(pi) + 0.028714564786428*sqrt(2)*exp(-0.0510126028581118*BETA**2)/sqrt(pi) + 0.027129906118566*sqrt(2)*exp(-0.0347157651329596*BETA**2)/sqrt(pi) + 0.0251339872667627*sqrt(2)*exp(-0.0222960750615538*BETA**2)/sqrt(pi) + 0.022757065495741*sqrt(2)*exp(-0.0133198644739499*BETA**2)/sqrt(pi) + 0.0200351750837502*sqrt(2)*exp(-0.00724451280416452*BETA**2)/sqrt(pi) + 0.0170095834530893*sqrt(2)*exp(-0.00346766973926267*BETA**2)/sqrt(pi) + 0.0137261739939589*sqrt(2)*exp(-0.00137833506369952*BETA**2)/sqrt(pi) + 0.0102347891753266*sqrt(2)*exp(-0.000406487440814915*BETA**2)/sqrt(pi) + 0.00658874665375808*sqrt(2)*exp(-6.80715702059458e-5*BETA**2)/sqrt(pi) + 0.002848449625256*sqrt(2)*exp(-2.46756468031828e-6*BETA**2)/sqrt(pi)
        beta_value = newton_raphson(F, F_PRIME, 0.0, 1E-15)

        return beta_value


def calc_pf_beta(df_or_path: Union[pd.DataFrame, str], numerical_model: Dict[str, str], n_constraints: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calculates the values of probability of failure or reliability index from the columns of a DataFrame that start with 'I_' (Indicator function). If a .txt file path is passed, this function evaluates pf and β values too.
    
    Args:
        df_or_path (DataFrame or String): The DataFrame containing the columns with boolean values about indicator function, or a path to a .txt file
        numerical_model (Dictionary): Containing the numerical model parameters
        n_constraints (Integer): Number of state limit functions or constraints 

    Returns:
        df_pf (DataFrame): DataFrame containing the values for probability of failure for each 'I_' column
        df_beta (DataFrame): DataFrame containing the values for beta for each 'I_' column
    """

    if isinstance(df_or_path, str) and df_or_path.endswith('.txt'):
        df = pd.read_csv(df_or_path, delimiter='\t')
    else:
        df = df_or_path
    if numerical_model['model sampling'].upper() in ['MCS', 'CRUDE MONTE CARLO', 'MONTE CARLO', 'CRUDE MCS']:
        filtered_df = df.filter(like='I_', axis=1)
        pf_results = filtered_df.mean(axis=0)
        df_pf = pd.DataFrame([pf_results.to_list()], columns=pf_results.index)
        beta_results = [beta_equation(pf) for pf in pf_results.to_list()] 
        df_beta = pd.DataFrame([beta_results], columns=pf_results.index)
    else:
        df_pf = pd.DataFrame()
        df_beta = pd.DataFrame()
        for i in range(n_constraints):
            filtered_df = df.filter(like=f'I_{i}', axis=1)
            pf_results = filtered_df.mean(axis=0)
            beta_results = [beta_equation(pf) for pf in pf_results.to_list()]
            df_pf[f'I_{i}'] = pf_results.to_list()
            df_beta[f'I_{i}'] = beta_results

    return df_pf, df_beta


def norm_array(ar: List[float]) -> float:
    """
    Evaluates the norm of the array ar.

    Args:
        ar (float): A list of numerical values (floats) representing the array.

    Returns:
        float: The norm of the array.
    """
    norm_ar = [i ** 2 for i in ar]
    norm_ar = sum(norm_ar) ** 0.5
    return norm_ar


def hasofer_lind_rackwitz_fiessler_algorithm(y_k: np.ndarray, g_y: float, grad_y_k: np.ndarray) -> np.ndarray:
    """
    This function calculates the y new value using the Hasofer-Lind-Rackwitz-Fiessler algorithm.
    
    Args:
        y_k (Float): Current y value
        g_y (Float): Objective function in point y_k
        grad_y_k (Float): Gradient of the objective function in point y_k
        
    Returns:
        y_new (Float): New y value
    """

    num = np.dot(np.transpose(grad_y_k), y_k) - np.array([[g_y]])
    print("num: ", num)
    num = num[0][0]
    den = (np.linalg.norm(grad_y_k)) ** 2
    print("den: ", den)
    aux = num / den
    y_new = aux * grad_y_k

    return y_new


def convergence_probability_failure(df: pd.DataFrame, column: str) -> Tuple[List[int], List[float], List[float], List[float], List[float]]:
    """
    This function calculates the convergence rate of a given column in a data frame. This function is used to check the convergence of the failure probability.

    Args:
        df (DataFrame): DataFrame containing the data with indicator function column
        column (String): Name of the column to be analyzed

    Returns:
        div (List): List containing sample sizes
        m (List): List containing the mean values of the column. pf value rate
        ci_l (List): List containing the lower confidence interval values of the column
        ci_u (List): List containing the upper confidence interval values of the column
        var (List): List containing the variance values of the column
    """
    
    column_values = df[column].to_list()
    step = 1000
    div = [i for i in range(step, len(column_values), step)]
    m = []
    ci_u = []
    ci_l = []
    var = []
    for i in range(0, len(div)+1):
        if i == len(div):
            aux = column_values.copy()
            div.append(len(column_values))
        else:
            aux = column_values[:div[i]]
        mean = np.mean(aux)
        std = np.std(aux, ddof=1)
        n = len(aux)
        confidence_level = 0.95
        t_critico = stats.t.ppf((1 + confidence_level) / 2, df=n-1)
        margin = t_critico * (std / np.sqrt(n))
        intervalo_confianca = (mean - margin, mean + margin)
        m.append(mean)
        ci_u.append(intervalo_confianca[1])
        ci_l.append(intervalo_confianca[0])
        var.append((mean * (1 - mean))/n)

    return div, m, ci_l, ci_u, var


def goodness_of_fit(data: Union[np.ndarray, List[float]], distributions: Union[str, List[str]] = 'all') -> Dict[str, Dict[str, Union[str, Tuple[float]]]]:
    """
    Evaluates the fit of distributions to the provided data.

    This function fits various distributions to the data using the distfit library and returns the top three distributions based on the fit score.

    Args:
        data (np.array or list): Data to which distributions will be fitted. It should be a list or array of numeric values.
        distributions (str or list, optional): Distributions to be tested. If 'all', all available distributions will be tested. Otherwise, it should be a list of strings specifying the names of the distributions to test. The default is 'all'.

    Returns:
        dict: A dictionary containing the top three fitted distributions. Each entry is a dictionary with the following keys:
            - 'rank': Ranking of the top three distributions based on the fit score.
            - 'type' (str): The name of the fitted distribution.
            - 'params' (tuple): Parameters of the fitted distribution.
    
    Raises:
        ValueError: If the expected 'score' column is not present in the DataFrame returned by `dist.summary()`.
    """

    if distributions == 'all':
        dist = distfit()
    else:
        dist = distfit(distr=distributions)
    
    dist.fit_transform(data)
    summary_df = dist.summary
    sorted_models = summary_df.sort_values(by='score').head(3)
    
    top_3_distributions = {
        f'rank_{i+1}': {
            'type': model['name'],
            'params': model['params']
        }
        for i, model in sorted_models.iterrows()
    }
    
    return top_3_distributions


def fbf(algorithm: str, n_constraints: int, time_analysis: int, results_about_data: pd.DataFrame) -> Tuple[pd.DataFrame, List[List[str]]]:
    """
    This function application first barrier failure algorithm.

    Args:
        algorithm (str): Name of the algorithm
        n_constraints (int): Number of constraints analyzed
        time_analysis (int): Time period for analysis
        results_about_data (pd.DataFrame): DataFrame containing the results to be processed 

    Returns:
        results_about_data: Updated DataFrame after processing
    """

    if algorithm.upper() in ['MCS-TIME', 'MCS_TIME', 'MCS TIME']:
        i_columns = []
        for i in range(n_constraints):
            aux_column_names = []
            for j in range(time_analysis):
                aux_column_names.append('I_' + str(i) + '_t=' + str(j))
            i_columns.append(aux_column_names)

        for i in i_columns:
            matrixx = results_about_data[i].values
            for id, linha in enumerate(matrixx):
                indice_primeiro_1 = np.argmax(linha == 1)
                if linha[indice_primeiro_1] == 1:
                    matrixx[id, indice_primeiro_1:] = 1
            results_about_data = pd.concat([results_about_data.drop(columns=i),
                                            pd.DataFrame(matrixx, columns=i)], axis=1)
    else:
        i_columns = []
        for i in range(n_constraints):
            i_columns.append(['I_' + str(i)])
    
    return results_about_data, i_columns


def log_message(message: str) -> None:
    """
    Logs a message with the current time.

    Args:
        message (str): The message to log.
    
    Returns:
        None
    """
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f'{current_time} - {message}')


def sampling_uniform_distribution(sampling_min: float, sampling_max: float, n_samples: int, seed: int) -> list:
    """
    This function generates a list of random uniform samples according to a given distribution.

    Args:
        sampling_min (float): Minimum value of the distribution
        sampling_max (float): Maximum value of the distribution
        n_samples (int): Number of samples
        seed (int): Seed for random number generation

    Returns:
        samples (List): List of random samples
    """
    np.random.seed(seed)
    samples = np.random.uniform(sampling_min, sampling_max, n_samples).tolist()
    
    return samples 


def uniform_lhs(n_samples: int, dimension: int, seed: int) -> np.ndarray:
    """
    This function generates a list of random samples according to a uniform distribution using the Latin Hypercube Sampling (LHS) method.

    Args:
        n_samples (int): Number of samples
        dimension (int): Number of dimensions
        seed (int): Seed for random number generation

    Returns:
        samples (np.array): Array of random samples
    """
    np.random.seed(seed)
    r = np.zeros((n_samples, dimension))
    p = np.zeros((n_samples, dimension))
    lista_original = [i for i in range(1, n_samples+1)]
    for i in range(dimension):
        r[:, i] = np.random.uniform(0, 1, n_samples) * (1 / n_samples)
        permutacao = lista_original.copy()
        random.shuffle(permutacao)
        if i == 0:
            p[:, i] = [i for i in range(1, n_samples + 1)]
        else:
            p[:, i] = permutacao.copy()

    p = p * (1 / n_samples)
    u_1 = p - r

    return u_1


def inverse_normal_sampling(n_samples: int, mean: float, std: float, seed: int, method: str) -> list:
    """
    This function generates a list of random samples according to a normal distribution.
    """

    if method.upper() == 'MCS':
        u_1 = sampling_uniform_distribution(0, 1, n_samples, seed)
        u_2 = sampling_uniform_distribution(0, 1, n_samples, seed+1)
    
    elif method.upper() == 'LHS':
        u_1 = uniform_lhs(n_samples, 1, seed)[:, 0]
        u_2 = uniform_lhs(n_samples, 1, seed)[:, 0]

    x_0 = []
    for i in range(n_samples):
        z_0 = np.sqrt(-2 * np.log(u_1[i])) * np.cos(2 * np.pi * u_2[i])
        x_0.append(mean + std * z_0)

    return x_0


def inverse_gumbel_r(n_samples: int, mean: float, std: float, seed: int, method: str) -> list:

    gamma = 1.1396
    beta = np.sqrt(6) * std / np.pi
    mu_n = mean - beta * gamma
    
    if method.upper() == 'MCS':
        u_1 = sampling_uniform_distribution(0, 1, n_samples, seed)

    elif method.upper() == 'LHS':
        u_1 = uniform_lhs(n_samples, 1, seed)

    x_0 = []
    for i in range(n_samples):
        x_0.append(mu_n - beta * np.log(-np.log(u_1[i])))

    return x_0


def inverse_gumbel_l(n_samples: int, mean: float, std: float, seed: int, method: str) -> list:

    gamma = 0.577216
    beta = np.sqrt(6) * std / np.pi
    mu_n = mean + beta * gamma
    
    if method.upper() == 'MCS':
        u_1 = sampling_uniform_distribution(0, 1, n_samples, seed)

    elif method.upper() == 'LHS':
        u_1 = uniform_lhs(n_samples, 1, seed)

    x_0 = []
    for i in range(n_samples):
        x_0.append(mu_n + beta * np.log(-np.log(u_1[i])))

    return x_0


def triangular_inverse_cdf(n_samples: int, a_min: float, a_mean: float, a_max: float, seed: int, method: str) -> list:
    """
    This function generates a list of random samples according to a triangular distribution.

    Args:
        n_samples (int): Number of samples
        a_min (float): Minimum value of the distribution
        a_mean (float): Mean value of the distribution
        a_max (float): Maximum value of the distribution
        seed (int): Seed for random number generation

    Returns:
        x_0 (List): List of random samples
    """

    if method.upper() == 'MCS':
        u_1 = sampling_uniform_distribution(0, 1, n_samples, seed)

    elif method.upper() == 'LHS':
        u_1 = uniform_lhs(n_samples, 1, seed)

    x_0 = []
    # Cálculo do ponto onde a PDF muda de forma
    f_c = (a_max - a_min) / (a_mean - a_min)
    for i in range(n_samples):
        if u_1[i] < f_c:
            x_0.append(a_min + np.sqrt(u_1[i] * (a_mean - a_min) * (a_max - a_min)))
        else:
            x_0.append(a_max - np.sqrt((1 - u_1[i]) * (a_max - a_mean) * (a_max - a_min)))

    return x_0


def inverse_lognormal_sampling(n_samples: int, mean: float, std: float, seed: int, method: str) -> list:
    """
    This function generates a list of random samples according to a lognormal distribution.
    """

    epsilon = np.sqrt(np.log(1 + (std/mean)**2))
    lambdaa = np.log(mean) - 0.5 * epsilon**2

    if method.upper() == 'MCS':
        u_1 = sampling_uniform_distribution(0, 1, n_samples, seed)
        u_2 = sampling_uniform_distribution(0, 1, n_samples, seed+1)

    elif method.upper() == 'LHS':
        u_1 = uniform_lhs(n_samples, 1, seed)[:, 0]
        u_2 = uniform_lhs(n_samples, 1, seed)[:, 0]

    x_0 = []
    for i in range(n_samples):
        z_0 = np.sqrt(-2 * np.log(u_1[i])) * np.cos(2 * np.pi * u_2[i])
        x_0.append(np.exp(lambdaa + epsilon * z_0))

    return x_0