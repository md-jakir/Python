# IN and NOT operator in List

country = ['BD', 'US', 'UK', 'Japan']
'BD' in country
True
'Canada' in country
False

# One program with NOT or IN operator

fruits = ['Apple', 'Mengo', 'Banana']
print('Enter your fruit name:')
name = input()
if name not in fruits:
  print('I do not have the fruit ' + name)
else:
  print(name + ' is my fruit. ')
  

  
