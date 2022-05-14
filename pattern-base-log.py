# Sorting log based on patter. 

# Read User file
f = open("pattern.txt", "r")
names = f.read().split() # List of user names
f.close()
# Read Log file
f = open("edb-node1-2022-05-12_095432.log", "r") # List of log lines
log_lines = f.read().split('\n')
f.close()

for i, log in enumerate(log_lines):
    for name in names:
        if name in log:
            print(name + ' is present in line ' + str(i + 1))
