import re
import matplotlib.pyplot as plt
import numpy as np
import os

pnl_total_lst = []
trade_cnt_lst = []
trade_cnt = 1

path="/home/sjefen/Dropbox/log/pcps_PnL"

filenames = os.listdir(path)
for fname in filenames:
    fname = str(path) + "/" + str(fname)
    print(fname)
    file = open(fname, "r")
    lines = file.readlines()
    file.close()
    #Parse pnl total from the file
    for line in lines:
        line=line.strip()
        if "PnL total:" in line:
            #line=re.findall(r"[-+]?\d*\.\d+|\d+", line)
            pnl_total=float(line[18:])
            pnl_total_lst.append(pnl_total)
            print(pnl_total_lst)
            trade_cnt_lst.append(trade_cnt)
            trade_cnt+=1
    #Plot the pnl vs trade_cnt
    plt.plot(trade_cnt_lst, pnl_total_lst)
    plt.xlabel("trade cnt")
    plt.ylabel("pnl total")
    plt.yticks(fontsize=6)
    plt.title(fname)
    plt.savefig(str(fname))

    #Initialize plot data
    trade_cnt = 1
    trade_cnt_lst = []
    pnl_total_lst = []
    plt.clf()