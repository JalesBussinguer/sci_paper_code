from math import log
from scipy.special import psi

# kp = shape of the gamma distribution 1
# kq = shape of the gamma distribution 2

# thetap = scale of the gamma distribution 1
# thetaq = scale of the gamma distribution 2

kq = 1
kp = 1
thetap = 1
thetaq = 1

dskl = ((kp - kq) * (psi(kp) + log(thetap) - psi(kq) - log(thetaq)) + ((kp*thetap - kq*thetaq) * ((thetap - thetaq) / (thetap * thetaq)))) / 2