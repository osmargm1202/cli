import tkinter as tk
from tkinter import ttk
from tkinter import Button

root = tk.Tk()
root.title("Test")
root.geometry("300x200")

button = Button(root, text="Click me", command=lambda: print("Button clicked"))
# button.pack()








root.mainloop()