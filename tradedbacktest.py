# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 23:46:28 2019

@author: joe
"""
import pandas as pd
import numpy as np
from modelfile import CMx
import matplotlib.pyplot as plt
import math


investMoney=100000
costConst=0
costPercent=0.004
#costPercent=0
longMx=CMx(pd.read_pickle("longsig.pkl"))
shortMx=CMx(pd.read_pickle("shortsig.pkl"))
priceMx=CMx(pd.read_pickle("pricesC.pkl"))


longDF=longMx.dfData
shortDF=shortMx.dfData
priceDF=priceMx.dfData
for cols in priceDF.columns:
    priceDF[cols]=priceDF[cols].interpolate(method='pad', limit=2)


#for convenience date are set in index
#main differenve from previous backtest comes from
#bsUnit[abs(priceDF.fillna(0).iloc[1:].set_index('Date')*bsUnit)<0.015*investMoney]=0
#this is for lowering the transaction cost 
#the other reason is that the way of calculating return (same $ investment for each day)
def getBSSharesPnL(longDF,priceDF):
    if(longDF.size==priceDF.size):
        buyUnit_v=np.trunc(investMoney*longDF.iloc[:-1,1:].values/priceDF.iloc[1:,1:].values)*-1
        buyUnit=pd.DataFrame(buyUnit_v,columns=priceDF.columns[1:],index=priceDF.iloc[1:,0]).fillna(0)
        sellUnit=pd.DataFrame(-1*buyUnit_v,columns=priceDF.columns[1:],index=priceDF.iloc[1:,0]).shift(1).fillna(0)
        bsUnit=buyUnit.add(sellUnit,fill_value=0)
        bsUnit[abs(priceDF.fillna(0).iloc[1:].set_index('Date')*bsUnit)<0.015*investMoney]=0
        price=priceDF.iloc[1:,:].set_index('Date')
        realizedPnL=((bsUnit*price)-abs(bsUnit*price)*costPercent-costConst).sum(axis=1).cumsum()
        unrealizedPnL=((-1*bsUnit.cumsum()*price)-abs(-1*bsUnit.cumsum()*price)*costPercent-costConst).sum(axis=1)
        PnL=realizedPnL+unrealizedPnL
        return bsUnit.reset_index(), PnL.reset_index()
    else:
        buyUnit_v=np.trunc(investMoney*longDF.iloc[:,1:].values/priceDF.iloc[1:-1,1:].values)*-1
        buyUnit=pd.DataFrame(buyUnit_v,columns=priceDF.columns[1:],index=priceDF.iloc[1:-1,0]).fillna(0)
        sellUnit=pd.DataFrame(-1*buyUnit_v,columns=priceDF.columns[1:],index=priceDF.iloc[2:,0]).fillna(0)
        bsUnit=buyUnit.add(sellUnit,fill_value=0)
        bsUnit[abs(priceDF.fillna(0).iloc[1:].set_index('Date')*bsUnit)<0.015*investMoney]=0
        price=priceDF.iloc[1:,:].set_index('Date')
        realizedPnL=((bsUnit*price)-abs(bsUnit*price)*costPercent-costConst).sum(axis=1).cumsum()
        unrealizedPnL=((-1*bsUnit.cumsum()*price)-abs(-1*bsUnit.cumsum()*price)*costPercent-costConst).sum(axis=1)
        PnL=realizedPnL+unrealizedPnL
        return bsUnit.reset_index(), PnL.reset_index()

bsUnitLong,PnLLong=getBSSharesPnL(longDF,priceDF)
bsUnitShort,PnLShort=getBSSharesPnL(-1*shortDF,priceDF)

fig, ax = plt.subplots()
PnLLong.plot(kind='line',x='Date',y=PnLLong.columns[1],color='blue',ax=ax)
PnLShort.plot(kind='line',x='Date',y=PnLShort.columns[1],color='LimeGreen',ax=ax)
plt.show()

print("PnLLong: ",PnLLong.iloc[-1,1])
print("PnLShort: ",PnLShort.iloc[-1,1])


print(longMx.getNonZeroPerDay(longDF.iloc[-1,0]))

#long part
print("=======Long Part=======")
AnnualizedReturn=252*(PnLLong.set_index('Date').diff().mean())/investMoney
AnnualizedStd=math.sqrt(252)*(PnLLong.set_index('Date').diff().std())/investMoney
MDD=np.max(1-(PnLLong.set_index('Date')+investMoney)/np.maximum.accumulate(PnLLong.set_index('Date')+investMoney))
print("AnnualizedReturn: ",AnnualizedReturn[0])
print("AnnualizedStd: ",AnnualizedStd[0])
print("MDD: ",MDD[0])