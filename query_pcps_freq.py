import xlrd
import os
import importlib
import write_to_excel

c_time=0
c_a60pcps=1
c_a30pcps_0_29=2
c_a30pcps_30_59=3
c_a20pcps_0_19=4
c_a20pcps_20_39=5
c_a20pcps_40_59=6
c_a60freq=7
c_a30freq_0_29=8
c_a30freq_30_59=9
c_a20freq_0_19=10
c_a20freq_20_39=11
c_a20freq_40_59=12

a60pcps=0
a30pcps_0_29=0
a30pcps_30_59=0
a20pcps_0_19=0
a20pcps_20_39=0
a20pcps_40_59=0

a60freq=0
a30freq_0_29=0
a30freq_30_59=0
a20freq_0_19=0
a20freq_20_39=0
a20freq_40_59=0


file="/home/sjefen/Dropbox/log/prices/analysis/2020-04-03/2020-04-03.xls"
file_export="/home/sjefen/Dropbox/log/prices/analysis/2020-04-03/entries_of_interest"
sheetname_export="2020-04-03"
row_counter_export = 1

#Return time and ticker with this config
a20pcps_0_19_threshold=0.04
a20freq_0_19_threshold=0.4

#Specify points of interest to gather data and save to a separeate export file
export_true=""
ticker1="ECOR.txt"
ticker1_times = ["15:41:00","15:47:00","16:11:00","16:33:00","16:56:00","17:11:00","17:16:00","17:17:00"]
ticker2="XSPA.txt"
ticker2_times = ["15:35:00","16:43:00","16:51:00","17:01:00","17:19:00"]
ticker3="CAPR.txt"
ticker3_times=["15:43:00","15:51:00"]

x1_workbook = xlrd.open_workbook(file)
sheet_names = x1_workbook.sheet_names()
noof_sheets = x1_workbook.nsheets
print("There are no of sheets: ", noof_sheets)
sheet_index=0

def append_to_export_file():
    global a60pcps
    global a30pcps_0_29
    global a30pcps_30_59
    global a20pcps_0_19
    global a20pcps_20_39
    global a20freq_40_59
    global a60freq
    global a30freq_0_29
    global a30freq_30_59
    global a20freq_0_19
    global a20freq_20_39
    global a20freq_40_59
    global row_counter_export


    a60pcps = this_row[c_a60pcps]
    a30pcps_0_29 = this_row[c_a30pcps_0_29]
    a30pcps_30_59 = this_row[c_a30freq_30_59]
    a20pcps_0_19 = this_row[c_a20pcps_0_19]
    a20pcps_20_39 = this_row[c_a20pcps_20_39]
    a20pcps_40_59 = this_row[c_a20pcps_40_59]

    a60freq = this_row[c_a60freq]
    a30freq_0_29 = this_row[c_a30freq_0_29]
    a30freq_30_59 = this_row[c_a30freq_30_59]
    a20freq_0_19 = this_row[c_a20freq_0_19]
    a20freq_20_39 = this_row[c_a20freq_20_39]
    a20freq_40_59 = this_row[c_a20freq_40_59]

    write_to_excel.write_data_to_workbok(file_export, sheetname_export, row_counter_export, this_row[c_time], a60pcps,
                                         a30pcps_0_29, a30pcps_30_59, a20pcps_0_19, a20pcps_20_39, a20pcps_40_59, a60freq,
                                         a30freq_0_29, a30freq_30_59, a20freq_0_19, a20freq_20_39, a20freq_40_59,
                                         sheet.name)
    row_counter_export += 1
if export_true == "yes":
    write_to_excel.setup_workbook(file_export,sheetname_export)
while sheet_index < noof_sheets:
    sheet = x1_workbook.sheet_by_index(sheet_index)

    row_counter=1
    sheet_nrows = sheet.nrows
    while row_counter < sheet_nrows:
        this_row = sheet.row_values(row_counter)
        if export_true != "yes":
            if this_row[c_a20pcps_0_19] >= a20pcps_0_19_threshold and this_row[c_a20freq_0_19] >= a20freq_0_19_threshold:
                print(sheet.name, this_row[c_time])
        else:
            if sheet.name == ticker1 and this_row[c_time] in ticker1_times:
                append_to_export_file()
            elif sheet.name == ticker2 and this_row[c_time] in ticker2_times:
                append_to_export_file()
            elif sheet.name == ticker3 and this_row[c_time] in ticker3_times:
                append_to_export_file()
        row_counter+=1
    row_counter=1
    sheet_index+=1

