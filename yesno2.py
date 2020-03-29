import tkinter
from tkinter import messagebox
price=10.2
ticker="BKIY"
std_txt="BUY"
questionmark="?"

msg_txt = str(std_txt) + str(ticker) + str(price)

messagebox.askyesno(ticker, std_txt)
