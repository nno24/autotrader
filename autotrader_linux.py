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
import nordnet_webelements
import nordnet_functions

driver = webdriver.Chrome('/usr/bin/chromedriver')
#driver2 = webdriver.Chrome('/usr/bin/chromedriver')

#Trade mode
#r = real money
#p = paper trade webull
#o = offline paper trade outside market american market hours.
#others: test mode - for testing new functions
trade_mode = "p"
trade_true = ""
strategy_orb = "orb" #Opening range breakout
strategy_pcps = "pcps" #Price change/s
use_trade_strategy = strategy_orb

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
trading_cash_usd = 10000.0
trade_cnt_real_max = 5
trade_cnt_max = 200
trade_cnt = 0
trade_status ="na"

#If the sell order was not completed within this timeinterval, modify sell order with new updated price
sell_order_timeout_udpate_price = 10

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
timer_interval = 1
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
ticker_holding_exit_offset = 0.01    #This is percent

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
file_trade_completed_status = 1

#Dates
date_now =""

#Modify order counters
modify_entry_cnt=0
modify_entry_cnt_max=20
modify_entry_tries=0
modify_entry_tries_max=2
modify_exit_cnt=0
modify_exit_cnt_max=20

filled_status = "unknown"
price=0.0

# monitor time and day
trade_range_days = range(0, 5)
today = datetime.datetime.today().weekday()
time_now = str(datetime.datetime.now().time())
time_getReady = "14:30:00"
time_lastCall = "20:55:00"
time_lastCallExit = "20:57:00"

# P&L parameters
bought_price = 0.0
sold_price = 0.0
PnL_total = 0.0
PnL_this_trade = 0.0
PnL_this_trade_w_fees = 0.0
PnL_total_w_fees = 0.0
Trade_fee_per_trade = 10

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
orb_quality_check = 15
bailout_of_entry_loop = 1
check_filled_if_cancelled_maxTries = 25

#pnl daily params -- keep track of only reporting once every 30 min
pnl_daily_0_cnt = 0
pnl_daily_30_cnt = 0

def dailY_pnL_tracker(full_or_half):
    global pnl_daily_0_cnt
    global pnl_daily_30_cnt

    print("The hour is: ", full_or_half)

    if full_or_half == "full":
        pnl_daily_0_cnt+=1
        pnl_daily_30_cnt = 0
    elif full_or_half == "half":
        pnl_daily_30_cnt+=1
        pnl_daily_0_cnt = 0
    #Get daily pnl
    pnl_daily_elem=driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[5]/div[2]")
    pnl_daily=pnl_daily_elem.text
    print(pnl_daily)

    subfolder = "/home/sjefen/Dropbox/log/PnL_daily"
    tday = str(datetime.datetime.now().date())
    time_n = datetime.datetime.now()
    l_fileName = str(subfolder) + "/" + str(tday)

    os.makedirs(subfolder, exist_ok=True)

    l_file = open(l_fileName, "a")
    l_file.write(str(time_n))
    l_file.write("\n")
    l_file.write("PnL daily:        ")
    l_file.write(str(pnl_daily))
    l_file.write("\n")
    l_file.write("Trade cnt succ:   ")
    l_file.write(str(trade_successful_cnt))
    l_file.write("\n")
    l_file.write("\n")
    l_file.close()
    print("****Successfully written to log file!!")

def refresh():
    global driver

    driver.refresh()
    refreshed = 1
    while refreshed == 1:
        try:
            #Click the "all" section, so failures can not present itself in the "working" tab. Have seen errors on server side
            elem_all = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/div[5]")
            elem_all.click()
            print("////// Refreshed webull OK")
            refreshed = 0
        except:
            print("Trying refresh..")

def get_gainers_watchlist():
    global driver
    # Get pre mkt top gainers
    g_mkt = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[2]/div[1]/div[4]/i")
    g_mkt.click()

    g_exth = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[2]/div[2]/div/div/div/div/div[2]")
    g_exth.click()
    time.sleep(1)

def cleanup_if_fail_purchase():
    # If pirce gap was too big - cancel.
    try:
        elem_cont = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/button[1]")
        elem_cont.click()
        print("Price gap too big..")
    except:
        print("no worries, no price gap")

    # Check if price increment was wrong - close popup dialouge
    try:
        time.sleep(0.6)
        p_price_incr = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/button")
        p_price_incr.click()
    except:
        print("no worries, price increment was OK.")


def fetch_prices():
    global dictionary_price_open
    global ticker_1_price_value
    global ticker_2_price_value
    global ticker_3_price_value
    global date_now
    global ticker_1_op
    global ticker_2_op
    global ticker_3_op

    try:
        # Get prices of tickers
        ticker_1_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_1_price_value = ticker_1_price.text
        ticker_2_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_2_price_value = ticker_2_price.text
        ticker_3_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_3_price_value = ticker_3_price.text
        # Update the opening prices vs tickers
        dictionary_price_open = {ticker_1_txt: ticker_1_op, ticker_2_txt: ticker_2_op, ticker_3_txt: ticker_3_op}
    except:
        print("UNABLE to fetch prices now:", date_now)

def fetch_holding_price():
    global pcps_max_ticker
    global ticker_holding_price_value
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    global ticker_holding_op
    global dictionary_price_open

    if pcps_max_ticker == ticker_1_txt:
        ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_holding_price_value = float(ticker_holding_price.text)
    elif pcps_max_ticker == ticker_2_txt:
        ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_holding_price_value = float(ticker_holding_price.text)
    elif pcps_max_ticker == ticker_3_txt:
        ticker_holding_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_holding_price_value = float(ticker_holding_price.text)

    ticker_holding_op = float(dictionary_price_open[pcps_max_ticker])
    print(pcps_max_ticker, "Open: ", ticker_holding_op, "Price: ", ticker_holding_price_value)

def file_trade():
    global h_ticker_holding_price
    global h_trade_time_table
    global h_buy_order_duration
    global h_sell_order_duration
    global h_buy_order_duration
    global h_buy_order_filled_time_now
    global h_sell_order_filled_time_now
    global h_selling_time_now
    global h_buying_time_now
    global h_trade_time_cnt
    global h_sold_timestamp
    global file_trade_completed_status

    h_trade_time_cnt+=1
    h_ticker_holding_price.append(float(ticker_holding_price_value))
    print("+-+-+FILiNG TRADE")

    #Update only pirce and time from buying until order filled
    if filled_status != "filled":
        h_trade_time_table.append(h_trade_time_cnt)
    elif filled_status == "filled":
        h_trade_time_table.append("BF")
        h_buy_order_duration = h_trade_time_cnt
        h_trade_time_cnt = 0
        file_trade_completed_status = 0


def plot_trade():
    global h_trade_time_table
    global h_ticker_holding_price

    #Prep saving files in subfolders depending on date
    topdir="buyorders"
    todays_date = datetime.datetime.today().date()
    subdirectory = str(topdir) + "/" + str(todays_date)
    file_path = str(topdir) + "/" + str(todays_date) + "/" + str(trade_successful_cnt)
    os.makedirs(subdirectory, exist_ok=True)

    #Prep title
    time_this_trade = datetime.datetime.today().time()
    time_now_this_trade = ("%.8s" % time_this_trade)
    title_this_trade = str(pcps_max_ticker) + "  " + "Buy-filled:  " + str(time_this_trade) + "  " + "PnL-trade:" + "  " + str(PnL_this_trade)

    plt.xticks(fontsize=6)
    plt.plot(h_trade_time_table,h_ticker_holding_price)
    plt.xlabel("Time (s)")
    plt.ylabel("Price")
    plt.title(str(title_this_trade))
    plt.savefig(str(file_path))

    #initialize tables and plot
    h_trade_time_table.clear()
    h_ticker_holding_price.clear()
    plt.clf()
    print("Plot trade lists iniitialized")


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
                trade=nordnet_functions.sell(ticker_holding_price_value)
                nordnet_functions.open_order_status()
                if trade == 0:
                    print("Bailed out!!!")
                else:
                    print("Unable to bail out - sell order not completed..")

            elif pcps_exit == 1:
                print("bear bailout cancelled, due to exit performed by pcps: ", pcps_exit)

    elif ticker_holding_price_value >= ticker_holding_op:
        bear_cnt=0

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

    #Start the global trader as a thread
    threading.Timer(timer_interval, global_trader).start()

    #Increment counters
    timer_cnt+=1
    timer_cnt_sec+=1
    timer_pcps_cnt+=1
    if modify_entry_cnt !=0:
        modify_entry_cnt+=1
        print("modify_entry: ",modify_entry_cnt)
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
    #Get the watchlist tickers - and fetch its prices
    get_watchlist_tickers()

    #Check if watchlist are different - if so set open prices to zero
    if ticker_1_txt != ticker_1_prev_txt:
        print("Initializing 1 min open price of: ",ticker_1_txt," ..due to watchlist update")
        ticker_1_op = 0.0
        ticker1_prev_high = 0
        ticker1_prev_1min_candle = []
    if ticker_2_txt != ticker_2_prev_txt:
        print("Initializing 1 min open price of: ",ticker_2_txt," ..due to watchlist update")
        ticker_2_op = 0.0
        ticker2_prev_high = 0
        ticker2_prev_1min_candle = []
    if ticker_3_txt != ticker_3_prev_txt:
        print("Initializing 1 min open price of: ",ticker_3_txt," ..due to watchlist update")
        ticker_3_op = 0.0
        ticker3_prev_high = 0
        ticker3_prev_1min_candle = []
    fetch_prices()

    #If BUY order yet not filled - cancel buy order
    if modify_entry_cnt == modify_entry_cnt_max and filled_status != "filled":
        print("CANCELLING order")
        cancel=nordnet_functions.cancel_order()
        if cancel == 1:
            print("ORDER FILLED - UNABLE TO CANCEL")
        else:
            trade_status = "c"

    #Fetch prices of pcps_max_ticker: if bought, sold or holding
    if trade_status == "b" or trade_status == "s" or holding_status == 1:
        fetch_holding_price()

        #Store 1 min closing price of pcps_max_ticker
        if time_now_sec == 59:
            timer_cnt_min+=1
            timer_cnt_sec=0
            ticker_holding_pcp = float(ticker_holding_price_value)
            ticker_holding_exit_point = (ticker_holding_pcp * (1 - float(ticker_holding_exit_offset)))
            print("the exit point is",ticker_holding_exit_point)
            print("the previous 1 min close of: ",pcps_max_ticker,"is",ticker_holding_pcp)

    #File trade from BUY until buy order filled
    if trade_status == "b" and file_trade_completed_status == 1:
        file_trade()

    #If SELL order yet not filled - edit sell order
    if modify_exit_cnt == modify_exit_cnt_max and filled_status != "filled":
        print("MODIFYING SELL ORDER")
        trade = nordnet_functions.modify_sell_order(str(ticker_holding_price_value))
        nordnet_functions.open_order_status()
        if modify_exit_cnt != 0:
            modify_exit_cnt=1
            print("Starting new exit_cnt: ",modify_exit_cnt)
        else:
            print("---Sell order already filled, no need to modify")


    #Get 1 min opening price of the tickers
    if time_now_sec == 0:
        try:
            #Set ticker 1 min opening prices
            ticker_1_op = float(ticker_1_price_value)
            ticker_2_op = float(ticker_2_price_value)
            ticker_3_op = float(ticker_3_price_value)
            print("1 min open: ",ticker_1_txt, ticker_1_op)
            print("1 min open: ",ticker_2_txt, ticker_2_op)
            print("1 min open: ",ticker_3_txt, ticker_3_op)

            # ORB: Get candle info
            ticker1_prev_high = max(ticker1_prev_1min_candle)
            ticker2_prev_high = max(ticker2_prev_1min_candle)
            ticker3_prev_high = max(ticker3_prev_1min_candle)

            ticker1_prev_cp = ticker1_prev_1min_candle[-1]
            ticker2_prev_cp = ticker2_prev_1min_candle[-1]
            ticker3_prev_cp = ticker3_prev_1min_candle[-1]

            ticker1_prev_op = ticker1_prev_1min_candle[0]
            ticker2_prev_op = ticker2_prev_1min_candle[0]
            ticker3_prev_op = ticker3_prev_1min_candle[0]


            print(ticker_1_txt, "previous high: ", ticker1_prev_high)
            print(ticker_2_txt, "previous high: ", ticker2_prev_high)
            print(ticker_3_txt, "previous high: ", ticker3_prev_high)
            print(ticker_1_txt, "previous close: ", ticker1_prev_cp)
            print(ticker_2_txt, "previous close: ", ticker2_prev_cp)
            print(ticker_3_txt, "previous close: ", ticker3_prev_cp)
            print(ticker_1_txt, "previous open: ", ticker1_prev_op)
            print(ticker_2_txt, "previous open: ", ticker2_prev_op)
            print(ticker_3_txt, "previous open: ", ticker3_prev_op)

            # Initialize
            ticker1_prev_1min_candle = []
            ticker2_prev_1min_candle = []
            ticker3_prev_1min_candle = []

            #Set opening value
            ticker1_prev_1min_candle.append(float(ticker_1_op))
            ticker2_prev_1min_candle.append(float(ticker_2_op))
            ticker3_prev_1min_candle.append(float(ticker_3_op))
        except:
            print("Unable to store 1 min opening prices..")
    elif time_now_sec > 0 and time_now_sec <= 59:
        try:
            ticker1_prev_1min_candle.append(float(ticker_1_price_value))
            ticker2_prev_1min_candle.append(float(ticker_2_price_value))
            ticker3_prev_1min_candle.append(float(ticker_3_price_value))
        except:
            print("Unable to append to 1 min candle..")

    #Set 1 min closing price of tickers
    if time_now_sec == 59:
        try:
            ticker_1_cp = float(ticker_1_price_value)
            ticker_2_cp = float(ticker_2_price_value)
            ticker_3_cp = float(ticker_3_price_value)
            print("1 min closing: ",ticker_1_txt, ticker_1_cp)
            print("1 min closing: ",ticker_2_txt, ticker_2_cp)
            print("1 min closing: ",ticker_3_txt, ticker_3_cp)
        except:
            print("Unable to store 1 min closing price..")

    #pnl daily
    if time_now_min == 0 and pnl_daily_0_cnt == 0 and trade_true == "yes":
        print("DAILY PnL log getting filed on full..")
        dailY_pnL_tracker("full")
    elif time_now_min == 30 and pnl_daily_30_cnt == 0 and trade_true == "yes":
        print("DAILY PnL log getting filed on half..")
        dailY_pnL_tracker("half")

def check_order_status():
    global holding_status
    global trade_status
    global filled_status
    filled_status = "unknown"

    while filled_status != "filled":
        try:
            elem_filled = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[7]")
            elem_filled_txt = elem_filled.text
            if elem_filled_txt == "":
                print("The order was not filled: ",elem_filled_txt)
                # Check if order was cancelled
                if trade_status == "c":
                    filled_status = "cancelled"
                    return filled_status
            else:
                print("The order was filled1: ",elem_filled_txt)
                filled_status = "filled"
                if trade_status == "c":
                    print("Cancelling failed - order filled")
                return filled_status
        except:
            print("Unable to check status on order")
            filled_status="failed"

def update_price_before_buy(pcps_max_ticker):
    global ticker_buy_price
    # 1. Get price now of holding ticker

    if pcps_max_ticker == ticker_1_txt:
        ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_buy_price = float(ticker_buy_price.text)
    elif pcps_max_ticker == ticker_2_txt:
        ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_buy_price = float(ticker_buy_price.text)
    elif pcps_max_ticker == ticker_3_txt:
        ticker_buy_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_buy_price = float(ticker_buy_price.text)

    ticker_buy_price = ticker_buy_price * (1 + (pcps_order_addon / 100))

    if ticker_buy_price < 1:
        ticker_buy_price = ("%.4f" % ticker_buy_price)  # 4 decimals below 1
    elif ticker_buy_price >1:
        ticker_buy_price = ("%.2f" % ticker_buy_price)  # 2 decimals above 1


    return ticker_buy_price

def update_price_before_sell(pcps_max_ticker):
    global ticker_sell_price
    # 1. Get price now of holding ticker
    if pcps_max_ticker == ticker_1_txt:
        ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_sell_price = float(ticker_sell_price.text)
    elif pcps_max_ticker == ticker_2_txt:
        ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_sell_price = float(ticker_sell_price.text)
    elif pcps_max_ticker == ticker_3_txt:
        ticker_sell_price = driver.find_element_by_xpath('/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_sell_price = float(ticker_sell_price.text)

    ticker_sell_price = ticker_sell_price * (1 - (pcps_order_addon / 100))
    if ticker_sell_price < 1:
        ticker_sell_price = ("%.4f" % ticker_sell_price)  # 4 decimals below 1
    elif ticker_sell_price >1:
        ticker_sell_price = ("%.2f" % ticker_sell_price)  # 2 decimals above 1 nordnet
    return ticker_sell_price
def find_volume(price):
    global trading_cash_usd
    vol = int(trading_cash_usd/price)
    print("calculated volum",vol)
    return vol

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

    logged_in = 1
    while logged_in == 1:
        try:
            #Click the "all" section, so failures can not present itself in the "working" tab. Have seen errors on server side
            elem_all = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[1]/div/div[5]")
            elem_all.click()
            logged_in = 0
        except:
            print("Waiting for server to login..")

def get_watchlist_tickers():
    global driver
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt
    try:
        #Get watchlist ticker no 1
        ticker_1 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[1]/div[1]/span[1]")
        ticker_1_txt = ticker_1.text

        #GET Watchlist ticker no2
        ticker_2 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[1]/div[1]/span[1]")
        ticker_2_txt = ticker_2.text

        #Get watchlist ticker no3
        ticker_3 = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[1]/div[1]/span[1]")
        ticker_3_txt = ticker_3.text
    except:
        print("Unable to fetch watchlist tickers...")
def paper_trade(ticker,type,price_initial,vol):
    global driver
    global ticker_holding_exit_point
    global ticker_holding_exit_offset
    global sample_interval
    global trade_status

    #History params
    global h_buy_price
    global h_sell_price
    global h_pcps_entry
    global h_buy_time
    global h_sell_time
    global price

    #Buy
    if type == "b":
        try:
            # input the ticker in search field
            p_ticker = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[1]/div/div[1]/input")
            p_ticker.clear()
            p_ticker.click()
            p_ticker.send_keys(Keys.BACKSPACE)
            p_ticker.send_keys(Keys.BACKSPACE)
            p_ticker.send_keys(Keys.BACKSPACE)
            p_ticker.send_keys(Keys.BACKSPACE)
            p_ticker.send_keys(Keys.BACKSPACE)
            p_ticker.send_keys(ticker)
            time.sleep(1)
            p_ticker.send_keys(Keys.RETURN)

            # Enter number of shares
            p_vol = driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div/input")
            p_vol.click()
            time.sleep(0.2)
            p_vol.send_keys(Keys.BACKSPACE)
            p_vol.send_keys(Keys.BACKSPACE)
            p_vol.send_keys(Keys.BACKSPACE)
            p_vol.send_keys(Keys.BACKSPACE)
            p_vol.send_keys(Keys.BACKSPACE)
            p_vol.send_keys(Keys.BACKSPACE)
            time.sleep(0.2)
            p_vol.send_keys(vol)

            #Enter limit price
            p_price = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div[1]/div[3]/div/div[2]/div[1]/input")
            p_price.click()
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)
            p_price.send_keys(Keys.BACKSPACE)

            #Update price before entering
            price = str(update_price_before_buy(ticker))
            p_price.click()
            p_price.send_keys(price)

            #Click buy
            p_buy = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]")
            p_buy.click()

            # click paper trade BUY button
            p_trade = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div/div[3]/button")
            p_trade.click()

            #Check if the ticker purchase was successful - and the order are placed waiting to get filled ... - if not exit and come back later
            time.sleep(2)
            p_available_ticker = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[2]")
            p_available_ticker_txt = str(p_available_ticker.text)
            p_available_qty = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[6]")
            p_available_qty_txt = str(p_available_qty.text)
            if p_available_ticker_txt in ticker and p_available_qty_txt == "0":
                print("The ticker is: ", p_available_ticker_txt)
                print("The qty is: ", p_available_qty_txt)
                print("$$ - Purchase order placed successfully!!")
            else:
                print("The ticker is: ",p_available_ticker_txt)
                print("The qty is: ",p_available_qty_txt)
                print("Error - unable to complete purchase - coming back later")
                print("Coulde be one of the following reasons")
                print("1. Ticker unavailable for purchase at this time")
                print("2. Price gap too big")
                print("3. Wrong price increment")
                return 1

            #Update history
            h_buy_price.append(price)
            h_ticker.append(ticker)

            print(datetime.datetime.now())
            print("BUYING",ticker,"at limit price",price)
            trade_status = "b"
            print("Purchase successful!!!")
            return 0
        except:
            print("Purchase not successful for some other reason!!!")
            print("Coming back later...")
            return 1

    #Sell
    elif type == "s":
        try:
            #click the 3 dots in correct possition
            p_close = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[4]/div[3]/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
            p_close.click()
            # close order button
            p_close_b = driver.find_element_by_xpath("/html/body/nav/div[1]")
            p_close_b.click()

            # enter sell price
            p_sell_price = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[3]/div[3]/div/div[2]/div[1]/input")
            p_sell_price.click()
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)

            # update sell price before entering
            price = update_price_before_sell(ticker)
            # price=price *(1-(pcps_order_addon/100))
            p_sell_price.send_keys(price)

            # click sell
            p_close_s = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
            p_close_s.click()

            #Check if price gap too big - if so, just accept.
            try:
                p_price_gap = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[3]/button[2]")
                p_price_gap.click()
                time.sleep(0.2)
                #hit the trade button
                # click paper trade BUY button
                p_trade = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[3]/button")
                p_trade.click()
                print("Confirming price gap, yes")
            except:
                print("no worreis, sell price not gapping too much")

            print(datetime.datetime.now())
            print("SELLING", ticker, "at limit price", price)
            trade_status = "s"
            return 0

        except:
           print("---Unable to sell order...")
           return 1

    #Modify buy order
    elif type == "b_m":
        try:
            #Modify buy order with current price
            p_close_m = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
            p_close_m.click()

            time.sleep(0.5)

            # Hit the modify button - do last check if order was filled or not
            p_modify_buy = driver.find_element_by_xpath("/html/body/nav/div[1]")
            p_modify_buy_txt = p_modify_buy.text
            if "Modify" in p_modify_buy_txt:
                print("Modifying OK, value of button is: ",p_modify_buy_txt)
                p_modify_buy.click()
            else:
                print("Modifying not available, value of button is: ",p_modify_buy_txt)
                print("Order already filled")
                return 0

            # Update the price
            p_buy_price = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[3]/div[2]/div/div[2]/div[1]/input")
            p_buy_price.click()
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)
            p_buy_price.send_keys(Keys.BACKSPACE)

            # update buy price before entering
            price = update_price_before_buy(ticker)
            p_buy_price.send_keys(price)

            # click paper trade
            p_close_b = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
            p_close_b.click()

            time.sleep(0.5)
            # Check if price gap too big - if so, just accept.
            try:
                p_price_gap = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[3]/button[2]")
                p_price_gap.click()
                time.sleep(0.2)

                # hit the trade button
                p_trade = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
                p_trade.click()

                print("Confirming price gap, yes")
            except:
                print("no worreis, sell price not gapping too much")

            # If order was already filled after opening the modify dialogue - close the trade dialoue window
            try:
                p_exit_dialogue = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/i")
                p_exit_dialogue.click()
                print("*** Buy order already filled - exiting")
                return 0
            except:
                print("Order updated successfully",ticker,price)
                return 0
        except:
            print("*** Unable to modify buy order ")
            return 1

    #Modify sell order
    elif type == "s_m":
        try:
            # Go on with updating the order with latest price
            p_close = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
            p_close.click()

            time.sleep(0.5)

            # Hit the modify button - do last check if order was filled or not
            p_modify_sell = driver.find_element_by_xpath("/html/body/nav/div[1]")
            p_modify_sell_txt = p_modify_sell.text
            if "Modify" in p_modify_sell_txt:
                print("Modifying OK, value of button is: ",p_modify_sell_txt)
                p_modify_sell.click()
            else:
                print("Modifying not available, value of button is: ",p_modify_sell_txt)
                print("$$Order already filled")
                return 0

            time.sleep(0.5)

            # enter sell price
            p_sell_price = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[3]/div[2]/div/div[2]/div[1]/input")
            p_sell_price.click()
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)
            p_sell_price.send_keys(Keys.BACKSPACE)

            # update sell price before entering
            price = update_price_before_sell(ticker)
            p_sell_price.send_keys(price)

            # click paper trade
            p_close_s = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
            p_close_s.click()

            time.sleep(0.5)

            # Check if price gap too big - if so, just accept.
            try:
                p_price_gap = driver.find_element_by_xpath("/html/body/div[3]/div[2]/div[3]/button[2]")
                p_price_gap.click()
                time.sleep(0.2)

                # hit the trade button
                p_trade = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
                p_trade.click()

                print("Confirming price gap, yes")
            except:
                print("no worreis, sell price not gapping too much")

            # If order was already executed after opening the modify dialogue - close the trade dialoue
            try:
                p_exit_dialogue = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[1]/i")
                p_exit_dialogue.click()
                print("---Sell order completed already- closing the dialogue")
                return 0
            except:
                print("Sell order successfully updated", ticker, price)
                return 0

        except:
            print("--- Unable to update sell order ")
            return 1

    #Cancel
    elif type == "c":
        # Cancel buy order
        try:
            # click the 3 dots in correct possition
            p_close = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
            p_close.click()

            time.sleep(0.5)

            # Hit the modify button - do last check if order was filled or not
            p_cancel_buy = driver.find_element_by_xpath("/html/body/nav/div[2]")
            p_cancel_buy_txt = p_cancel_buy.text
            if "Cancel" in p_cancel_buy_txt:
                print("Cancelleing OK, value of button is: ",p_cancel_buy_txt)
                p_cancel_buy.click()
            else:
                print("Cancel not available, value of button is: ",p_cancel_buy_txt)
                print("Order already filled")
                return 0

            time.sleep(0.3)

            # click ok in popupmenu
            p_popup = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/button[2]")
            p_popup.click()

            print("Buy order cancelled successfully")
            return 0
        except:
            print("Unable to cancel buy order")
            return 1

def log_PnL(pnl_this_trade, pnl_total, pnl_this_trade_w_fees, pnl_total_w_fees, trade_succes_cnt, pcpsMax):

    subfolder = "/home/sjefen/Dropbox/log/pcps_PnL"
    tday = str(datetime.datetime.now().date())
    time_n = datetime.datetime.now()
    l_fileName = str(subfolder) + "/" + str(tday)

    os.makedirs(subfolder, exist_ok=True)

    l_file = open(l_fileName, "a")
    l_file.write(str(time_n))
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
    l_file.write("pcps value:       ")
    l_file.write(str(pcpsMax))
    l_file.write("\n")
    l_file.write("\n")
    l_file.close()
    print("****Successfully written to log file!!")

def clear_plot_history():
    global h_trade_time_table
    global h_ticker_holding_price
    global h_trade_time_cnt
    h_trade_time_table.clear()
    h_ticker_holding_price.clear()
    h_trade_time_cnt = 0
    print("plot history cleared!!!")

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
    global file_trade_completed_status


    #Set time now minute
    time_now_min_start = time_now_min

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
                   if trade_mode == "r":
                       trade=trade_nordnet_watchlist(pcps_max_ticker,"b",ticker_buy_price,vol)
                   if trade == 1:
                       return 1
                   elif trade_mode == "p":
                       trade=paper_trade(pcps_max_ticker,"b",ticker_buy_price,vol)
                   if trade == 1:
                       return 1
                       sample_periods = 0
                       break


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
                time_now = str(datetime.datetime.now().time())
                if time_now > time_lastCall:
                    print("Trading reached EOD - exiting entry routine")
                    return 5
                try:
                    if float(ticker_1_price_value) > float(ticker1_prev_high) and float(ticker1_prev_high) != 0 and float(ticker1_prev_cp) > float(ticker1_prev_op):
                        print("Entered quality check on: ", ticker_1_txt)
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_1_price_value))
                        nordnet_functions.prefill_buy_order(str(1), str(vol))
                        time.sleep(orb_quality_check)
                        if float(ticker_1_price_value) > float(ticker1_prev_high):
                            nordnet_functions.buy(str(ticker_1_price_value), str(vol))
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
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_2_price_value))
                        nordnet_functions.prefill_buy_order(str(2), vol)
                        time.sleep(orb_quality_check)
                        ##Get volume
                        if float(ticker_2_price_value) > float(ticker2_prev_high):
                            nordnet_functions.buy(ticker_2_price_value, vol)
                            nordnet_functions.prefill_sell_order(vol)
                            nordnet_functions.open_order_status()
                            pcps_max_ticker = ticker_2_txt
                            orb_breakout_true = "yes"
                            continue
                        else:
                            print("Quality check not passed - not entering trade", ticker_2_txt)
                            nordnet_functions.enter_watchlist()
                    if float(ticker_3_price_value) > float(ticker3_prev_high) and float(ticker3_prev_high) != 0 and float(ticker3_prev_cp) > float(ticker3_prev_op):
                        print("Entered quality check on: ", ticker_3_txt)
                        #Get BUY order ready in case of quality passes
                        vol = find_volume(float(ticker_3_price_value))
                        nordnet_functions.prefill_buy_order(str(3), vol)
                        time.sleep(orb_quality_check)
                        if float(ticker_3_price_value) > float(ticker3_prev_high):
                            nordnet_functions.buy(ticker_3_price_value, vol)
                            nordnet_functions.prefill_sell_order(vol)
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
    #Check if order was filled
    if trade_status == "b":
        modify_entry_cnt = 1
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
            pass

            if filled_status != "filled":
                print("Buy cancelled - exiting the trade")
                # initialize tables and plot
                clear_plot_history()
                #Initialize trade counters.
                modify_entry_cnt = 0
                modify_entry_tries = 0
                return 1

    # Start the "Exit trade routine - if holding ticker AND bear bailout has not entered the exit"
    while holding_status == 1 and bear_bailout_status == 0:
        time.sleep(1)
        today = datetime.datetime.today().weekday()
        time_now = str(datetime.datetime.now().time())
        #1. Call the bear bailout exit if holding ticker
        if holding_status == 1 and bear_bailout_status == 0 and pcps_exit == 0 and trade_status != "s":
            bear_bailout()

        #2. Sell if price shoots below exit point and bear bailout status is 0
        if ticker_holding_price_value <= ticker_holding_exit_point and bear_bailout_status == 0:
            #Say that we exit the trade, so not conflicting with other exit strategies
            pcps_exit = 1
            ticker_sell_price = ticker_holding_price_value *(1-(pcps_order_addon/100))
            ticker_sell_price = ("%.2f" %ticker_sell_price)
            print("--Exiting trade with exit point routine")
            nordnet_functions.sell(ticker_holding_price_value)
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break

        #3. Get out before closing in case holding
        elif time_now > time_lastCallExit:
            pcps_exit = 1
            ticker_sell_price = ticker_holding_price_value *(1-(pcps_order_addon/100))
            ticker_sell_price = ("%.2f" %ticker_sell_price)
            print("Exiting trade due to market closing soon...")
            nordnet_functions.sell(ticker_holding_price_value)
            nordnet_functions.open_order_status()
            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break


    #Check if order was filled
    if trade_status == "s":
        modify_exit_cnt = 1
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
            if file_trade_completed_status == 1:
                file_trade()
            else:
                print("Skipping compliting file of trade, completed from global_trader thread")
            file_trade_completed_status = 1
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

            #Plot the trade
            plot_trade()

            print("")
            print(datetime.datetime.now())
            print("PnL this trade:        ",PnL_this_trade)
            print("PnL total:             ",PnL_total)
            print("PnL this trade w fees: ",PnL_this_trade_w_fees)
            print("PnL total w fees:      ",PnL_total_w_fees)
            print("Trade cnt:             ",trade_successful_cnt)
            print("pcps:                  ",pcps_max)
            print("")

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
            time.sleep(10)
            time_now = str(datetime.datetime.now().time())

        if time_now < time_lastCall and time_now > time_getReady:
            print("let' trade")
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

            #Initialize intraday PnL values

            #Update P&L
            PnL_this_trade = 0.0
            PnL_this_trade = 0.0
            PnL_total = 0.0
            PnL_this_trade_w_fees = 0.0
            PnL_total_w_fees = 0.0
    else:
        print("its weekend")
        trade_true = "no"
        time.sleep(3600)

    return trade_true

def trade_or_not():
    global trade_true
    trade_now = ""

    while trade_now != "yes":
        print("checking time and day now..")
        trade_now = str(check_time_day())
        time.sleep(10)


#Start trading...
if trade_mode =="r":
    trade_fail_cnt=0
    trade_successful_cnt=0
    open_webull()
    logon_webull()
    nordnet_functions.login_nordnet()
    global_trader()

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
                cleanup_if_fail_purchase()
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

else:
    nordnet_functions.login_nordnet()
    nordnet_functions.prefill_buy_order(str(1), str(vol))






