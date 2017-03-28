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
from video_proc import *

#%%
res = pd.read_csv("resultados_practica.csv", sep="\t")

# Los vectores angulo
rang1 = array(res[["M1RX", "M1RY", "M1RZ"]])
rang2 = array(res[["M2RX", "M2RY", "M2RZ"]])


#%% El angulo relativo

relat = array([rodrigues(r1, -r2) for r1, r2 in zip(rang1, rang2)])

modulo = norm(relat, axis=1)
unit = array([r/m for r, m in zip(relat, modulo)])

angulo = 2*arctan(modulo)*180/pi

subplot(2,1,1)
plot(angulo)

subplot(2,1,2)
plot(unit)
legend(["x", "y", "z"])

