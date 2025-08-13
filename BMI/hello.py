from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import datetime
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("bmi_history.db")
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS bmi_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weight REAL,
        height REAL,
        bmi REAL,
        category TEXT,
        timestamp TEXT
    )
''')
conn.commit()

root = Tk()
root.title("BMI Calculator")
root.geometry("450x400")
root.resizable(False,False)

default_font = ("Helvetica",12)

title_frame= Frame(root, pady=10)
title_frame.pack()

separator = ttk.Separator(root, orient='horizontal').pack(fill='x', pady=10)


input_frame= Frame(root, pady=10)
input_frame.pack()

result_frame= Frame(root, pady=10)
result_frame.pack()

Label(title_frame,text="BMI CALCULATOR", font=("Helvetica", 12, "bold")).pack()

Label(title_frame,text="Track and Analyze your BMI", font=("Helvetica",12)).pack()

Label(input_frame,text="Weight (kg): ", font=("Helvetica",12)).grid(row=0,column=0,padx=5,pady=10,sticky='w')
weight_entry = Entry(input_frame, font=("Helvetica", 12))
weight_entry.grid(row=0,column=1,padx=5,pady=10)

Label(input_frame,text="Height (m): ", font=("Helvetica",12)).grid(row=1,column=0,padx=5,pady=10,sticky='w')
height_entry = Entry(input_frame, font=("Helvetica", 12))
height_entry.grid(row=1,column=1,padx=5,pady=10)

def calculate_bmi():
    try:
        weight = float(weight_entry.get())
        height = float(height_entry.get())


        if height > 100:
            height /= 100

        if weight > 250:
            weight *= 0.453592

        bmi = weight /( height ** 2)

        normal_min_weight = 18.5 * (height ** 2)
        normal_max_weight = 24.9 * (height ** 2)

        if bmi < 18.5:
            category, color = "Underweight", "blue"
            diff = normal_min_weight - weight
            message = f"You are {diff:.2f} kg underweight to reach normal weight."
        elif 18.5 <= bmi <= 24.9:
            category, color = "Normal Weight", "green"
            message = "You are within the normal weight range."
        elif 25 <= bmi <= 29.9:
            category, color = "Overweight", "orange"
            diff = weight - normal_max_weight
            message = f"You are {diff:.2f} kg overweight beyond normal weight."
        else:
            category, color = "Obese", "red"
            diff = weight - normal_max_weight
            message = f"You are {diff:.2f} kg obese beyond normal weight."

        timestamp= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result_label.config(text=f"BMI: {bmi:.2f} ({category})\n{message}", fg=color)
        cursor.execute('''
                       INSERT INTO bmi_records (weight, height, bmi, category, timestamp)
                       VALUES (?,?,?,?,?)
                       ''',(weight,height,bmi,category,timestamp))
        conn.commit()
    except ValueError:
        result_label.config(text="Please enter valid numbers.")

style_btn= Button(root, text="Calculate BMI",
                  font=("Helvetica",12,"bold"),
                  bg="#187ec8",fg="white",
                  activebackground="#125a91",
                  activeforeground="white",
                  padx=10,pady=5,
                  relief="flat",
                  command=calculate_bmi)
style_btn.pack(pady=10)

def show_bmi_graphs():
    df = pd.read_sql_query("SELECT * FROM bmi_records",conn)

    if df.empty:
        messagebox.showerror("No BMI records found","There are no BMI records to display.")
        return
    
    color_map = {"Underweight" : "blue",
                 "Normal Weight" : "green",
                 "Overweight" : "orange",
                 "Obese" : "red"}
    
    plt.figure(figsize=(8,5))

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    for category, color in color_map.items():
        subset = df[df['category'] == category]
        if not subset.empty:
            plt.scatter(subset['timestamp'], subset['bmi'],color=color,label=category)

    df_sorted = df.sort_values('timestamp')
    plt.plot(df_sorted['timestamp'], df_sorted['bmi'], color='gray', linestyle='--', alpha=0.5)         
    plt.title("Graph of BMI records")
    plt.xlabel("Time")
    plt.ylabel("BMI values")
    plt.xticks(rotation = 45)
    plt.tight_layout()
    plt.show()

graph_btn = Button(root, text="Show Graph on Past Records",
                   font=default_font,bg="#28a745", fg="white",
                   activebackground="#1e7e34",
                   activeforeground="white",
                   padx=10, pady=5,
                   relief="flat",
                   command=show_bmi_graphs)
graph_btn.pack(pady=5)

result_label = Label(root,text="",font=("Helvetica",12))
result_label.pack()


root.mainloop()