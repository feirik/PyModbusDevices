import tkinter as tk
from functools import partial

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
from colors import HPHMI

class ButtonView:
    def __init__(self, master, controller):
        self.controller = controller
        self.fig, self.ax = plt.subplots(figsize=(4.4, 3.2))
        
        # Hide the default axis
        self.ax.axis('off')
        
        # Style attributes
        self.fig.patch.set_facecolor(HPHMI.gray)  # Set figure background color
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor=HPHMI.dark_gray, linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        # Initial setup
        self._setup_view()

        # Embed the widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        

    def _setup_view(self):
        # Set point button
        self.sp_button_ax = self.fig.add_axes([0.075, 0.74, 0.314, 0.12])
        
        # Create the button with hover effect
        self.sp_button = Button(self.sp_button_ax, 'SET\nSET POINT', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.sp_button.on_clicked(partial(self._on_button_click_set_value, title="Update Set Point", prompt="Enter value (0-1024):", addr=2))

        # Give it a thick border (You can adjust the rectangle's linewidth for the desired thickness)
        # Here, the rectangle is slightly smaller than the full button
        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.sp_button_ax.add_patch(rectangle)

        # Max limit button
        self.max_button_ax = self.fig.add_axes([0.075, 0.575, 0.314, 0.12])
        
        # Create the button with hover effect
        self.max_button = Button(self.max_button_ax, 'SET\nMAX LIMIT', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.max_button.on_clicked(partial(self._on_button_click_set_value, title="Set Max Limit", prompt="Enter value (0-1024):", addr=4))

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.max_button_ax.add_patch(rectangle)

        # Min limit button
        self.min_button_ax = self.fig.add_axes([0.075, 0.41, 0.314, 0.12])

        # Create the button with hover effect
        self.min_button = Button(self.min_button_ax, 'SET\nMIN LIMIT', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.min_button.on_clicked(partial(self._on_button_click_set_value, title="Set Min Limit", prompt="Enter value (0-1024):", addr=3))

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.min_button_ax.add_patch(rectangle)

        # Enable output toggle button
        self.en_output_button_ax = self.fig.add_axes([0.075, 0.245, 0.314, 0.12])

        # Create the button with hover effect
        self.en_output_button = Button(self.en_output_button_ax, 'TOGGLE\nENABLE OUTPUT', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.en_output_button.on_clicked(partial(self._on_toggle_button_click, title="Change Enable Output", prompt="Enable output will be toggeled.", addr=0))

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.en_output_button_ax.add_patch(rectangle)

        # Enable override toggle button
        self.en_override_button_ax = self.fig.add_axes([0.075, 0.08, 0.314, 0.12])

        # Create the button with hover effect
        self.en_override_button = Button(self.en_override_button_ax, 'TOGGLE\nENBL OVERRIDE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.en_override_button.on_clicked(partial(self._on_toggle_button_click, title="Change Enable Override", prompt="Enable override will be toggeled.", addr=1))

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.en_override_button_ax.add_patch(rectangle)

        # View 0-400V button
        self.high_view_button_ax = self.fig.add_axes([0.495, 0.295, 0.25, 0.07])

        # Create the button with hover effect
        self.high_view_button = Button(self.high_view_button_ax, '0-400V', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.high_view_button.on_clicked(self.controller.set_high_view)

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.high_view_button_ax.add_patch(rectangle)

        # View 200-260V button
        self.def_view_button_ax = self.fig.add_axes([0.495, 0.1875, 0.25, 0.07])

        # Create the button with hover effect
        self.def_view_button = Button(self.def_view_button_ax, '200-260V', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.def_view_button.on_clicked(self.controller.set_default_view)

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.def_view_button_ax.add_patch(rectangle)

        # View 100-140V button
        self.low_view_button_ax = self.fig.add_axes([0.495, 0.08, 0.25, 0.07])

        # Create the button with hover effect
        self.low_view_button = Button(self.low_view_button_ax, '100-140V', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.low_view_button.on_clicked(self.controller.set_low_view)

        rectangle = plt.Rectangle((0.033, 0.03), 0.94, 0.94, 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1.5)
        self.low_view_button_ax.add_patch(rectangle)

        # Create faceplate zone
        rect = [0.465, 0.52, 0.51, 0.433]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Reserved Faceplate Zone\n", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create select view rectangle
        rect = [0.465, 0.045, 0.31, 0.40]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        y_placement = 0.405

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, y_placement, "SELECT VIEW", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create manual actions zone
        rect = [0.028, 0.045, 0.41, 0.907]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        y_placement = 0.91

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, y_placement, "MANUAL ACTIONS", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create info rectangle
        rect = [0.8, 0.045, 0.175, 0.40]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Static\nInfo\nZone", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)



    def _on_button_click_set_value(self, event, title, prompt, addr):
        # Display the custom input dialog and get the user input
        self.input_dialog(title, prompt)
        self.canvas._tkcanvas.master.wait_window(self.dialog_window)  # Wait until the dialog is closed
        user_input = self.result

        if user_input is not None:
            try:
                user_input = int(user_input)
                if 0 <= user_input <= 1024:
                    # Check the result of the write operation
                    success = self.controller.write_register(addr, user_input)
                    if not success:
                        self.error_dialog("Register write failed.")
                else:
                    self.error_dialog("Input out of range.")

            except ValueError:
                self.error_dialog("Invalid input.")


    def _on_toggle_button_click(self, event, title, prompt, addr):
        # Display the toggle dialog
        self.toggle_dialog(title, prompt)
        self.canvas._tkcanvas.master.wait_window(self.dialog_window)  # Wait until the dialog is closed
        confirmed = self.result

        if confirmed:
            current_value = self.controller.read_coil(addr)

            # Toggle the value
            toggled_value = 1 if current_value == 0 else 0

            # Write the toggled value back to the coil
            result = self.controller.write_coil(addr, toggled_value)


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

        cancel_button = tk.Button(self.dialog_window, text="Cancel", command=self.cancel_window)
        cancel_button.grid(row=2, column=2, padx=5, pady=10, sticky=tk.W)

        # Bind the close window action (clicking the 'X' button) to the close_window method
        self.dialog_window.protocol("WM_DELETE_WINDOW", self.close_window)


    def toggle_dialog(self, title, prompt):
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
        label.grid(row=0, column=1, columnspan=2, pady=15)

        confirm_button = tk.Button(self.dialog_window, text="Confirm", command=self.confirm_toggle)
        confirm_button.grid(row=1, column=1, padx=5, pady=10, sticky=tk.E)

        cancel_button = tk.Button(self.dialog_window, text="Cancel", command=self.cancel_window)
        cancel_button.grid(row=1, column=2, padx=5, pady=10, sticky=tk.W)

        # Bind the close window action (clicking the 'X' button) to the close_window method
        self.dialog_window.protocol("WM_DELETE_WINDOW", self.close_window)


    def submit_input(self):
        self.result = self.entry.get()
        self.dialog_window.destroy()

    def cancel_window(self):
        self.result = None
        self.dialog_window.destroy()

    def confirm_toggle(self):
        self.result = True
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
