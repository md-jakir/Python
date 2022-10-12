from click import password_option


while True:
    print('Who are you?')
    name = input()
    if name != 'Jakir':
        continue
    print('Hello, Jakir. What is the password?')
    password = input()
    if password == 'abcd':
        break
print('Access Granted.')
