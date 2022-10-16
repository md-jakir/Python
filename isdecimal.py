while True:
    print('Enter your age:')
    age = input()
    if age.isdecimal():
        break
    print('Select a number for you age.')
