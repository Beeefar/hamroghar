import re
from django.contrib import messages

def validatePassword(request, password):
    isValid = True
    errorText = ''
    i = 1

    # Checking for length of password
    if len(password) < 8:
        errorText += f'{i}. Password must at least be 8 characters long.\n'
        i += 1
        isValid = False

    # Checking for digit
    if not len(re.findall('\d', password)) >= 1:
        errorText += f'{i}. Password must at least have 1 digit.\n'
        i += 1
        isValid = False

    # Checking for uppercase
    if not re.findall('[A-Z]', password):
        errorText += f'{i}. Password must at least have 1 uppercase letter.\n'
        i += 1
        isValid = False

    # checking for lowercase
    if not re.findall('[a-z]', password):
        errorText += f'{i}. Password must at least have 1 lowercase letter.\n'
        i += 1
        isValid = False

    # checking for symbols
    if not re.findall('[!@#$%^&*_]', password):
        errorText += f'{i}. Password must at least have 1 symbol. (!@#$%^&*_)\n'
        i += 1
        isValid = False
    
    if not isValid:
        errorText = re.sub("(\n+)$", "", errorText)
        print(errorText)
        messages.error(request,errorText)
    return isValid
