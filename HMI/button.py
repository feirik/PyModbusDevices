import tkinter as tk
import sys
import os
from functools import partial

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
        self.sp_button.on_clicked(partial(self._on_button_click_set_value, title="Update Set Point", prompt="Enter value (0-1024):", addr=2))

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


    def _on_button_click_set_value(self, event, title, prompt, addr):
        # Display the custom input dialog and get the user input
        self.input_dialog(title, prompt)
        self.canvas._tkcanvas.master.wait_window(self.dialog_window)  # Wait until the dialog is closed
        user_input = self.result

        if user_input is not None:
            try:
                user_input = int(user_input)
                if 0 <= user_input <= 1024:
                    print(user_input)

                    client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
                    client.write_register(addr, user_input)
                    client.close()
                else:
                    self.error_dialog("Input out of range.")

            except ValueError:
                self.error_dialog("Invalid input.")



    def input_dialog(self, title, prompt):
        x = 815
        y = 514
        width = 225
        height = 106

        self.dialog_window = tk.Toplevel(self.canvas._tkcanvas.master)
        self.dialog_window.geometry(f"{width}x{height}+{x}+{y}")
        self.dialog_window.title(title)

        # Set the column weights. The center columns (1 and 2) have higher weights.
        self.dialog_window.grid_columnconfigure(0, weight=1)
        self.dialog_window.grid_columnconfigure(1, weight=2)
        self.dialog_window.grid_columnconfigure(2, weight=2)
        self.dialog_window.grid_columnconfigure(3, weight=1)

        label = tk.Label(self.dialog_window, text=prompt)
        label.grid(row=0, column=1, columnspan=2, pady=5)

        self.entry = tk.Entry(self.dialog_window, width=15)
        self.entry.grid(row=1, column=1, columnspan=2, pady=0)

        submit_button = tk.Button(self.dialog_window, text="Apply", command=self.submit_input)
        submit_button.grid(row=2, column=1, padx=5, pady=10, sticky=tk.E)

        cancel_button = tk.Button(self.dialog_window, text="Cancel", command=self.cancel_input)
        cancel_button.grid(row=2, column=2, padx=5, pady=10, sticky=tk.W)

        # Bind the close window action (clicking the 'X' button) to the close_window method
        self.dialog_window.protocol("WM_DELETE_WINDOW", self.close_window)


    def submit_input(self):
        self.result = self.entry.get()
        self.dialog_window.destroy()

    def cancel_input(self):
        self.result = None
        self.dialog_window.destroy()


    def error_dialog(self, message):
        x = 815
        y = 514
        width = 225
        height = 106

        error_window = tk.Toplevel(self.canvas._tkcanvas.master)
        error_window.geometry(f"{width}x{height}+{x}+{y}")
        error_window.title("ERROR")

        label = tk.Label(error_window, text=message)
        label.pack(pady=15)

        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy, width=12)
        ok_button.pack(pady=10)

    def close_window(self):
        self.result = None
        self.dialog_window.destroy()
