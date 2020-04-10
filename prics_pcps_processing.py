import re
import matplotlib.pyplot as plt
import numpy as np
import os
import importlib
import write_to_excel

path="/home/sjefen/Dropbox/log/prices/"
dayofinterest="2020-04-03"
path=str(path) + str(dayofinterest)
path_save="/home/sjefen/Dropbox/log/prices/analysis/"
path_save = str(path_save) + str(dayofinterest)
os.makedirs(path_save, exist_ok=True)
filenames = os.listdir(path)
print(filenames)

time_hh=999
time_mm=999
time_ss=999
current_minute=999
row_counter=0

r0_4=range(0,5)
r5_9=range(5,10)
r10_14=range(10,15)
r15_19=range(15,20)
r20_24=range(20,25)
r25_29=range(25,30)
r30_34=range(30,35)
r35_39=range(35,40)
r40_44=range(40,45)
r45_49=range(45,50)
r50_54=range(50,55)
r55_59=range(55,59)

r0_4_pcps = []
r5_9_pcps = []
r10_14_pcps = []
r15_19_pcps = []
r20_24_pcps = []
r25_29_pcps = []
r30_34_pcps = []
r35_39_pcps = []
r40_44_pcps = []
r45_49_pcps = []
r50_54_pcps = []
r55_59_pcps = []


a60pcps=0
a30pcps_0_29=0
a30pcps_30_59=0
a20pcps_0_19=0
a20pcps_20_39=0
a20pcps_40_59=0
a15pcps_0_14=0
a15pcps_15_29=0
a15pcps_30_44=0
a15pcps_45_59=0
a10pcps_0_9=0
a10pcps_10_19=0
a10pcps_20_29=0
a10pcps_30_39=0
a10pcps_40_49=0
a10pcps_50_59=0
a5pcps_0_4=0
a5pcps_5_9=0
a5pcps_10_14=0
a5pcps_15_19=0
a5pcps_20_24=0
a5pcps_25_29=0
a5pcps_30_34=0
a5pcps_35_39=0
a5pcps_40_44=0
a5pcps_45_49=0
a5pcps_50_54=0
a5pcps_55_59=0

a60freq=0
a30freq_0_29=0
a30freq_30_59=0
a20freq_0_19=0
a20freq_20_39=0
a20freq_40_59=0
a15freq_0_14=0
a15freq_15_29=0
a15freq_30_44=0
a15freq_45_59=0
a10freq_0_9=0
a10freq_10_19=0
a10freq_20_29=0
a10freq_30_39=0
a10freq_40_49=0
a10freq_50_59=0
a5freq_0_4=0
a5freq_5_9=0
a5freq_10_14=0
a5freq_15_19=0
a5freq_20_24=0
a5freq_25_29=0
a5freq_30_34=0
a5freq_35_39=0
a5freq_40_44=0
a5freq_45_49=0
a5freq_50_54=0
a5freq_55_59=0



def clear_lists():

    global r0_4_pcps
    global r5_9_pcps
    global r10_14_pcps
    global r15_19_pcps
    global r20_24_pcps
    global r25_29_pcps
    global r30_34_pcps
    global r35_39_pcps
    global r40_44_pcps
    global r45_49_pcps
    global r50_54_pcps
    global r55_59_pcps

    r0_4_pcps = []
    r5_9_pcps = []
    r10_14_pcps = []
    r15_19_pcps = []
    r20_24_pcps = []
    r25_29_pcps = []
    r30_34_pcps = []
    r35_39_pcps = []
    r40_44_pcps = []
    r45_49_pcps = []
    r50_54_pcps = []
    r55_59_pcps = []

def calc_pcps_average():
    global a60pcps
    global a30pcps_0_29
    global a30pcps_30_59
    global a20pcps_0_19
    global a20pcps_20_39
    global a20pcps_40_59
    global a15pcps_0_14
    global a15pcps_15_29
    global a15pcps_30_44
    global a15pcps_45_59
    global a10pcps_0_9
    global a10pcps_10_19
    global a10pcps_20_29
    global a10pcps_30_39
    global a10pcps_40_49
    global a10pcps_50_59
    global a5pcps_0_4
    global a5pcps_5_9
    global a5pcps_10_14
    global a5pcps_15_19
    global a5pcps_20_24
    global a5pcps_25_29
    global a5pcps_30_34
    global a5pcps_35_39
    global a5pcps_40_44
    global a5pcps_45_49
    global a5pcps_50_54
    global a5pcps_55_59

    #5 sec average
    a5pcps_0_4 = sum(r0_4_pcps)/5
    a5pcps_0_4 = float("%.3f" % a5pcps_0_4)
    a5pcps_5_9 = sum(r5_9_pcps)/5
    a5pcps_5_9 = float("%.3f" % a5pcps_5_9)
    a5pcps_10_14 = sum(r10_14_pcps)/5
    a5pcps_10_14 = float("%.3f" % a5pcps_10_14)
    a5pcps_15_19 = sum(r15_19_pcps)/5
    a5pcps_15_19 = float("%.3f" % a5pcps_15_19)
    a5pcps_20_24 = sum(r20_24_pcps)/5
    a5pcps_20_24 = float("%.3f" % a5pcps_20_24)
    a5pcps_25_29 = sum(r25_29_pcps)/5
    a5pcps_25_29 = float("%.3f" % a5pcps_25_29)
    a5pcps_30_34 = sum(r30_34_pcps)/5
    a5pcps_30_34 = float("%.3f" % a5pcps_30_34)
    a5pcps_35_39 = sum(r35_39_pcps)/5
    a5pcps_35_39 = float("%.3f" % a5pcps_35_39)
    a5pcps_40_44 = sum(r40_44_pcps)/5
    a5pcps_40_44 = float("%.3f" % a5pcps_40_44)
    a5pcps_45_49 = sum(r45_49_pcps)/5
    a5pcps_45_49 = float("%.3f" % a5pcps_45_49)
    a5pcps_50_54 = sum(r50_54_pcps)/5
    a5pcps_50_54 = float("%.3f" % a5pcps_50_54)
    a5pcps_55_59 = sum(r55_59_pcps)/5
    a5pcps_55_59 = float("%.3f" % a5pcps_55_59)

    #10 sec average
    a10pcps_0_9=(a5pcps_0_4 + a5pcps_5_9)/2
    a10pcps_0_9=float("%.3f" % a10pcps_0_9)
    a10pcps_10_19=(a5pcps_10_14 + a5pcps_15_19)/2
    a10pcps_10_19=float("%.3f" % a10pcps_10_19)
    a10pcps_20_29=(a5pcps_20_24 + a5pcps_25_29)/2
    a10pcps_20_29=float("%.3f" % a10pcps_20_29)
    a10pcps_30_39=(a5pcps_30_34 + a5pcps_35_39)/2
    a10pcps_30_39=float("%.3f" % a10pcps_30_39)
    a10pcps_40_49=(a5pcps_40_44 + a5pcps_45_49)/2
    a10pcps_40_49=float("%.3f" % a10pcps_40_49)
    a10pcps_50_59=(a5pcps_50_54 + a5pcps_55_59)/2
    a10pcps_50_59=float("%.3f" % a10pcps_50_59)

    #20 sec average
    a20pcps_0_19=(a10pcps_0_9 + a10pcps_10_19)/2
    a20pcps_0_19=float("%.3f" % a20pcps_0_19)
    a20pcps_20_39=(a10pcps_20_29 + a10pcps_30_39)/2
    a20pcps_20_39=float("%.3f" % a20pcps_20_39)
    a20pcps_40_59=(a10pcps_40_49 + a10pcps_40_49)/2
    a20pcps_40_59=float("%.3f" % a20pcps_40_59)

    #30 sec average
    a30pcps_0_29=(a10pcps_0_9 + a10pcps_10_19 + a10pcps_20_29)/3
    a30pcps_0_29=float("%.3f" % a30pcps_0_29)
    a30pcps_30_59=(a10pcps_30_39 + a10pcps_40_49 + a10pcps_50_59)/3
    a30pcps_30_59=float("%.3f" % a30pcps_30_59)

    #60 sec average
    a60pcps=(a30pcps_0_29 + a30pcps_30_59)/2
    a60pcps=float("%.3f" % a60pcps)

    print("a60pcps", a60pcps)
    print("\n")

    print("a30pcps_0_29", a30pcps_0_29)
    print("a30pcps_30_59", a30pcps_30_59)
    print("\n")

    print("a20pcps_0_19", a20pcps_0_19)
    print("a20pcps_20_39", a20pcps_20_39)
    print("a20pcps_40_59", a20pcps_40_59)
    print("\n")

    print("a10pcps_0_9", a10pcps_0_9)
    print("a10pcps_10_19", a10pcps_10_19)
    print("a10pcps_20_29", a10pcps_20_29)
    print("a10pcps_30_39", a10pcps_30_39)
    print("a10pcps_40_49", a10pcps_40_49)
    print("a10pcps_50_59", a10pcps_50_59)
    print("\n")

    print("a5pcps_0_4", a5pcps_0_4)
    print("a5pcps_5_9", a5pcps_5_9)
    print("a5pcps_10_14", a5pcps_10_14)
    print("a5pcps_15_19", a5pcps_15_19)
    print("a5pcps_20_24", a5pcps_20_24)
    print("a5pcps_25_29", a5pcps_25_29)
    print("a5pcps_30_34", a5pcps_30_34)
    print("a5pcps_35_39", a5pcps_35_39)
    print("a5pcps_40_44", a5pcps_40_44)
    print("a5pcps_45_49", a5pcps_45_49)
    print("a5pcps_50_54", a5pcps_50_54)
    print("a5pcps_55_59", a5pcps_55_59)
    print("\n")


def calc_freq_average():
    global a60freq
    global a30freq_0_29
    global a30freq_30_59
    global a20freq_0_19
    global a20freq_20_39
    global a20freq_40_59
    global a15freq_0_14
    global a15freq_15_29
    global a15freq_30_44
    global a15freq_45_59
    global a10freq_0_9
    global a10freq_10_19
    global a10freq_20_29
    global a10freq_30_39
    global a10freq_40_49
    global a10freq_50_59
    global a5freq_0_4
    global a5freq_5_9
    global a5freq_10_14
    global a5freq_15_19
    global a5freq_20_24
    global a5freq_25_29
    global a5freq_30_34
    global a5freq_35_39
    global a5freq_40_44
    global a5freq_45_49
    global a5freq_50_54
    global a5freq_55_59

    r0_4_freq_cnt=0
    r5_9_freq_cnt=0
    r10_14_freq_cnt=0
    r15_19_freq_cnt=0
    r20_24_freq_cnt=0
    r25_29_freq_cnt=0
    r30_34_freq_cnt=0
    r35_39_freq_cnt=0
    r40_44_freq_cnt=0
    r45_49_freq_cnt=0
    r50_54_freq_cnt=0
    r55_59_freq_cnt=0

    for x in r0_4_pcps:
        if x != 0:
            r0_4_freq_cnt+=1
    a5freq_0_4 = (r0_4_freq_cnt/5)
    print("a5freq_0_4", a5freq_0_4)

    for x in r5_9_pcps:
        if x != 0:
            r5_9_freq_cnt+=1
    a5freq_5_9 = (r5_9_freq_cnt/5)
    print("a5freq_5_9", a5freq_5_9)

    for x in r10_14_pcps:
        if x != 0:
            r10_14_freq_cnt+=1
    a5freq_10_14 = (r10_14_freq_cnt/5)
    print("a5freq_10_14", a5freq_10_14)

    for x in r15_19_pcps:
        if x != 0:
            r15_19_freq_cnt+=1
    a5freq_15_19 = (r15_19_freq_cnt/5)
    print("a5freq_15_19", a5freq_15_19)

    for x in r20_24_pcps:
        if x != 0:
            r20_24_freq_cnt+=1
    a5freq_20_24 = (r20_24_freq_cnt/5)
    print("a5freq_20_24", a5freq_20_24)

    for x in r25_29_pcps:
        if x != 0:
            r25_29_freq_cnt+=1
    a5freq_25_29 = (r25_29_freq_cnt/5)
    print("a5freq_25_29", a5freq_25_29)

    for x in r30_34_pcps:
        if x != 0:
            r30_34_freq_cnt+=1
    a5freq_30_34 = (r30_34_freq_cnt/5)
    print("a5freq_30_34", a5freq_30_34)

    for x in r35_39_pcps:
        if x != 0:
            r35_39_freq_cnt+=1
    a5freq_35_39 = (r35_39_freq_cnt/5)
    print("a5freq_35_39", a5freq_35_39)

    for x in r40_44_pcps:
        if x != 0:
            r40_44_freq_cnt+=1
    a5freq_40_44 = (r40_44_freq_cnt/5)
    print("a5freq_40_44", a5freq_40_44)

    for x in r45_49_pcps:
        if x != 0:
            r45_49_freq_cnt+=1
    a5freq_45_49 = (r45_49_freq_cnt/5)
    print("a5freq_45_49", a5freq_45_49)

    for x in r50_54_pcps:
        if x != 0:
            r50_54_freq_cnt+=1
    a5freq_50_54 = (r50_54_freq_cnt/5)
    print("a5freq_50_54", a5freq_50_54)

    for x in r55_59_pcps:
        if x != 0:
            r55_59_freq_cnt+=1
    a5freq_55_59 = (r55_59_freq_cnt/5)
    print("a5freq_55_59", a5freq_55_59)
    print("\n")

    #average 10s frequency
    a10freq_0_9 = (a5freq_0_4 + a5freq_5_9)/2
    a10freq_0_9 = float("%.2f" % a10freq_0_9)
    a10freq_10_19 = (a5freq_10_14 + a5freq_15_19)/2
    a10freq_10_19 = float("%.2f" % a10freq_10_19)
    a10freq_20_29 = (a5freq_20_24 + a5freq_25_29)/2
    a10freq_20_29 = float("%.2f" % a10freq_20_29)
    a10freq_30_39 = (a5freq_30_34 + a5freq_35_39)/2
    a10freq_30_39 = float("%.2f" % a10freq_30_39)
    a10freq_40_49 = (a5freq_40_44 + a5freq_45_49)/2
    a10freq_40_49 = float("%.2f" % a10freq_40_49)
    a10freq_50_59 = (a5freq_50_54 + a5freq_55_59)/2
    a10freq_50_59 = float("%.2f" % a10freq_50_59)

    print("a10freq_0_9", a10freq_0_9)
    print("a10freq_10_19", a10freq_10_19)
    print("a10freq_20_29", a10freq_20_29)
    print("a10freq_30_39", a10freq_30_39)
    print("a10freq_40_49", a10freq_40_49)
    print("a10freq_50_59", a10freq_50_59)
    print("\n")

    #average 20 freq
    a20freq_0_19 = (a10freq_0_9 + a10freq_10_19)/2
    a20freq_0_19 = float("%.2f" % a20freq_0_19)
    a20freq_20_39 = (a10freq_20_29 + a10freq_30_39)/2
    a20freq_20_39 = float("%.2f" % a20freq_20_39)
    a20freq_40_59 = (a10freq_40_49 + a10freq_50_59)/2
    a20freq_40_59 = float("%.2f" % a20freq_40_59)

    print("a20freq_0_19", a20freq_0_19)
    print("a20freq_20_39", a20freq_20_39)
    print("a20freq_40_59", a20freq_40_59)
    print("\n")

    #average 30 freq
    a30freq_0_29 = (a10freq_0_9 + a10freq_10_19 + a10freq_20_29)/3
    a30freq_0_29 = float("%.2f" % a30freq_0_29)
    a30freq_30_59 = (a10freq_30_39 + a10freq_40_49 + a10freq_50_59)/3
    a30freq_30_59 = float("%.2f" % a30freq_30_59)

    print("a30freq_0_29", a30freq_0_29)
    print("a30freq_30_59", a30freq_30_59)
    print("\n")

    #average 60 freq
    a60freq=(a30freq_0_29 + a30freq_30_59)/2
    a60freq=float("%.2f" % a60freq)
    print("a60freq", a60freq)
    print("\n")






for fname in filenames:
    global row_counter
    fname_save= str(path_save) + "/" + str(dayofinterest)
    sheetname=fname
    fname = str(path) + "/" + str(fname)
    print(fname)
    file = open(fname, "r")
    lines = file.readlines()
    file.close()
    write_to_excel.setup_workbook(fname_save,sheetname)
    for line in lines:
        #time=str(line[0:8])
        time, price, pcps = line.split(" ")
        time = str(time[0:8])
        time_hh = int(time[0:2])
        time_mm = int(time[3:5])
        time_ss = int(time[6:8])
        pcps = float(pcps[0:6])
        if time >= "15:30:10" and time <= "22:35:00":
            if current_minute != time_mm and current_minute != 999:
                print("FOLLOWING LAST MIN DATA UNTIL ",time )
                row_counter += 1
                calc_pcps_average()
                calc_freq_average()
                write_to_excel.write_data_to_workbok(fname_save,sheetname,row_counter, time, a60pcps,a30pcps_0_29,a30pcps_30_59,a20pcps_0_19,a20pcps_20_39,a20pcps_40_59,a60freq,a30freq_0_29,a30freq_30_59,a20freq_0_19,a20freq_20_39,a20freq_40_59,"")
                clear_lists()
            current_minute=time_mm
            if time_ss in r0_4:
                r0_4_pcps.append(pcps)
            elif time_ss in r5_9:
                r5_9_pcps.append(pcps)
            elif time_ss in r10_14:
                r10_14_pcps.append(pcps)
            elif time_ss in r15_19:
                r15_19_pcps.append(pcps)
            elif time_ss in r20_24:
                r20_24_pcps.append(pcps)
            elif time_ss in r25_29:
                r25_29_pcps.append(pcps)
            elif time_ss in r30_34:
                r30_34_pcps.append(pcps)
            elif time_ss in r35_39:
                r35_39_pcps.append(pcps)
            elif time_ss in r40_44:
                r40_44_pcps.append(pcps)
            elif time_ss in r45_49:
                r45_49_pcps.append(pcps)
            elif time_ss in r50_54:
                r50_54_pcps.append(pcps)
            elif time_ss in r55_59 or time_ss == 59:
                r55_59_pcps.append(pcps)
    row_counter = 0
