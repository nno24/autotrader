#!/usr/bin/python3

import os
import time, threading
import importlib
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui
from playsound import playsound


#Trade mode
#r = real money
#p = paper trade webull
#o = offline paper trade outside market american market hours.
#others: test mode - for testing new functions
trade_mode = "p"
autotrader = "yes"  #if not left to "yes", manual mode is entered.
trade_true = ""
strategy_orb = "orb" #Opening range breakout
strategy_pcps = "pcps" #Price change/s
strategy_15min_breakout="15min_breakout"
use_trade_strategy = strategy_15min_breakout

if trade_mode == "r":
    import nordnet_webelements
    import nordnet_functions
    driver = webdriver.Chrome('/usr/bin/chromedriver')
else:
    import webull_webelements_2
    import webull_paper_functions

#Strategy pcps params
oneminute_buysignal = 0.0 #if a one minute bullish candle are bigger than "oneminute_buysignal"%
sample_interval = 3
sample_periods = 0
order_delay = 0 #assuming delay due to filing of order.This will be used to adjust limit price up or down depending on buy or sell.
pcps_threshold = float(((oneminute_buysignal/60)*sample_interval))   #price change per second times sample interval
pcps_threshold = float(1.0)
pcps_threshold_s = -(pcps_threshold/3)
pcps_order_addon = ((oneminute_buysignal/60)*order_delay)
pcps_max_ticker = ""
pcps_max = 0.0
pcps_exit = 0
ticker_1_pcps = 0.0
ticker_2_pcps = 0.0
ticker_3_pcps = 0.0

#Daily trade parameters
trading_cash_usd = 2500
trade_cnt_real_max = 10
trade_cnt_max = 10
trade_cnt = 0
trade_status ="na"
kurtasje=3.75
kurtasje_trade=kurtasje*2
break_even=(kurtasje_trade/trading_cash_usd)*100
break_even_or_greater=0.0
price_buy=0.0

#Other trade variables
ticker_1_price_value_previous=0.0
ticker_2_price_value_previous=0.0
ticker_3_price_value_previous=0.0

ticker_1_price_value = 0.0
ticker_2_price_value = 0.0
ticker_3_price_value = 0.0

ticker_buy_price = 0.0
ticker_sell_price = 0.0

ticker_1_txt =""
ticker_2_txt =""
ticker_3_txt =""

holding_status = 0
ticker_holding_price = ""
ticker_holding_price_value = 0.0
ticker_holding_price_value_previous = 0.0
ticker_holding_pcps = 0.0

# Relation between tickers and current price / open price
dictionary_price = {}
dictionary_price_open = {}

#Fetch prices global parameters
timer_cnt = 0
timer_cnt_sec = 0
timer_cnt_min = 0
timer_cnt_hour = 0
timer_global_trader_interval = 5 
timer_15min_interval = 5 
timer_pcps_cnt = 0
prices_ticker_1 = []
prices_ticker_2 = []
prices_ticker_3 = []
time_ticker_1 = []
time_ticker_2 = []
time_ticker_3 = []
prices_holding_ticker = []
time_holding_ticker = []

#Tickers opening/closing price ( 1min )
ticker_1_op = 0.0
ticker_2_op = 0.0
ticker_3_op = 0.0
ticker_1_cp = 0.0
ticker_2_cp = 0.0
ticker_3_cp = 0.0

#Holding ticker previous closing price ( 1min )
ticker_holding_pcp = 0.0
ticker_holding_op = 0.0
#Holding ticker exit point - will be updated according to 1 min closing prices
ticker_holding_exit_point = 0.0
#ticker_holding_exit_offset = 0.0125    #This is percent
ticker_holding_exit_offset = 0.015   #This is percent

#counter for meausuring a bearish signal
bear_cnt = 0
bear_bailout_cnt_max = 6
bear_bailout_status = 0
vol=0

#Trade history
h_buy_price = []
h_sell_price = []
h_ticker = []
h_pcps_entry = []
h_buy_time = []
h_sell_time = []

h_ticker_holding_price = []
h_trade_time_table = []
h_buy_order_duration = 0.0
h_sell_order_duration = 0.0
h_buying_time_now = 0.0
h_selling_time_now = 0.0
h_buy_order_filled_time_now = 0.0
h_sell_order_filled_time_now = 0.0
h_trade_time_cnt = 0
h_sold_timestamp = 0

#Dates
date_now =""

#Modify order counters
modify_entry_cnt=0
modify_entry_cnt_max=30
modify_entry_tries=0
modify_entry_tries_max=2
modify_exit_cnt=0
modify_exit_cnt_max=30

filled_status = "unknown"
price=0.0

# monitor time and day
trade_range_days = range(0, 7)
today = datetime.datetime.today().weekday()
time_now = str(datetime.datetime.now().time())
time_getReady = "09:30:06"
time_lastCall = "15:45:00"
time_lastCallExit = "15:55:00"

# P&L parameters
bought_price = 0.0
sold_price = 0.0
PnL_total = 0.0
PnL_this_trade = 0.0
PnL_this_trade_w_fees = 0.0
PnL_total_w_fees = 0.0
Trade_fee_per_trade = 7.5

cancel_cnt = 0
cancel_cnt_max = 15

#orb parameters
ticker1_prev_1min_candle = []
ticker2_prev_1min_candle = []
ticker3_prev_1min_candle = []
ticker1_prev_high = 0
ticker2_prev_high = 0
ticker3_prev_high = 0
ticker1_prev_op = 0
ticker2_prev_op = 0
ticker3_prev_op = 0
ticker1_prev_cp = 0
ticker2_prev_cp = 0
ticker3_prev_cp = 0
time_now_sec = 1
time_now_min = 1
orb_quality_check = 20
bailout_of_entry_loop = 1
check_filled_if_cancelled_maxTries = 25

#15 min breakout parameters
ticker1_prev_15min_candle = []
ticker2_prev_15min_candle = []
ticker3_prev_15min_candle = []
ticker1_prev_15min_high = 0
ticker2_prev_15min_high = 0
ticker3_prev_15min_high = 0
ticker1_prev_15min_low = 0
ticker2_prev_15min_low = 0
ticker3_prev_15min_low = 0
ticker1_prev_15min_op = 0
ticker2_prev_15min_op = 0
ticker3_prev_15min_op = 0
ticker1_prev_15min_cp = 0
ticker2_prev_15min_cp = 0
ticker3_prev_15min_cp = 0
build_15min_candle=""
current_minute=999   #iniial value, so that the 15 min can be built on open.
profit_target=3.0   #if gain/trade (%) exceeds this, sell
profit_target_daily=16   #if reached total (%) gain per day, finish for today.


#pnl daily params -- keep track of only reporting once every 30 min
pnl_daily_0_cnt = 0
pnl_daily_30_cnt = 0

#User input variables
buy_now = ""
sell_now = ""
cancel_now = ""

#pcps calc
ticker_1_prev_price_value = 0.0
ticker_2_prev_price_value = 0.0
ticker_3_prev_price_value = 0.0

ticker1_pcps_this_min_lst = []
ticker2_pcps_this_min_lst = []
ticker3_pcps_this_min_lst = []
ticker1_a20pcps_0_19=0
ticker2_a20pcps_0_19=0
ticker3_a20pcps_0_19=0
ticker1_a20freq_0_19=0
ticker2_a20freq_0_19=0
ticker3_a20freq_0_19=0

a20pcps_0_19_threshold=0.04
a20freq_0_19_threshold=0.4

#MClear up mem
timer_cancel_interval = [28,29,30,31,32]

def test_webelements_paper():
    global pcps_max_ticker

    webull_paper_functions.watch_ticker_1_quality_check_paper()
    time.sleep(5)
    webull_paper_functions.watch_ticker_2_quality_check_paper()
    time.sleep(5)
    webull_paper_functions.watch_ticker_3_quality_check_paper()
    time.sleep(5)
    webull_paper_functions.watch_ticker_1_quality_check_paper()
    time.sleep(5)
    # Do a purchase, and cancel it
    pcps_max_ticker=ticker_1_txt
    vol = 1
    price=update_price_before_buy_paper(pcps_max_ticker)
    webull_paper_functions.prefill_buy_order(1)
    webull_paper_functions.buy(str(price))
    time.sleep(10)
    webull_paper_functions.cancel_buy_order()


def refresh():
    global driver
    try:
        driver.refresh()
    except:
        print("Unable to refresh..")

def fetch_prices():
    global dictionary_price_open
    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global date_now
    global ticker_1_op
    global ticker_2_op
    global ticker_3_op

    # Get prices of tickers
    try:
        ticker_1_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_1_price_value = ticker_1_price.text
        ticker_2_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_2_price_value = ticker_2_price.text
        ticker_3_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_3_price_value = ticker_3_price.text
        dictionary_price_open = {ticker_1_txt: ticker_1_op, ticker_2_txt: ticker_2_op, ticker_3_txt: ticker_3_op}
    except:
        print("UNABLE to fetch prices", date_now)

def fetch_prices_paper():
    global dictionary_price_open
    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global date_now
    global ticker_1_op
    global ticker_2_op
    global ticker_3_op

    # Get prices of tickers
    try:
        ticker_1_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_price)
        ticker_1_price_value = ticker_1_price.text
        ticker_2_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_price)
        ticker_2_price_value = ticker_2_price.text
        ticker_3_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_price)
        ticker_3_price_value = ticker_3_price.text
        dictionary_price_open = {ticker_1_txt: ticker_1_op, ticker_2_txt: ticker_2_op, ticker_3_txt: ticker_3_op}
    except:
        print("UNABLE to fetch prices..", date_now)

def fetch_holding_price():
    global pcps_max_ticker
    global ticker_holding_price_value
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    global ticker_holding_op
    global dictionary_price_open

    try:
        if pcps_max_ticker == ticker_1_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)

        ticker_holding_op = float(dictionary_price_open[pcps_max_ticker])
        print(pcps_max_ticker, "Open: ", ticker_holding_op, "Price: ", ticker_holding_price_value)
    except:
        print("UNABLE TO FETCH HOLDING PRICE", date_now)

def fetch_holding_price_paper():
    global pcps_max_ticker
    global ticker_holding_price_value
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    global ticker_holding_op
    global dictionary_price_open

    try:
        if pcps_max_ticker == ticker_1_txt:
            ticker_holding_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_price)
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_holding_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_price)
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_holding_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_price)
            ticker_holding_price_value = float(ticker_holding_price.text)

        ticker_holding_op = float(dictionary_price_open[pcps_max_ticker])
        print(pcps_max_ticker, "Open: ", ticker_holding_op, "Price: ", ticker_holding_price_value)
    except:
        print("UNABLE TO FETCH HOLDING PRICE", date_now)

def bear_bailout():
    global ticker_holding_price_value
    global ticker_holding_op
    global bear_cnt
    global bear_bailout_status
    global bear_bailout_cnt_max
    global pcps_exit
    global vol
    global holding_status
    global sample_periods
    global trade_status
    global modify_exit_cnt


    # If price is bearish and holding for a certain period of time ( bear_bailout ) - also check that no pcps has not started exit routine
    if ticker_holding_price_value < ticker_holding_op:
        bear_cnt += 1
        print("bear bail out cnt is: ", bear_cnt)
        if bear_cnt == bear_bailout_cnt_max:
            # Get the heck out
            bear_cnt = 0
            if pcps_exit == 0:
                print("BAILING OUT!!! - bears are coming!!!")
                bear_bailout_status = 1
                price=update_price_before_sell(pcps_max_ticker)
                trade_status=nordnet_functions.sell(str(price))
                nordnet_functions.open_order_status()
                if trade_status == "s":
                    print("Bailed out!!!")
                else:
                    print("Unable to bail out - sell order not completed..")

            elif pcps_exit == 1:
                print("bear bailout cancelled, due to exit performed by pcps: ", pcps_exit)

    elif ticker_holding_price_value >= ticker_holding_op:
        bear_cnt=0

def bear_bailout_paper():
    global ticker_holding_price_value
    global ticker_holding_op
    global bear_cnt
    global bear_bailout_status
    global bear_bailout_cnt_max
    global pcps_exit
    global vol
    global holding_status
    global sample_periods
    global trade_status
    global modify_exit_cnt


    # If price is bearish and holding for a certain period of time ( bear_bailout ) - also check that no pcps has not started exit routine
    if ticker_holding_price_value < ticker_holding_op:
        bear_cnt += 1
        print("bear bail out cnt is: ", bear_cnt)
        if bear_cnt == bear_bailout_cnt_max:
            # Get the heck out
            bear_cnt = 0
            if pcps_exit == 0:
                print("BAILING OUT!!! - bears are coming!!!")
                bear_bailout_status = 1
                price=update_price_before_sell_paper(pcps_max_ticker)
                trade_status="s"
                if trade_status == "s":
                    print("Bailed out!!!")
                else:
                    print("Unable to bail out - sell order not completed..")

            elif pcps_exit == 1:
                print("bear bailout cancelled, due to exit performed by pcps: ", pcps_exit)

    elif ticker_holding_price_value >= ticker_holding_op:
        bear_cnt=0
def append_pcps_this_min():
    global ticker1_pcps_this_min_lst
    global ticker2_pcps_this_min_lst
    global ticker3_pcps_this_min_lst
    try:
        ticker1_pcps_this_min_lst.append(ticker_1_pcps)
        ticker2_pcps_this_min_lst.append(ticker_2_pcps)
        ticker3_pcps_this_min_lst.append(ticker_3_pcps)
    except:
        print("Unable to append pcps 1min lst..")

def clear_pcps_lst_this_min():
    global ticker1_pcps_this_min_lst
    global ticker2_pcps_this_min_lst
    global ticker3_pcps_this_min_lst
    try:
        ticker1_pcps_this_min_lst = []
        ticker2_pcps_this_min_lst = []
        ticker3_pcps_this_min_lst = []
    except:
        print("Unable to clear 1min pcps lst...")
def clear_20pcps_20freq():
    global ticker1_a20pcps_0_19
    global ticker2_a20pcps_0_19
    global ticker3_a20pcps_0_19
    global ticker1_a20freq_0_19
    global ticker2_a20freq_0_19
    global ticker3_a20freq_0_19
    try:
        ticker1_a20pcps_0_19 = 0
        ticker2_a20pcps_0_19 = 0
        ticker3_a20pcps_0_19 = 0
        ticker1_a20freq_0_19 = 0
        ticker2_a20freq_0_19 = 0
        ticker3_a20freq_0_19 = 0
    except:
        print("Unable to clear pcps_0_19 and freq_0_19..")

def global_get_prices():
    global pcps_this_min_lst
    threading.Timer(timer_interval, global_get_prices).start()
    # Fetch prices of pcps_max_ticker: if bought, sold or holding
    if trade_status == "b" or trade_status == "s" or holding_status == 1:
        fetch_holding_price()
    fetch_prices()
    calc_pcps()
    #Appned pcps values to list..
    if time_now_sec == 0:
        print(ticker_1_txt, "prev 1 min pcps lst:", ticker1_pcps_this_min_lst)
        print(ticker_2_txt, "prev 1 min pcps lst:", ticker2_pcps_this_min_lst)
        print(ticker_3_txt, "prev 1 min pcps lst:", ticker3_pcps_this_min_lst)
        clear_pcps_lst_this_min()
        clear_20pcps_20freq()
    else:
        append_pcps_this_min()

    #Calculate a20pcps/freq
    if time_now_sec == 20:
        calc_a20_pcps()
        calc_a20_freq()

    save_prices()

def global_get_prices_paper():
    global pcps_this_min_lst
    threading.Timer(timer_interval, global_get_prices_paper).start()
    # Fetch prices of pcps_max_ticker: if bought, sold or holding
    if trade_status == "b" or trade_status == "s" or holding_status == 1:
        fetch_holding_price_paper()
    fetch_prices_paper()
    calc_pcps()
    #Appned pcps values to list..
    if time_now_sec == 0:
        print(ticker_1_txt, "prev 1 min pcps lst:", ticker1_pcps_this_min_lst)
        print(ticker_2_txt, "prev 1 min pcps lst:", ticker2_pcps_this_min_lst)
        print(ticker_3_txt, "prev 1 min pcps lst:", ticker3_pcps_this_min_lst)
        clear_pcps_lst_this_min()
        clear_20pcps_20freq()
    else:
        append_pcps_this_min()

    #Calculate a20pcps/freq
    if time_now_sec == 20:
        calc_a20_pcps()
        calc_a20_freq()

    save_prices()
def calc_a20_pcps():
    global ticker1_a20pcps_0_19
    global ticker2_a20pcps_0_19
    global ticker3_a20pcps_0_19
    global ticker1_pcps_this_min_lst
    global ticker2_pcps_this_min_lst
    global ticker3_pcps_this_min_lst
    try:
        if len(ticker1_pcps_this_min_lst) > 18:
            ticker1_a20pcps_0_19 = sum(ticker1_pcps_this_min_lst)/20
            print(ticker_1_txt, "lengt of pcps_this_min", len(ticker1_pcps_this_min_lst))
        else:
            ticker1_a20pcps_0_19=0
            print(ticker_1_txt, "lengt of pcps_this_min TOO SHORT", len(ticker1_pcps_this_min_lst))
        if len(ticker2_pcps_this_min_lst) > 18:
            ticker2_a20pcps_0_19 = sum(ticker2_pcps_this_min_lst)/20
            print(ticker_2_txt, "lengt of pcps_this_min", len(ticker2_pcps_this_min_lst))
        else:
            ticker2_a20pcps_0_19=0
            print(ticker_2_txt, "lengt of pcps_this_min TOO SHORT", len(ticker2_pcps_this_min_lst))
        if len(ticker3_pcps_this_min_lst) > 18:
            ticker3_a20pcps_0_19 = sum(ticker3_pcps_this_min_lst)/20
            print(ticker_3_txt, "lengt of pcps_this_min", len(ticker3_pcps_this_min_lst))
        else:
            ticker3_a20pcps_0_19=0
            print(ticker_3_txt, "lengt of pcps_this_min TOO SHORT", len(ticker3_pcps_this_min_lst))

        print(ticker_1_txt, "a20pcpc_0_19", ticker1_a20pcps_0_19)
        print(ticker_2_txt, "a20pcpc_0_19", ticker2_a20pcps_0_19)
        print(ticker_3_txt, "a20pcpc_0_19", ticker3_a20pcps_0_19)
    except:
        print("Unable to calcualte a20_pcps_0_19..")


def calc_a20_freq():
    global ticker1_a20freq_0_19
    global ticker2_a20freq_0_19
    global ticker3_a20freq_0_19

    index = 0
    ticker1_freq_cnt=0
    ticker2_freq_cnt=0
    ticker3_freq_cnt=0
    try:
        while index > 18:
            if ticker1_pcps_this_min_lst[index] != 0:
                ticker1_freq_cnt+=1
            if ticker2_pcps_this_min_lst[index] != 0:
                ticker2_freq_cnt+=1
            if ticker3_pcps_this_min_lst[index] != 0:
                ticker3_freq_cnt+=1
            index+=1

        ticker1_a20freq_0_19 = float(ticker1_freq_cnt/20)
        ticker2_a20freq_0_19 = float(ticker2_freq_cnt/20)
        ticker3_a20freq_0_19 = float(ticker3_freq_cnt/20)

        print(ticker_1_txt, "a20freq_0_19", ticker1_a20freq_0_19)
        print(ticker_2_txt, "a20freq_0_19", ticker2_a20freq_0_19)
        print(ticker_3_txt, "a20freq_0_19", ticker3_a20freq_0_19)
    except IndexError as e:
        print(e)
        print("UNABLE TO CALCULATE a20freq")


def calc_pcps():
    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global ticker_1_prev_price_value
    global ticker_2_prev_price_value
    global ticker_3_prev_price_value
    global ticker_1_pcps
    global ticker_2_pcps
    global ticker_3_pcps

    try:
        try:
            ticker_1_pcps = (((float(ticker_1_price_value) - float(ticker_1_prev_price_value)) / float(ticker_1_prev_price_value)) * 100)/timer_interval
            ticker_2_pcps = (((float(ticker_2_price_value) - float(ticker_2_prev_price_value)) / float(ticker_2_prev_price_value)) * 100)/timer_interval
            ticker_3_pcps = (((float(ticker_3_price_value) - float(ticker_3_prev_price_value)) / float(ticker_3_prev_price_value)) * 100)/timer_interval
        except ZeroDivisionError as e:
            print(e)

        ticker_1_prev_price_value = ticker_1_price_value
        ticker_2_prev_price_value = ticker_2_price_value
        ticker_3_prev_price_value = ticker_3_price_value
    except:
        print("UNABLE TO CALCULATE PCPS")

def make_15_min_candle():
    global ticker1_prev_15min_candle
    global ticker2_prev_15min_candle
    global ticker3_prev_15min_candle

    try:
        ticker1_prev_15min_candle.append(float(ticker_1_price_value))
        ticker2_prev_15min_candle.append(float(ticker_2_price_value))
        ticker3_prev_15min_candle.append(float(ticker_3_price_value))
    except ValueError as e:
        print(e)
        print("Unable to append to 15 min candle..")

def clear_15_min_candle():
    global ticker1_prev_15min_candle
    global ticker2_prev_15min_candle
    global ticker3_prev_15min_candle
    try:
        print(ticker_1_txt,"Previous 15 min to be cleared", ticker1_prev_15min_candle)
        print(ticker_2_txt,"Previous 15 min to be cleared", ticker2_prev_15min_candle)
        print(ticker_3_txt,"Previous 15 min to be cleared", ticker3_prev_15min_candle)
        print("\n")
        print("\n")
        ticker1_prev_15min_candle = []
        ticker2_prev_15min_candle = []
        ticker3_prev_15min_candle = []
    except:
        print("Unable to clear 15 min candles")


def calc_15_min_candle():
    global ticker1_prev_15min_high
    global ticker2_prev_15min_high
    global ticker3_prev_15min_high
    global ticker1_prev_15min_low
    global ticker2_prev_15min_low
    global ticker3_prev_15min_low
    global ticker1_prev_15min_op
    global ticker2_prev_15min_op
    global ticker3_prev_15min_op
    global ticker1_prev_15min_cp
    global ticker2_prev_15min_cp
    global ticker3_prev_15min_cp
    try:
        ticker1_prev_15min_high = max(ticker1_prev_15min_candle)
        ticker2_prev_15min_high = max(ticker2_prev_15min_candle)
        ticker3_prev_15min_high = max(ticker3_prev_15min_candle)

        ticker1_prev_15min_low = min(ticker1_prev_15min_candle)
        ticker2_prev_15min_low = min(ticker2_prev_15min_candle)
        ticker3_prev_15min_low = min(ticker3_prev_15min_candle)

        ticker1_prev_15min_op = ticker1_prev_15min_candle[0]
        ticker2_prev_15min_op = ticker2_prev_15min_candle[0]
        ticker3_prev_15min_op = ticker3_prev_15min_candle[0]

        ticker1_prev_15min_cp = ticker1_prev_15min_candle[len(ticker1_prev_15min_candle) - 1]
        ticker2_prev_15min_cp = ticker2_prev_15min_candle[len(ticker2_prev_15min_candle) - 1]
        ticker3_prev_15min_cp = ticker3_prev_15min_candle[len(ticker3_prev_15min_candle) - 1]

        print(ticker_1_txt, "prev 15 high", ticker1_prev_15min_high)
        print(ticker_1_txt, "prev 15 low", ticker1_prev_15min_low)
        print(ticker_1_txt, "prev 15 open", ticker1_prev_15min_op)
        print(ticker_1_txt, "prev 15 close", ticker1_prev_15min_cp)
        print("\n")
        print(ticker_2_txt, "prev 15 high", ticker2_prev_15min_high)
        print(ticker_2_txt, "prev 15 low", ticker2_prev_15min_low)
        print(ticker_2_txt, "prev 15 open", ticker2_prev_15min_op)
        print(ticker_2_txt, "prev 15 close", ticker2_prev_15min_cp)
        print("\n")
        print(ticker_3_txt, "prev 15 high", ticker3_prev_15min_high)
        print(ticker_3_txt, "prev 15 low", ticker3_prev_15min_low)
        print(ticker_3_txt, "prev 15 open", ticker3_prev_15min_op)
        print(ticker_3_txt, "prev 15 close", ticker3_prev_15min_cp)
        print("\n")
    except:
        print("Unable to calculate 15 min candle..")



def global_trader():
    global driver
    global timer_cnt
    global timer_cnt_sec
    global timer_cnt_min
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global ticker_holding_price_value
    global ticker_holding_pcp
    global ticker_holding_exit_point
    global ticker_holding_exit_offset
    global pcps_max_ticker
    global timer_pcps_cnt
    global sample_interval
    global ticker_1_op
    global ticker_2_op
    global ticker_3_op
    global ticker_1_cp
    global ticker_2_cp
    global ticker_3_cp
    global dictionary_price
    global dictionary_price_open
    global ticker_holding_op
    global bear_cnt
    global vol
    global bear_bailout_status
    global pcps_exit
    global sample_periods
    global holding_status
    global date_now
    global trade_status
    global modify_entry_cnt
    global modify_entry_cnt_max
    global modify_entry_tries
    global modify_entry_tries_max
    global modify_exit_cnt
    global modify_exit_cnt_max
    global filled_status
    global cancel_cnt
    global cancel_cnt_max
    global time_now_sec
    global time_now_min

    global ticker1_prev_1min_candle
    global ticker2_prev_1min_candle
    global ticker3_prev_1min_candle
    global ticker1_prev_high
    global ticker2_prev_high
    global ticker3_prev_high
    global ticker1_prev_op
    global ticker2_prev_op
    global ticker3_prev_op
    global ticker1_prev_cp
    global ticker2_prev_cp
    global ticker3_prev_cp

    global cancel_now
    global break_even_or_greater
    global price_buy

    global breakout_15min_cleared_status
    global ticker1_prev_15min_candle
    global ticker2_prev_15min_candle
    global ticker3_prev_15min_candle

    global ticker1_prev_15min_high
    global ticker1_prev_15min_low
    global ticker1_prev_15min_cp
    global ticker1_prev_15min_op

    global ticker2_prev_15min_high
    global ticker2_prev_15min_low
    global ticker2_prev_15min_cp
    global ticker2_prev_15min_op

    global ticker3_prev_15min_high
    global ticker3_prev_15min_low
    global ticker3_prev_15min_cp
    global ticker3_prev_15min_op
    global build_15min_candle
    global time_now
    global timer_global_trader_cancel_status

    #Start the global trader as a thread
    t=threading.Timer(timer_global_trader_interval, global_trader)
    t.start()
    if time_now > time_lastCallExit:
        t.cancel()
        print("Initializing trading parameters for tomorrow...")
        ticker_1_op = 0.0
        ticker1_prev_high = 0
        ticker1_prev_1min_candle = []
        ticker1_prev_15min_candle = []
        ticker1_prev_15min_low = 0
        ticker1_prev_15min_high = 0
        ticker1_prev_15min_op = 0
        ticker1_prev_15min_cp = 0
        ticker_2_op = 0.0
        ticker2_prev_high = 0
        ticker2_prev_1min_candle = []
        ticker2_prev_15min_candle = []
        ticker2_prev_15min_low = 0
        ticker2_prev_15min_high = 0
        ticker2_prev_15min_op = 0
        ticker2_prev_15min_cp = 0
        ticker_3_op = 0.0
        ticker3_prev_high = 0
        ticker3_prev_1min_candle = []
        ticker3_prev_15min_candle = []
        ticker3_prev_15min_low = 0
        ticker3_prev_15min_high = 0
        ticker3_prev_15min_op = 0
        ticker3_prev_15min_cp = 0
        build_15min_candle = "no"
        return 0

    time_now = str(datetime.datetime.now().time())
    print("Global trader: ",time_now)

    #Increment counters
    timer_cnt+=1
    timer_cnt_sec+=1
    timer_pcps_cnt+=1
    if modify_entry_cnt !=0:
        modify_entry_cnt+=timer_global_trader_interval
        print("cancel buy order cnt: ",modify_entry_cnt)
        print("max: ",modify_entry_cnt_max)
    elif modify_exit_cnt !=0:
        modify_exit_cnt+=1
        print("modify_exit: ",modify_exit_cnt)
        print("max: ",modify_exit_cnt_max)

    #Set time info
    time_s = datetime.datetime.now().time()
    date_now = datetime.datetime.now()
    time_now_sec = date_now.second
    time_now_min = date_now.minute

    #file prev watchlist tickers - in case an update
    ticker_1_prev_txt = ticker_1_txt
    ticker_2_prev_txt = ticker_2_txt
    ticker_3_prev_txt = ticker_3_txt
    #Get the watchlist tickers
    if trade_mode == "r":
        get_watchlist_tickers()
    else:
        get_watchlist_tickers_paper()


    #Check if watchlist are different - if so set open prices to zero
    if ticker_1_txt != ticker_1_prev_txt:
        print("Initializing 1 min open price of: ",ticker_1_txt," ..due to watchlist update")
        ticker_1_op = 0.0
        ticker1_prev_high = 0
        ticker1_prev_1min_candle = []
        ticker1_prev_15min_candle = []
        ticker1_prev_15min_low = 0
        ticker1_prev_15min_high = 0
        ticker1_prev_15min_op = 0
        ticker1_prev_15min_cp = 0
        build_15min_candle = "no"
    if ticker_2_txt != ticker_2_prev_txt:
        print("Initializing 1 min open price of: ",ticker_2_txt," ..due to watchlist update")
        ticker_2_op = 0.0
        ticker2_prev_high = 0
        ticker2_prev_1min_candle = []
        ticker2_prev_15min_candle = []
        ticker2_prev_15min_low = 0
        ticker2_prev_15min_high = 0
        ticker2_prev_15min_op = 0
        ticker2_prev_15min_cp = 0
        build_15min_candle = "no"
    if ticker_3_txt != ticker_3_prev_txt:
        print("Initializing 1 min open price of: ",ticker_3_txt," ..due to watchlist update")
        ticker_3_op = 0.0
        ticker3_prev_high = 0
        ticker3_prev_1min_candle = []
        ticker3_prev_15min_candle = []
        ticker3_prev_15min_low = 0
        ticker3_prev_15min_high = 0
        ticker3_prev_15min_op = 0
        ticker3_prev_15min_cp = 0
        build_15min_candle = "no"

    #Fetch & prices
    if trade_status == "b" or trade_status == "s" or holding_status == 1:
        if trade_mode == "r":
            fetch_holding_price()
        else:
            fetch_holding_price_paper()
    if trade_mode == "r":
        fetch_prices()
    else:
        fetch_prices_paper()

    #save_prices()

    #If BUY order yet not filled -  automatic cancel buy order
    if modify_entry_cnt >= modify_entry_cnt_max and filled_status != "filled" and trade_status != "c":
        print("CANCELLING order")
        trade_status=webull_paper_functions.cancel_buy_order()
        if trade_status == "c":
            print("Success - CANCELLING ORDER OK")
        else:
            print("ORDER FILLED - UNABLE TO CANCEL")
            modify_entry_cnt = 0


    #If SELL order yet not filled - edit sell order
    if modify_exit_cnt == modify_exit_cnt_max and filled_status != "filled":
        print("MODIFYING SELL ORDER")
        price=update_price_before_sell_paper(pcps_max_ticker)
        modify_status=webull_paper_functions.modify_sell_order(str(price))
        if modify_exit_cnt != 0:
            modify_exit_cnt=1
            print("Starting new exit_cnt: ",modify_exit_cnt)
        else:
            print("---Sell order already filled, no need to modify")
        if modify_status != "success":
            print("MODIFYING NOT SUCCESS...refreshing")
            webull_paper_functions.refresh()


    if holding_status == 1:
        # Inform if holding price is above break even
        try:
            break_even_or_greater = ((float(ticker_holding_price_value) - float(price_buy))/float(price_buy))*100
            print("ticker holding price", ticker_holding_price_value)
            print("ticker buy price", price_buy)
            print("break even or greater: ", break_even_or_greater)
            print("break even:", break_even)
        except ZeroDivisionError as e:
            print(e)
            print("Unable to calc break even or greater")
    '''
    #release thread mem
    if time_now_sec in timer_cancel_interval:
        t.cancel()
        print("Celaning up mem globa trader..")
        time.sleep(timer_global_trader_interval)
        global_trader()
        return 0
    '''

def timer_15min():
    global build_15min_candle
    global current_minute

    t15=threading.Timer(timer_15min_interval, timer_15min)
    t15.start()
    if time_now > time_lastCallExit:
        t15.cancel()
        current_minute = 999
        return 0
    '''
    elif time_now_sec in timer_cancel_interval:
        t15.cancel()
        print("Celaning up mem on xmin timer")
        time.sleep(timer_15min_interval)
        timer_15min()
        return 0
    '''
    interval15_startpoints=[0,15,30,45]

    if current_minute != time_now_min or current_minute == 999:
        if time_now_min in interval15_startpoints:
            if build_15min_candle == "yes":
                calc_15_min_candle()
                set_15min_breakout_exit()
            else:
                print("Unable to calculate 15 min data -- candle not complete")
            print("Starting new 15 min build of candle...")
            clear_15_min_candle()
            build_15min_candle = "yes"

    if build_15min_candle == "yes":
        make_15_min_candle()
    else:
        build_15min_candle="no"

    current_minute = time_now_min

def timer_5min():
    global build_15min_candle
    global current_minute

    t15=threading.Timer(timer_15min_interval, timer_5min)
    t15.start()
    if time_now > time_lastCallExit:
        t15.cancel()
        current_minute = 999
        return 0
    '''
    elif time_now_sec in timer_cancel_interval:
        t15.cancel()
        print("Celaning up mem on xmin timer")
        time.sleep(timer_15min_interval)
        timer_3min()
        return 0
    '''
    interval15_startpoints=range(0,60,5)

    if current_minute != time_now_min or current_minute == 999:
        if time_now_min in interval15_startpoints:
            if build_15min_candle == "yes":
                calc_15_min_candle()
                set_15min_breakout_exit()
            else:
                print("Unable to calculate 15 min data -- candle not complete")
            print("Starting new 15 min build of candle...")
            clear_15_min_candle()
            build_15min_candle = "yes"

    if build_15min_candle == "yes":
        make_15_min_candle()
    else:
        build_15min_candle="no"

    current_minute = time_now_min

def timer_2min():
    global build_15min_candle
    global current_minute

    t15=threading.Timer(timer_15min_interval, timer_2min)
    t15.start()
    if time_now > time_lastCallExit:
        t15.cancel()
        current_minute = 999
        return 0
    '''
    elif time_now_sec in timer_cancel_interval:
        t15.cancel()
        print("Celaning up mem on xmin timer")
        time.sleep(timer_15min_interval)
        timer_2min()
        return 0
    '''
    interval15_startpoints=range(0,60,2)

    if current_minute != time_now_min or current_minute == 999:
        if time_now_min in interval15_startpoints:
            if build_15min_candle == "yes":
                calc_15_min_candle()
                set_15min_breakout_exit()
            else:
                print("Unable to calculate 15 min data -- candle not complete")
            print("Starting new 15 min build of candle...")
            clear_15_min_candle()
            build_15min_candle = "yes"

    if build_15min_candle == "yes":
        make_15_min_candle()
    else:
        build_15min_candle="no"

    current_minute = time_now_min

def timer_1min():
    global build_15min_candle
    global current_minute

    t15=threading.Timer(timer_15min_interval, timer_1min)
    t15.start()
    if time_now > time_lastCallExit:
        t15.cancel()
        current_minute = 999
        return 0
    '''
    elif time_now_sec in timer_cancel_interval:
        t15.cancel()
        print("Celaning up mem on xmin timer")
        time.sleep(timer_15min_interval)
        timer_1min()
        return 0
    '''
    interval15_startpoints=range(0,60,1)

    if current_minute != time_now_min or current_minute == 999:
        if time_now_min in interval15_startpoints:
            if build_15min_candle == "yes":
                calc_15_min_candle()
                set_15min_breakout_exit()
            else:
                print("Unable to calculate 15 min data -- candle not complete")
            print("Starting new 15 min build of candle...")
            clear_15_min_candle()
            build_15min_candle = "yes"

    if build_15min_candle == "yes":
        make_15_min_candle()
    else:
        build_15min_candle="no"

    current_minute = time_now_min



def update_price_before_buy(pcps_max_ticker):
    global ticker_buy_price
    # 1. Get price now of holding ticker
    try:
        if pcps_max_ticker == ticker_1_txt:
            ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
            ticker_buy_price = float(ticker_buy_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
            ticker_buy_price = float(ticker_buy_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
            ticker_buy_price = float(ticker_buy_price.text)

        ticker_buy_price = ticker_buy_price * (1 + (pcps_order_addon / 100))

        if ticker_buy_price < 1:
            ticker_buy_price = ("%.4f" % ticker_buy_price)  # 4 decimals below 1
        elif ticker_buy_price >1:
            ticker_buy_price = ("%.2f" % ticker_buy_price)  # 2 decimals above 1


        return ticker_buy_price
    except:
        print("Unable to update price before BUY")

def update_price_before_buy_paper(pcps_max_ticker):
    global ticker_buy_price
    # 1. Get price now of holding ticker

    try:

        if pcps_max_ticker == ticker_1_txt:
            ticker_buy_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_price)
            ticker_buy_price = float(ticker_buy_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_buy_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_price)
            ticker_buy_price = float(ticker_buy_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_buy_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_price)
            ticker_buy_price = float(ticker_buy_price.text)

        ticker_buy_price = ticker_buy_price * (1 + (pcps_order_addon / 100))

        if ticker_buy_price < 1:
            ticker_buy_price = ("%.4f" % ticker_buy_price)  # 4 decimals below 1
        elif ticker_buy_price >1:
            ticker_buy_price = ("%.2f" % ticker_buy_price)  # 2 decimals above 1


        return ticker_buy_price
    except:
        print("Unable to update price before BUY")

def update_price_before_sell(pcps_max_ticker):
    global ticker_sell_price
    try:
        # 1. Get price now of holding ticker
        if pcps_max_ticker == ticker_1_txt:
            ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
            ticker_sell_price = float(ticker_sell_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
            ticker_sell_price = float(ticker_sell_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
            ticker_sell_price = float(ticker_sell_price.text)

        ticker_sell_price = ticker_sell_price * (1 - (pcps_order_addon / 100))
        if ticker_sell_price < 1:
            ticker_sell_price = ("%.4f" % ticker_sell_price)  # 4 decimals below 1
        elif ticker_sell_price >1:
            ticker_sell_price = ("%.2f" % ticker_sell_price)  # 2 decimals above 1 nordnet
        return ticker_sell_price
    except:
        print("Unable to upate price before sell..")

def update_price_before_sell_paper(pcps_max_ticker):
    global ticker_sell_price
    try:
        # 1. Get price now of holding ticker
        if pcps_max_ticker == ticker_1_txt:
            ticker_sell_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_price)
            ticker_sell_price = float(ticker_sell_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_sell_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_price)
            ticker_sell_price = float(ticker_sell_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_sell_price = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_price)
            ticker_sell_price = float(ticker_sell_price.text)

        ticker_sell_price = ticker_sell_price * (1 - (pcps_order_addon / 100))
        if ticker_sell_price < 1:
            ticker_sell_price = ("%.4f" % ticker_sell_price)  # 4 decimals below 1
        elif ticker_sell_price >1:
            ticker_sell_price = ("%.2f" % ticker_sell_price)  # 2 decimals above 1 nordnet
        return ticker_sell_price
    except:
        print("Unable to update price before sell..")
def find_volume(price):
    global trading_cash_usd
    vol = int(trading_cash_usd/price)
    print("calculated volum",vol)
    return vol
def get_watchlist_tickers():
    global driver
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    try:
        # Get watchlist ticker no 1
        ticker_1 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[1]/div[1]/span[1]")
        ticker_1_txt = ticker_1.text
    except:
        print("Ticker 1 not available")
    try:
        # GET Watchlist ticker no2
        ticker_2 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[1]/div[1]/span[1]")
        ticker_2_txt = ticker_2.text
    except:
        print("Ticker 2 not available")
    try:
        # Get watchlist ticker no3
        ticker_3 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[1]/div[1]/span[1]")
        ticker_3_txt = ticker_3.text
    except:
        print("Ticker 3 not available")

def get_watchlist_tickers_paper():
    global driver
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    try:
        # Get watchlist ticker no 1
        ticker_1 = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_txt)
        ticker_1_txt = ticker_1.text
        # GET Watchlist ticker no2
        ticker_2 = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_txt)
        ticker_2_txt = ticker_2.text
        ticker_3 = webull_paper_functions.driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_txt)
        ticker_3_txt = ticker_3.text
    except:
        print("Tickers not available")


def open_webull():
    global driver

    driver.implicitly_wait(10) # seconds
    driver.get("https://app.webull.com/paper")
def logon_webull():
    global driver
    #Click OK when page loads
    try:
        elem_ok = driver.find_element_by_class_name("jss198")
        time.sleep(2)
        elem_ok.click()
    except:
        pass

    #Login
    elem_login = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div")
    elem_login.click()

    elem_login_uname = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div/form/div[2]/div[1]/div/input")
    elem_login_uname.clear()
    elem_login_uname.click()
    elem_login_uname.send_keys("nicolai.norseng@gmail.com")
    elem_login_uname.send_keys(Keys.TAB)

    elem_passwd = driver.switch_to_active_element()
    elem_passwd.clear()
    elem_passwd.send_keys("Lwle17109")

    #login button
    elem_login_b = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div/form/input")
    elem_login_b.click()

    w_ready=1
    while w_ready == 1:
        try:
            #Enter the stocks section
            elem_stocks = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[2]/div[1]/div[3]/i")
            elem_stocks.click()
            print("Entered stocks - logon completed")
            w_ready = 0
        except:
            print("Entering stocks..")


def watch_ticker_1_quality_check():
    try:
        elem_watch_t1 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[1]")
        elem_watch_t1.click()
        print("WATCHING  TICKER 1")
    except:
        print("Unable to watch ticker 1 on webull")
def watch_ticker_2_quality_check():
    try:
        elem_watch_t2 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[2]")
        elem_watch_t2.click()
        print("WATCHING  TICKER 2")
    except:
        print("Unable to watch ticker 2 on webull")

def watch_ticker_3_quality_check():
    try:
        elem_watch_t3 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div[1]/div[2]/div/div[2]/div/div[2]/div/li[3]")
        elem_watch_t3.click()
        print("WATCHING  TICKER 3")
    except:
        print("Unable to watch ticker 3 on webull")

def save_prices():
    try:
        subfolder = "/home/autotrader/log/prices"
        tday = str(datetime.datetime.now().date())
        time_n = datetime.datetime.now().time()
        subfolder2 = str(subfolder) + "/" + str(tday)
        os.makedirs(subfolder2, exist_ok=True)
        fname_1 = str(subfolder2) + "/" + str(ticker_1_txt) + str(".txt")
        fname_2 = str(subfolder2) + "/" + str(ticker_2_txt) + str(".txt")
        fname_3 = str(subfolder2) + "/" + str(ticker_3_txt) + str(".txt")

        a_fname_1 = open(fname_1, "a")
        a_fname_1.write(str(time_n))
        a_fname_1.write(" ")
        a_fname_1.write(str(ticker_1_price_value))
        a_fname_1.write(" ")
        a_fname_1.write(str(ticker_1_pcps))
        a_fname_1.write("\n")

        a_fname_2 = open(fname_2, "a")
        a_fname_2.write(str(time_n))
        a_fname_2.write(" ")
        a_fname_2.write(str(ticker_2_price_value))
        a_fname_2.write(" ")
        a_fname_2.write(str(ticker_2_pcps))
        a_fname_2.write("\n")

        a_fname_3 = open(fname_3, "a")
        a_fname_3.write(str(time_n))
        a_fname_3.write(" ")
        a_fname_3.write(str(ticker_3_price_value))
        a_fname_3.write(" ")
        a_fname_3.write(str(ticker_3_pcps))
        a_fname_3.write("\n")
    except:
        print("UNABLE TO SAVE PRICES")


def log_PnL(pnl_this_trade, pnl_total, pnl_this_trade_w_fees, pnl_total_w_fees, trade_succes_cnt, a20pcps_0_19, a20freq_0_19, ticker,time_entry,time_exit):
    try:
        subfolder = "/home/autotrader/log/pcps_PnL/5min_breakout"
        tday = str(datetime.datetime.now().date())
        l_fileName = str(subfolder) + "/" + str(tday)

        os.makedirs(subfolder, exist_ok=True)

        l_file = open(l_fileName, "a")
        l_file.write("Time entry:       ")
        l_file.write(str(time_entry))
        l_file.write("\n")
        l_file.write("Time exit:        ")
        l_file.write(str(time_exit))
        l_file.write("\n")
        l_file.write("Ticker:           ")
        l_file.write(str(ticker))
        l_file.write("\n")
        l_file.write("Size(USD):        ")
        l_file.write(str(trading_cash_usd))
        l_file.write("\n")
        l_file.write("PnL trade:        ")
        l_file.write(str(pnl_this_trade))
        l_file.write("\n")
        l_file.write("PnL total:        ")
        l_file.write(str(pnl_total))
        l_file.write("\n")
        l_file.write("PnL trade w fees: ")
        l_file.write(str(pnl_this_trade_w_fees))
        l_file.write("\n")
        l_file.write("PnL total w fees: ")
        l_file.write(str(pnl_total_w_fees))
        l_file.write("\n")
        l_file.write("Trade cnt succ:   ")
        l_file.write(str(trade_succes_cnt))
        l_file.write("\n")
        l_file.write("a20pcps_0_19:     ")
        l_file.write(str(a20pcps_0_19))
        l_file.write("\n")
        l_file.write("a20freq_0_19:     ")
        l_file.write(str(a20freq_0_19))
        l_file.write("\n")
        l_file.write("\n")
        l_file.close()
        print("****Successfully written to log file!!")
    except:
        print("Unable to write to log file...")

def pcps():
    global driver
    global pcps_threshold
    global pcps_threshold_s
    global pcps_max_ticker
    global sample_interval
    global sample_periods
    global holding_status

    global ticker_1_pcps
    global ticker_2_pcps
    global ticker_3_pcps

    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global ticker_buy_price
    global ticker_sell_price

    global ticker_1_price_value_previous
    global ticker_2_price_value_previous
    global ticker_3_price_value_previous

    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt

    global ticker_holding_price
    global ticker_holding_price_value
    global ticker_holding_price_value_previous
    global ticker_holding_pcps

    global pcps_order_addon

    global ticker_1_op
    global ticker_2_op
    global ticker_3_op
    global ticker_holding_pcp
    global ticker_holding_exit_point

    global dictionary_price_open
    global dictionary_price
    global vol
    global bear_bailout_status
    global pcps_exit
    global pcps_max
    global h_pcps_entry
    global trade_status

    global modify_entry_cnt
    global modify_entry_tries
    global modify_exit_cnt
    global modify_exit_cnt_max
    global price
    global bear_cnt
    global filled_status

    global today
    global time_now

    global bought_price
    global sold_price
    global PnL_total
    global PnL_total_w_fees
    global Trade_fee_per_trade
    global PnL_this_trade
    global PnL_this_trade_w_fees

    global trade_successful_cnt

    global buy_now
    global sell_now
    global cancel_now

    global price_buy



    # Start the "Enter trade routine"
    if use_trade_strategy == strategy_pcps:
        while holding_status == 0:
            #Relation between tickers and current price
            dictionary_price ={ticker_1_txt:ticker_1_price_value,ticker_2_txt:ticker_2_price_value,ticker_3_txt:ticker_3_price_value}
            #Relation between tickers and 1 min opening prices
            dictionary_price_open ={ticker_1_txt:ticker_1_op,ticker_2_txt:ticker_2_op,ticker_3_txt:ticker_3_op}

            #2. Wait "sample_interval" seconds
            time.sleep(sample_interval)

            #3.1 Get pcps between price now and previous price and find the ticker with best pcps.
            if sample_periods != 0:
               try:
                   ticker_1_pcps = (float(ticker_1_price_value)/float(ticker_1_price_value_previous) -1)*100
                   ticker_2_pcps = (float(ticker_2_price_value)/float(ticker_2_price_value_previous) -1)*100
                   ticker_3_pcps = (float(ticker_3_price_value)/float(ticker_3_price_value_previous) -1)*100

               except:
                   print("Unable to calculate pcps values this time, waiting for next opportunity..")
               try:
                   #relation between tickers and its pcps
                   dictionary_pcps = {ticker_1_pcps:ticker_1_txt,ticker_2_pcps:ticker_2_txt,ticker_3_pcps:ticker_3_txt}

                   pcps_max = float(max(dictionary_pcps))
                   pcps_max_ticker = dictionary_pcps.get(max(dictionary_pcps))

                   #Find the price of best pcps ticker
                   ticker_price = float(dictionary_price[pcps_max_ticker])
                   ticker_buy_price = ticker_price * (1 + (pcps_order_addon / 100))
                   ticker_buy_price = float(("%.4f" % ticker_buy_price))  # 4 decimals

                   #Find what the 1 min open price of that ticker was
                   ticker_open_1min = float(dictionary_price_open[pcps_max_ticker])
               except:
                   print("Unable to find price of best pcps ...coming back later ")
                   continue

               # Print: ticker, price, pcps and 1 min open of each ticker
               print("")
               print("T    ", "O    ", "C   ", "PCPS")
               print(datetime.datetime.now())
               print(ticker_1_txt, ticker_1_op, ticker_1_price_value, ticker_1_pcps)
               print(ticker_2_txt, ticker_2_op, ticker_2_price_value, ticker_2_pcps)
               print(ticker_3_txt, ticker_3_op, ticker_3_price_value, ticker_3_pcps)
               print("")
               print("Ticker with best pcps: ", pcps_max_ticker, pcps_max)
               print("")


               #3.2 Buy if pcps on best ticker is greater than pcps_threshold AND the current price is greater than the opening price and the opening price is not equal to zero
               if pcps_max > pcps_threshold and ticker_buy_price > ticker_open_1min and ticker_open_1min != 0:
                   #Get the volume
                   vol = find_volume(float(ticker_buy_price))
                   #Append pcps_max to history
                   h_pcps_max = ("%.3f" % pcps_max)
                   h_pcps_entry.append(h_pcps_max)
                   #Buy now real or paper


            #4. File previous price.
            ticker_1_price_value_previous = ticker_1_price_value
            ticker_2_price_value_previous = ticker_2_price_value
            ticker_3_price_value_previous = ticker_3_price_value

            sample_periods+=1
    elif use_trade_strategy == strategy_orb:
        while holding_status == 0:
            #Check if any of the stocks break the high - and holds for a specified time.
            orb_breakout_true = "no"
            while orb_breakout_true == "no":
                #Check time
                if time_now > time_lastCall:
                    print("Trading reached EOD - exiting entry routine")
                    return 5
                try:
                    if float(ticker_1_price_value) > float(ticker1_prev_high) and float(ticker1_prev_high) != 0 and float(ticker1_prev_cp) > float(ticker1_prev_op):
                        print("Entered quality check on: ", ticker_1_txt)
                        watch_ticker_1_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_1_price_value))
                        nordnet_functions.prefill_buy_order(str(1), str(vol))
                        time.sleep(orb_quality_check)
                        if float(ticker_1_price_value) > float(ticker1_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_1_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_1_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_1_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_1_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_1_txt
                                orb_breakout_true = "yes"
                                continue

                        else:
                            print("Quality check not passed - not entering trade", ticker_1_txt)
                            nordnet_functions.enter_watchlist()
                    if float(ticker_2_price_value) > float(ticker2_prev_high) and float(ticker2_prev_high) != 0 and float(ticker2_prev_cp) > float(ticker2_prev_op):
                        print("Entered quality check on: ", ticker_2_txt)
                        watch_ticker_2_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_2_price_value))
                        nordnet_functions.prefill_buy_order(str(2), str(vol))
                        time.sleep(orb_quality_check)
                        ##Get volume
                        if float(ticker_2_price_value) > float(ticker2_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_2_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_2_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_2_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_2_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_2_txt
                                orb_breakout_true = "yes"
                                continue
                        else:
                            print("Quality check not passed - not entering trade", ticker_2_txt)
                            nordnet_functions.enter_watchlist()
                    if float(ticker_3_price_value) > float(ticker3_prev_high) and float(ticker3_prev_high) != 0 and float(ticker3_prev_cp) > float(ticker3_prev_op):
                        print("Entered quality check on: ", ticker_3_txt)
                        watch_ticker_3_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_3_price_value))
                        nordnet_functions.prefill_buy_order(str(3), str(vol))
                        time.sleep(orb_quality_check)
                        if float(ticker_3_price_value) > float(ticker3_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_3_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_3_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_3_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_3_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_3_txt
                                orb_breakout_true = "yes"
                                continue
                        else:
                            print("Quality check not passed - not entering trade: ", ticker_3_txt)
                            nordnet_functions.enter_watchlist()
                except:
                    print("Unable to compare prices..retrying")

            if orb_breakout_true == "yes":
                print("Entering ORB - moving on to check if order was filled")
                break
    #Ask if manual cancel && Check if order was filled
    if trade_status == "b":
        modify_entry_cnt = 1
        filled_status="unknown"
        if autotrader != "yes":
            cancel_now = pyautogui.confirm("CANCEL NOW?", pcps_max_ticker,timeout=modify_entry_cnt_max*1000)
            if cancel_now == "OK":
                print("CANCELLING order")
                trade_status = nordnet_functions.cancel_order()
                if trade_status == "c":
                    print("Success - CANCELLING ORDER OK")
                    nordnet_functions.enter_watchlist()
                else:
                    print("UNABLE TO CANCEL")
                    nordnet_functions.enter_watchlist()
            elif cancel_now == "Timeout":
                print("MANUAL CANCEL TIMED OUT")

        #Check filled status
        filled_status=nordnet_functions.check_order_status()
        if filled_status == "filled":
            modify_entry_cnt = 0
            time.sleep(0.5)
            modify_entry_cnt = 0
            modify_entry_tries = 0
            # Set initial exit point
            ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
            print("The initial exit point is: ", ticker_holding_exit_point)
            print("The buy Limit price was: ", price)
            holding_status=1
            #Update P&L status
            bought_price = price
        elif filled_status == "cancelled":
            #No double checking needed
            print("No double checking needed if order was filled or cancelled...")

            if filled_status != "filled":
                print("Buy cancelled - exiting the trade")
                #Initialize trade counters.
                modify_entry_cnt = 0
                modify_entry_tries = 0
                return 1
    else:
        return 1
        print("BUY FAILED --- EXITING")

    # Start the "Exit trade routine - if holding ticker AND bear bailout has not entered the exit"
    sell_now = "maybe"
    while holding_status == 1 and bear_bailout_status == 0:
        time.sleep(1)
        today = datetime.datetime.today().weekday()
        if autotrader != "yes":
            #0. Manual input for selling ( first priority - Only asking 1 time)
            if sell_now == "maybe":
                sell_now = pyautogui.confirm("SELL NOW?", pcps_max_ticker)
                if sell_now == "OK":
                    print("--Exiting trade manually..")
                    price=update_price_before_sell(pcps_max_ticker)
                    trade_status=nordnet_functions.sell(str(price))
                    nordnet_functions.open_order_status()
                    #Set sample_periods to zero and break enter trade routine
                    sample_periods = 0
                    pcps_exit = 0
                    break


        #1. Call the bear bailout exit if holding ticker
        if holding_status == 1 and bear_bailout_status == 0 and pcps_exit == 0 and trade_status != "s":
            bear_bailout()

        #2. Sell if price shoots below exit point and bear bailout status is 0
        if ticker_holding_price_value <= ticker_holding_exit_point and bear_bailout_status == 0:
            #Say that we exit the trade, so not conflicting with other exit strategies
            pcps_exit = 1
            print("--Exiting trade with exit point routine")
            price=update_price_before_sell(pcps_max_ticker)
            trade_status=nordnet_functions.sell(str(price))
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break

        #3. Get out before closing in case holding
        elif time_now > time_lastCallExit:
            pcps_exit = 1
            print("Exiting trade due to market closing soon...")
            price=update_price_before_sell(pcps_max_ticker)
            trade_status=nordnet_functions.sell(str(price))
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break


    #Check if order was filled
    if trade_status == "s":
        modify_exit_cnt = 1
        filled_status="unknown"
        filled_status = nordnet_functions.check_order_status()
        if filled_status == "filled":
            modify_exit_cnt = 0
            print("Resetting trading parameters, trade done")
            print("the exit_cnt rest: ",modify_exit_cnt)
            bear_bailout_status = 0
            bear_cnt = 0
            pcps_exit = 0
            sample_periods = 0
            holding_status = 0
            trade_successful_cnt+=1
            trade_status = "na"

            #Update P&L
            sold_price = price
            PnL_this_trade = (float(sold_price) - float(bought_price))*int(vol)
            PnL_this_trade = float("%.2f" % PnL_this_trade)
            PnL_total = float(PnL_total) + float(PnL_this_trade)
            PnL_this_trade_w_fees = float(PnL_this_trade) - float(Trade_fee_per_trade)
            PnL_total_w_fees = float(PnL_total_w_fees) + float(PnL_this_trade_w_fees)

            #Update log file
            log_PnL(PnL_this_trade, PnL_total, PnL_this_trade_w_fees, PnL_total_w_fees, trade_successful_cnt, pcps_max)


            print("")
            print(datetime.datetime.now())
            print("PnL this trade:        ",PnL_this_trade)
            print("PnL total:             ",PnL_total)
            print("PnL this trade w fees: ",PnL_this_trade_w_fees)
            print("PnL total w fees:      ",PnL_total_w_fees)
            print("Trade cnt:             ",trade_successful_cnt)
            print("pcps:                  ",pcps_max)
            print("")

            #Get back to watchlist
            nordnet_functions.enter_watchlist()

    #Exit routine exited or bear bailout -wait until we dont hold the ticker anymore
    while trade_status != "na":
        time.sleep(1)
    print("Success exited trade!!")
    return 0

def pcps_paper():
    global driver
    global pcps_threshold
    global pcps_threshold_s
    global pcps_max_ticker
    global sample_interval
    global sample_periods
    global holding_status

    global ticker_1_pcps
    global ticker_2_pcps
    global ticker_3_pcps

    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global ticker_buy_price
    global ticker_sell_price

    global ticker_1_price_value_previous
    global ticker_2_price_value_previous
    global ticker_3_price_value_previous

    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt

    global ticker_holding_price
    global ticker_holding_price_value
    global ticker_holding_price_value_previous
    global ticker_holding_pcps

    global pcps_order_addon

    global ticker_1_op
    global ticker_2_op
    global ticker_3_op
    global ticker_holding_pcp
    global ticker_holding_exit_point

    global dictionary_price_open
    global dictionary_price
    global vol
    global bear_bailout_status
    global pcps_exit
    global pcps_max
    global h_pcps_entry
    global trade_status

    global modify_entry_cnt
    global modify_entry_tries
    global modify_exit_cnt
    global modify_exit_cnt_max
    global price
    global bear_cnt
    global filled_status

    global today
    global time_now

    global bought_price
    global sold_price
    global PnL_total
    global PnL_total_w_fees
    global Trade_fee_per_trade
    global PnL_this_trade
    global PnL_this_trade_w_fees

    global trade_successful_cnt

    global buy_now
    global sell_now
    global cancel_now

    global price_buy
    global break_even_or_greater

    val_a20pcps_0_19=0
    val_a20freq_0_19=0




    # Start the "Enter trade routine"
    if use_trade_strategy == strategy_pcps:
        while holding_status == 0:
            #Relation between tickers and current price
            dictionary_price ={ticker_1_txt:ticker_1_price_value,ticker_2_txt:ticker_2_price_value,ticker_3_txt:ticker_3_price_value}
            #Relation between tickers and 1 min opening prices
            dictionary_price_open ={ticker_1_txt:ticker_1_op,ticker_2_txt:ticker_2_op,ticker_3_txt:ticker_3_op}

            #2. Wait "sample_interval" seconds
            time.sleep(sample_interval)

            #3.1 Get pcps between price now and previous price and find the ticker with best pcps.
            if sample_periods != 0:
                try:
                    ticker_1_pcps = (float(ticker_1_price_value)/float(ticker_1_price_value_previous) -1)*100
                    ticker_2_pcps = (float(ticker_2_price_value)/float(ticker_2_price_value_previous) -1)*100
                    ticker_3_pcps = (float(ticker_3_price_value)/float(ticker_3_price_value_previous) -1)*100

                except:
                    print("Unable to calculate pcps values this time, waiting for next opportunity..")
                try:
                    #relation between tickers and its pcps
                    dictionary_pcps = {ticker_1_pcps:ticker_1_txt,ticker_2_pcps:ticker_2_txt,ticker_3_pcps:ticker_3_txt}

                    pcps_max = float(max(dictionary_pcps))
                    pcps_max_ticker = dictionary_pcps.get(max(dictionary_pcps))

                    #Find the price of best pcps ticker
                    ticker_price = float(dictionary_price[pcps_max_ticker])
                    ticker_buy_price = ticker_price * (1 + (pcps_order_addon / 100))
                    ticker_buy_price = float(("%.4f" % ticker_buy_price))  # 4 decimals

                    #Find what the 1 min open price of that ticker was
                    ticker_open_1min = float(dictionary_price_open[pcps_max_ticker])
                except:
                    print("Unable to find price of best pcps ...coming back later ")
                    continue

                # Print: ticker, price, pcps and 1 min open of each ticker
                print("")
                print("T    ", "O    ", "C   ", "PCPS")
                print(datetime.datetime.now())
                print(ticker_1_txt, ticker_1_op, ticker_1_price_value, ticker_1_pcps)
                print(ticker_2_txt, ticker_2_op, ticker_2_price_value, ticker_2_pcps)
                print(ticker_3_txt, ticker_3_op, ticker_3_price_value, ticker_3_pcps)
                print("")
                print("Ticker with best pcps: ", pcps_max_ticker, pcps_max)
                print("")


                #3.2 Buy if pcps on best ticker is greater than pcps_threshold AND the current price is greater than the opening price and the opening price is not equal to zero
                if pcps_max > pcps_threshold and ticker_buy_price > ticker_open_1min and ticker_open_1min != 0:
                    #Get the volume
                    vol = find_volume(float(ticker_buy_price))
                    #Append pcps_max to history
                    h_pcps_max = ("%.3f" % pcps_max)
                    h_pcps_entry.append(h_pcps_max)
                    #Buy now real or paper


            #4. File previous price.
            ticker_1_price_value_previous = ticker_1_price_value
            ticker_2_price_value_previous = ticker_2_price_value
            ticker_3_price_value_previous = ticker_3_price_value

            sample_periods+=1
    elif use_trade_strategy == strategy_orb:
        while holding_status == 0:
            #Check if any of the stocks break the high - and holds for a specified time.
            orb_breakout_true = "no"
            while orb_breakout_true == "no":
                #Check time
                if time_now > time_lastCall:
                    print("Trading reached EOD - exiting entry routine")
                    return 5
                try:
                    if float(ticker_1_price_value) > float(ticker1_prev_high) and float(ticker1_prev_high) != 0 and float(ticker1_prev_cp) > float(ticker1_prev_op):
                        print("Entered quality check on: ", ticker_1_txt)
                        webull_paper_functions.watch_ticker_1_quality_check_paper()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_1_price_value))
                        time.sleep(orb_quality_check)
                        if float(ticker_1_price_value) > float(ticker1_prev_high) and float(ticker1_a20pcps_0_19) >= a20pcps_0_19_threshold and float(ticker1_a20freq_0_19) >= a20freq_0_19_threshold:
                            price = update_price_before_buy_paper(ticker_1_txt)
                            price_buy = float(price)
                            time_entry=time_now
                            trade_status = "b"
                            pcps_max_ticker = ticker_1_txt
                            val_a20pcps_0_19=ticker1_a20pcps_0_19
                            val_a20freq_0_19=ticker1_a20freq_0_19
                            orb_breakout_true = "yes"
                            continue

                        else:
                            print("Quality check not passed - not entering trade", ticker_1_txt)
                    if float(ticker_2_price_value) > float(ticker2_prev_high) and float(ticker2_prev_high) != 0 and float(ticker2_prev_cp) > float(ticker2_prev_op):
                        print("Entered quality check on: ", ticker_2_txt)
                        webull_paper_functions.watch_ticker_2_quality_check_paper()
                        # Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_2_price_value))
                        time.sleep(orb_quality_check)
                        if float(ticker_2_price_value) > float(ticker2_prev_high) and float(ticker2_a20pcps_0_19) >= a20pcps_0_19_threshold and float(ticker2_a20freq_0_19) >= a20freq_0_19_threshold:
                            price = update_price_before_buy_paper(ticker_2_txt)
                            price_buy = float(price)
                            time_entry=time_now
                            trade_status = "b"
                            pcps_max_ticker = ticker_2_txt
                            val_a20pcps_0_19=ticker2_a20pcps_0_19
                            val_a20freq_0_19=ticker2_a20freq_0_19
                            orb_breakout_true = "yes"
                            continue

                        else:
                            print("Quality check not passed - not entering trade", ticker_2_txt)
                    if float(ticker_3_price_value) > float(ticker3_prev_high) and float(ticker3_prev_high) != 0 and float(ticker3_prev_cp) > float(ticker3_prev_op):
                        print("Entered quality check on: ", ticker_3_txt)
                        webull_paper_functions.watch_ticker_3_quality_check_paper()
                        # Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_3_price_value))
                        time.sleep(orb_quality_check)
                        if float(ticker_3_price_value) > float(ticker3_prev_high) and float(ticker3_a20pcps_0_19) >= a20pcps_0_19_threshold and float(ticker3_a20freq_0_19) >= a20freq_0_19_threshold:
                            price = update_price_before_buy_paper(ticker_3_txt)
                            price_buy = float(price)
                            time_entry=time_now
                            trade_status = "b"
                            pcps_max_ticker = ticker_3_txt
                            val_a20pcps_0_19=ticker3_a20pcps_0_19
                            val_a20freq_0_19=ticker3_a20freq_0_19
                            orb_breakout_true = "yes"
                            continue

                        else:
                            print("Quality check not passed - not entering trade", ticker_2_txt)
                except:
                    print("Unable to compare prices..retrying")

            if orb_breakout_true == "yes":
                print("Entering ORB - moving on to check if order was filled")
                break
    elif use_trade_strategy == strategy_15min_breakout:
        while holding_status == 0:
            try:
                if float(ticker_1_price_value) > float(ticker1_prev_15min_high) and float(ticker1_prev_15min_high) != 0:
                    pcps_max_ticker = ticker_1_txt
                    val_a20pcps_0_19 = ticker1_a20pcps_0_19
                    val_a20freq_0_19 = ticker1_a20freq_0_19
                    break
                if float(ticker_2_price_value) > float(ticker2_prev_15min_high) and float(ticker2_prev_15min_high) != 0:
                    pcps_max_ticker = ticker_2_txt
                    val_a20pcps_0_19 = ticker2_a20pcps_0_19
                    val_a20freq_0_19 = ticker2_a20freq_0_19
                    break
                if float(ticker_3_price_value) > float(ticker3_prev_15min_high) and float(ticker3_prev_15min_high) != 0:
                    pcps_max_ticker = ticker_3_txt
                    val_a20pcps_0_19 = ticker3_a20pcps_0_19
                    val_a20freq_0_19 = ticker3_a20freq_0_19
                    break
                if time_now > time_lastCall:
                    print("Leaving pcps cause time limit reached for today..")
                    return 3
            except ValueError as e:
                print(e)
                print("15min breakout: unable to compare prices...")
    #perform the purchase
    if pcps_max_ticker == ticker_1_txt:
        webull_paper_functions.watch_ticker_1_quality_check_paper()
        vol = find_volume(float(ticker_1_price_value))
        price = update_price_before_buy_paper(ticker_1_txt)
        price_buy = float(price)
        time_entry = str(datetime.datetime.now().time())
        webull_paper_functions.prefill_buy_order(vol)
        trade_status = webull_paper_functions.buy(str(price))
    elif pcps_max_ticker == ticker_2_txt:
        webull_paper_functions.watch_ticker_2_quality_check_paper()
        vol = find_volume(float(ticker_2_price_value))
        price = update_price_before_buy_paper(ticker_2_txt)
        price_buy = float(price)
        time_entry = str(datetime.datetime.now().time())
        webull_paper_functions.prefill_buy_order(vol)
        trade_status = webull_paper_functions.buy(str(price))
    elif pcps_max_ticker == ticker_3_txt:
        webull_paper_functions.watch_ticker_3_quality_check_paper()
        vol = find_volume(float(ticker_3_price_value))
        price = update_price_before_buy_paper(ticker_3_txt)
        price_buy = float(price)
        time_entry = str(datetime.datetime.now().time())
        webull_paper_functions.prefill_buy_order(vol)
        trade_status = webull_paper_functions.buy(str(price))

    #Ask if manual cancel && Check if order was filled
    if trade_status == "b":
        modify_entry_cnt = 1
        filled_status="unknown"
        #Wait until the order is sent to exhange, if not it will look at the order bf
        time.sleep(5)
        #Check filled status
        filled_status=webull_paper_functions.check_filled_status(timer_global_trader_interval)
        if filled_status == "filled":
            modify_entry_cnt = 0
            time.sleep(0.5)
            modify_entry_cnt = 0
            modify_entry_tries = 0
            # Set initial exit point
            if use_trade_strategy == strategy_15min_breakout:
                set_15min_breakout_exit()
            else:
                ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
            print("The initial exit point is: ", ticker_holding_exit_point)
            print("The buy Limit price was: ", price)
            holding_status=1
            #Update P&L status
            bought_price = price
        elif filled_status == "cancelled":
            #Double check in case the order was filled
            for check_now in range(0, check_filled_if_cancelled_maxTries):
                print("///Double checking if the order was actually fillled after cancelling")
                print("Double check cnt: ", check_now)
                time.sleep(1)
                filled_status=webull_paper_functions.check_filled_status(timer_global_trader_interval)
                if filled_status == "filled":
                    modify_entry_cnt = 0
                    modify_entry_tries = 0
                    # Set initial exit point
                    if use_trade_strategy == strategy_15min_breakout:
                        set_15min_breakout_exit()
                    else:
                        ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
                    print("The initial exit point is: ", ticker_holding_exit_point)
                    print("The buy Limit price was: ", price)
                    holding_status = 1
                    bought_price = price
                    break

            if filled_status != "filled":
                print("Buy cancelled - exiting the trade")
                #Initialize trade counters.
                modify_entry_cnt = 0
                modify_entry_tries = 0
                return 1
    else:
        return 1
        print("BUY FAILED --- EXITING")

    # Start the "Exit" routine..
    if use_trade_strategy == strategy_15min_breakout:
        while holding_status == 1:
            print(time_now)
            time.sleep(5)
            exit_now=exit_15min_breakout_stopout()
            if exit_now == "yes":
                print("Selling now - stopped out..")
                break
            exit_now=exit_15min_profit_limit()
            if exit_now == "yes":
                print("Selling cause reached profit target on trade..")
                break
            if time_now >= time_lastCallExit:
                print("Selling now -- reached time linim of today...")
                break
        #Perform the sale..
        webull_paper_functions.prefill_sell_order(vol)
        price = update_price_before_sell_paper(pcps_max_ticker)
        trade_status = webull_paper_functions.sell(str(price))
    else:
        while holding_status == 1 and bear_bailout_status == 0:
            today = datetime.datetime.today().weekday()

            #1. Call the bear bailout exit if holding ticker
            if holding_status == 1 and bear_bailout_status == 0 and pcps_exit == 0 and trade_status != "s":
                bear_bailout()

            #2. Sell if price shoots below exit point and bear bailout status is 0
            if ticker_holding_price_value <= ticker_holding_exit_point and bear_bailout_status == 0:
                #Say that we exit the trade, so not conflicting with other exit strategies
                pcps_exit = 1
                print("--Exiting trade with exit point routine")
                price=update_price_before_sell_paper(pcps_max_ticker)
                trade_status="s"
                #Set sample_periods to zero and break enter trade routine
                sample_periods = 0
                pcps_exit = 0
                break

            #3. Get out before closing in case holding
            elif time_now > time_lastCallExit:
                pcps_exit = 1
                print("Exiting trade due to market closing soon...")
                price=update_price_before_sell_paper(pcps_max_ticker)
                trade_status="s"
                #Set sample_periods to zero and break enter trade routine
                sample_periods = 0
                pcps_exit = 0
                break


    #Check if order was filled
    if trade_status == "s":
        modify_exit_cnt = 1
        filled_status="unknown"
        #Wait until the order is sent to exhange, if not it will look at the order bf
        time.sleep(7)
        filled_status = webull_paper_functions.check_filled_status(timer_global_trader_interval)
        if filled_status == "filled":
            modify_exit_cnt = 0
            print("Resetting trading parameters, trade done")
            print("the exit_cnt rest: ",modify_exit_cnt)
            bear_bailout_status = 0
            bear_cnt = 0
            pcps_exit = 0
            sample_periods = 0
            holding_status = 0
            break_even_or_greater = 0
            trade_successful_cnt+=1
            trade_status = "na"
            time_exit = time_now

            #Update P&L
            sold_price = price
            PnL_this_trade = (float(sold_price) - float(bought_price))*int(vol)
            PnL_this_trade = float("%.2f" % PnL_this_trade)
            PnL_total = float(PnL_total) + float(PnL_this_trade)
            PnL_this_trade_w_fees = float(PnL_this_trade) - float(Trade_fee_per_trade)
            PnL_total_w_fees = float(PnL_total_w_fees) + float(PnL_this_trade_w_fees)

            #Update log file
            log_PnL(PnL_this_trade, PnL_total, PnL_this_trade_w_fees, PnL_total_w_fees, trade_successful_cnt, val_a20pcps_0_19, val_a20freq_0_19, pcps_max_ticker,time_entry,time_exit)


            print("")
            print(pcps_max_ticker)
            print(datetime.datetime.now())
            print("PnL this trade:        ",PnL_this_trade)
            print("PnL total:             ",PnL_total)
            print("PnL this trade w fees: ",PnL_this_trade_w_fees)
            print("PnL total w fees:      ",PnL_total_w_fees)
            print("Trade cnt:             ",trade_successful_cnt)
            print("a20pcps_0_19:          ",val_a20pcps_0_19)
            print("a20freq_0_19:          ",val_a20freq_0_19)
            print("")

    #Exit routine exited or bear bailout -wait until we dont hold the ticker anymore
    while trade_status != "na":
        time.sleep(1)
    print("Success exited trade!!")
    return 0

def set_15min_breakout_exit():
    global ticker_holding_exit_point
    try:
        if pcps_max_ticker == ticker_1_txt and ticker1_prev_15min_op !=0:
            ticker_holding_exit_point = float(ticker1_prev_15min_op)
        elif pcps_max_ticker == ticker_2_txt and ticker2_prev_15min_op !=0:
            ticker_holding_exit_point = float(ticker2_prev_15min_op)
        elif pcps_max_ticker == ticker_3_txt and ticker3_prev_15min_op !=0:
            ticker_holding_exit_point = float(ticker3_prev_15min_op)

        print(pcps_max_ticker, "15min breakout exit point:",ticker_holding_exit_point)
        print(pcps_max_ticker, "15min breakout exit point:",ticker_holding_exit_point)
        print(pcps_max_ticker, "15min breakout exit point:",ticker_holding_exit_point)
    except:
        print("Unable to set 15min breakout exit point...")

def exit_15min_breakout_stopout():
    try:
        if float(ticker_holding_price_value) < float(ticker_holding_exit_point):
            print(pcps_max_ticker, " Exiting trade -- price broke low of previous 15min..")
            print(pcps_max_ticker, "current price", ticker_holding_price_value)
            print(pcps_max_ticker, "Exit point", ticker_holding_exit_point)
            exit_now="yes"
            return exit_now
        else:
            print(pcps_max_ticker, "current price", ticker_holding_price_value)
            print(pcps_max_ticker, "Exit point", ticker_holding_exit_point)
            exit_now="no"
            return exit_now
    except:
        print("Unable to check 15min breakout stoppout yes/no")

def exit_15min_profit_limit():
    try:
        if float(break_even_or_greater) >= float(profit_target):
            print(pcps_max_ticker, "exiting trade --- reached PROFIT LIMIT..")
            print(pcps_max_ticker, "exiting trade --- reached PROFIT LIMIT..")
            print(pcps_max_ticker, "exiting trade --- reached PROFIT LIMIT..")
            print(pcps_max_ticker, "break even or greater: ", break_even_or_greater)
            exit_now="yes"
            return exit_now
        else:
            print(pcps_max_ticker, "break even or greater", break_even_or_greater)
            print(pcps_max_ticker, "15min_breakout_profit limit", profit_target)
            exit_now="no"
            return exit_now
    except:
        print("Unable to check 15min profit limit stoppout...")

def pcps_test():
    global driver
    global pcps_threshold
    global pcps_threshold_s
    global pcps_max_ticker
    global sample_interval
    global sample_periods
    global holding_status

    global ticker_1_pcps
    global ticker_2_pcps
    global ticker_3_pcps

    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global ticker_buy_price
    global ticker_sell_price

    global ticker_1_price_value_previous
    global ticker_2_price_value_previous
    global ticker_3_price_value_previous

    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt

    global ticker_holding_price
    global ticker_holding_price_value
    global ticker_holding_price_value_previous
    global ticker_holding_pcps

    global pcps_order_addon

    global ticker_1_op
    global ticker_2_op
    global ticker_3_op
    global ticker_holding_pcp
    global ticker_holding_exit_point

    global dictionary_price_open
    global dictionary_price
    global vol
    global bear_bailout_status
    global pcps_exit
    global pcps_max
    global h_pcps_entry
    global trade_status

    global modify_entry_cnt
    global modify_entry_tries
    global modify_exit_cnt
    global modify_exit_cnt_max
    global price
    global bear_cnt
    global filled_status

    global today
    global time_now

    global bought_price
    global sold_price
    global PnL_total
    global PnL_total_w_fees
    global Trade_fee_per_trade
    global PnL_this_trade
    global PnL_this_trade_w_fees

    global trade_successful_cnt

    global buy_now
    global sell_now
    global cancel_now

    global price_buy



    # Start the "Enter trade routine"
    if use_trade_strategy == strategy_pcps:
        while holding_status == 0:
            #Relation between tickers and current price
            dictionary_price ={ticker_1_txt:ticker_1_price_value,ticker_2_txt:ticker_2_price_value,ticker_3_txt:ticker_3_price_value}
            #Relation between tickers and 1 min opening prices
            dictionary_price_open ={ticker_1_txt:ticker_1_op,ticker_2_txt:ticker_2_op,ticker_3_txt:ticker_3_op}

            #2. Wait "sample_interval" seconds
            time.sleep(sample_interval)

            #3.1 Get pcps between price now and previous price and find the ticker with best pcps.
            if sample_periods != 0:
                try:
                    ticker_1_pcps = (float(ticker_1_price_value)/float(ticker_1_price_value_previous) -1)*100
                    ticker_2_pcps = (float(ticker_2_price_value)/float(ticker_2_price_value_previous) -1)*100
                    ticker_3_pcps = (float(ticker_3_price_value)/float(ticker_3_price_value_previous) -1)*100

                except:
                    print("Unable to calculate pcps values this time, waiting for next opportunity..")
                try:
                    #relation between tickers and its pcps
                    dictionary_pcps = {ticker_1_pcps:ticker_1_txt,ticker_2_pcps:ticker_2_txt,ticker_3_pcps:ticker_3_txt}

                    pcps_max = float(max(dictionary_pcps))
                    pcps_max_ticker = dictionary_pcps.get(max(dictionary_pcps))

                    #Find the price of best pcps ticker
                    ticker_price = float(dictionary_price[pcps_max_ticker])
                    ticker_buy_price = ticker_price * (1 + (pcps_order_addon / 100))
                    ticker_buy_price = float(("%.4f" % ticker_buy_price))  # 4 decimals

                    #Find what the 1 min open price of that ticker was
                    ticker_open_1min = float(dictionary_price_open[pcps_max_ticker])
                except:
                    print("Unable to find price of best pcps ...coming back later ")
                    continue

                # Print: ticker, price, pcps and 1 min open of each ticker
                print("")
                print("T    ", "O    ", "C   ", "PCPS")
                print(datetime.datetime.now())
                print(ticker_1_txt, ticker_1_op, ticker_1_price_value, ticker_1_pcps)
                print(ticker_2_txt, ticker_2_op, ticker_2_price_value, ticker_2_pcps)
                print(ticker_3_txt, ticker_3_op, ticker_3_price_value, ticker_3_pcps)
                print("")
                print("Ticker with best pcps: ", pcps_max_ticker, pcps_max)
                print("")


                #3.2 Buy if pcps on best ticker is greater than pcps_threshold AND the current price is greater than the opening price and the opening price is not equal to zero
                if pcps_max > pcps_threshold and ticker_buy_price > ticker_open_1min and ticker_open_1min != 0:
                    #Get the volume
                    vol = find_volume(float(ticker_buy_price))
                    #Append pcps_max to history
                    h_pcps_max = ("%.3f" % pcps_max)
                    h_pcps_entry.append(h_pcps_max)
                    #Buy now real or paper


            #4. File previous price.
            ticker_1_price_value_previous = ticker_1_price_value
            ticker_2_price_value_previous = ticker_2_price_value
            ticker_3_price_value_previous = ticker_3_price_value

            sample_periods+=1
    elif use_trade_strategy == strategy_orb:
        while holding_status == 0:
            #Check if any of the stocks break the high - and holds for a specified time.
            orb_breakout_true = "no"
            while orb_breakout_true == "no":
                #Check time
                if time_now > time_lastCall:
                    print("Trading reached EOD - exiting entry routine")
                    return 5
                try:
                    #if float(ticker_1_price_value) > float(ticker1_prev_high) and float(ticker1_prev_high) != 0 and float(ticker1_prev_cp) > float(ticker1_prev_op):
                    if float(ticker_1_price_value) == float(ticker1_prev_high):
                        print("Entered quality check on: ", ticker_1_txt)
                        watch_ticker_1_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_1_price_value))
                        nordnet_functions.prefill_buy_order(str(1), str(vol))
                        time.sleep(orb_quality_check)
                        #if float(ticker_1_price_value) > float(ticker1_prev_high):
                        if float(ticker_1_price_value) == float(ticker1_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_1_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_1_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_1_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_1_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_1_txt
                                orb_breakout_true = "yes"
                                continue

                        else:
                            print("Quality check not passed - not entering trade", ticker_1_txt)
                            nordnet_functions.enter_watchlist()
                    #if float(ticker_2_price_value) > float(ticker2_prev_high) and float(ticker2_prev_high) != 0 and float(ticker2_prev_cp) > float(ticker2_prev_op):
                    if float(ticker_2_price_value) == float(ticker2_prev_high):
                        print("Entered quality check on: ", ticker_2_txt)
                        watch_ticker_2_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_2_price_value))
                        nordnet_functions.prefill_buy_order(str(2), str(vol))
                        time.sleep(orb_quality_check)
                        ##Get volume
                        #if float(ticker_2_price_value) > float(ticker2_prev_high):
                        if float(ticker_2_price_value) == float(ticker2_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_2_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_2_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_2_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_2_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_2_txt
                                orb_breakout_true = "yes"
                                continue
                        else:
                            print("Quality check not passed - not entering trade", ticker_2_txt)
                            nordnet_functions.enter_watchlist()
                    #if float(ticker_3_price_value) > float(ticker3_prev_high) and float(ticker3_prev_high) != 0 and float(ticker3_prev_cp) > float(ticker3_prev_op):
                    if float(ticker_3_price_value) == float(ticker3_prev_high):
                        print("Entered quality check on: ", ticker_3_txt)
                        watch_ticker_3_quality_check()
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_3_price_value))
                        nordnet_functions.prefill_buy_order(str(3), str(vol))
                        time.sleep(orb_quality_check)
                        #if float(ticker_3_price_value) > float(ticker3_prev_high):
                        if float(ticker_3_price_value) == float(ticker3_prev_high):
                            if autotrader != "yes":
                                buy_now = "maybe"
                                buy_now=pyautogui.confirm("BUY NOW?", ticker_3_txt)
                                if buy_now == "OK":
                                    price = update_price_before_buy(ticker_3_txt)
                                    price_buy=float(price)
                                    trade_status=nordnet_functions.buy(str(price), str(vol))
                                    nordnet_functions.prefill_sell_order(str(vol))
                                    nordnet_functions.open_order_status()
                                    pcps_max_ticker = ticker_3_txt
                                    orb_breakout_true = "yes"
                                    continue
                                else:
                                    print("Skipping trade..")
                                    nordnet_functions.enter_watchlist()
                                    time.sleep(5)
                            else:
                                price = update_price_before_buy(ticker_3_txt)
                                price_buy = float(price)
                                trade_status = nordnet_functions.buy(str(price), str(vol))
                                nordnet_functions.prefill_sell_order(str(vol))
                                nordnet_functions.open_order_status()
                                pcps_max_ticker = ticker_3_txt
                                orb_breakout_true = "yes"
                                continue

                        else:
                            print("Quality check not passed - not entering trade: ", ticker_3_txt)
                            nordnet_functions.enter_watchlist()
                except:
                    print("Unable to compare prices..retrying")

            if orb_breakout_true == "yes":
                print("Entering ORB - moving on to check if order was filled")
                break
    #Ask if manual cancel && Check if order was filled
    if trade_status == "b":
        modify_entry_cnt = 1
        filled_status="unknown"
        if autotrader != "yes":
            cancel_now = pyautogui.confirm("CANCEL NOW?", pcps_max_ticker,timeout=modify_entry_cnt_max*1000)
            if cancel_now == "OK":
                print("CANCELLING order")
                trade_status = nordnet_functions.cancel_order()
                if trade_status == "c":
                    print("Success - CANCELLING ORDER OK")
                    nordnet_functions.enter_watchlist()
                else:
                    print("UNABLE TO CANCEL")
                    nordnet_functions.enter_watchlist()
            elif cancel_now == "Timeout":
                print("MANUAL CANCEL TIMED OUT")

        #Check filled status
        filled_status=nordnet_functions.check_order_status()
        if filled_status == "filled":
            modify_entry_cnt = 0
            modify_entry_tries = 0
            # Set initial exit point
            ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
            print("The initial exit point is: ", ticker_holding_exit_point)
            print("The buy Limit price was: ", price)
            holding_status=1
            #Update P&L status
            bought_price = price
        elif filled_status == "cancelled":
            #No double checking needed
            print("No double checking needed if order was filled or cancelled...")

            if filled_status != "filled":
                print("Buy cancelled - exiting the trade")
                #Initialize trade counters.
                modify_entry_cnt = 0
                modify_entry_tries = 0
                return 1

    # Start the "Exit trade routine - if holding ticker AND bear bailout has not entered the exit"
    sell_now = "maybe"
    while holding_status == 1 and bear_bailout_status == 0:
        time.sleep(1)
        today = datetime.datetime.today().weekday()
        if autotrader != "yes":
            #0. Manual input for selling ( first priority - Only asking 1 time)
            if sell_now == "maybe":
                sell_now = pyautogui.confirm("SELL NOW?", pcps_max_ticker)
                if sell_now == "OK":
                    print("--Exiting trade manually..")
                    price=update_price_before_sell(pcps_max_ticker)
                    trade_status=nordnet_functions.sell(str(price))
                    nordnet_functions.open_order_status()
                    #Set sample_periods to zero and break enter trade routine
                    sample_periods = 0
                    pcps_exit = 0
                    break

        print("NOT SELLING MANUALLY!!!")

        #1. Call the bear bailout exit if holding ticker
        if holding_status == 1 and bear_bailout_status == 0 and pcps_exit == 0 and trade_status != "s":
            bear_bailout()

        #2. Sell if price shoots below exit point and bear bailout status is 0
        if ticker_holding_price_value <= ticker_holding_exit_point and bear_bailout_status == 0:
            #Say that we exit the trade, so not conflicting with other exit strategies
            pcps_exit = 1
            print("--Exiting trade with exit point routine")
            price=update_price_before_sell(pcps_max_ticker)
            trade_status=nordnet_functions.sell(str(price))
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break

        #3. Get out before closing in case holding
        elif time_now > time_lastCallExit:
            pcps_exit = 1
            print("Exiting trade due to market closing soon...")
            price=update_price_before_sell(pcps_max_ticker)
            trade_status=nordnet_functions.sell(str(price))
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break


    #Check if order was filled
    if trade_status == "s":
        modify_exit_cnt = 1
        filled_status="unknown"
        filled_status = nordnet_functions.check_order_status()
        if filled_status == "filled":
            modify_exit_cnt = 0
            print("Resetting trading parameters, trade done")
            print("the exit_cnt rest: ",modify_exit_cnt)
            bear_bailout_status = 0
            bear_cnt = 0
            pcps_exit = 0
            sample_periods = 0
            holding_status = 0
            trade_successful_cnt+=1
            trade_status = "na"

            #Update P&L
            sold_price = price
            PnL_this_trade = (float(sold_price) - float(bought_price))*int(vol)
            PnL_this_trade = float("%.2f" % PnL_this_trade)
            PnL_total = float(PnL_total) + float(PnL_this_trade)
            PnL_this_trade_w_fees = float(PnL_this_trade) - float(Trade_fee_per_trade)
            PnL_total_w_fees = float(PnL_total_w_fees) + float(PnL_this_trade_w_fees)

            #Update log file
            log_PnL(PnL_this_trade, PnL_total, PnL_this_trade_w_fees, PnL_total_w_fees, trade_successful_cnt, pcps_max)

            print("")
            print(datetime.datetime.now())
            print("PnL this trade:        ",PnL_this_trade)
            print("PnL total:             ",PnL_total)
            print("PnL this trade w fees: ",PnL_this_trade_w_fees)
            print("PnL total w fees:      ",PnL_total_w_fees)
            print("Trade cnt:             ",trade_successful_cnt)
            print("pcps:                  ",pcps_max)
            print("")

            #Get back to watchlist
            nordnet_functions.enter_watchlist()

    #Exit routine exited or bear bailout -wait until we dont hold the ticker anymore
    while trade_status != "na":
        time.sleep(1)
    print("Success exited trade!!")
    return 0

def check_time_day():
    #monitor time and day
    global trade_range_days
    global today
    global time_now
    global time_getReady
    global time_lastCall
    global trade_cnt
    global trade_successful_cnt
    global trade_fail_cnt
    global PnL_this_trade
    global PnL_this_trade
    global PnL_total
    global PnL_this_trade_w_fees
    global PnL_total_w_fees
    global trade_true

    today = datetime.datetime.today().weekday()
    time_now = str(datetime.datetime.now().time())

    print("today is: ",today)
    print("current time is",time_now)

    #Check the day first - if 0 -4 ( monday until firday )
    if today in trade_range_days:
        print("it's a weekday, let's go ahead and check the time")
        while time_now < time_getReady:
            #stand by - fetch the time every 60 sec.
            time.sleep(1)
            time_now = str(datetime.datetime.now().time())

        if time_now < time_lastCall and time_now > time_getReady:
            print("let' trade")
            webull_paper_functions.refresh()
            if trade_cnt == 0:
                print("Starting up timers....")
                get_watchlist_tickers_paper()
                global_trader()
                timer_5min()
            trade_true = "yes"
        else:
            print("it's too late. waiting for tomorrow")
            trade_true = "no"

            #initialize trade counters to get ready for next trading day
            trade_fail_cnt = 0
            trade_successful_cnt = 0
            trade_cnt = 0
            print("initialized trade_fail_cnt: ", trade_fail_cnt)
            print("initialized trade_successful cnt: ", trade_successful_cnt)

            #Update P&L
            PnL_this_trade = 0.0
            PnL_this_trade = 0.0
            PnL_total = 0.0
            PnL_this_trade_w_fees = 0.0
            PnL_total_w_fees = 0.0

            while time_now > time_lastCallExit or time_now < time_getReady:
                time_now = str(datetime.datetime.now().time())
                time.sleep(0.5)
                print("Waiting to get ready..", time_now)

            if today in trade_range_days:
                print("let' trade")
                webull_paper_functions.refresh()
                get_watchlist_tickers_paper()
                global_trader()
                timer_5min()
                trade_true="yes"
            else:
                print("its weeknd..")
                print(time_now)
                trade_true="no"
    else:
        print("its weekend")
        trade_true = "no"
        time.sleep(3600)
        time_now = str(datetime.datetime.now().time())

    return trade_true

def trade_or_not():
    global trade_true
    trade_now = ""

    while trade_now != "yes":
        print("checking time and day now..")
        trade_now = str(check_time_day())


#Start trading...
if trade_mode =="r":
    trade_fail_cnt=0
    trade_successful_cnt=0
    open_webull()
    logon_webull()
    nordnet_functions.login_nordnet()
    global_trader()
    global_get_prices()

    while trade_successful_cnt <= trade_cnt_max:
        trade_or_not()
        #Start new trade as long as previous trade was completed
        while holding_status == 1:
            print("Still holding possition - waiting for sell order to complete")
            time.sleep(1)

        #Start pcps trade
        refresh()
        trade_pcps=pcps()
        if trade_pcps == 1:
            trade_fail_cnt+=1
            print("Successful trades: ", trade_successful_cnt)
            print("Trade failed, total fails: ",trade_fail_cnt)
        elif trade_pcps == 5:
            #Trading reached EOD - getting setup for tomorrow
            pass
        else:
            #NOTE the successful cnt is incremented in the pcps function.
            print("Successful trades: ", trade_successful_cnt)
            print("Trade failed, total fails: ",trade_fail_cnt)

    print("Daily trade cnt reached - stopping")
elif trade_mode =="p":
    trade_fail_cnt=0
    trade_successful_cnt=0
    webull_paper_functions.open_webull()
    webull_paper_functions.logon_webull()

    while 1:
        trade_or_not()
        #Start new trade as long as previous trade was completed
        while holding_status == 1:
            print("Still holding possition - waiting for sell order to complete")
            time.sleep(1)
        trade_pcps=pcps_paper()
        trade_cnt+=1
        if trade_pcps == 1:
            trade_fail_cnt+=1
            print("Successful trades: ", trade_successful_cnt)
            print("Trade failed, total fails: ",trade_fail_cnt)
        elif trade_pcps == 3:
            print("TRADING REACHED EOD -- getting ready for tomorrow..")
        else:
            #NOTE the successful cnt is incremented in the pcps function.
            print("Successful trades: ", trade_successful_cnt)
            print("Trade failed, total fails: ",trade_fail_cnt)
            print("Total trade cnt:",trade_cnt)


else:
    test_trade="s"
    webull_paper_functions.open_webull()
    webull_paper_functions.logon_webull()
    time.sleep(10)
    webull_paper_functions.refresh()
    global_trader()
    global_get_prices_paper()
    timer_15min()
    if test_trade == "s":
        #pretend we hold
        pcps_max_ticker=ticker_1_txt
        holding_status=1
        vol=1
        modify_exit_cnt = 0
        webull_paper_functions.prefill_sell_order(vol)
        price=update_price_before_sell_paper(pcps_max_ticker)
        trade_status = webull_paper_functions.sell(str(price))
        while trade_status != "s":
            print("UNABLE TO SELL _ TRYING AGAIN")
            webull_paper_functions.refresh()
            time.sleep(10)
            webull_paper_functions.prefill_sell_order(vol)
            price = update_price_before_sell_paper(pcps_max_ticker)
            trade_status = webull_paper_functions.sell(str(price))
        modify_exit_cnt = 1
        webull_paper_functions.check_filled_status()
    elif test_trade == "b":
        #pretend we buy
        webull_paper_functions.watch_ticker_1_quality_check_paper()
        vol = find_volume(float(ticker_1_price_value))
        price = update_price_before_buy_paper(ticker_1_txt)
        price_buy = float(price)
        webull_paper_functions.prefill_buy_order(vol)
        trade_status = webull_paper_functions.buy(str(price))
        pcps_max_ticker = ticker_1_txt
        #Ask if manual cancel && Check if order was filled
        if trade_status == "b":
            modify_entry_cnt = 1
            filled_status="unknown"
            #Wait until the order is sent to exhange, if not it will look at the order bf
            time.sleep(5)
            #Check filled status
            filled_status=webull_paper_functions.check_filled_status()
            if filled_status == "filled":
                modify_entry_cnt = 0
                time.sleep(0.5)
                modify_entry_cnt = 0
                modify_entry_tries = 0
                # Set initial exit point
                if use_trade_strategy == strategy_15min_breakout:
                    set_15min_breakout_exit()
                else:
                    ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
                print("The initial exit point is: ", ticker_holding_exit_point)
                print("The buy Limit price was: ", price)
                holding_status=1
                #Update P&L status
                bought_price = price
            elif filled_status == "cancelled":
                #Double check in case the order was filled
                for check_now in range(0, check_filled_if_cancelled_maxTries):
                    print("///Double checking if the order was actually fillled after cancelling")
                    print("Double check cnt: ", check_now)
                    time.sleep(1)
                    filled_status=webull_paper_functions.check_filled_status()
                    if filled_status == "filled":
                        modify_entry_cnt = 0
                        modify_entry_tries = 0
                        # Set initial exit point
                        if use_trade_strategy == strategy_15min_breakout:
                            set_15min_breakout_exit()
                        else:
                            ticker_holding_exit_point = (float(price) * (1 - ticker_holding_exit_offset))
                        print("The initial exit point is: ", ticker_holding_exit_point)
                        print("The buy Limit price was: ", price)
                        holding_status = 1
                        bought_price = price
                        break

                if filled_status != "filled":
                    print("Buy cancelled - exiting the trade")
                    #Initialize trade counters.
                    modify_entry_cnt = 0
                    modify_entry_tries = 0








