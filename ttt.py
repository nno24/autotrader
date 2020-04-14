import threading, datetime, time

x = 1

while x != 10:
    while 1:
        time.sleep(1)
        x+=1
        print(x)
