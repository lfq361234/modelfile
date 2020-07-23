# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 17:02:38 2019

@author: joe
"""
from modelfile import CGetMx,Rank,DivCrossSum,Mean,LT,LEQ,GT,GEQ,EQ,Lead,Lag,DeMean\
                       ,Add,Sub,Mul,Div,CSimulation,InstSum,InstMean,InstStdev,InstMin\
                       ,InstMax,CMx

#signal.mt begin 
#must assign value to test,long,short,PricesC
#Now backtest.df is the data source of Mx 
#get each Mx from data sources
#CMx是另外的東西不用管他，基本上用CGetMx就可以了，Add Sub Mul等函數已經定義在modelfile.py之中 
def signalMT(df,df2):
    f=CGetMx(df,df2)
    PricesC=f.PricesC()
    PricesO=f.PricesO()
    PricesH=f.PricesH()
    PricesL=f.PricesL()
    PricesV=f.PricesV()
    PE=f.PERatio()
# 
#    factor1=(CMx(PricesH)-CMx(PricesL)).getDFData() 
#    signal=factor1
    
#    signal=f.Returns(-80)   
#    f2=InstMean(f.Returns(-1),126)
    
#    f1=Mul(InstSum(f.Returns(-1),30),f.ToMx(-1))
#    f1a=Add(Add(Mul(f1,f.ToMx(0.5)),Mul(Lag(f1,1),f.ToMx(1/3))),Mul(Lag(f1,2),f.ToMx(1/6)))

#volume  
    f2=Mul(InstMean(PricesV,30),f.ToMx(-1))
#52WH
#    f3=Div(PricesC,InstMax(PricesH,252))
#    signal=f3

#    f4=InstMean(PricesC,100)
#    signal=Sub(PricesC,f4)

#ratio
#    avg=Mul(Add(PricesH,PricesL),f.ToMx(0.5))
#    ra=Sub(avg,PricesC)
    
# volume Prices    
    avg=Div(Add(PricesH,PricesL),f.ToMx(2))
    avgRatio=Div(Sub(avg,PricesC),PricesC)
    signal0=InstSum(avgRatio,30)
    signal=Add(Rank(signal0),Rank(f2))
    signal=f2
    #start simulation
    long=GT(Rank(signal),f.ToMx(0.9))
    short=LT(Rank(signal),f.ToMx(0.1))


    fReturn=Lead(f.Returns(1),1)
    test=DeMean(fReturn)
    
    PricesAdjC=f.PricesAdjC()
    return test,long,short,PricesAdjC
