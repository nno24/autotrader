import socket
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
import nordnet_webelements
import autotrader_linux
import test_include

driver2 = webdriver.Chrome('/usr/bin/chromedriver')
time_now = str(datetime.datetime.now().time())

#Trade parameters
price=""
ticker=""
trading_cash_usd=2206
sell_order_timeout_udpate_price=15
trade_state="READY"


def check_order_status():
 filled_status ="unknown"
 while filled_status != "filled":
  try:
   elem_order_exist = driver2.find_element_by_xpath(nordnet_webelements.e_order_exist)
   time_now = str(datetime.datetime.now().time())
   print("Buy order not filled...", time_now)
  except:
   if autotrader_linux.trade_status == "c":
    print("BUY ORDER CANCELLED - NOT FILLED")
    filled_status = "cancelled"
    return filled_status
   else:
    time_now = str(datetime.datetime.now().time())
    print("Buy order FILLED: ", time_now)
    filled_status = "filled"
    return filled_status

def enter_watchlist():
 try:
  # enter watchlist in nordnet
  elem_mine_sider = driver2.find_element_by_xpath(nordnet_webelements.e_mine_sider_1)
  elem_mine_sider.click()

  # select watchlist
  elem_watchlist = driver2.find_element_by_xpath(nordnet_webelements.e_watchlist_1)
  elem_watchlist.click()
  return 0
 except:
  print("UNABLE TO ENTER WATCHLIST")
  return 1

def prefill_buy_order(ticker, vol):
 try:
  if ticker == "1":
   # select buy on the first ticker in list
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 1", time_now)
   elem_buy_1 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_1)
   elem_buy_1.click()
  elif ticker == "2":
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 2", time_now)
   # select 2nd ticker in watchlist
   elem_buy_2 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_2)
   elem_buy_2.click()
  elif ticker == "3":
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 3", time_now)
   # select 3rd ticker in watchlist
   elem_buy_3 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_3)
   elem_buy_3.click()
  time.sleep(1)
  # select dropdown account
  elem_dropd = driver2.find_element_by_css_selector(nordnet_webelements.e_select_account_dropdown_css)
  elem_dropd.click()

  # select AF account
  elem_account = driver2.find_element_by_xpath(nordnet_webelements.e_select_af_account)
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
  return 0
 except:
  print("UNABLE TO PREFILL BUY ORDER")
  return 1

def buy(price, vol):
 try:
  elem_price = driver2.find_element_by_id("price")
  elem_price.click()
  elem_price.send_keys(price)
  #time.sleep(0.5)
  # buy/sell button
  elem_buy_sell = driver2.find_element_by_xpath(nordnet_webelements.b_buy_sell_order)
  elem_buy_sell.click()

  time_now = str(datetime.datetime.now().time())
  print("buying: ", vol, "of: ", ticker, "at price: ", price, time_now)
  time.sleep(1)

  # ordren er mottatt - ok
  elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
  elem_order_ok.click()
  time_now = str(datetime.datetime.now().time())
  print("Ordre mottatt - ikke tilgjengelig", time_now)
  autotrader_linux.trade_status = "b"
  return 0
 except:
  print("UNABLE TO COMPLETE PURCHASE")
  return 1

def sell(price):
 try:
  # enter price
  elem_price = driver2.find_element_by_id("price")
  elem_price.click()
  time.sleep(0.2)
  elem_price.send_keys(price)

  time.sleep(0.2)

  # buy/sell button
  elem_buy_sell = driver2.find_element_by_xpath(nordnet_webelements.b_buy_sell_order)
  elem_buy_sell.click()
  time_now = str(datetime.datetime.now().time())
  print("selling:", price, time_now)

  time.sleep(1)

  # Ordren er mottatt dialog - etter sender inn ordre
  elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
  elem_order_ok.click()
  time_now = str(datetime.datetime.now().time())
  print("Ordre mottatt - OK", time_now)
  autotrader_linux.trade_status="s"
  return 0
 except:
  print("UNABLE TO COMPLETE SELL ORDER")
  return 1

def modify_sell_order(price):
 try:
  # click the edit symbol under order
  elem_edit = driver2.find_element_by_xpath(nordnet_webelements.b_modify_order_1)
  elem_edit.click()
  time.sleep(1)
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

  elem_price.send_keys(price)

  time.sleep(0.3)

  # Hit edit/submit: try in case the order was completed after clicking the change button and before i did change it again.
  elem_change = driver2.find_element_by_xpath(nordnet_webelements.b_modify_confirm)
  elem_change.click()
  time_now = str(datetime.datetime.now().time())
  print("Order already completed - no need to update price", time_now)

  time.sleep(1)

  elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
  elem_order_ok.click()
  time_now = str(datetime.datetime.now().time())
  print("Ordre mottatt - ikke tilgjengelig", time_now)
  return 0
 except:
  print("**** UNABLE TO MODIFY SELL ORDER *****")
  return 1

def prefill_sell_order(vol):
 try:
  # Hit the sell button
  elem_sell = driver2.find_element_by_xpath(nordnet_webelements.b_sell)
  elem_sell.click()

  # select dropdown account
  elem_dropd = driver2.find_element_by_css_selector(nordnet_webelements.e_select_account_dropdown_css)
  elem_dropd.click()

  # select AF account
  elem_account = driver2.find_element_by_xpath(nordnet_webelements.e_select_af_account)
  elem_account.click()

  # select volume
  elem_volume = driver2.find_element_by_id("volume")
  elem_volume.clear()
  elem_volume.send_keys(vol)

  # clear price
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
  return 0
 except:
  print("UNABLE TO PREFILL SELL ORDER")
  return 1


def cancel_order():
 try:
  # cancel buy order
  elem_cancel_order = driver2.find_element_by_xpath(nordnet_webelements.b_cancel_order_1)
  elem_cancel_order.click()
  return 0
 except:
  print("UNABLE TO CANCEL ORDER")
  return 1

def open_order_status():
 try:
  # open the order section to follow order execution status
  elem_order = driver2.find_element_by_xpath(nordnet_webelements.e_status_order_1)
  elem_order.click()
  return 0
 except:
  print("UNABLE TO OPEN ORDER STATUS")
  return 1


def login_nordnet():
 try:
  driver2.implicitly_wait(10)  # seconds

  driver2.get("https://classic.nordnet.no/mux/login/startNO.html?clearEndpoint=0&intent=next")

  # Login
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

  time.sleep(25)

  enter_watchlist()
  time.sleep(1.5)

  #select OK to cockies warning
  elem_cockie = driver2.find_element_by_xpath(nordnet_webelements.b_cookie_warn)
  elem_cockie.click()
  return 0
 except:
  print("UNABLE TO LOGIN TO NORDNET")
  return 1

def trade_nordnet_watchlist(ticker, type, price, vol):
 global time_now

 if type == "b":
  try:
   if ticker == "1":
    # select buy on the first ticker in list
    time_now = str(datetime.datetime.now().time())
    print("buying ticker 1", time_now)
    elem_buy_1 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_1)
    elem_buy_1.click()
   elif ticker == "2":
    time_now = str(datetime.datetime.now().time())
    print("buying ticker 2", time_now)
    # select 2nd ticker in watchlist
    elem_buy_2 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_2)
    elem_buy_2.click()
   elif ticker == "3":
    time_now = str(datetime.datetime.now().time())
    print("buying ticker 3", time_now)
    # select 3rd ticker in watchlist
    elem_buy_3 = driver2.find_element_by_xpath(nordnet_webelements.b_buy_ticker_3)
    elem_buy_3.click()
   time.sleep(1)
   # select dropdown account
   elem_dropd = driver2.find_element_by_css_selector(nordnet_webelements.e_select_account_dropdown_css)
   elem_dropd.click()

   # select AF account
   elem_account = driver2.find_element_by_xpath(nordnet_webelements.e_select_af_account)
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

   elem_price.send_keys(price)

   time.sleep(0.5)

   # buy/sell button
   elem_buy_sell = driver2.find_element_by_xpath(nordnet_webelements.b_buy_sell_order)
   elem_buy_sell.click()

   time_now = str(datetime.datetime.now().time())
   print("buying: ", vol, "of: ", ticker, "at price: ", price, time_now)
   time.sleep(1)

   # ordren er mottatt - ok
   elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
   elem_order_ok.click()
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ikke tilgjengelig", time_now)

   # PREFILL the sell order except the price
   # Hit the sell button
   elem_sell = driver2.find_element_by_xpath(nordnet_webelements.b_sell)
   elem_sell.click()

   # select dropdown account
   elem_dropd = driver2.find_element_by_css_selector(nordnet_webelements.e_select_account_dropdown_css)
   elem_dropd.click()

   # select AF account
   elem_account = driver2.find_element_by_xpath(nordnet_webelements.e_select_af_account)
   elem_account.click()

   # select volume
   elem_volume = driver2.find_element_by_id("volume")
   elem_volume.clear()
   elem_volume.send_keys(vol)

   # clear price
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
   elem_order = driver2.find_element_by_xpath(nordnet_webelements.e_status_order_1)
   elem_order.click()
   return 0
  except:
   print("UNABLE TO COMPLETE BUY ORDER -- OR PREFILL THE SELL ORDER")
   return 1
 elif type == "s":
  try:
   # enter price
   elem_price = driver2.find_element_by_id("price")
   elem_price.click()
   time.sleep(0.2)
   elem_price.send_keys(price)

   time.sleep(0.2)

   # buy/sell button
   elem_buy_sell = driver2.find_element_by_xpath(nordnet_webelements.b_buy_sell_order)
   elem_buy_sell.click()
   time_now = str(datetime.datetime.now().time())
   print("selling: ", vol, "of: ", ticker, "at price: ", price, time_now)

   time.sleep(1)

   # ordren er mottatt dialog - etter sender inn ordre
   elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
   elem_order_ok.click()
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ok eksisterer ikke på salg", time_now)

   # reopen the order section to follow order execution status
   elem_order = driver2.find_element_by_xpath(nordnet_webelements.e_status_order_1)
   elem_order.click()
   return 0
  except:
   print("UNABLE TO COMPLETE SELL")
   return 1

  time_now = str(datetime.datetime.now().time())
 elif type == "m":
  try:
   # click the edit symbol under order
   elem_edit = driver2.find_element_by_xpath(nordnet_webelements.b_modify_order_1)
   elem_edit.click()
   time.sleep(1)
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

   elem_price.send_keys(price)

   time.sleep(0.3)

   # Hit edit/submit: try in case the order was completed after clicking the change button and before i did change it again.
   elem_change = driver2.find_element_by_xpath(nordnet_webelements.b_modify_confirm)
   elem_change.click()
   time_now = str(datetime.datetime.now().time())
   print("Order already completed - no need to update price", time_now)

   time.sleep(1)

   elem_order_ok = driver2.find_element_by_xpath(nordnet_webelements.b_ordre_mottatt)
   elem_order_ok.click()
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ikke tilgjengelig", time_now)

   # open the order section to follow order execution status
   elem_order = driver2.find_element_by_xpath(nordnet_webelements.e_status_order_1)
   elem_order.click()
   return 0
  except:
   print("**** UNABLE TO MODIFY SELL ORDER *****")
   return 1

 elif type == "c":
  #CANCEL buy order
  cancel_order()
  enter_watchlist()
  print("buy order canceled", ticker, time_now)


def find_volume(price):
 global time_now
 vol = int(trading_cash_usd / price)
 time_now = str(datetime.datetime.now().time())
 print("calculated volum", vol, time_now)
 return vol

