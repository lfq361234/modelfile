# -*- coding: utf-8 -*-
"""
Created on Mon Aug 12 23:40:53 2019

@author: joe
"""

import pandas as pd
import numpy as np
ABSPath="C:/Users/joe/Desktop/CodeImplementation/MyTrading/TWList_Data_Grab/"
from modelfile import CGetMx,Rank,DivCrossSum,Mean,LT,LEQ,GT,GEQ,EQ,Lead,Lag,DeMean\
                       ,Add,Sub,Mul,Div,CSimulation,InstSum
import signalM 
import matplotlib.pyplot as plt
#import time
#tStart = time.time()

#['Date', '證券代號', '收盤價', '開盤價', '最高價', '最低價', '成交股數', '成交筆數', '本益比']
#select 50 stocks as universe
def getUniverse(year):
    df=pd.read_pickle(ABSPath+str(year)+".pkl")
    dfClose=df["收盤價"]
    dfShares=df["成交股數"]
    df["liquidity"]=dfClose*dfShares
    AllSec=df.groupby("證券代號").sum()
    AllSec=AllSec.sort_values(["liquidity"], ascending = False)
    UniSec=AllSec.index[:50]
    return UniSec


def Simulate(year):
    #set of MXs: close open high low volume p/e
    #must assign df for signal.py(the data source of Mx)
    UniSec=getUniverse(year-1)
    df=pd.read_pickle(ABSPath+str(year-1)+".pkl")
    df=df.append(pd.read_pickle(ABSPath+str(year)+".pkl"), ignore_index=True)
    if year<2019:
        df=df.append(pd.read_pickle(ABSPath+str(year+1)+".pkl").iloc[0:50000,:], ignore_index=True)
    df=df[df["證券代號"].isin(UniSec)].reset_index(drop=True)
    dfAdj=pd.read_pickle(ABSPath+"AdjustMxSource.pkl").sort_values(by=['Date'])
    #Require df and dfAdj have same range of end date
    if df.iloc[-1,0]>dfAdj.iloc[-1,0]:
        df=df.iloc[0:df.loc[df['Date'] == dfAdj.iloc[-1,0]].index[-1]+1]
    elif dfAdj.iloc[-1,0]>df.iloc[-1,0]:
        dfAdj=dfAdj.iloc[0:dfAdj.loc[dfAdj['Date'] == df.iloc[-1,0]].index[-1]+1]
    #model file function testing area (import modelfile.py functions ) 
    #strategy (signal.mt)
    test,long,short,PricesC=signalM.signalMT(df,dfAdj)
    #Simulation  test, long, short are specified in signal.py
    sDate=str(year)+"0101"
    eDate=str(year)+"1231"
    SIM=CSimulation(test,long,short,sDate,eDate)
    L,S,T=SIM.L,SIM.S,SIM.T
    longWeight,shortWeight=SIM.longWeight,SIM.shortWeight
    LTC,STC=SIM.TradedCount()
    LTO,STO,TTO=SIM.TurnOver()
    L_M,S_M,T_M=SIM.LST_Moment()
    PricesC=PricesC[PricesC['Date']>=sDate].reset_index(drop=True)
    if(any(PricesC['Date']>eDate)):
        PricesC=PricesC.iloc[0:PricesC[PricesC['Date']>eDate].index[0]+2]
    return L,S,T,longWeight,shortWeight,LTC,STC,LTO,STO,TTO,L_M,S_M,T_M,PricesC
def Draw(L,S,T):
    fig, ax = plt.subplots()
    L.plot(kind='line',x='Date',y='L',color='blue',ax=ax)
    S.plot(kind='line',x='Date',y='S',color='LimeGreen',ax=ax)
    T.plot(kind='line',x='Date',y='T',color='orange',ax=ax)
    plt.show()
    print("Return: ",T.iloc[:,1].tail(1).values[0])
    if(T.iloc[:,1].diff().std()!=0):
        print("Sharpe: ",T.iloc[:,1].diff().mean()/T.iloc[:,1].diff().std())
    else:
        print("Sharpe: nan")
    print("MDD:    ",np.max(1-T.iloc[:,1]/np.maximum.accumulate(T.iloc[:,1])))



L_M0=pd.DataFrame()
S_M0=pd.DataFrame()
T_M0=pd.DataFrame()
LTC0=pd.DataFrame()
STC0=pd.DataFrame()
LTO0=pd.DataFrame()
STO0=pd.DataFrame()
TTO0=pd.DataFrame()
longWeightAll=pd.DataFrame()
shortWeightAll=pd.DataFrame()
PricesCAll=pd.DataFrame()
for year in range(2016,2020):
    L,S,T,longWeight,shortWeight,LTC,STC,LTO,STO,TTO,L_M,S_M,T_M,PricesC=Simulate(year)
#   moment return    
    L_M0=L_M0.append(L_M, ignore_index=True)
    S_M0=S_M0.append(S_M, ignore_index=True)
    T_M0=T_M0.append(T_M, ignore_index=True)
#   traded count    
    LTC0=LTC0.append(LTC, ignore_index=True)
    STC0=STC0.append(STC, ignore_index=True)
#   turnover
    LTO0=LTO0.append(LTO, ignore_index=True)
    STO0=STO0.append(STO, ignore_index=True)
    TTO0=TTO0.append(TTO, ignore_index=True)
    longWeightAll=longWeightAll.append(longWeight, ignore_index=True,sort=True).fillna(0)
    shortWeightAll=shortWeightAll.append(shortWeight, ignore_index=True,sort=True).fillna(0)
#   append prices in different years for tradedbacktest 
    PricesCAll=pd.concat([PricesCAll,PricesC], ignore_index=True,sort=True).drop_duplicates('Date')
    PricesCAll=PricesCAll.set_index('Date')
    PricesC=PricesC.set_index('Date')
    intersect=set(PricesCAll.columns.tolist()).intersection(set(PricesC.columns.tolist()))
    for cols in PricesC:
        if cols in intersect:
            PricesCAll.loc[PricesC.index,cols]=PricesC.loc[PricesC.index,cols]
    PricesCAll=PricesCAll.reset_index('Date')
    
#LST cumulative return graph 
L_M0['L']=L_M0['L'].cumsum()  
S_M0['S']=S_M0['S'].cumsum()
T_M0['T']=T_M0['T'].cumsum()
Draw(L_M0,S_M0,T_M0)
B=S_M0
A=L_M0

print("LongRetun: ",L_M0.iloc[-1,1])
print("ShortRetun: ",-1*S_M0.iloc[-1,1])
print("LongTurnover:",LTO0.iloc[:,1].mean() )
print("ShortTurnover:",STO0.iloc[:,1].mean() )

#tEnd = time.time()
#print(tEnd - tStart)

#return after considering turnover


#signal for traded backtest
longWeightAll.to_pickle("longsig.pkl")
shortWeightAll.to_pickle("shortsig.pkl")
PricesCAll.to_pickle("pricesC.pkl")


#Research Method
#regression/simulation/dailystat/histogram/caar/corrMatrix

#backtest mimic model file (write function in modelfile.py)
#mocktrading.py mimic realistic trading account
