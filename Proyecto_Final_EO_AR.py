# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:35:53 2019

@author: eduor
"""

import numpy as np
from pyswarm import pso
import pandas as pd
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
from dateutil.relativedelta import relativedelta
import numpy as np
import math
import time
#%%
# =============================================================================
# Definimos funciones a utilizar
# =============================================================================

def date_range(start_date, end_date, increment, period):
    #Funcion que crea vector de fechas con incremento especifico
    result = []
    nxt = start_date
    delta = relativedelta(**{period:increment})
    while nxt <= end_date:
        result.append(nxt)
        nxt += delta
    return result

def ag_car(cadena):
    #Funcion que agrega caracteres a cadena, fin especifico para funcion de oanda
    nueva=cadena[0:10]+"T"+cadena[11:-1]+"Z"
    return nueva
def rsi_fun(prices,ind,n):
    #Funcion que obtiene el RSI de ciertos precios con cierto periodo
    
    gains=[]
    losses=[]
    ind=ind-(n)
    for i in range(n) :
        dife=float(prices[ind+1])-float(prices[ind])
        if dife>=0:
            gains.append(dife)
        else:
            losses.append(dife*-1)
        ind=ind+1
    gains=np.array(gains)
    losses=np.array(losses)
    rsi=100-(100/(1+((gains.sum()/14)/(losses.sum()/14))))
    return rsi
