import threading,time

x=0
def test():
   global x
   t=threading.Timer(1,test)
   if x == 5:
      t.cancel()
      x=0
      return 0
   t.start()
   x+=1
   print(x)

test()
time.sleep(10)
test()

