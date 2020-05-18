import time, threading
import datetime
import random
import matplotlib.pyplot as plt
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import imaplib
import webull_webelements_2
driver = webdriver.Chrome('/usr/bin/chromedriver')
time_now = str(datetime.datetime.now().time())

trade_status=""

def check_if_warnings():
    elem_buy=driver.find_element_by_xpath(webull_webelements_2.b_buy)
    elem_buy.click()

def refresh():
    try:
        driver.refresh()
        wait = 1
        while wait == 1:
            try:
                elem_all_section = driver.find_element_by_xpath(webull_webelements_2.e_all_section)
                elem_all_section.click()
                #Check if refresh was ok -- by checking if the xpath of the all selector is available
                try:
                    elem_all_selector = driver.find_element_by_xpath(webull_webelements_2.b_all_selector)
                    wait = 0
                except:
                    elem_markets=driver.find_element_by_xpath(webull_webelements_2.b_markets)
                    elem_markets.click()
                    time.sleep(2)
                    elem_paccount=driver.find_element_by_xpath(webull_webelements_2.b_paper_account)
                    elem_paccount.click()
                    time.sleep(2)
            except:
                print("Waiting refresh to complete...")

    except:
        print("Unable to refresh..")

def open_webull():
    global driver

    driver.implicitly_wait(10) # seconds
    driver.get("https://app.webull.com/paper")

def logon_webull():
    global driver
    #Click OK when page loads
    try:
        elem_ok = driver.find_element_by_xpath(webull_webelements_2.b_release_confirm)
        elem_ok.click()
    except:
        pass

    #Login
    elem_login = driver.find_element_by_xpath(webull_webelements_2.e_login)
    elem_login.click()

    elem_login_uname = driver.find_element_by_xpath(webull_webelements_2.e_uname)
    elem_login_uname.clear()
    elem_login_uname.click()
    elem_login_uname.send_keys("autotrader326@yahoo.com")
    elem_login_uname.send_keys(Keys.TAB)

    elem_passwd = driver.switch_to_active_element()
    elem_passwd.clear()
    elem_passwd.send_keys("Lwle171010")
    #login button
    elem_login_b = driver.find_element_by_xpath(webull_webelements_2.b_login)
    elem_login_b.click()
    time.sleep(10)
    wait=1
    while wait == 1:
        try:
            elem_all_section = driver.find_element_by_xpath(webull_webelements_2.e_all_section)
            elem_all_section.click()
            wait = 0
        except:
            print("Waiting..")


def prefill_buy_order(vol):
    try:
        elem_buy=driver.find_element_by_xpath(webull_webelements_2.b_buy)
        elem_buy.click()

        elem_vol=driver.find_element_by_xpath(webull_webelements_2.e_volume)
        elem_vol.clear()
        elem_vol.click()
        elem_vol.send_keys(Keys.BACK_SPACE)
        elem_vol.send_keys(Keys.BACK_SPACE)
        elem_vol.send_keys(Keys.BACK_SPACE)
        elem_vol.send_keys(Keys.BACK_SPACE)
        elem_vol.send_keys(Keys.BACK_SPACE)
        elem_vol.send_keys(vol)

        elem_price=driver.find_element_by_xpath(webull_webelements_2.e_price)
        elem_price.clear()
        elem_price.click()
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
        elem_price.send_keys(Keys.BACK_SPACE)
    except:
        print("UNABLE TO PREFILL BUY ORDER")
def check_price_gap():
    try:
        elem_price_gap = driver.find_element_by_xpath(webull_webelements_2.b_continue_price_gap)
        elem_price_gap.click()
        print("Continuing price gap..")
    except:
        print("No price gap, ok..")

def check_price_gap_last_vs_limit():
    try:
        elem_price_gap_last_limit = driver.find_element_by_xpath(webull_webelements_2.b_continue_price_gap_last_limit_buy)
        elem_price_gap_last_limit.click()
        print("Continuing price gap last vs limit..")
    except:
        print("No price gap last vs. limit")

def check_price_gap_last_vs_limit_sell():
    try:
        elem_price_gap_last_limit = driver.find_element_by_xpath(webull_webelements_2.b_continue_price_gap_last_limit_sell)
        elem_price_gap_last_limit.click()
        print("Continuing price gap last vs limit..")
    except:
        print("No price gap last vs. limit")

def check_price_increment_buy():
    try:
        elem_price_incr=driver.find_element_by_xpath(webull_webelements_2.b_ok_price_increment)
        elem_price_incr.click()
        print("Accepting price increment..")
        elem_ptrade=driver.find_element_by_xpath(webull_webelements_2.b_paper_trade)
        elem_ptrade.click()
    except:
        print("Price increment ok...")

def check_price_increment_sell():
    try:
        elem_price_incr=driver.find_element_by_xpath(webull_webelements_2.b_ok_price_increment)
        elem_price_incr.click()
        print("Accepting price increment..")
        elem_close_order_ptrade=driver.find_element_by_xpath(webull_webelements_2.b_close_order_paper_trade)
        elem_close_order_ptrade.click()
    except:
        print("Price increment ok...")

def check_price_increment_modify():
    try:
        elem_price_incr=driver.find_element_by_xpath(webull_webelements_2.b_ok_price_increment)
        elem_price_incr.click()
        print("Accepting price increment..")
        elem_modify_paper_trade=driver.find_element_by_xpath(webull_webelements_2.b_modify_paper_trade)
        elem_modify_paper_trade.click()
    except:
        print("Price increment ok...")

def buy(price):
    global trade_status
    try:
        elem_price=driver.find_element_by_xpath(webull_webelements_2.e_price)
        elem_price.click()
        elem_price.send_keys(price)

        elem_ptrade=driver.find_element_by_xpath(webull_webelements_2.b_paper_trade)
        elem_ptrade.click()

        #Check if any warnings first...
        try:
            time.sleep(5)
            check_if_warnings()
        except:
            check_price_increment_buy()
            check_price_gap_last_vs_limit()

        trade_status ="b"
        return trade_status
    except:
        trade_status="fail"
        return trade_status
        print("UNABLE TO BUY:.")

def prefill_sell_order(vol):
    try:
        elem_pos_sel = driver.find_element_by_xpath(webull_webelements_2.b_possition_seleector)
        elem_pos_sel.click()

        elem_close_order = driver.find_element_by_xpath(webull_webelements_2.e_close_order)
        elem_close_order.click()

        elem_close_order_vol=driver.find_element_by_xpath(webull_webelements_2.e_close_order_vol)
        elem_close_order_vol.clear()
        elem_close_order_vol.click()
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(Keys.BACK_SPACE)
        elem_close_order_vol.send_keys(vol)

        elem_close_order_price=driver.find_element_by_xpath(webull_webelements_2.e_close_order_price)
        elem_close_order_price.clear()
        elem_close_order_price.click()
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
        elem_close_order_price.send_keys(Keys.BACK_SPACE)
    except:
        print("UNABLE TO PREFILL SELL ORDER")


def sell(price):
    global trade_status
    try:
        elem_close_order_price=driver.find_element_by_xpath(webull_webelements_2.e_close_order_price)
        elem_close_order_price.click()
        elem_close_order_price.send_keys(price)

        elem_close_order_ptrade=driver.find_element_by_xpath(webull_webelements_2.b_close_order_paper_trade)
        elem_close_order_ptrade.click()
        #Check if any warnings first...
        try:
            time.sleep(5)
            check_if_warnings()
        except:
            check_price_increment_sell()
            check_price_gap_last_vs_limit_sell()

        trade_status ="s"
        return trade_status
    except:
        trade_status="fail"
        print("UNABLE TO SELL..")

def check_filled_status(timer_global_trader_interval):
    filled_status="unknown"
    while filled_status != "filled":
        try:
            elem_filled = driver.find_element_by_xpath(webull_webelements_2.e_filled_time)
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
            print("UNABLE TO CHECK FILLED STATUS")
        time.sleep(timer_global_trader_interval)

def cancel_buy_order():
    global trade_status
    try:
        elem_all_selector = driver.find_element_by_xpath(webull_webelements_2.b_all_selector)
        elem_all_selector.click()

        elem_cancel=driver.find_element_by_xpath(webull_webelements_2.e_cancel)
        elem_cancel.click()

        elem_cancel_confirm=driver.find_element_by_xpath(webull_webelements_2.b_cancel_confirm)
        elem_cancel_confirm.click()
        trade_status = "c"
        return trade_status
    except:
        print("UNABLE TO CANCEL ORDER")

def modify_sell_order(price):
    modify_status="unknown"
    try:
        elem_all_selector = driver.find_element_by_xpath(webull_webelements_2.b_all_selector)
        elem_all_selector.click()

        elem_modify=driver.find_element_by_xpath(webull_webelements_2.e_modify)
        elem_modify_txt = elem_modify.text
        if elem_modify_txt != "Modify…":
            print("already filled...exiting...not modifying")
            elem_all_selector.click()
            modify_status="success"
            return modify_status
        else:
            elem_modify.click()

        elem_modify_price=driver.find_element_by_xpath(webull_webelements_2.e_modify_price)
        elem_modify_price.clear()
        elem_modify_price.click()
        elem_modify_price.send_keys(Keys.BACK_SPACE)
        elem_modify_price.send_keys(Keys.BACK_SPACE)
        elem_modify_price.send_keys(Keys.BACK_SPACE)
        elem_modify_price.send_keys(Keys.BACK_SPACE)
        elem_modify_price.send_keys(Keys.BACK_SPACE)
        elem_modify_price.send_keys(Keys.BACK_SPACE)

        elem_modify_price.send_keys(price)

        elem_modify_paper_trade=driver.find_element_by_xpath(webull_webelements_2.b_modify_paper_trade)
        elem_modify_paper_trade.click()

        #Check if any warnings first...
        try:
            time.sleep(5)
            check_if_warnings()
        except:
            check_price_increment_modify()
            check_price_gap_last_vs_limit_sell()
        
        #Check if the order already was filled..
        try:
            time.sleep(2)
            elem_close_dialogue=driver.find_element_by_xpath(webull_webelements_2.b_modify_close_dialogue)
            elem_close_dialogue.click()
            print("Unable to modify, order already sold")
        except:
            print("Modify order success!!!")
        modify_status="success"
        return modify_status
    except:
        print("UNABLE TO MODIFY ORDER")
        modify_status="fail"
        return modify_status


def watch_ticker_1_quality_check_paper():
    try:
        elem_watch_t1 = driver.find_element_by_xpath(webull_webelements_2.e_ticker_1_lst)
        elem_watch_t1.click()
        print("WATCHING  TICKER 1")
    except:
        print("Unable to watch ticker 1 on webull")

def watch_ticker_2_quality_check_paper():
    try:
        elem_watch_t2 = driver.find_element_by_xpath(webull_webelements_2.e_ticker_2_lst)
        elem_watch_t2.click()
        print("WATCHING  TICKER 2")
    except:
        print("Unable to watch ticker 2 on webull")

def watch_ticker_3_quality_check_paper():
    try:
        elem_watch_t3 = driver.find_element_by_xpath(webull_webelements_2.e_ticker_3_lst)
        elem_watch_t3.click()
        print("WATCHING  TICKER 3")
    except:
        print("Unable to watch ticker 3 on webull")



