import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys

def choose_input():
    file = filedialog.askopenfilename()
    if file:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file)

def choose_output():
    file = filedialog.asksaveasfilename()
    if file:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, file)

def convert():
    input_file = input_entry.get()
    output_file = output_entry.get()

    if not input_file or not output_file:
        messagebox.showerror("Error", "Please select input and output files.")
        return

    try:
        subprocess.run([sys.executable, "cli.py", input_file, output_file], check=True)
        messagebox.showinfo("Success", "File converted successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))


root = tk.Tk()
root.title("File Converter")
root.geometry("520x200")
root.resizable(False, False)

# Title
title = tk.Label(root, text="File Converter", font=("Arial", 16, "bold"))
title.grid(row=0, column=0, columnspan=3, pady=10)

# Input row
tk.Label(root, text="Input File:").grid(row=1, column=0, padx=10, pady=5, sticky="w")

input_entry = tk.Entry(root, width=40)
input_entry.grid(row=1, column=1, pady=5)

tk.Button(root, text="Browse", width=10, command=choose_input).grid(row=1, column=2, padx=10)

# Output row
tk.Label(root, text="Output File:").grid(row=2, column=0, padx=10, pady=5, sticky="w")

output_entry = tk.Entry(root, width=40)
output_entry.grid(row=2, column=1, pady=5)

tk.Button(root, text="Save As", width=10, command=choose_output).grid(row=2, column=2, padx=10)

# Convert button
convert_button = tk.Button(root, text="Convert", width=20, height=2, command=convert)
convert_button.grid(row=3, column=0, columnspan=3, pady=20)

root.mainloop()