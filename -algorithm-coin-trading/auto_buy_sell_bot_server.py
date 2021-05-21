# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 17:19:27 2021

@author: tkdan
"""

import pyupbit
import pandas as pd
import requests
import time
import technical_indicator as ti
import telepot
from datetime import datetime
from auto_buy_sell import buy_sell

tickers=pyupbit.get_tickers(fiat="KRW")
tickers1=tickers[:100]
tickers2=tickers[100:]

#high_rsi=75
low_rsi=25
number = 15
update_want_sec = 300
stop_loss_seconds = 300

url = "https://api.upbit.com/v1/ticker"

message_send_check = [datetime.now() for i in range(number)]

data_columns = ['market', 'acc_trade_price_24h', 'acc_trade_price','acc_trade_volume','acc_trade_volume_24h','change','change_price','change_rate',
              'high_price','highest_52_week_date','highest_52_week_price','low_price','lowest_52_week_date','lowest_52_week_price','opening_price',
              'prev_closing_price','signed_change_price','signed_change_rate','timestamp','trade_date','trade_date_kst','trade_time',
              'trade_time_kst','trade_timestamp','trade_volume', 'trade_price']

with open("auto_trading_bot_telegram_info.txt") as f:
    lines=f.readlines()
    TELEGRAM_TOKEN=lines[0].strip()
    CHAT_ID=lines[1].strip()

print("TELEGRAM_TOKEN: " + TELEGRAM_TOKEN)
print("CHAT_ID: "+ CHAT_ID)

bot = telepot.Bot(TELEGRAM_TOKEN)

bot.sendMessage(chat_id=CHAT_ID, text ="auto_trading_bot_server Start")
print("auto_trading_bot_server_Start")
stop_loss_check = False
try:
    trading_time = datetime.now()
    while True:
        start=time.time()
        rsi_list = []

        coin_data = pd.DataFrame(columns=data_columns)
        
        querystring = {"markets": tickers1}
        response = requests.request("GET", url, params=querystring)
        data1=response.json()
        
        querystring = {"markets": tickers2}
        response = requests.request("GET", url, params=querystring)
        data2 = response.json()
    
        new_df = pd.DataFrame(data1)
        coin_data = pd.concat([coin_data, new_df], ignore_index=True)
        new_df = pd.DataFrame(data2)
        coin_data=pd.concat([coin_data, new_df], ignore_index=True)
        coin_data.sort_values(by = ['acc_trade_price_24h'], axis = 0, ascending = False,inplace = True)
        coin_data.reset_index(drop=True, inplace=True)
    
        coin_data.drop(coin_data.index[number:],inplace=True)

        for i in range(number):
            ticker = coin_data['market'][i]
            rsi_result = ti.index(ticker)['rsi']

            if rsi_result <= low_rsi:
                if coin_data['trade_price'][i] < 400000 :
                    if not stop_loss_check:
                        trading_time, stop_loss_check = buy_sell(ticker, bot, CHAT_ID)
                    elif (datetime.now() - trading_time).seconds > stop_loss_seconds:
                        trading_time, stop_loss_check = buy_sell(ticker, bot, CHAT_ID)
                    else:
                        print(ticker," 스탑로스 3분 안지나서 아직 매매 안함")
                
            rsi_list.append(rsi_result)
            
            time.sleep(0.05)
            
        coin_data.insert(len(data_columns), "rsi", rsi_list)
        
        #print(coin_data, time.strftime('%x %X', time.localtime(time.time())))
        #print("걸린 시간 : ", time.time()-start, "sec")
        time.sleep(0.02)
except :
    bot.sendMessage(chat_id=CHAT_ID, text ="Error occur\n auto_trading_bot_server End")
    print("auto_trading_bot_server_End")