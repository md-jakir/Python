# From numerous log file we can short those files by date and time.

import pathlib
import time
import datetime
import numpy as np
import os
file_list = os.listdir('/root/dbnode1_log/')
arr_list = np.array(file_list)
#print(arr_list[0])
y = 0 
while (y < len(arr_list)):
    fname = pathlib.Path(arr_list[y])
    assert fname.exists(), f'No such file: {fname}'
#print(fname.stat())  # will print all status of a file
#print(fname.stat().st_mtime)
    timestamp = fname.stat().st_mtime
    old_time = datetime.datetime.fromtimestamp(timestamp)
    new_time = old_time.replace(second=0).timestamp()
#timestamp1 = datetime.timestamp(new_time)
#print(new_time)
#print(timestamp1) 

# # Converting unix timestamp to humanreadable 
#time_readable = time.ctime(int(timestamp))
    time_readable = time.ctime(int(new_time))
    # time_readable = time_readable1.replace(second=0)
    #print(time_readable)
    #print(type(time_readable))

    # #Taking time from User
    #date_time = str(input('Enter data and time(yyyy, mm, dd, hour, min): '))
    yyyy = input('Enter the yeaer(yyy): ')
    mm = input('Enter the month(mm): ')
    dd = input('Enter date(dd): ')
    hour = input('Enter hour(hh): ')
    mn = input('Enter minute(mn): ')
    date_time = datetime.datetime(int(yyyy), int(mm), int(dd), int(hour), int(mn))
    input_time = date_time.strftime("%c")
    #print(input_time)

    # IF condition apply
    if time_readable == input_time:
        print(fname)
        #print("This is input time =", input_time)
    else:
        print("This is readable time =", time_readable)
    y += 1
#datatype = type(date_time)
#print(datatype)

