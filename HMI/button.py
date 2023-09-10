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

        # Create faceplate zone
        rect = [0.415, 0.52, 0.56, 0.433]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Reserved Faceplate Zone\n", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create reserved information block
        rect = [0.415, 0.045, 0.56, 0.40]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Reserved Zone\n For Information", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create manual actions zone
        rect = [0.028, 0.045, 0.36, 0.907]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        y_placement = 0.91

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, y_placement, "MANUAL ACTIONS", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

    def _on_button_click(self, event):
        # Get the top-left corner of the widget
        x = self.canvas._tkcanvas.winfo_rootx()
        y = self.canvas._tkcanvas.winfo_rooty()
    
        # Get the dimensions of the widget
        width = self.canvas._tkcanvas.winfo_width()
        height = self.canvas._tkcanvas.winfo_height()
    
        # Calculate the position for the popup to appear adjacent to the bottom-right corner of the widget
        x = 795
        y = 513
    
        print(f"x: {x}, y: {y}")  # Debug print for coordinates
    
        # Display the custom input dialog
        user_input = CustomInputDialog(self.canvas._tkcanvas.master, "Input", "Please enter a value:", x, y).result
        
        if user_input is not None:
            print(user_input)
