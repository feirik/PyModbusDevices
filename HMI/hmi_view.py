import tkinter as tk

# Importing Matplotlib's backend to embed plots in a Tkinter application.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class HMIView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.configure(bg='#D5D5D5')
        self.grid()
