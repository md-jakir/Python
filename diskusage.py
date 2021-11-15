# Subprocess module which is used to get linux disk usage status comparing threshold value
import subprocess
partition_usage_threshold = 5
df_cmd = subprocess.check_output(['df','-hT'])
df_str = df_cmd.decode("utf-8")
lines = df_str.splitlines()
for line in lines[1:]:
    columns = line.split()
    used_percentage = columns[5]
    used_percentage = used_percentage.replace('%','')
    if int(used_percentage) >= partition_usage_threshold:
        print("partition %s usage is beyond threshold at %s " % (columns[0], columns[5]))
