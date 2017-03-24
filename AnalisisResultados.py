#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 10:30:06 2017

@author: juanma
"""

from numpy import *
from matplotlib.pyplot import *
import pandas as pd
from scipy.linalg import norm

#%%
res = pd.read_csv("results_med.csv", sep="\t")

# Los vectores angulo
vang1 = array(res[["M1RX", "M1RY", "M1RZ"]])
vang2 = array(res[["M2RX", "M2RY", "M2RZ"]])

alfa1 = array(res["M1a"])
alfa2 = array(res["M2a"])

#%% Calculamos los vectores de Rodrigues
ang1 = norm(vang1, axis=1)
ang2 = norm(vang2, axis=1)

u1 = array( [v/a for v, a in zip(vang1,ang1)])
u2 = array( [v/a for v, a in zip(vang2,ang2)])

rodr_1 = array([u*tan(a/2) for u,a in zip(u1, ang1)])
rodr_2 = array([u*tan(a/2) for u,a in zip(u2, ang2)])

#rodr_1 = ang1
#rodr_2 = ang2

#%% La transposicion de movimientos segun Rodriges
def rodrigues(Omega1, Omega2):
    res = (Omega1 + Omega2 - cross(Omega1, Omega2))/(1 - dot(Omega1, Omega2))
    
    return res


#%% El angulo relativo

relat = array([rodrigues(r1, -r2) for r1, r2 in zip(rodr_1, rodr_2)])

modulo = norm(relat, axis=1)
unit = array([r/m for r, m in zip(relat, modulo)])

angulo = 2*arctan(modulo)*180/pi

subplot(2,1,1)
plot(angulo)

subplot(2,1,2)
plot(unit)
legend(["x", "y", "z"])

#%% Vamos a compensar el angulo
rod_alfa1 = array([tan(a/2.)*array([0., 0., 1.]) for a in alfa1])
tot_ang1 = array([rodrigues(r1, r2) for r1, r2 in zip(rod_alfa1, rodr_1)])
plot(tot_ang1)


#%% Y ahora lo calculamos con la compensacion

relat = array([rodrigues(r1, -r2) for r1, r2 in zip(tot_ang1, rodr_2)])

modulo = norm(relat, axis=1)
unit = array([r/m for r, m in zip(relat, modulo)])

angulo = 2*arctan(modulo)*180/pi

subplot(2,1,1)
plot(angulo)

subplot(2,1,2)
plot(unit)
legend(["x", "y", "z"])
