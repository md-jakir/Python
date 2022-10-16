from mimetypes import init


while True:
    print('Enter your age:')
    age = input()
    if age.isdecimal():
        break
    print('Select a number for you age.')

while True:
    print('Select a new password (Letter & number only):')
    passwd = input()
    if passwd.isalnum(): # Only letters or only number or both are combined are accecptable
        break
    print('Password can only have letters & numbers')
