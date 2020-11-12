tradecap=input("enter tradecap/trade: ")
riskprofile=input("enter max risk per trade - e.g 2 for 2%: ")
risk_trade = float(tradecap) * (float(riskprofile) / 100)
risk_trade = float("{:.3f}".format(risk_trade))
print("risk per trade: ", risk_trade)

while True:
    entry = input("enter entry price: ")
    stop = input("enter stoploss: ")
    pt = input("enter profit target: ")
    risk_share=float(entry) - float(stop)
    risk_share=float("{:.3f}".format(risk_share))



    print("risk per share is:", risk_share)
    sharesize=int(risk_trade/risk_share)
    print("sharesize is: ", sharesize)
    potential_profitt=(float(pt) - float(entry))*sharesize
    potential_profitt = float("{:.3f}".format(potential_profitt))
    print("potential profitt is:", potential_profitt)
    risk_rew=int(potential_profitt/risk_trade)
    print("risk reward for this trade: ", risk_rew)
    print("\n")



