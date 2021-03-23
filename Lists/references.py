# In python list are referred to a reference variable like below
# spam is called reference variable for the list
spam = [10, 20, 30, 40]
cheese = spam # here, just reference variable is copied to cheese variable not list's values but now both referenecs have a same ID which points to list 

# Passing references

def country(parameter):
  parameter.append('Japan')
  
clist = ['BD', 'UK', 'US']
country(clist)
print(clist)

# copy() and deepcopy() with copy() module in python
in this expect, there have no same ID for variables used in code like below

import copy
numbers = [10, 30, 40, 50]
cheese = copy.copy(numbers)
cheese.insert(1, 20)
print(numbers)
print(cheese)

Output:
[10, 30, 40, 50]
[10, 20, 30, 40, 50]
