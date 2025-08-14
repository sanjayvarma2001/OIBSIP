import tkinter as tk
from tkinter import *
import secrets
import string

root = Tk()
root.title("Password Generator")
root.geometry("500x500")

default_font = ("Helvetica", 12)

title_frame = Frame(root, pady=10)
title_frame.pack()

input_frame = Frame(root, pady=10)
input_frame.pack()

options_frame = Frame(root, pady=10)
options_frame.pack()

result_frame = Frame(root, pady=10)
result_frame.pack()

Label(title_frame, text="Customizable Password Generator", font=("Helvetica", 14, "bold")).pack()

Label(input_frame, text="Enter the Length of Password:", font=default_font).grid(row=0, column=0, padx=5, pady=10, sticky='w')
length_password = Entry(input_frame, font=default_font)
length_password.grid(row=0, column=1, padx=5, pady=10)

lower_var = BooleanVar(value=True)
upper_var = BooleanVar(value=True)
digit_var = BooleanVar(value=True)
symbol_var = BooleanVar(value=True)

Checkbutton(options_frame, text="Lowercase", variable=lower_var, font=default_font).grid(row=0, column=0, sticky='w')
Checkbutton(options_frame, text="Uppercase", variable=upper_var, font=default_font).grid(row=1, column=0, sticky='w')
Checkbutton(options_frame, text="Digits", variable=digit_var, font=default_font).grid(row=0, column=1, sticky='w')
Checkbutton(options_frame, text="Symbols", variable=symbol_var, font=default_font).grid(row=1, column=1, sticky='w')

result_label = Label(result_frame, text="", font=("Helvetica", 14, "bold"), fg="green")
result_label.pack(pady=10)

def generate_password():
    try:
        length = int(length_password.get())

        characters = ""
        selected_types = []

        if lower_var.get():
            characters += string.ascii_lowercase
            selected_types.append(string.ascii_lowercase)
        if upper_var.get():
            characters += string.ascii_uppercase
            selected_types.append(string.ascii_uppercase)
        if digit_var.get():
            characters += string.digits
            selected_types.append(string.digits)
        if symbol_var.get():
            characters += string.punctuation
            selected_types.append(string.punctuation)

        if not characters:
            result_label.config(text="Select at least one character type", fg="red")
            return

        password = [secrets.choice(s) for s in selected_types]

        for _ in range(length - len(password)):
            password.append(secrets.choice(characters))

        secrets.SystemRandom().shuffle(password)
        final_password = "".join(password)

        result_label.config(text=final_password, fg="green")

    except ValueError:
        result_label.config(text="Enter a valid number", fg="red")

def copy_to_clipboard():
    password = result_label.cget("text")
    if password and "Password" not in password:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()
        result_label.config(text="Password copied to clipboard!", fg="blue")

generate_btn = Button(input_frame, text="Generate", 
                      command=generate_password, font=default_font,
                      bg="#187ec8",fg="white",
                      activebackground="#125a91",
                      activeforeground="white",
                      padx=10,pady=5,
                      relief="flat")
generate_btn.grid(row=1, column=0, columnspan=2, pady=10)

copy_btn = Button(result_frame, text="Copy to Clipboard", 
                  command=copy_to_clipboard, font=default_font,
                  bg="#187ec8",fg="white",
                  activebackground="#125a91",
                  activeforeground="white",
                  padx=10,pady=5,
                  relief="flat")
copy_btn.pack(pady=5)

root.mainloop()
