# Writing to an excel
# sheet using Python
import xlwt
from xlwt import Workbook

# Workbook is created
wb = Workbook()
sheet1=""

# add_sheet is used to create sheet.
def setup_workbook(filename,sheetname):
    global sheet1
    sheet1 = wb.add_sheet(sheetname)
    fname = str(filename) + str(".xls")
    sheet1.write(0, 0, 'Time')
    sheet1.write(0, 1, 'a60pcps')
    sheet1.write(0, 2, 'a30pcps_0_29')
    sheet1.write(0, 3, 'a30pcps_30_59')
    sheet1.write(0, 4, 'a20pcps_0_19')
    sheet1.write(0, 5, 'a20pcps_20_39')
    sheet1.write(0, 6, 'a20pcps_40_59')
    sheet1.write(0, 7, 'a60freq')
    sheet1.write(0, 8, 'a30freq_0_29')
    sheet1.write(0, 9, 'a30freq_30_39')
    sheet1.write(0, 10, 'a20freq_0_19')
    sheet1.write(0, 11, 'a20freq_20_39')
    sheet1.write(0, 12, 'a20freq_40_59')
    sheet1.write(0, 13, 'Comment')

    wb.save(fname)

def write_data_to_workbok(filename,sheetname, row_counter, time, a60pcps, a30pcps_0_29, a30pcps_30_59, a20pcps_0_19,a20pcps_20_39,a20pcps_40_59,a60freq,a30freq_0_29,a30freq_30_59,a20freq_0_19,a20freq_20_39,a20freq_40_59,comment):
    global sheet1
    fname = str(filename) + str(".xls")
    sheet1.write(row_counter, 0, time)
    sheet1.write(row_counter, 1, a60pcps)
    sheet1.write(row_counter, 2, a30pcps_0_29)
    sheet1.write(row_counter, 3, a30pcps_30_59)
    sheet1.write(row_counter, 4, a20pcps_0_19)
    sheet1.write(row_counter, 5, a20pcps_20_39)
    sheet1.write(row_counter, 6, a20pcps_40_59)
    sheet1.write(row_counter, 7, a60freq)
    sheet1.write(row_counter, 8, a30freq_0_29)
    sheet1.write(row_counter, 9, a30freq_30_59)
    sheet1.write(row_counter, 10, a20freq_0_19)
    sheet1.write(row_counter, 11, a20freq_20_39)
    sheet1.write(row_counter, 12, a20freq_40_59)
    sheet1.write(row_counter, 13, comment)

    wb.save(fname)



