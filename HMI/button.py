import tkinter as tk
import sys
import os

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI

# TEMP values
IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1


class CustomInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, x, y, width=225, height=106):
        super().__init__(parent)
        self.geometry(f"{width}x{height}+{x}+{y}")  # Set both position and dimensions
        self.title(title)

        self.label = tk.Label(self, text=prompt)
        self.label.pack(pady=5)

        self.entry = tk.Entry(self, width=17)  # Set width of the Entry widget
        self.entry.pack(pady=0)

        self.button_frame = tk.Frame(self)  # Create a frame for the buttons
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="Apply", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=5)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=0, column=1, padx=5)

        self.result = None

    def submit(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()



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

        self.sp_button_ax = self.fig.add_axes([0.075, 0.74, 0.314, 0.12])
        
        # Create the button with hover effect
        self.sp_button = Button(self.sp_button_ax, 'UPDATE\nSET POINT', color='#999999', hovercolor='#008000')
        self.sp_button.on_clicked(self._on_button_click)

        # Give it a thick border (You can adjust the rectangle's linewidth for the desired thickness)
        # Here, the rectangle is slightly smaller than the full button
        inset_ratio = 0.03
        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor='#D5D5D5', edgecolor='#999999', linewidth=1.5)
        self.sp_button_ax.add_patch(rectangle)

        # Create faceplate zone
        rect = [0.465, 0.52, 0.51, 0.433]

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
        rect = [0.465, 0.045, 0.31, 0.40]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Set View", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create manual actions zone
        rect = [0.028, 0.045, 0.41, 0.907]

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
        
        x = 815
        y = 514

        # Display the custom input dialog
        dialog = CustomInputDialog(self.canvas._tkcanvas.master, "Update Value", "Enter value:", x, y)
        self.canvas._tkcanvas.master.wait_window(dialog)  # Wait until dialog is closed
        user_input = dialog.result

        if user_input is not None:
            try:
                user_input = int(user_input)
                print(user_input)

                client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
                client.write_register(2, user_input)
                client.close()
                
            except ValueError:
                print("Entered value is not a valid integer!")

