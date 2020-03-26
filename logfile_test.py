import os
import  datetime, time

folder="log"
today=datetime.datetime.today().date()
subdir=str(folder)
PnL_file=str(folder) + "/" + str(today)

os.makedirs(subdir, exist_ok=True)

def log_PnL(pnl_this_trade, pnl_total, pnl_this_trade_w_fees, pnl_total_w_fees, trade_succes_cnt, pcpsMax):
    global PnL_file
    time_n = datetime.datetime.now()
    file = open(PnL_file, "a")
    file.write(str(time_n))
    file.write("\n")
    file.write("PnL trade:        ")
    file.write(str(pnl_this_trade))
    file.write("\n")
    file.write("PnL total:        ")
    file.write(str(pnl_total))
    file.write("\n")
    file.write("PnL trade w fees: ")
    file.write(str(pnl_this_trade_w_fees))
    file.write("\n")
    file.write("PnL total w fees: ")
    file.write(str(pnl_total_w_fees))
    file.write("\n")
    file.write("Trade cnt succ:   ")
    file.write(str(trade_succes_cnt))
    file.write("\n")
    file.write("pcps value:       ")
    file.write(str(pcpsMax))
    file.write("\n")
    file.write("\n")
    file.close()

log_PnL(100,50,30,110,5,1.334)
time.sleep(30)


