import string
import secrets
import random

password_len = int(input("Enter the length of password: "))

inp_low = input("include lowercase: (y/n)").lower() == "y"
inp_upp= input("include uppercase: (y/n)").lower() == "y"
inp_dig = input("include digits: (y/n)").lower() == "y"
inp_sym = input("include symbol: (y/n)").lower() == "y"

char_sets = []
count = 0
if inp_low:
    char_sets.append(list(string.ascii_lowercase))
    count += 1

if inp_upp:
    char_sets.append(list(string.ascii_uppercase))
    count += 1

if inp_dig:
    char_sets.append(list(string.digits))
    count += 1

if inp_sym:
    char_sets.append(list(string.punctuation))
    count += 1

password_chars = [secrets.choice(char_set) for char_set in char_sets]

all_chars = [char for char_set in char_sets for char in char_set]
length = password_len - count
password_chars.extend(secrets.choice(all_chars) for _ in range(length))

random.shuffle(password_chars)

print("".join(password_chars))