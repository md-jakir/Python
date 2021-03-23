# List is an like array consisting of element separated with comma in [] like below

animal = ['cat', 'bat', 'rat', 'monkey', 'elephant']
animal[0]='cat' # 0 index value 
animal[1]='bat' # 1 index value
animal[-1]='elaphant' # negative index will give last value in a list
animal[-2]='monkey'   # 2nd-to-last element in a list

# List in a List like this

multilist = [['cat', 'bat'], ['rat', 'monkey', 'elephant']]
multilist[0]=['cat', 'bat']   # this will give first list in a multilist
multilist[1]=['rat', 'monkey', 'elephant']  # 2nd list in a multilist
multilist[0][0]='cat'   # first element of first list in a multilist
multilist[0][1]='bat'   # 2nd element as well
multilist[1][2]='elephant'   # 3rd element of 2nd list in a multilist


