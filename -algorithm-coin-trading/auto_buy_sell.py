# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 00:51:35 2021

@author: tkdan
"""

import pyupbit
import time
#from sell_price_set import sell_price_buy_set,sell_price_sell_set
from datetime import datetime

def sell_price_buy_set(sell_price):
    if sell_price < 10:
        sell_price = round(sell_price, 2) +0.01
    elif sell_price < 100:
        sell_price = round(sell_price, 1) + 0.1
    elif sell_price < 1000:
        sell_price = round(sell_price) + 1
    elif sell_price < 10000:
        sell_price = round(sell_price, -1) + 5
    elif sell_price < 100000:
        sell_price = round(sell_price, -1) + 10
    elif sell_price < 400000:
        sell_price = round(sell_price, -2) + 50
    return sell_price

def sell_price_sell_set(sell_price):
    if sell_price < 10:
        sell_price = round(sell_price, 2)
    elif sell_price < 100:
        sell_price = round(sell_price, 1)
    elif sell_price < 1000:
        sell_price = round(sell_price)
    elif sell_price < 10000:
        sell_price = round(sell_price, -1)
    elif sell_price < 100000:
        sell_price = round(sell_price, -1)
    elif sell_price < 400000:
        sell_price = round(sell_price, -2)
    return sell_price

def buy_sell(ticker, bot, CHAT_ID):
    try:
        profit_rate = 1.01
        fee = 0.001
        with open("upbit.txt") as f:
            lines=f.readlines()
            access=lines[0].strip()
            secret=lines[1].strip()
        
        upbit=pyupbit.Upbit(access, secret)
        print("upbit login complete")
        
        fomer_krw = int(upbit.get_balance(ticker="KRW"))
        krw_balance=round(fomer_krw * 0.999)
        
        if krw_balance > 5000:
            print("buy_info\n", upbit.buy_market_order(ticker, krw_balance))
            buy_check = True
            while buy_check:
                if not upbit.get_order(ticker):
                    print("buy complete")
                    buy_check = False
                else :
                    print("buy yet")
                time.sleep(1)
        
        avg_buy_price = upbit.get_avg_buy_price(ticker)
        sell_price = sell_price_buy_set(avg_buy_price * (profit_rate + fee))
        sell_amount = upbit.get_balance(ticker)
        
        print("buy_price : ", avg_buy_price)
        print("sell_price : " , sell_price)
        sell_info = upbit.get_order(ticker)
        
        if not sell_info:
            order = upbit.sell_limit_order(ticker, sell_price, sell_amount)
            print("sell_info\n", order)
        else:
            print("sell_info\n", sell_info)
        stop_loss_check = False
        
        while True:
            sell_info = upbit.get_order(ticker)
            if not sell_info:
                print("sell complete")
                break
            elif pyupbit.get_current_price(ticker) < avg_buy_price * 0.98:
                upbit.cancel_order(sell_info[0]['uuid'])
                sell = upbit.sell_market_order(ticker, sell_amount)
                while True:
                    if not upbit.get_order(ticker):
                        krw_balance=int(upbit.get_balance(ticker="KRW"))
                        sell_price = sell_price_sell_set(krw_balance/float(sell['volume']))
                        print("stop loss complete")
                        bot.sendMessage(chat_id=CHAT_ID, text = ticker + " stop loss operate")
                        stop_loss_check = True
                        break
            time.sleep(1)
        latter_krw = int(upbit.get_balance(ticker="KRW"))
        trading_time = datetime.now()
        bot.sendMessage(chat_id=CHAT_ID, text = ticker + '\n' + "avg_buy_price : " + str(avg_buy_price) + '\n' 
                                    + "sell_price : " + str(sell_price) + '\n' + "profit : " + str(round(avg_buy_price/sell_price*(-100)+99.9,2))+ "% \n" + 
                                    "이전 krw : "+ "{:,}".format(fomer_krw) + ' 원 \n' + "이후 krw : " + "{:,}".format(latter_krw) + ' 원 \n' 
                                    + "차액 : " +"{:,}".format(latter_krw - fomer_krw) + ' 원')
        return trading_time, stop_loss_check

    except:
        bot.sendMessage(chat_id=CHAT_ID, text ="buy_sell Error occur\n auto_trading_bot_server End")
        print("buy_sell Error occur auto_trading_bot_server_End")
