# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 11:35:53 2019

@author: eduor
"""
from twilio.rest import Client
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
account_sid = "AC7ca38f83e6fec4679c7ed1ff8fa2e036"
# Your Auth Token from twilio.com/console
auth_token  = "dc8dc79a5e89417c4e3319ff0551c265"

client =Client(account_sid, auth_token)

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
start_date = datetime(2016, 4, 1)
end_date = datetime(2019, 4, 1)
fechas = date_range(start_date, end_date, 5, 'minutes')#Creamos vector de fechas con intervalo de 5 minutos

A1_OA_Da = 17                     # Day Align
A1_OA_Ta = "America/Mexico_City"  # Time Align

A1_OA_Ai = "101-004-2221697-001"  # Id de cuenta
A1_OA_At = "practice"             # Tipo de cuenta

A1_OA_In = "USD_MXN"              # Instrumento
A1_OA_Gn = "M5"                   # Granularidad de velas

A1_OA_Ak = "a1a2738e43e01183e07cbb8dec8e2ca4-771e2b55a25bd1f6cb73b42ca4b1f432"


F1=ag_car(str(fechas[0])) #Fecha 1 inicial
F2=ag_car(str(fechas[5000])) #Fecha 2 inicial

# =============================================================================
# Inicializar API de Oanda
# =============================================================================
api = API(access_token=A1_OA_Ak)
#

lista = [] #Inicializamos lista 
n=5000
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
#%%
def main_function(x):
    up_rsi,down_rsi,stop_loss,take_profit,ventana,fin=x[0],x[1],x[2],x[3],int(x[4]),500
    capital_i=100000 #Capital Inicial USD
    flotante=0 
    p_o=.10 #Porcentaje de capital por operacion
    cap=capital_i
    oper_act=False
    folio_v=1
    folio_c=1
    venta=False
    for i in range(ventana,fin):
        rsi_=rsi_fun(df1_precios.iloc[:,2],i,ventana)
        open_price=float(df1_precios.iloc[i,1])
        #hi_price=float(df1_precios.iloc[i,2])
        #low_price=float(df1_precios.iloc[i,3])
        close_price=float(df1_precios.iloc[i,4])
       
        if rsi_>=up_rsi and oper_act==False :
            #Cambios en Data Frame 2: Operaciones
            df2_operaciones.iloc[i,1]="V_"+str(folio_v)
            df2_operaciones.iloc[i,2]=-1
            monto=p_o*cap
            unidades=math.floor(monto)
            df2_operaciones.iloc[i,3]=unidades
            df2_operaciones.iloc[i,5]="RSI a: "+str(rsi_)
            df2_operaciones.iloc[i,6]=open_price
            #Cambios en Data Frame 3: Cuenta
            cap=cap-monto
            df3_cuenta.iloc[i,5]="Se abrió operación: venta"
            precio_operacion=open_price
            #Cambios generales por operacion
            ult_folio="V_"+str(folio_v)
            folio_v+=1
            oper_act=True
            venta=True
    
        if rsi_<=down_rsi and oper_act==False :
            #Cambios en Data Frame 2: Operaciones
            df2_operaciones.iloc[i,1]="C_"+str(folio_c)
            df2_operaciones.iloc[i,2]=1
            monto=p_o*cap
            unidades=math.floor(monto)
            df2_operaciones.iloc[i,3]=unidades
            df2_operaciones.iloc[i,5]="RSI a: "+str(rsi_)
            df2_operaciones.iloc[i,6]=open_price
            #Cambios en Data Frame 3: Cuenta
            cap=cap-monto
            df3_cuenta.iloc[i,5]="Se abrió operación: compra"
            precio_operacion=open_price
            #Cambios generales por operacion
            ult_folio="C_"+str(folio_c)
            folio_c+=1
            oper_act=True
        if oper_act==True: #Si existe una operación activa
            if venta:#Si la operación activa es una venta
                flotante=((precio_operacion-close_price)*unidades)/close_price+unidades
            else:
                flotante=((close_price-precio_operacion)*unidades)/close_price+unidades
            pr_lo= flotante-unidades
            if pr_lo>=take_profit or pr_lo<=stop_loss: #Si se cumple alguno de los parametros
                df3_cuenta.iloc[i,1]=cap+flotante
                cap=cap+flotante
                df3_cuenta.iloc[i,2]=0
                df3_cuenta.iloc[i,3]=df3_cuenta.iloc[i,1]
                df3_cuenta.iloc[i,4]=df3_cuenta.iloc[i,3]/capital_i-1
                df3_cuenta.iloc[i,5]="Se cerró operación: Con pérdida/ganancia: " + str(pr_lo)
                
                df2_operaciones.iloc[i,1]=ult_folio
                if pr_lo<=stop_loss: #Si se cumple el stop loss
                    df2_operaciones.iloc[i,5]="Se ejecutó Stop Loss: "+str(pr_lo)
                else:
                    if pr_lo>=take_profit: #Si se cumple el take profit
                        df2_operaciones.iloc[i,5]="Se ejecutó Take Profit: "+str(pr_lo)
                df2_operaciones.iloc[i,7]=close_price
                oper_act=False #Ponemos como inactiva las operación abierta
            else: #Si no se cumple ningun parametro (stop loss,take profit)
                df3_cuenta.iloc[i,1]=cap
                df3_cuenta.iloc[i,2]=flotante
                df3_cuenta.iloc[i,3]=df3_cuenta.iloc[i,1]+df3_cuenta.iloc[i,2]
                df3_cuenta.iloc[i,4]=df3_cuenta.iloc[i,3]/capital_i-1
        else: #si no existe alguna operación activa
            df3_cuenta.iloc[i,1]=cap
            df3_cuenta.iloc[i,2]=0
            df3_cuenta.iloc[i,3]=df3_cuenta.iloc[i,1]+df3_cuenta.iloc[i,2]
            df3_cuenta.iloc[i,4]=df3_cuenta.iloc[i,3]/capital_i-1
        print(i)
    rendimiento_final=df3_cuenta.iloc[i-1,4]
    
    return rendimiento_final
