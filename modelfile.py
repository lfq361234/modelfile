# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 00:26:02 2019

@author: joe
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#########################################get MX from data source
class CGetMx():
    def __init__(self, df,dfAdj):
        self.df = df
        self.dfAdj=dfAdj
        self.adjC=self.PricesAdjC()
    def PricesC(self):
        return pd.pivot_table(self.df, values='收盤價', index=['Date'],columns=['證券代號']).reset_index()
    def PricesO(self):
        return pd.pivot_table(self.df, values='開盤價', index=['Date'],columns=['證券代號']).reset_index()
    def PricesH(self):
        return pd.pivot_table(self.df, values='最高價', index=['Date'],columns=['證券代號']).reset_index()
    def PricesL(self):
        return pd.pivot_table(self.df, values='最低價', index=['Date'],columns=['證券代號']).reset_index()
    def PricesV(self):
        return pd.pivot_table(self.df, values='成交股數', index=['Date'],columns=['證券代號']).reset_index()
    def PERatio(self):
        return pd.pivot_table(self.df, values='本益比', index=['Date'],columns=['證券代號']).reset_index()
    def Returns(self,days):
        AdjC=self.adjC.set_index('Date')
        if days>0:
            return ((AdjC.shift(-days)-AdjC)/AdjC).reset_index()
        else:
            return ((AdjC-AdjC.shift(-days))/AdjC.shift(-days)).reset_index()
    def ToMx(self,number):
        self.df['number']=number
        return pd.pivot_table(self.df, values='number', index=['Date'],columns=['證券代號']).reset_index()
    def PricesAdjC(self):
        PricesC=pd.pivot_table(self.df, values='收盤價', index=['Date'],columns=['證券代號']).reset_index()
        PricesC=PricesC.set_index('Date')
        AdjSet=self.dfAdj
        AdjSet=AdjSet.set_index('Date')
        intersect=set(PricesC.columns.tolist()).intersection(set(AdjSet.columns.tolist()))
        intersectIndex=set(PricesC.index.tolist()).intersection(set(AdjSet.index.tolist()))
        B=AdjSet[intersect].reindex(index=intersectIndex)
        for cols in PricesC:
            if cols in intersect:
                PricesC.loc[B.index,cols]=B.loc[B.index,cols]
        C=PricesC.reset_index()
        return C
###########################################single Mx content
class CMx():
    def __init__(self, dfData):
        self.dfData = dfData
        self.SecCode = dfData.columns[1:]
        self.Date = dfData['Date']
    def getSecCode(self):
        return self.SecCode
    def getDate(self):
        return self.Date
    def getDFData(self):
        return self.dfData
    def getNonZeroPerDay(self,strDate):
        df=self.dfData
        subdf=df[df['Date']==strDate]
        subdf=subdf.loc[:,(subdf!= 0).any()]
        return subdf
    def getPerDay(self,strDate):
        df=self.dfData
        subdf=df[df['Date']==strDate]
        return subdf
    def __add__(self,other):
        self.dfData=Add(self.dfData,other.dfData)
        return self
    def __sub__(self,other):
        self.dfData=Sub(self.dfData,other.dfData)
        return self
    def __mul__(self,other):
        self.dfData=Mul(self.dfData,other.dfData)
        return self
    def __truediv__(self,other):
        self.dfData=Div(self.dfData,other.dfData)
        return self
    def __gt__(self,other):
        self.dfData=GT(self.dfData,other.dfData)
        return self
    def __ge__(self,other):
        self.dfData=GEQ(self.dfData,other.dfData)
        return self
    def __lt__(self,other):
        self.dfData=LT(self.dfData,other.dfData)
        return self
    def __le__(self,other):
        self.dfData=LEQ(self.dfData,other.dfData)
        return self
    def __eq__(self,other):
        self.dfData=EQ(self.dfData,other.dfData)
        return self

    

############################################Simulation 
class CSimulation():
    def __init__(self,test,long,short,sDate,eDate):
        self.test=test
        self.long=long
        self.short=short
        self.sDate=sDate
        self.eDate=eDate
        self.longWeight,self.shortWeight=self.LSWeight()
        self.L,self.S,self.T=self.LST_Moment()
    def LSWeight(self):
        long=self.long
        short=self.short
        sDate=self.sDate
        eDate=self.eDate
        long=long[(long['Date']>=sDate)&(long['Date']<=eDate)].reset_index(drop=True)
        short=short[(short['Date']>=sDate)&(short['Date']<=eDate)].reset_index(drop=True)
        longWeight=DivCrossSum(long)
        longWeight=longWeight.fillna(0)
        shortWeight=DivCrossSum(short)
        shortWeight=shortWeight.fillna(0)
        return longWeight,shortWeight
    def SimulateLST(self): 
        test=self.test
        sDate=self.sDate
        eDate=self.eDate 
        test=test[(test['Date']>=sDate)&(test['Date']<=eDate)].reset_index(drop=True)
        test=test.fillna(0)
        longWeight=self.longWeight.copy()
        shortWeight=self.shortWeight.copy()
        R_v=test.set_index('Date').values
        L_v=longWeight.set_index('Date').values
        S_v=shortWeight.set_index('Date').values
        L=(L_v*R_v).sum(axis=1).cumsum()
        S=(S_v*R_v).sum(axis=1).cumsum()
        T=L-S
        L=pd.DataFrame(L[:,np.newaxis],index=test['Date'],columns=['L']).reset_index()
        S=pd.DataFrame(S[:,np.newaxis],index=test['Date'],columns=['S']).reset_index()
        T=pd.DataFrame(T[:,np.newaxis],index=test['Date'],columns=['T']).reset_index()
        return L,S,T
    def LST_Moment(self): 
        test=self.test
        sDate=self.sDate
        eDate=self.eDate 
        test=test[(test['Date']>=sDate)&(test['Date']<=eDate)].reset_index(drop=True)
        test=test.fillna(0)
        longWeight=self.longWeight.copy()
        shortWeight=self.shortWeight.copy()
        R_v=test.set_index('Date').values
        L_v=longWeight.set_index('Date').values
        S_v=shortWeight.set_index('Date').values
        L=(L_v*R_v).sum(axis=1)
        S=(S_v*R_v).sum(axis=1)
        T=L-S
        L=pd.DataFrame(L[:,np.newaxis],index=test['Date'],columns=['L']).reset_index()
        S=pd.DataFrame(S[:,np.newaxis],index=test['Date'],columns=['S']).reset_index()
        T=pd.DataFrame(T[:,np.newaxis],index=test['Date'],columns=['T']).reset_index()
        return L,S,T
    def Ret(self,T):
        return T.iloc[:,1].tail(1).values[0]
    def Sharpe(self,T):
        return T.iloc[:,1].diff().mean()/T.iloc[:,1].diff().std()
    def MDD(self,T):
        maximums = np.maximum.accumulate(T.iloc[:,1])
        return np.max(1-T.iloc[:,1]/maximums)
    def TradedCount(self):
        longWeight=self.longWeight
        shortWeight=self.shortWeight
        BL=(longWeight[longWeight.columns[1:]]>0).astype(float)
        BS=(shortWeight[shortWeight.columns[1:]]>0).astype(float)
        BL=BL.sum(axis=1)
        BS=BS.sum(axis=1)
        BLdf=pd.DataFrame(BL,columns=['LtradedCount'])
        BSdf=pd.DataFrame(BS,columns=['StradedCount'])
        BLdf['Date']=longWeight['Date']
        BSdf['Date']=shortWeight['Date']
        BLdf=BLdf.reindex(columns=['Date'] + list(BLdf.columns[:-1]))
        BSdf=BSdf.reindex(columns=['Date'] + list(BSdf.columns[:-1]))
        return BLdf,BSdf
    def TurnOver(self):
        longWeight=self.longWeight
        shortWeight=self.shortWeight     
        L_v=longWeight.set_index('Date')
        S_v=shortWeight.set_index('Date')
        LTO=(L_v.diff().abs().sum(axis=1)/2).reset_index()
        STO=(S_v.diff().abs().sum(axis=1)/2).reset_index()
        LTO_v=LTO.set_index('Date').values
        STO_v=STO.set_index('Date').values
        LTC,STC=self.TradedCount()
        LTC=LTC['LtradedCount'].values[:,np.newaxis]
        STC=STC['StradedCount'].values[:,np.newaxis]
        TTO=pd.DataFrame(LTO_v*LTC/(LTC+STC)+STO_v*STC/(LTC+STC))
        TTO['Date']=longWeight['Date']
        TTO=TTO.reindex(columns=['Date'] + list(TTO.columns[:-1]))
        return LTO,STO,TTO
    def DrawLSTPerYear(self):
        fig, ax = plt.subplots()
        L=self.L
        S=self.S
        T=self.T
        L.plot(kind='line',x='Date',y='L',color='blue',ax=ax)
        S.plot(kind='line',x='Date',y='S',color='LimeGreen',ax=ax)
        T.plot(kind='line',x='Date',y='T',color='orange',ax=ax)
        plt.show()
        print("Return: ",self.Ret(T))
        print("Sharpe: ",self.Sharpe(T))
        print("MDD:    ",self.MDD(T))

#################Mx operation functions which do not depend on data sources Ex. InstMean
#################Mx(Dataframe): 'Date'(str)(20110101) , SecCodes(float)

        
def Rank(Mx):
    df=Mx.set_index('Date')
    dfRaw=df.rank(axis=1,pct=True)
    dfMin=dfRaw.min(axis=1)/2
    for cols in dfRaw:
        dfRaw.loc[:,cols]=dfRaw.loc[:,cols]-dfMin.values
    return dfRaw.reset_index()
def DivCrossSum(Mx):
    Mx_v=Mx.set_index('Date').values
    Mx_v[np.isnan(Mx_v)]=0
    S_v=Mx.set_index('Date').sum(axis=1).values
    np.seterr(divide='ignore', invalid='ignore')
    Res_v=(Mx_v.T/S_v).T
    Res_df=pd.DataFrame(Res_v,columns=Mx.columns[1:])
    Res_df['Date']=Mx['Date']
    return Res_df.reindex(columns=['Date'] + list(Res_df.columns[:-1]))
def Mean(Mx):
    df=Mx.set_index('Date')
    Mean_v=df.mean(axis=1)
    #repeat vector
    Res_v=np.broadcast_to(Mean_v[:,np.newaxis],(df.index.size,df.columns.size))
    Res_df=pd.DataFrame(Res_v,columns=df.columns,index=df.index)
    return Res_df.reset_index()
  
def LT(Mx1,Mx2):
    B=(Mx1[Mx1.columns[1:]]<Mx2[Mx2.columns[1:]]).astype(float)
    B['Date']=Mx1['Date']
    return B.reindex(columns=['Date'] + list(B.columns[:-1]))
def LEQ(Mx1,Mx2):
    B=(Mx1[Mx1.columns[1:]]<=Mx2[Mx2.columns[1:]]).astype(float)
    B['Date']=Mx1['Date']
    return B.reindex(columns=['Date'] + list(B.columns[:-1]))
def GT(Mx1,Mx2):
    B=(Mx1[Mx1.columns[1:]]>Mx2[Mx2.columns[1:]]).astype(float)
    B['Date']=Mx1['Date']
    return B.reindex(columns=['Date'] + list(B.columns[:-1]))
def GEQ(Mx1,Mx2):
    B=(Mx1[Mx1.columns[1:]]>=Mx2[Mx2.columns[1:]]).astype(float)
    B['Date']=Mx1['Date']
    return B.reindex(columns=['Date'] + list(B.columns[:-1]))
def EQ(Mx1,Mx2):
    B=(Mx1[Mx1.columns[1:]]==Mx2[Mx2.columns[1:]]).astype(float)
    B['Date']=Mx1['Date']
    return B.reindex(columns=['Date'] + list(B.columns[:-1]))
def Lead(Mx,number):
    df=Mx.set_index('Date')
    df=df.shift(-1*number)
    return df.reset_index()
def Lag(Mx,number):
    df=Mx.set_index('Date')
    df=df.shift(number)
    return df.reset_index()
def DeMean(Mx):
    df=Mx.set_index('Date')
    dfMean=Mean(Mx).set_index('Date')
    return (df-dfMean).reset_index()
def Add(Mx1,Mx2):
    df1=Mx1.set_index('Date')
    df2=Mx2.set_index('Date')
    df3=df1.add(df2)
    return df3.reset_index() 
def Sub(Mx1,Mx2):
    df1=Mx1.set_index('Date')
    df2=Mx2.set_index('Date')
    df3=df1.sub(df2)
    return df3.reset_index()   
def Mul(Mx1,Mx2):
    df1=Mx1.set_index('Date')
    df2=Mx2.set_index('Date')
    df3=df1.mul(df2)
    return df3.reset_index()   
def Div(Mx1,Mx2):
    df1=Mx1.set_index('Date')
    df2=Mx2.set_index('Date')
    return (df1/df2).reset_index()     
def InstSum(Mx,number):
    df=Mx.set_index('Date')
    df=df.rolling(number).sum()
    return df.reset_index()
def InstMean(Mx,number):
    df=Mx.set_index('Date')
    df=df.rolling(number).mean()
    return df.reset_index()
def InstStdev(Mx,number):
    df=Mx.set_index('Date')
    df=df.rolling(number).std()
    return df.reset_index()
def InstMin(Mx,number):
    df=Mx.set_index('Date')
    df=df.rolling(number).min()
    return df.reset_index()
def InstMax(Mx,number):
    df=Mx.set_index('Date')
    df=df.rolling(number).max()
    return df.reset_index()

