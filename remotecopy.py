# This python script is used to copy multiple file or log file to remote server

import subprocess
import numpy as np
import os
file_list = os.listdir('/root/dbnode1_log/')  # listing files under directory
arr_list = np.array(file_list)  # converting list into array
y = 0 
while (y < len(arr_list)):
    subprocess.run(["scp", arr_list[y], "root@x.x.x.x:/root/dbnode1_log"])
    y += 1
