import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle

import tkinter as tk
from tkinter.simpledialog import SimpleDialog, _QueryString

class CustomInputDialog(_QueryString):
    def __init__(self, parent, title, prompt, x, y, **kwargs):
        self.x = x
        self.y = y
        super().__init__(parent, title, prompt, **kwargs)
        
    def body(self, master):
        super().body(master)
        self.master.after(10, self.set_geometry)  # Delay the geometry setting

    def set_geometry(self):
        self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.x}+{self.y}")

class ButtonView:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(figsize=(4.4, 3.2))
        
        # Hide the default axis
        self.ax.axis('off')
        
        # Style attributes
        self.fig.patch.set_facecolor('#D5D5D5')  # Set figure background color
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        # Initial setup
        self._setup_view()

        # Embed the widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        
    def _setup_view(self):
        # Define an area (l, b, w, h) in the bottom right for the button
        button_ax = self.fig.add_axes([0.8, 0.01, 0.15, 0.05])
        self.button = Button(button_ax, 'Click Me!', color='lightgray', hovercolor='0.7')
        self.button.on_clicked(self._on_button_click)
        
    def _on_button_click(self, event):
        # Get the top-left corner of the widget
        x = self.canvas._tkcanvas.winfo_rootx()
        y = self.canvas._tkcanvas.winfo_rooty()
    
        # Get the dimensions of the widget
        width = self.canvas._tkcanvas.winfo_width()
        height = self.canvas._tkcanvas.winfo_height()
    
        # Calculate the position for the popup to appear adjacent to the bottom-right corner of the widget
        x = 700
        y = 500  # Adjust as needed
    
        print(f"x: {x}, y: {y}")  # Debug print for coordinates
    
        # Display the custom input dialog
        user_input = CustomInputDialog(self.canvas._tkcanvas.master, "Input", "Please enter a value:", x, y).result
        
        if user_input is not None:
            print(user_input)
