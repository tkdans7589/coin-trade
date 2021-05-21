# -*- coding: utf-8 -*-
"""
Created on Sat Apr 17 15:20:54 2021

@author: tkdan
"""
import pandas as pd
import requests
import talib
import numpy as np

def index(symbol):
    url = "https://api.upbit.com/v1/candles/minutes/1"
    querystring = {"market":symbol,"count":"200"}
    response = requests.request("GET", url, params=querystring)
    data = response.json()
    df = pd.DataFrame(data)
    df=df.reindex(index=df.index[::-1]).reset_index()

    rsi_result = round(talib.RSI(np.asarray(df['trade_price']),14)[-1],2)
    indicator_result = {'rsi': rsi_result}
    
    return indicator_result
