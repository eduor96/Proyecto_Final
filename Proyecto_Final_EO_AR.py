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
#%%
# =============================================================================
# Ciclo para descargar precios de oanda
# =============================================================================
while pd.to_datetime(F2)<fechas[-1]:
    params = {"granularity": A1_OA_Gn, "price": "M", "dailyAlignment": A1_OA_Da,
              "alignmentTimezone": A1_OA_Ta, "from": F1, "to": F2}
    A1_Req1 = instruments.InstrumentsCandles(instrument=A1_OA_In, params=params)
    A1_Hist = api.request(A1_Req1)
    
    for i in range(len(A1_Hist['candles'])-1):

            lista.append({'TimeStamp': A1_Hist['candles'][i]['time'],
                          'Open': A1_Hist['candles'][i]['mid']['o'],
                          'High': A1_Hist['candles'][i]['mid']['h'],
                          'Low': A1_Hist['candles'][i]['mid']['l'],
                          'Close': A1_Hist['candles'][i]['mid']['c']})
            
    F1=ag_car(str(fechas[n+1]))
    n=n+5000
    try:F2=ag_car(str(fechas[n]))
    except IndexError:
        break
# =============================================================================
# Data Frame 1: Precios
# =============================================================================
df1_precios = pd.DataFrame(lista)
df1_precios = df1_precios[['TimeStamp', 'Open', 'High', 'Low', 'Close']]
df1_precios['TimeStamp'] = pd.to_datetime(df1_precios['TimeStamp'])
#%%
# =============================================================================
# Data Frame 2: Operaciones
# =============================================================================
n=len(df1_precios)
data=np.empty((n,8))
df2_operaciones=pd.DataFrame(data,columns=['Fecha','Folio','Operacion',
                             'Unidades','Margen','Comentario','Precio_Apertura',
                             'Precio_Cierre']).replace(0,"-")
df2_operaciones['Fecha']=df1_precios.iloc[:,0]
# =============================================================================
# Data Frame 3: Cuenta
# =============================================================================
data=np.empty((n,6))
df3_cuenta=pd.DataFrame(data,columns=['Fecha','Capital','Flotante',
                             'Balance','Rendimiento','Comentario']).replace(0,"-")
df3_cuenta['Fecha']=df1_precios.iloc[:,0]
# =============================================================================
# Inicializacion de parametros
# =============================================================================
