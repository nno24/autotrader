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


driver2 = webdriver.Chrome('/usr/local/bin/chromedriver')
time_now = str(datetime.datetime.now().time())

#Network specifics agains client.
TCP_IP = '127.0.0.1'
TCP_PORT = 5105
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)


#Trade parameters
price=""
ticker=""
trading_cash_usd=2206
sell_order_timeout_udpate_price=15
trade_state="READY"

def check_buy_order_status():
 global trade_state

 try:
  elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[3]")
  time_now = str(datetime.datetime.now().time())
  print("Buy order not filled...", time_now)
  return 1
 except:
  time_now = str(datetime.datetime.now().time())
  print("Buy order FILLED: ", time_now)
  trade_state = "HOLDING"
  return 0

def check_sell_order_status():
 global trade_state

 try:
  #elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[3]")
  elem_order_exist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[1]/div/div/span[1]")
  time_now = str(datetime.datetime.now().time())
  print("Sell order not filled...", time_now)
  return 1
 except:
  time_now = str(datetime.datetime.now().time())
  print("Sell order FILLED: ", time_now)
  # Go back to watchlist to get ready for next buy
  enter_watchlist()
  time_now = str(datetime.datetime.now().time())
  trade_state = "READY"
  return 0

def enter_watchlist():
 # enter watchlist in nordnet
 #elem_mine_sider = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/button/span/span/span")
 elem_mine_sider = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/button/span/span/span")
 elem_mine_sider.click()

 # select watchlist
 #elem_watchlist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/div/div/div/div[1]/div[1]/div/ul/li[5]/span/a")
 elem_watchlist = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[2]/div/div/div/div[1]/div/nav/ul/li[1]/div/div/div/div[1]/div[1]/div/ul/li[5]/span/a")
 elem_watchlist.click()

def cancel_order():
 # cancel buy order
 # elem_cancel_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[2]/button")
 # elem_cancel_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[2]/button")
 elem_cancel_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[2]/button")
 elem_cancel_order.click()


def login_nordnet():
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
 elem_cockie = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div/div/div/div/div[3]/div/button")
 elem_cockie.click()

def trade_nordnet_watchlist(ticker, type, price, vol):
 global time_now

 if type == "b":

  if ticker == "1":
   # select buy on the first ticker in list
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 1", time_now)
   elem_buy_1 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[1]/td[1]/div/a[1]/div/span")
   elem_buy_1.click()
  elif ticker == "2":
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 2", time_now)
   # select 2nd ticker in watchlist
   elem_buy_2 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[2]/td[1]/div/a[1]/div/span")
   elem_buy_2.click()
  elif ticker == "3":
   time_now = str(datetime.datetime.now().time())
   print("buying ticker 3", time_now)
   # select 3rd ticker in watchlist
   elem_buy_3 = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div/div[2]/div/div/div/div[2]/div/section/div/div/div[2]/div/div/table/tbody/tr[3]/td[1]/div/a[1]/div/span")
   elem_buy_3.click()
  time.sleep(1)
  # select dropdown account
  elem_dropd = driver2.find_element_by_css_selector("#instrument-order-accounts-select > div > div > span")
  elem_dropd.click()

  # select AF account
  #elem_account = driver2.find_element_by_css_selector("#instrument-order-accounts-select-option-0 > div > div > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.faownn > div")
  elem_account = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/form/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div/ul/li[1]/div/div/div[1]/div")
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
  #elem_buy_sell = driver2.find_element_by_css_selector("#main-content > div.PageWrapper__Outer-sc-1ur2ylx-0.fLylmR.PageLayoutOverview__StyledPageWrapper-dawtfj-0.dsucPW > div > div.CssGrid__StyledDiv-bu5cxy-0.iGVYku > div.CssGrid__RawCssGridItem-bu5cxy-1.sc-bdVaJa.ibCVYD > div > div > div:nth-child(1) > div > form > div.Box__StyledDiv-sc-1bfv3i9-0.GUVl > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.hEJJeD > div:nth-child(2) > button")
  elem_buy_sell = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/form/div[2]/div[1]/div[2]/button")
  elem_buy_sell.click()

  time_now = str(datetime.datetime.now().time())
  print("buying: ", vol, "of: ", ticker, "at price: ", price, time_now)
  '''
  # confirmation button - not needed anymore. message wont show.
  try:
   elem_conf = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div[2]/div/div[10]/div/div[2]/button")
   elem_conf.click()
  except:
   print("Confirm order not available - order already sent to exhange")
  '''
  time.sleep(1)

  try:
   # ordren er mottatt - ok
   #elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
   elem_order_ok = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div/div/div[3]/div/div/div[2]/a")
   elem_order_ok.click()
  except:
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ikke tilgjengelig", time_now)

  # PREFILL the sell order except the price
  # Hit the sell button
  #elem_sell = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.iXLhXW")
  elem_sell = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[1]/div[1]/div/div/div[1]/div[3]/div/div[2]/div[2]/div/div/div/div[2]/a")
  elem_sell.click()

  # select dropdown account
  elem_dropd = driver2.find_element_by_css_selector("#instrument-order-accounts-select > div > div > span")
  elem_dropd.click()

  # select AF account
  #elem_account = driver2.find_element_by_css_selector("#instrument-order-accounts-select-option-0 > div > div > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.faownn > div")
  elem_account = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/form/div[1]/div/div[1]/div/div/div/div/div/div/div/div/div[2]/div/div/ul/li[1]/div/div/div[1]/div")
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
  #elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[2]/ul/li[1]/button/span")
  #elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[3]/div/ul/li[1]/button")
  elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[1]/div[3]/div/ul/li[1]/button")
  elem_order.click()

 elif type == "s":
  # enter price
  elem_price = driver2.find_element_by_id("price")
  elem_price.click()
  time.sleep(0.2)
  elem_price.send_keys(price)

  time.sleep(0.2)

  # buy/sell button
  #elem_buy_sell = driver2.find_element_by_css_selector("#main-content > div.PageWrapper__Outer-sc-1ur2ylx-0.fLylmR.PageLayoutOverview__StyledPageWrapper-dawtfj-0.dsucPW > div > div.CssGrid__StyledDiv-bu5cxy-0.iGVYku > div.CssGrid__RawCssGridItem-bu5cxy-1.sc-bdVaJa.ibCVYD > div > div > div:nth-child(1) > div > form > div.Box__StyledDiv-sc-1bfv3i9-0.GUVl > div.Flexbox__StyledFlexbox-sc-1ob4g1e-0.hEJJeD > div:nth-child(2) > button")
  elem_buy_sell = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/form/div[2]/div[1]/div[2]/button")
  elem_buy_sell.click()
  time_now = str(datetime.datetime.now().time())
  print("selling: ", vol, "of: ", ticker, "at price: ", price, time_now)

  time.sleep(1)
  '''
  # confirmation button - not needed anymore. message wont show.
  try:
   elem_conf = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div[2]/div/div[10]/div/div[2]/button")
   elem_conf.click()
  except:
   print("Confirm order not available - order already sent to exhange")
  '''
  time.sleep(2)

  # ordren er mottatt dialog - etter sender inn ordre
  try:
   # elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
   elem_order_ok = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div/div/div[3]/div/div/div[2]/a")
   elem_order_ok.click()
  except:
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ok eksisterer ikke på salg", time_now)

  # reopen the order section to follow order execution status
  #elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[3]/div/ul/li[1]/button")
  elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[1]/div[3]/div/ul/li[1]/button")
  elem_order.click()

  time_now = str(datetime.datetime.now().time())
 elif type == "m":
  # click the edit symbol under order
  #elem_edit = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[1]/a[1]/button")
  #elem_edit = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[1]/a[2]/button")
  elem_edit = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[2]/div/div[2]/div/div/div/div[1]/div/ul/li/ul/li[2]/span/span[1]/a[2]/button")
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

  # Request price from master..
  elem_price.send_keys(price)

  time.sleep(0.3)

  # Hit edit/submit: try in case the order was completed after clicking the change button and before i did change it again.
  try:
   elem_change = driver2.find_element_by_xpath("/html/body/div[1]/div/div[3]/main/div[2]/div/div[1]/div[8]/div/div/div[1]/div/div/form/div/div[13]/div/div[2]/button")
   elem_change.click()
  except:
   time_now = str(datetime.datetime.now().time())
   print("Order already completed - no need to update price", time_now)

  time.sleep(1)

  try:
   # ordren er mottatt - ok
   # elem_order_ok = driver2.find_element_by_class_name("Button__StyledLink-lqp9m3-1.bnsRvn")
   elem_order_ok = driver2.find_element_by_xpath("/html/body/div[3]/div[3]/div/div/div/div/div/div[3]/div/div/div[2]/a")
   elem_order_ok.click()
  except:
   time_now = str(datetime.datetime.now().time())
   print("Ordre mottatt - ikke tilgjengelig", time_now)

  # open the order section to follow order execution status
  #elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div[2]/div[1]/div/div/div[3]/div/ul/li[1]/button")
  elem_order = driver2.find_element_by_xpath("/html/body/div[1]/div/header/div/div/div[1]/div/div[1]/div[3]/div/ul/li[1]/button")
  elem_order.click()

  time.sleep(2)

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


#MAIN Program

login_nordnet()

#Variables
buy_filled_master=""
sell_filled_master=""

while 1:
 conn, addr = s.accept()
 time_now = str(datetime.datetime.now().time())
 print('Incoming msg from master:', addr, time_now)
 while 1:
  data = conn.recv(BUFFER_SIZE).decode("utf-8")
  if not data: break
  time_now = str(datetime.datetime.now().time())
  print("received data:", data, time_now)
  #Check the mesasge
  if data[0] == "B" and trade_state =="READY":
   ticker=data[1]
   price=float(data[2:])
   vol=find_volume(price)
   time_now = str(datetime.datetime.now().time())
   print("BUY ticker:", ticker, "at price", price, "volume", vol, time_now)
   trade_nordnet_watchlist(ticker,"b",str(price),vol)
   trade_state="BOUGHT"
  elif data[0] == "S":
   ticker=data[1]
   price=float(data[2:])
   vol=find_volume(price)
   time_now = str(datetime.datetime.now().time())
   #First Check if BUY order was completed.
   check_buy_order_status()
   if trade_state == "HOLDING":
    print("SELL ticker:", ticker, "at price:", price, "volume", vol, time_now)
    trade_nordnet_watchlist(ticker,"s",str(price),vol)
    trade_state="SELLING"
    time.sleep(7)
    check_sell_order_status()
   else:
    #Cancel buy order
    print("CANCEL buy order", time_now)
    trade_nordnet_watchlist(ticker, "c", 0, 0)
    trade_state = "READY"
  elif data[0] == "C" and trade_state == "BOUGHT":
   time_now = str(datetime.datetime.now().time())
   print("CANCEL buy order", time_now)
   trade_nordnet_watchlist(ticker, "c", 0, 0)
   trade_state = "READY"
  elif data[0] == "M" and trade_state == "SELLING":
   time_now = str(datetime.datetime.now().time())
   print("MODIFY sell order:", ticker, "at price", price, time_now)
   ticker=data[1]
   price=float(data[2:])
   #First check if sell order is filled
   check_sell_order_status()
   if trade_state != "READY":
    trade_nordnet_watchlist(ticker, "m", str(price), vol)
    time.sleep(7)
    check_sell_order_status()
  elif data[0] == "F":
   time_now = str(datetime.datetime.now().time())
   print("buy filled at master", time_now)
   buy_filled_master="true"
  elif data[0] == "R":
   time_now = str(datetime.datetime.now().time())
   print("sell filled at master", time_now)
   sell_filled_master="true"


  #EXCEPTIONS:
  #case 1: BUY filled at master before cancel timeout, but not at nordnet:
  #-No cancel msg are sent to nordnet, the next msg will be a sell msg.
  if data[0] == "S" and trade_state == "BOUGHT":
   trade_nordnet_watchlist(ticker, "c", 0, 0)

  #case 2: BUY filled at nordnet but not at master within the cancel period.
  #-master will send CANCEL msg til nordnet. Price shall be included in the Cancel message.
  elif data[0] == "C" and trade_state == "HOLDING":
   ticker=data[1]
   price=float(data[2:])
   vol=find_volume(price)
   time_now = str(datetime.datetime.now().time())
   print("Exception 2: SELL ticker:", ticker, "at price:", price, "volume", vol, time_now)
   trade_nordnet_watchlist(ticker,"s",str(price),vol)
   trade_state="SELLING"
   time.sleep(10)
   status=check_sell_order_status()
   if status == 1:
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
   time.sleep(20)
   status=check_sell_order_status()
   if status == 1:
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")

  #case 3: SELL filled at master, but still not at nordnet:
  #-no more SELL MODIFY msg will be sent to nordnet.
  elif data [0] == "R" and trade_state == "SELLING":
   #-start local monitoring according to the following input:
	#a.) live prices available from master
	#b) local countdown for SELL MODIFY
   time_now = str(datetime.datetime.now().time())
   print("Exception case 3 happened, no action implemented yet", time_now)
   print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
   time.sleep(10)
   status=check_sell_order_status()
   if status == 1:
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
   time.sleep(20)
   status=check_sell_order_status()
   if status == 1:
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")
    print("*********** MANUAL ACTION NEEDED FOLLOW UP SELL ORDER ************")

  #case 4: SELL filled at nordnet, but still not at master:
  #-nordnet will receive SELL MODIFY when ready.
  elif data[0] == "M" and trade_state == "READY":
   time_now = str(datetime.datetime.now().time())
   print("No action needed, nordnet already completed its trade.", time_now)

  #case 5: what if master crashes, and nordnet holding a position.
  #WE ARE FUCKED.



  #conn.send(data)  # echo
 conn.close()
