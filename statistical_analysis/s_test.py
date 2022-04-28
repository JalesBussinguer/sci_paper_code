from scipy.stats import chi2
from scipy.special import psi
from math import log

# kp = shape of the gamma distribution 1
# kq = shape of the gamma distribution 2

# thetap = scale of the gamma distribution 1
# thetaq = scale of the gamma distribution 2

kq = 1
kp = 1
thetap = 1
thetaq = 1

dskl = ((kp - kq) * (psi(kp) + log(thetap) - psi(kq) - log(thetaq)) + ((kp*thetap - kq*thetaq) * ((thetap - thetaq) / (thetap * thetaq)))) / 2

m = 1
n = 1

s = ((2*m*n) / (m + n)) * dskl

p_value = chi2.sf(s, 0.95)

if p_value <= 0.05:
    print('Reject H0')