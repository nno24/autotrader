import re
import matplotlib.pyplot as plt
import numpy as np
import os

pnl_trade_lst = [0]*30
trade_cnt_lst = list(range(1,31))
pnl_trade=0
trade_cnt=0

path="log/pcps_PnL/1min_breakout"

filenames = os.listdir(path)
with open('pnl_concat', 'w') as outfile:
    for fname in filenames:
        fname = str(path) + "/" + str(fname)
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)



file = open("pnl_concat", "r")
lines = file.readlines()
file.close()

for line in lines:
    line=line.strip()
    if "PnL trade w fees:" in line:
        #line=re.findall(r"[-+]?\d*\.\d+|\d+", line)
        pnl_trade=float(line[18:])
        #pnl_trade_lst.append(pnl_trade)
        print(pnl_trade_lst)
    if "Trade cnt succ:" in line:
        trade_cnt=int(line[18:])
        print(trade_cnt)

    #Append to list - sum the elements
    if trade_cnt <=30:
        pnl_trade_lst[trade_cnt-1]=pnl_trade+pnl_trade_lst[trade_cnt-1]



plt.plot(trade_cnt_lst,pnl_trade_lst)
plt.ylabel("pnl total - w fee")
plt.xlabel("trade cnt")
plt.show()


