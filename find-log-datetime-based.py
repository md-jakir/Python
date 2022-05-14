from datetime import datetime

#s1 = "2022-05-12 18:13:13.057"
s1 = "2022-05-12 18:13:13"
#s2 = "2022-05-12 18:17:51.534"
s2 = "2022-05-12 18:17:51"

#fmt = '%Y-%m-%d %H:%M:%S.%f'
fmt = '%Y-%m-%d %H:%M:%S'

start = datetime.strptime(s1, fmt)
stop = datetime.strptime(s2, fmt)


with open('edb-node1-2022-05-12_095432.log', 'r') as file:
    for line in file:
        line = line.strip()

        try:
            ts = datetime.strptime(' '.join(line.split(' ', maxsplit=2)[:2]), fmt)

            if start <= ts <= stop:
                print(line)

        except:
            pass
