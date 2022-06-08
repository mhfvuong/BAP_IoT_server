from tkinter import *
from tkinter import ttk
import time
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np


def stop():
    global loop
    loop = False
    global root
    root.destroy()


loop = True
root = Tk()
frm = ttk.Frame(root, padding=10)
ttk.Label(frm, text=datetime.today().strftime('%M:%S')).grid(column=0, row=0)
ttk.Button(frm, text='Exit', command=stop).grid(column=1, row=0)

t = np.arange(0, 3, .01)
fig = Figure(figsize=(5, 4), dpi=100)
a = fig.add_subplot(111)
a.plot(t, 2 * np.sin(2 * np.pi * t))
canvas = FigureCanvasTkAgg(fig, frm)
canvas.draw()
canvas.get_tk_widget().grid(column=2, row=0)

frm.grid()

root.update()
while loop:
    ttk.Label(frm, text=datetime.today().strftime('%M:%S')).grid(column=0, row=0)
    root.update()
    time.sleep(0.1)
