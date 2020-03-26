import re
import matplotlib.pyplot as plt
import numpy as np
import os

pnl_trade_lst = []
pcps_lst = []

path="log/pcps_PnL"

filenames = os.listdir(path)
with open('pcps_concat', 'w') as outfile:
    for fname in filenames:
        fname = str(path) + "/" + str(fname)
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)



file = open("pcps_concat", "r")
lines = file.readlines()
file.close()

for line in lines:
    line=line.strip()
    if "PnL trade:" in line:
        #line=re.findall(r"[-+]?\d*\.\d+|\d+", line)
        pnl_trade=float(line[18:])
        pnl_trade_lst.append(pnl_trade)
        print(pnl_trade_lst)
    if "pcps" in line:
        pcps=float(line[18:21])
        pcps_lst.append(pcps)
        print(pcps_lst)


#Argsort
order = np.argsort(pcps_lst)
xs = np.array(pcps_lst)[order]
ys = np.array(pnl_trade_lst)[order]

#Append stragiht line
plt.xticks(np.arange(min(xs), max(xs)+0.0, 0.2))
plt.xticks(fontsize=6)
plt.grid()
plt.plot(xs,ys)
plt.xlabel("pcps")
plt.ylabel("P&L trade")
plt.show()

plt.xticks(np.arange(min(xs), max(xs)+0.0, 0.2))
plt.xticks(fontsize=6)
plt.grid()
plt.scatter(xs,ys)
plt.xlabel("pcps")
plt.ylabel("P&L trade")
plt.show()

