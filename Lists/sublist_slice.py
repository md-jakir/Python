# slicing is like creating a sublist from a list. In a slice, the first integer is the index where the slice starts. The second integer is the index where the slice ends.
# A slice is a new list
sublist = [10, 20, 30, 50, 60]
sublist[1:4] is a list with a slice (two integers).
sublist[1:4]=[20, 30, 50] 
sublist[0:-1]=[10, 20, 30, 50]

# sublist in multilist 

submullist = [['cat', 'bat', 'rat'], [10, 20, 30, 40, 50, 60]]
submullist[0][0:2]='cat', 'bat'
submullist[0][0:-1]='cat', 'bat'
submullist[1][0:3]=10, 20, 30
submullist[1][1:-2]=20, 30, 40

# Getting length of a list

len(summulist)=2    # here two lists are made a list called multilist

# Changing value in a list with indexes

submullist[0][1] = 'mouse'
