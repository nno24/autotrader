import datetime
import matplotlib.pyplot as plt
import os

path="test"
today=datetime.datetime.today().date()
time_now = datetime.datetime.today().time()
time_now = ("%.8s" % time_now)
print(time_now)
cnt=2
directory=str(path) + "/" + str(today)
os.makedirs(directory, exist_ok=True)

file=str(path) + "/" + str(today) + "/" + str(cnt)
print(file)

h_trade_time_table = ["1","2"]
h_ticker_holding_price = ["1","2"]
PnL_this_trade = 100.5
ticker = "AXSM"
title = str(ticker) + "  " + "  " + "Buy-filled:  " + str(time_now) + "  " + "PnL-trade:" + "  " + str(PnL_this_trade)

plt.xticks(fontsize=6)
plt.plot(h_trade_time_table,h_ticker_holding_price)
plt.xlabel("Time (s)")
plt.ylabel("Price")
plt.title(str(title))
plt.show()
plt.savefig(str(file))