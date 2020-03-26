#!/usr/bin/python3

import time
import datetime
import random
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

offline_mode = 0
#Strategy pcps params
oneminute_buysignal = 9.0 #if a one minute bullish candle are bigger than "oneminute_buysignal"%
sample_interval = 8
sample_periods = 0
order_delay = 8 #assuming delay due to filing of order.This will be used to adjust limit price up or down depending on buy or sell.
pcps_threshold = ((oneminute_buysignal/60)*sample_interval)   #price change per second times sample interval
pcps_threshold_s = -(pcps_threshold/3)
pcps_order_addon = ((oneminute_buysignal/60)*order_delay)
ticker_1_pcps = 0.0
ticker_2_pcps = 0.0
ticker_3_pcps = 0.0

#Daily trade parameters
trade_cnt_max = 100
trade_cnt = 0

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

holding_status = 0.0
ticker_holding_price = ""
ticker_holding_price_value = 0.0
ticker_holding_price_value_previous = 0.0
ticker_holding_pcps = 0.0



def open_website():
    global driver

    driver.implicitly_wait(10) # seconds
    driver.get("https://app.webull.com/paper")
def logon_routine():
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

    time.sleep(2)
def get_watchlist_tickers():
    global driver
    global ticker_1_txt
    global ticker_2_txt
    global ticker_3_txt

    #Get watchlist ticker no 1
    ticker_1 = driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[1]/div[1]/span[1]")
    ticker_1_txt = ticker_1.text
    print(ticker_1_txt)

    #GET Watchlist ticker no2
    ticker_2 = driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[1]/div[1]/span[1]")
    ticker_2_txt = ticker_2.text
    print(ticker_2_txt)

    #Get watchlist ticker no3
    ticker_3 = driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[1]/div[1]/span[1]")
    ticker_3_txt = ticker_3.text
    print(ticker_3_txt)
def paper_trade(ticker,type,price):
    global driver

    #Buy or sell
    if type == "b":
        # input the ticker in search field
        p_ticker = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[1]/div/div[1]/input")
        time.sleep(1)
        p_ticker.clear()
        p_ticker.send_keys(ticker)
        time.sleep(1)
        p_ticker.send_keys(Keys.RETURN)

        # Enter number of shares
        p_vol = driver.find_element_by_xpath(
            "/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div/input")
        p_vol.click()
        p_vol_500 = driver.find_element_by_xpath("/html/body/div[2]/div/div[4]")
        p_vol_500.click()

        #Enter limit price
        p_price = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[3]/div/div[2]/div[1]/input")
        p_price.click()
        time.sleep(0.1)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)
        p_price.send_keys(Keys.BACKSPACE)

        time.sleep(0.1)
        p_price.send_keys(price)

        time.sleep(0.3)
        #Click buy
        p_buy = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]")
        p_buy.click()

        # click paper trade BUY button
        p_trade = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[3]/button")
        p_trade.click()

        print(datetime.datetime.now())
        print("BUYING",ticker,"at limit price",price)

    elif type == "s":
        #click the 3 dots in correct possition
        p_close = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[7]/div[3]/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
        p_close.click()

        #close order button
        p_close_b = driver.find_element_by_xpath("/html/body/nav/div[1]")
        p_close_b.click()

        #enter sell price
        p_sell_price = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[3]/div[3]/div/div[2]/div[1]/input")
        p_sell_price.click()
        time.sleep(0.1)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        p_sell_price.send_keys(Keys.BACKSPACE)
        time.sleep(0.1)
        p_sell_price.send_keys(price)

        time.sleep(0.3)
        #click sell
        p_close_s = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[1]/div/div[5]/button")
        p_close_s.click()

        print(datetime.datetime.now())
        print("SELLING",ticker,"at limit price",price)

def paper_trade_offline(ticker,type,price):
    global driver

    #Buy or sell
    if type == "b":
        # input the ticker in search field
        p_ticker = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[1]/div/div[1]/input")
        time.sleep(1)
        p_ticker.clear()
        p_ticker.send_keys(ticker)
        time.sleep(1)
        p_ticker.send_keys(Keys.RETURN)

        # Enter number of shares
        p_vol = driver.find_element_by_xpath(
            "/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[2]/div[2]/div[2]/div/input")
        p_vol.click()
        p_vol_500 = driver.find_element_by_xpath("/html/body/div[2]/div/div[4]")
        p_vol_500.click()

        #Enter limit price
        #p_price = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[3]/div/div[2]/div[1]/input")
        #p_price.clear()

        #p_price.send_keys(price)

        #Click buy
        p_buy = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[1]/div[1]/div[2]/div[1]")
        p_buy.click()

        # click paper trade BUY button
        p_trade = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[6]/div[3]/div/div/div[3]/button")
        p_trade.click()

        print(datetime.datetime.now())
        print("BUYING",ticker,"at limit price",price)

    elif type == "s":
        #Just cancel order in webull - not possible to close order outside of market opening hours
        #click the 3 dots in correct possition
        p_close = driver.find_element_by_xpath("/html/body/div/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[5]/div[3]/div/div/div/div/div[1]/table/tbody/tr[1]/td[1]")
        p_close.click()

        #cancel order button
        p_close_b = driver.find_element_by_xpath("/html/body/nav/div[2]")
        p_close_b.click()

        #click ok in popupmenu
        p_popup = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/button[2]")
        p_popup.click()


        print(datetime.datetime.now())
        print("SELLING",ticker,"at limit price",price)

def trade():
    global trade_cnt_max
    global trade_cnt

    while trade_cnt <= trade_cnt_max:
        pcps()
        trade_cnt+=1
        print("the trade_cnt value is", trade_cnt)
    print("Trading is over!")

def pcps():
    global driver
    global pcps_threshold
    global pcps_threshold_s
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


    # Start the "Enter trade routine"
    while holding_status == 0:
        #1. Get price of tickers now
        ticker_1_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
        ticker_1_price_value = ticker_1_price.text
        ticker_2_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
        ticker_2_price_value = ticker_2_price.text
        ticker_3_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
        ticker_3_price_value = ticker_3_price.text

        dictionary_price ={ticker_1_txt:ticker_1_price_value,ticker_2_txt:ticker_2_price_value,ticker_3_txt:ticker_3_price_value}

        #2. Wait "sample_interval" seconds
        time.sleep(sample_interval)

        #3.1 Get pcps between price now and previous price and find the ticker with best pcps.
        if sample_periods != 0:
            ticker_1_pcps = (float(ticker_1_price_value)/float(ticker_1_price_value_previous) -1)*100
            ticker_2_pcps = (float(ticker_2_price_value)/float(ticker_2_price_value_previous) -1)*100
            ticker_3_pcps = (float(ticker_3_price_value)/float(ticker_3_price_value_previous) -1)*100

            #Print: ticker, price, pcps of each ticker
            print(datetime.datetime.now())
            print(ticker_1_txt, ticker_1_price_value, ticker_1_pcps)
            print(ticker_2_txt, ticker_2_price_value, ticker_2_pcps)
            print(ticker_3_txt, ticker_3_price_value, ticker_3_pcps)

            dictionary_pcps = {ticker_1_pcps:ticker_1_txt,ticker_2_pcps:ticker_2_txt,ticker_3_pcps:ticker_3_txt}
            pcps_max = max(dictionary_pcps)
            pcps_max_ticker = dictionary_pcps.get(max(dictionary_pcps))
            print("The ticker with highest pcps is: ",pcps_max_ticker, pcps_max)
            print("")

            #3.2 Buy if pcps on best ticker is greater than pcps_threshold
            if pcps_max >= pcps_threshold:
                ticker_price = float(dictionary_price[pcps_max_ticker])
                ticker_buy_price = ticker_price * (1 + (pcps_order_addon / 100))
                ticker_buy_price = ("%.2f" %ticker_buy_price) #only 3 decimals
                paper_trade(pcps_max_ticker,"b",ticker_buy_price)
                #Update holding status, set sample_periods to zero and break enter trade routine
                holding_status = 1
                sample_periods = 0
                #Wait to start exit routine for order to come through
                time.sleep(sample_interval)
                break


        #4. File previous price.
        ticker_1_price_value_previous = ticker_1_price_value
        ticker_2_price_value_previous = ticker_2_price_value
        ticker_3_price_value_previous = ticker_3_price_value

        sample_periods+=1

    # Start the "Exit trade routine"
    while holding_status == 1:
        #1. Get price now of holding ticker
        if pcps_max_ticker == ticker_1_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[1]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_2_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[2]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)
        elif pcps_max_ticker == ticker_3_txt:
            ticker_holding_price = driver.find_element_by_xpath('/html/body/div[1]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/div[3]/div[3]/div/div[2]/div/div[2]/div/li[3]/div[2]/div[2]/div[1]')
            ticker_holding_price_value = float(ticker_holding_price.text)

        #2. Wait "sample_interval" seconds
        time.sleep(sample_interval)

        if sample_periods != 0:
            ticker_holding_pcps = (float(ticker_holding_price_value)/float(ticker_holding_price_value_previous) -1)*100
            print(datetime.datetime.now())
            print(pcps_max_ticker, ticker_holding_price_value, ticker_holding_pcps)

            #3. Sell if pcps shoots below pcps sell_threshold
            if ticker_holding_pcps < pcps_threshold_s:
                ticker_sell_price = ticker_holding_price_value *(1-(pcps_order_addon/100))
                ticker_sell_price = ("%.2f" %ticker_sell_price) #only 3 decimals
                paper_trade(pcps_max_ticker,"s",ticker_sell_price)
                #Update holding status, set sample_periods to zero and break enter trade routine
                holding_status = 0
                sample_periods = 0
                break


        #4. File previous price.
        ticker_holding_price_value_previous = ticker_holding_price_value

        sample_periods+=1
    print("Completed pcps trade on",pcps_max_ticker)


def pcps_offline():
    global driver
    global pcps_threshold
    global pcps_threshold_s
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

   #Set init price values
    ticker_1_price_value= float(10.93)
    ticker_2_price_value = float(10.93)
    ticker_3_price_value = float(10.93)


    # Start the "Enter trade routine"
    while holding_status == 0:

        #Generate random price change
        random_1f = random.uniform(-0.1, 0.1)
        random_1 = float("%.2f" %random_1f)
        random_2f = random.uniform(-0.1, 0.1)
        random_2 = float("%.2f" %random_1f)
        random_3f = random.uniform(-0.1, 0.1)
        random_3 = float("%.2f" %random_1f)

        #1. Get price of tickers now
        ticker_1_price_value = ticker_1_price_value + random_1
        ticker_2_price_value = ticker_2_price_value + random_2
        ticker_3_price_value = ticker_3_price_value + random_3

        dictionary_price ={ticker_1_txt:ticker_1_price_value,ticker_2_txt:ticker_2_price_value,ticker_3_txt:ticker_3_price_value}

        #2. Wait "sample_interval" seconds
        time.sleep(sample_interval)

        #3.1 Get pcps between price now and previous price and find the ticker with best pcps.
        if sample_periods != 0:
            ticker_1_pcps = (float(ticker_1_price_value)/float(ticker_1_price_value_previous) -1)*100
            ticker_2_pcps = (float(ticker_2_price_value)/float(ticker_2_price_value_previous) -1)*100
            ticker_3_pcps = (float(ticker_3_price_value)/float(ticker_3_price_value_previous) -1)*100

            #Print: ticker, price, pcps of each ticker
            print(datetime.datetime.now())
            print(ticker_1_txt, ticker_1_price_value, ticker_1_pcps)
            print(ticker_2_txt, ticker_2_price_value, ticker_2_pcps)
            print(ticker_3_txt, ticker_3_price_value, ticker_3_pcps)

            dictionary_pcps = {ticker_1_pcps:ticker_1_txt,ticker_2_pcps:ticker_2_txt,ticker_3_pcps:ticker_3_txt}
            pcps_max = max(dictionary_pcps)
            pcps_max_ticker = dictionary_pcps.get(max(dictionary_pcps))
            print("The ticker with highest pcps is: ",pcps_max_ticker, pcps_max)
            print("")

            #3.2 Buy if pcps on best ticker is greater than pcps_threshold
            if pcps_max >= pcps_threshold:
                ticker_price = dictionary_price[pcps_max_ticker]
                ticker_buy_price = ticker_price * (1 + (pcps_order_addon / 100))
                ticker_buy_price = ("%.2f" %ticker_buy_price) #only 2 decimals
                paper_trade_offline(pcps_max_ticker,"b",ticker_buy_price)
                #Update holding status, set sample_periods to zero and break enter trade routine
                ticker_holding_price_value = ticker_buy_price
                holding_status = 1
                sample_periods = 0
                break


        #4. File previous price.
        ticker_1_price_value_previous = ticker_1_price_value
        ticker_2_price_value_previous = ticker_2_price_value
        ticker_3_price_value_previous = ticker_3_price_value

        sample_periods+=1

    # Start the "Exit trade routine"
    while holding_status == 1:
        #1. Get price now of holding ticker
        # Generate random price change
        random_1f = random.uniform(-0.1, 0.1)
        random_1 = float("%.2f" % random_1f)
        ticker_holding_price_value = float(ticker_holding_price_value) + random_1
        #2. Wait "sample_interval" seconds
        time.sleep(sample_interval)

        if sample_periods != 0:
            ticker_holding_pcps = (float(ticker_holding_price_value)/float(ticker_holding_price_value_previous) -1)*100
            print(datetime.datetime.now())
            print(pcps_max_ticker, ticker_holding_price_value, ticker_holding_pcps)

            #3. Sell if pcps shoots below pcps sell_threshold
            if ticker_holding_pcps < pcps_threshold_s:
                ticker_sell_price = ticker_holding_price_value *(1-(pcps_order_addon/100))
                ticker_sell_price = ("%.2f" %ticker_sell_price) #only 2 decimals
                paper_trade_offline(pcps_max_ticker,"s",ticker_sell_price)
                #Update holding status, set sample_periods to zero and break enter trade routine
                holding_status = 0
                sample_periods = 0
                break


        #4. File previous price.
        ticker_holding_price_value_previous = ticker_holding_price_value

        sample_periods+=1
    print("Completed pcps trade on",pcps_max_ticker)

#New functions
def find_volume():
    total_cash = 650
    cash_to_use = 600


#START program routine
open_website()
logon_routine()
get_watchlist_tickers()

#Start trading type of strategy
if offline_mode == 1:
    trade(pcps_offline())
else:
    trade()






