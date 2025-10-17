import random
import string

def generate_key(length=25, use_upper=True, use_digits=True):
    characters = string.ascii_lowercase
    
    if use_upper:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    
    # Generate password
    password = "CS_" + ''.join(random.choice(characters) for _ in range(length))
    return password
