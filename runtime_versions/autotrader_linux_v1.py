#!/usr/bin/python3

import os
import time, threading
import datetime
import random
import matplotlib.pyplot as plt
import numpy as np
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = webdriver.Chrome('/usr/bin/chromedriver')
#driver2 = webdriver.Chrome('/usr/local/bin/chromedriver')

#Trade mode
#r = real money
#p = paper trade webull
#o = offline paper trade outside market american market hours.
#others: test mode - for testing new functions
trade_mode = "p"
trade_true = ""

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
trading_cash_usd = 5000.0
trade_cnt_real_max = 5
trade_cnt_max = 100
trade_cnt = 38
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

#Tickers opening price ( 1min )
ticker_1_op = 0.0
ticker_2_op = 0.0
ticker_3_op = 0.0

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
modify_entry_cnt_max=10
modify_entry_tries=0
modify_entry_tries_max=2
modify_exit_cnt=0
modify_exit_cnt_max=10

filled_status = "unknown"
price=0.0

# monitor time and day
trade_range_days = range(0, 5)
today = datetime.datetime.today().weekday()
time_now = str(datetime.datetime.now().time())
time_getReady = "15:30:00"
time_lastCall = "21:58:30"
time_lastCallExit = "21:59:00"

# P&L parameters
bought_price = 0.0
sold_price = 0.0
PnL_total = 0.0
PnL_this_trade = 0.0
PnL_this_trade_w_fees = 0.0
PnL_total_w_fees = 0.0
Trade_fee_per_trade = 5.42

cancel_cnt = 0
cancel_cnt_max = 5


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
                if trade_mode == "r":
                    trade=trade_nordnet_watchlist(pcps_max_ticker, "s", ticker_holding_price_value, vol)
                    while trade == 1:
                        trade = trade_nordnet_watchlist(pcps_max_ticker, "s", ticker_holding_price_value, vol)
                    print("Bailed out!!!")

                elif trade_mode == "p":
                    trade=paper_trade(pcps_max_ticker, "s", ticker_holding_price_value, vol)
                    while trade == 1:
                        trade = paper_trade(pcps_max_ticker, "s", ticker_holding_price_value, vol)
                    print("Bailed out!!!")

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
    if ticker_2_txt != ticker_2_prev_txt:
        print("Initializing 1 min open price of: ",ticker_2_txt," ..due to watchlist update")
        ticker_2_op = 0.0
    if ticker_3_txt != ticker_3_prev_txt:
        print("Initializing 1 min open price of: ",ticker_3_txt," ..due to watchlist update")
        ticker_3_op = 0.0
    fetch_prices()

    #If BUY order yet not filled - edit the buy order
    if modify_entry_cnt == modify_entry_cnt_max and filled_status != "filled":
        print("MODIFYING BUY ORDER")
        trade = paper_trade(pcps_max_ticker, "b_m", ticker_holding_price_value, vol)
        while trade == 1:
            trade = paper_trade(pcps_max_ticker, "b_m", ticker_holding_price_value, vol)

        if modify_entry_cnt != 0:
            modify_entry_cnt = 1
            print("Starting new entry_cnt: ",modify_entry_cnt)
        else:
            print("**BUY order already filled, no need to modify")

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
        trade = paper_trade(pcps_max_ticker, "s_m", ticker_holding_price_value, vol)
        while trade == 1:
            trade = paper_trade(pcps_max_ticker, "s_m", ticker_holding_price_value, vol)
        if modify_exit_cnt != 0:
            modify_exit_cnt=1
            print("Starting new exit_cnt: ",modify_exit_cnt)
        else:
            print("---Sell order already filled, no need to modify")


    #Get 1 min opening price of the tickers
    if time_now_sec == 0:
        #Set ticker 1 min opening prices
        ticker_1_op = float(ticker_1_price_value)
        ticker_2_op = float(ticker_2_price_value)
        ticker_3_op = float(ticker_3_price_value)
        print("1 min open: ",ticker_1_txt, ticker_1_op)
        print("1 min open: ",ticker_2_txt, ticker_2_op)
        print("1 min open: ",ticker_3_txt, ticker_3_op)



def check_order_status():
    global holding_status
    global trade_status
    global filled_status
    filled_status = "unknown"

    while filled_status != "filled":
        #Check if order was cancelled
        if trade_status == "c":
            filled_status = "cancelled"
            return filled_status
        try:
            elem_filled = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[2]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[7]")
            elem_filled_txt = elem_filled.text
            if elem_filled_txt == "":
                print("The order was not filled: ",elem_filled_txt)
            else:
                print("The order was filled1: ",elem_filled_txt)
                filled_status = "filled"
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
def login_nordnet():
    driver2.implicitly_wait(10) # seconds

    driver2.get("https://classic.nordnet.no/mux/login/startNO.html?clearEndpoint=0&intent=next")

    #Login
    elem_login_b = driver2.find_element_by_class_name("button.primary.block")
    elem_login_b.click()

    elem_bd = driver2.find_element_by_id("birthDate")
    elem_bd.clear()
    elem_bd.send_keys("120390")

    elem_ph = driver2.find_element_by_id("phone")
    elem_ph.clear()
    elem_ph.send_keys("46781037")

    elem_login_b2 = driver2.find_element_by_class_name("button.primary.block")
    elem_login_b2.click()

    time.sleep(sample_interval*2)

    # enter watchlist in nordnet
    elem_mine_sider = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/button/span/span/span")
    elem_mine_sider.click()

    # select watchlist
    elem_watchlist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/div/div/div/div[1]/div[1]/div/ul/li[5]/span/a")
    elem_watchlist.click()

    time.sleep(1.5)
def trade_nordet(ticker,type,price,vol):
    # Enter ticker in search field
    global driver2

    search_quote = '"'
    elem_ticker = driver2.find_element_by_class_name("c02259")
    elem_ticker.click()
    elem_ticker.clear()
    elem_ticker.send_keys(search_quote)
    elem_ticker.send_keys(ticker)
    time.sleep(0.8)
    elem_ticker.send_keys(Keys.ARROW_DOWN)
    elem_ticker.send_keys(Keys.RETURN)

    #wait until page loads before proceeding
    time.sleep(2)

    # buy or sell
    if type == "b":
        elem_buy = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.eIVjgI")
        elem_buy.click()
    elif type == "s":
        elem_sell = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.iXLhXW")
        elem_sell.click()

    # select dropdown account
    elem_dropd = driver2.find_element_by_css_selector("#instrument-order-accounts-select > div > div > span")
    elem_dropd.click()
    # select AF account
    elem_account = driver2.find_element_by_css_selector("#instrument-order-accounts-select-option-0 > div > div > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.faownn > div")
    elem_account.click()

    # select volume
    elem_volume = driver2.find_element_by_id("volume")
    elem_volume.clear()
    elem_volume.send_keys(vol)

    # enter price
    elem_price = driver2.find_element_by_id("price")
    elem_price.click()
    elem_price.clear()
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)
    elem_price.send_keys(Keys.BACK_SPACE)

    #update price before entering
    if type == "b":
        price = str(update_price_before_buy(ticker))
    elif type == "s":
        price = str(update_price_before_sell(ticker))
    print("the price is",price)
    elem_price.send_keys(price)

    # buy/sell button
    #elem_buy_sell = driver2.find_element_by_class_name("NormalizedButton__Button-ey7f5x-0.Button__StyledButton-lqp9m3-0.enBkkS ActionButtons__RelativeButton-sc-80k9dq-1.hktbZI")
    elem_buy_sell = driver2.find_element_by_css_selector("#main-content > div.PageWrapper__Outer-sc-1ur2ylx-0.fLylmR.PageLayoutOverview__StyledPageWrapper-dawtfj-0.dsucPW > div > div.CssGrid__StyledDiv-bu5cxy-0.iGVYku > div.CssGrid__RawCssGridItem-bu5cxy-1.sc-bdVaJa.ibCVYD > div > div > div:nth-child(1) > div > form > div.Box__StyledDiv-sc-1bfv3i9-0.GUVl > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.hEJJeD > div:nth-child(2) > button")
    elem_buy_sell.click()

    # confirmation button
    elem_conf = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div[2]/div/div[10]/div/div[2]/button")
    elem_conf.click()

    #ordren er mottatt - ok
    elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
    elem_order_ok.click()

    # open the order section to follow order execution status
    elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[2]/ul/li[1]/button/span")
    elem_order.click()
def trade_nordnet_watchlist(ticker,type,price,vol):

    if type == "b":

        if ticker == ticker_1_txt:
            # select buy on the first ticker in list
            elem_buy_1 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[1]/td[2]/div/a[1]/div/span")
            elem_buy_1.click()
        elif ticker == ticker_2_txt:
            # select 2nd ticker in watchlist
            elem_buy_2 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[2]/td[2]/div/a[1]/div/span")
            elem_buy_2.click()
        elif ticker == ticker_3_txt:
            # select 3rd ticker in watchlist
            elem_buy_3 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[3]/td[2]/div/a[1]/div/span")
            elem_buy_3.click()
        time.sleep(1)
        # select dropdown account
        elem_dropd = driver2.find_element_by_css_selector("#instrument-order-accounts-select > div > div > span")
        elem_dropd.click()

        # select AF account
        elem_account = driver2.find_element_by_css_selector("#instrument-order-accounts-select-option-0 > div > div > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.faownn > div")
        elem_account.click()

        # select volume
        elem_volume = driver2.find_element_by_id("volume")
        elem_volume.clear()
        elem_volume.send_keys(vol)

        # enter price
        elem_price = driver2.find_element_by_id("price")
        elem_price.click()
        elem_price.clear()
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)

        #update price before entering
        price = str(update_price_before_buy(ticker))

        elem_price.send_keys(price)

        time.sleep(0.5)

        # buy/sell button
        elem_buy_sell = driver2.find_element_by_css_selector("#main-content > div.PageWrapper__Outer-sc-1ur2ylx-0.fLylmR.PageLayoutOverview__StyledPageWrapper-dawtfj-0.dsucPW > div > div.CssGrid__StyledDiv-bu5cxy-0.iGVYku > div.CssGrid__RawCssGridItem-bu5cxy-1.sc-bdVaJa.ibCVYD > div > div > div:nth-child(1) > div > form > div.Box__StyledDiv-sc-1bfv3i9-0.GUVl > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.hEJJeD > div:nth-child(2) > button")
        elem_buy_sell.click()

        print("buying: ",vol,"of: ",ticker,"at price: ",price)

        # confirmation button - not needed anymore. message wont show.
        try:
            elem_conf = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div[2]/div/div[10]/div/div[2]/button")
            elem_conf.click()
        except:
            print("Confirm order not available - order already sent to exhange")

        time.sleep(2)

        try:
            #ordren er mottatt - ok
            elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
            elem_order_ok.click()
        except:
           print("Ordre mottatt - ikke tilgjengelig")



        #PREFILL the sell order except the price
        #Hit the sell button
        elem_sell = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.iXLhXW")
        elem_sell.click()

        # select dropdown account
        elem_dropd = driver2.find_element_by_css_selector("#instrument-order-accounts-select > div > div > span")
        elem_dropd.click()

        # select AF account
        elem_account = driver2.find_element_by_css_selector("#instrument-order-accounts-select-option-0 > div > div > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.faownn > div")
        elem_account.click()

        # select volume
        elem_volume = driver2.find_element_by_id("volume")
        elem_volume.clear()
        elem_volume.send_keys(vol)

        #clear price
        elem_price = driver2.find_element_by_id("price")
        elem_price.click()
        elem_price.clear()
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)

        # open the order section to follow order execution status
        elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[2]/ul/li[1]/button/span")
        elem_order.click()


    elif type == "s":
        # Check if the buy order still exists
        try:
            elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[1]")
            order_status = "active"
            print("The buy order was not completed on: ",ticker, "deleting")
        except:
            order_status = "completed"
            print("The buy order was completed, selling: ",ticker)

        if order_status == "completed":

            # enter price
            elem_price = driver2.find_element_by_id("price")
            elem_price.click()
            price = str(update_price_before_sell(ticker))
            time.sleep(0.2)
            elem_price.send_keys(price)

            time.sleep(0.2)

            # buy/sell button
            elem_buy_sell = driver2.find_element_by_css_selector("#main-content > div.PageWrapper__Outer-sc-1ur2ylx-0.fLylmR.PageLayoutOverview__StyledPageWrapper-dawtfj-0.dsucPW > div > div.CssGrid__StyledDiv-bu5cxy-0.iGVYku > div.CssGrid__RawCssGridItem-bu5cxy-1.sc-bdVaJa.ibCVYD > div > div > div:nth-child(1) > div > form > div.Box__StyledDiv-sc-1bfv3i9-0.GUVl > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.hEJJeD > div:nth-child(2) > button")
            elem_buy_sell.click()
            print("selling: ", vol, "of: ", ticker,"at price: ", price)

            time.sleep(1)

            # confirmation button - not needed anymore. message wont show.
            try:
                elem_conf = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div[2]/div/div[10]/div/div[2]/button")
                elem_conf.click()
            except:
                print("Confirm order not available - order already sent to exhange")

            time.sleep(2)

            #ordren er mottatt dialog - etter sender inn ordre
            try:
                elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
                elem_order_ok.click()
            except:
                print("Ordre mottatt - ok eksisterer ikke på salg")



            #Routine to make sure the order is sold -------------------------------------------
            # reopen the order section to follow order execution status
            elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[2]/ul/li[1]/button/span")
            elem_order.click()

            #First wait one cycle periode
            time.sleep(sell_order_timeout_udpate_price)

            # Check if the sell order still exists
            try:
                elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[1]")
                order_status = "active"
                print("the element exist")
            except:
                order_status = "completed"
                print("the element dont exist")

            #If sell order still active
            while order_status == "active":
                #update order with current price

                # click the edit symbol under order
                elem_edit = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[1]/a[1]/button")
                elem_edit.click()
                time.sleep(0.2)

                # enter price
                elem_price = driver2.find_element_by_id("price")
                elem_price.click()
                elem_price.clear()
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                elem_price.send_keys(Keys.BACK_SPACE)
                price = str(update_price_before_sell(ticker))
                elem_price.send_keys(price)

                time.sleep(0.3)

                #Hit edit/submit: try in case the order was completed after clicking the change button and before i did change it again.
                try:
                    elem_change = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/div/form/div/div[13]/div/div[2]/button")
                    elem_change.click()
                except:
                    print("Order already completed - no need to update price")
                    break

                time.sleep(1)

                # open the order section to follow order execution status
                elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[2]/ul/li[1]/button/span")
                elem_order.click()

                # ordren er mottatt dialog - etter endring av ordre - eller at ordren var delvis utført
                try:
                    elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
                    elem_order_ok.click()
                except:
                    print("No confirmation on change order needed for: ",ticker)

                '''
                #If order already completed after clicking the change button but before I hit the submit button
                try:
                    elem_order_already_done = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/div/form/div/div[1]/div/div/span/div[2]")
                    elem_order_already_done_text = elem_order_already_done.text
                    if elem_order_already_done_text == "Ordren din er gjennomført":
                        print("the order already done, not possible to change")
                        order_status = "completed"
                        break
                except:
                    print("lets go on, order still in process")
                '''

                time.sleep(sell_order_timeout_udpate_price)

                # Check if the sell order still exists
                try:
                    elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[1]")
                    order_status = "active"
                    print("the element exist")
                except:
                    order_status = "completed"
                    print("the element dont exist")
            print("success, sell order completed",ticker,"at price",price)

            # Go back to watchlist to get ready for next buy
            # enter watchlist in nordnet
            elem_mine_sider = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/button/span/span/span")
            elem_mine_sider.click()

            # select watchlist
            elem_watchlist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/div/div/div/div[1]/div[1]/div/ul/li[5]/span/a")
            elem_watchlist.click()

        #Cancel buy order if still active
        elif order_status == "active":
            #cancel buy order
            elem_cancel_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[2]/button")
            elem_cancel_order.click()

            # Go back to watchlist to get ready for next buy
            # enter watchlist in nordnet
            elem_mine_sider = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/button/span/span/span")
            elem_mine_sider.click()

            # select watchlist
            elem_watchlist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/div/div/div/div[1]/div[1]/div/ul/li[5]/span/a")
            elem_watchlist.click()
            print("buy order canceled",ticker)

def open_webull():
    global driver

    driver.implicitly_wait(10) # seconds
    driver.get("https://app.webull.com/paper")
def logon_webull():
    global driver
    #Click OK when page loads
    elem_ok = driver.find_element_by_class_name("jss198")
    time.sleep(2)
    elem_ok.click()

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

            # cancel order button
            p_close_b = driver.find_element_by_xpath("/html/body/nav/div[2]")
            p_close_b.click()

            time.sleep(0.5)

            # click ok in popupmenu
            p_popup = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/button[2]")
            p_popup.click()

            h_sell_price.append("C")

            print("Buy order cancelled successfully")
            return 0
        except:
            print("Unable to cancel buy order")
            return 1

def log_PnL(pnl_this_trade, pnl_total, pnl_this_trade_w_fees, pnl_total_w_fees, trade_succes_cnt, pcpsMax):

    subfolder = "log/pcps_PnL"
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

    #If offline mode only
    if trade_mode == "o":
        #Get init prices of tickers
        ticker_1_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_1_price_value = ticker_1_price.text
        ticker_2_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_2_price_value = ticker_2_price.text
        ticker_3_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_3_price_value = ticker_3_price.text

    # Start the "Enter trade routine"
    while holding_status == 0:
        if trade_mode == "o":
            print("getting prices in offline mode")
            #Generate random price change
            random_1f = random.uniform(-1, 1)
            random_1 = float("%.2f" %random_1f)
            random_2f = random.uniform(-0.5, 0.7)
            random_2 = float("%.2f" %random_1f)
            random_3f = random.uniform(-0.1, 0.1)
            random_3 = float("%.2f" %random_1f)

            #1. Get price of tickers now
            ticker_1_price_value = float(ticker_1_price_value) + float(random_1)
            ticker_2_price_value = float(ticker_2_price_value) + float(random_2)
            ticker_3_price_value = float(ticker_3_price_value) + float(random_3)

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

    #Check if order was filled
    if trade_status == "b":
        modify_entry_cnt = 1
        check_order_status()
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
            print("Buy cancelled - exiting the trade")
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
            if trade_mode == "r":
                trade=trade_nordnet_watchlist(pcps_max_ticker,"s",ticker_sell_price,vol)
                while trade == 1:
                    trade = trade_nordnet_watchlist(pcps_max_ticker, "s", ticker_sell_price, vol)

            elif trade_mode == "p":
                trade=paper_trade(pcps_max_ticker,"s",ticker_sell_price,vol)
                while trade == 1:
                    trade = paper_trade(pcps_max_ticker, "s", ticker_sell_price, vol)

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
            if trade_mode == "r":
                trade=trade_nordnet_watchlist(pcps_max_ticker,"s",ticker_sell_price,vol)
                while trade == 1:
                    trade = trade_nordnet_watchlist(pcps_max_ticker, "s", ticker_sell_price, vol)

            elif trade_mode == "p":
                trade=paper_trade(pcps_max_ticker,"s",ticker_sell_price,vol)
                while trade == 1:
                    trade = paper_trade(pcps_max_ticker, "s", ticker_sell_price, vol)


            #Set sample_periods to zero and break enter trade routine
            sample_periods = 0
            pcps_exit = 0
            break


    #Check if order was filled
    if trade_status == "s":
        modify_exit_cnt = 1
        filled_status = check_order_status()
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


#Start trading type of strategy
if trade_mode == "r":
    while trade_cnt <= trade_cnt_real_max:
        trade_or_not()
        if trade_cnt == 1:
            open_webull()
            logon_webull()
            login_nordnet()
            time.sleep(sample_interval)
            get_watchlist_tickers()
        pcps()
        trade_cnt+=1
        print("the trade_cnt value is", trade_cnt)
    print("Trading is over!")

elif trade_mode =="p":
    trade_fail_cnt=0
    trade_successful_cnt=0
    open_webull()
    logon_webull()
    global_trader()

    while trade_cnt <= trade_cnt_max:
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
        else:
            print("Successful trades: ", trade_successful_cnt)
            print("Trade failed, total fails: ",trade_fail_cnt)

        trade_cnt+=1
    print("Daily trade cnt reached - stopping")

elif trade_mode =="o":

    while trade_cnt <= trade_cnt_max:
        #trade_or_not()
        if trade_cnt == 1:
            open_webull()
            logon_webull()
            #login_nordnet()
            get_watchlist_tickers()
            fetch_prices()
            pcps()
        trade_cnt+=1
        print("the trade_cnt value is", trade_cnt)
    print("Trading is over today!")

    #Check when it's a new day, then initialize trade_cnt
    today = str(datetime.datetime.today().weekday())
    new_day = today
    while today == new_day:
        print("checking when it's a new trading day")
        time.sleep(3600)
        new_day = str(datetime.datetime.today().weekday())
    trade_cnt = 1

else:
    print("entering testmode")

    trade_status = "b"
    filled_status="unknown"

    ticker_holding_price_value = 10.0
    file_trade()
    ticker_holding_price_value = 11.0
    filled_status="filled"
    file_trade()
    ticker_holding_price_value = 12.0
    file_trade()
    trade_status = "s"
    filled_status="unknown"
    file_trade()
    filled_status="filled"
    file_trade()

    plot_trade()






