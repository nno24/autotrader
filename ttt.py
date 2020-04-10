import threading, datetime, time

lst_15sec=[]
interval_startpoints=[0,15,30,45]

sec_0_15_range = range(0,(15 + 1))
sec_15_30_range = range(15,30)
sec_30_45_range = range(30,45)
sec_45_00_range = range(45,59)


start_build=""

def p_time():
    global start_build
    global lst_15sec

    threading.Timer(1, p_time).start()
    time_now = datetime.datetime.now()
    time_now_ss = time_now.second
    time_now_mm = time_now.minute

    if time_now_ss in interval_startpoints:
        print(lst_15sec)
        lst_15sec = []
        start_build = "y"


    if start_build == "y":
        lst_15sec.append(time_now_ss)
    else:
        start_build = "no"

    print(lst_15sec)




p_time()

