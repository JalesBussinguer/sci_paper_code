from scipy.stats import chi2
from scipy.special import psi
from math import log
import pandas as pd
import numpy as np

def gamma_s_test(k_p, k_q, theta_p, theta_q, m, n, significance_level=0.05):

    """Implements the hypothesis test for Kullback-Leibler distances of gamma distributions.

    Based on Nascimento et al (2010) - DOI: 10.1109/TGRS.2009.2025498

    H0: Two samples obtained in different regions can be described by the same distribution
    
    Args:
        k_p (float): shape of the gamma distribution 1
        k_q (float): shape of the gamma distribution 2
        theta_p (float): scale of the gamma distribution 1
        theta_q (float): scale of the gamma distribution 2
        m (int): number of samples of the distribution 1
        n (int): number of samples of the distribution 2
        significance_level (float, optional): Significance level of the test. Defaults to 0.05.

    Returns:
        int: the result of the test. 0 = Accept H0 and 1 = Reject H0.
    """

    # Kullback-Leibler distances (simmetrized)
    dskl_g = ((k_p - k_q) * (psi(k_p) + log(theta_p) - psi(k_q) - log(theta_q)) + ((k_p * theta_p - k_q * theta_q) * ((theta_p - theta_q) / (theta_p * theta_q)))) / 2

    # Statistic
    s = ((2*m*n) / (m + n)) * dskl_g

    p_value = chi2.sf(s, df=2) # df = degrees of freedom (number of parameters of the distribution)

    # Hypothesis test
    if p_value <= significance_level:
        result = 1 # Reject H0

    if p_value > significance_level:
        result = 0 # Accept H0
    
    return result

def lognorm_s_test(scale_p, scale_q, shape_p, shape_q, m, n, significance_level=0.05):

    """Implements the hypothesis test for Kullback-Leibler distances of lognormal distributions.

    Based on Nascimento et al (2010) - DOI: 10.1109/TGRS.2009.2025498

    H0: Two samples obtained in different regions can be described by the same distribution

    Args:
        sc_p (float): scale of the lognormal distribution 1
        sc_q (float): scale of the lognormal distribution 2
        sh_p (float): shape of the lognormal distribution 1
        sh_q (float): shape of the lognormal distribution 2
        m (int): number of samples of the distribution 1
        n (int): number of samples of the distribution 2
        significance_level (float, optional): Significance level of the test. Defaults to 0.05.

    Returns:
        int: the result of the test. 0 = Accept H0 and 1 = Reject H0.
    """

    # Scipy parametrization: scale = exp(mu) and shape = sigma

    mu_p = log(scale_p)
    mu_q = log(scale_q)
    var_p = np.power(shape_p, 2)
    var_q = np.power(shape_q, 2)

    # Kullback-Leibler distances (simmetrized)
    dskl_ln = (var_p * np.power((mu_p - mu_q), 2) + var_q * np.power((mu_q - mu_p), 2) + np.power((var_p - var_q), 2)) / (2 * var_p * var_q)

    s = ((2*m*n) / (m + n)) * dskl_ln # statistic

    p_value = chi2.sf(s, df=2)

    if p_value <= significance_level:
        result = 1 # Reject H0
        
    if p_value >= significance_level:
        result = 0 # Accept H0
    
    return result

    

if __name__ == '__main__':

    dataset = 1

    df = pd.read_csv(dataset)

    for i in len(df.index):
        for j in len(df.index):
            
            lognorm_s_test(i, j)

            # Record the result of the s test in a Mij matrix