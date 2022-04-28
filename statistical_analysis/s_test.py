from scipy.stats import chi2

dskl = 1
m = 1
n = 1

s = ((2*m*n) / (m + n)) * dskl

p_value = chi2.sf(s)