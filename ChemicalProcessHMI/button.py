import tkinter as tk
from functools import partial
from tkinter import Toplevel, Button, Label
from PIL import Image, ImageTk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
from colors import HPHMI

# Dialog dimensions and position
DIALOG_X_POSITION = 935
DIALOG_Y_POSITION = 514
DIALOG_WIDTH = 362
DIALOG_HEIGHT = 106

INPUT_LOW_LIMIT = 0
INPUT_HIGH_LIMIT = 100

POPUP_WIDTH = 1280
POPUP_HEIGHT = 720

# Button, text and rectangle positions
BTN_POS = {
    'powder_btn': [0.075, 0.78, 0.314, 0.07],
    'powder_prop_btn': [0.075, 0.68, 0.314, 0.07],
    'liquid_btn': [0.075, 0.58, 0.314, 0.07],
    'liquid_prop': [0.075, 0.48, 0.314, 0.07],
    'relief_btn': [0.075, 0.38, 0.314, 0.07],
    'outlet_btn': [0.075, 0.28, 0.314, 0.07],
    'mixer_btn': [0.075, 0.18, 0.314, 0.07],
    'heater_btn': [0.075, 0.08, 0.314, 0.07],
    'auto_btn': [0.495, 0.23, 0.25, 0.11],
    'show_drawing_btn': [0.495, 0.08, 0.25, 0.11],
}

RECT = {
    'faceplate_zone': [0.465, 0.52, 0.51, 0.433],
    'misc_operations': [0.465, 0.045, 0.31, 0.40],
    'manual_actions': [0.028, 0.045, 0.41, 0.907],
    'info_zone': [0.8, 0.045, 0.175, 0.40]
}

BTN_RECT_BORDER = {
    'start': (0.033, 0.03),
    'size': (0.94, 0.94),
    'line_width': 1.5
}

TEXT_PLACEMENT = {
    'misc_operations': (0, 0.405),
    'manual_actions': (0, 0.91),
    'info_zone': (0, -0.02)  # Relative to the center_y
}

class ButtonView:
    def __init__(self, master, controller, os):
        self.controller = controller
        self.fig, self.ax = plt.subplots(figsize=(7, 3.2))
        self.os = os

        # Update location of popup dialog for PIOS
        global DIALOG_X_POSITION, DIALOG_Y_POSITION

        if self.os == "PIOS":
            DIALOG_X_POSITION = 775
            DIALOG_Y_POSITION = 505
        
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
        # Powder inlet valve button
        self.powder_valve_ax = self.fig.add_axes(BTN_POS['powder_btn'])

        # Create the button with hover effect
        self.powder_valve = Button(self.powder_valve_ax, 'TOGGLE POWDER VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.powder_valve.on_clicked(partial(self._on_toggle_button_click, title="Change Powder Inlet Valve", prompt="Toggle powder inlet valve position.", addr=200))

        # Here, the rectangle is slightly smaller than the full button
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.powder_valve_ax.add_patch(rectangle)

        # Powder inlet propoprtional valve
        self.powder_prop_ax = self.fig.add_axes(BTN_POS['powder_prop_btn'])

        # Create the button with hover effect
        self.powder_prop = Button(self.powder_prop_ax, 'SET POWDER PROP VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.powder_prop.on_clicked(partial(self._on_button_click_set_value, title="Change Powder Prop. Valve", prompt="Set proportional valve position.", addr=231))

        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.powder_prop_ax.add_patch(rectangle)

        # Liquid inlet valve button
        self.liquid_valve_ax = self.fig.add_axes(BTN_POS['liquid_btn'])

        # Create the button with hover effect
        self.liquid_valve = Button(self.liquid_valve_ax, 'TOGGLE LIQUID VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.liquid_valve.on_clicked(partial(self._on_toggle_button_click, title="Change Liquid Inlet Valve", prompt="Toggle liquid inlet valve position.", addr=201))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.liquid_valve_ax.add_patch(rectangle)

        # Liquid inlet propoprtional valve
        self.liquid_prop_ax = self.fig.add_axes(BTN_POS['liquid_prop'])

        # Create the button with hover effect
        self.liquid_prop = Button(self.liquid_prop_ax, 'SET LIQUID PROP VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.liquid_prop.on_clicked(partial(self._on_button_click_set_value, title="Change Liquid Prop. Valve", prompt="Set proportional valve position.", addr=233))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.liquid_prop_ax.add_patch(rectangle)

        # Relief valve button
        self.relief_valve_ax = self.fig.add_axes(BTN_POS['relief_btn'])

        # Create the button with hover effect
        self.relief_valve = Button(self.relief_valve_ax, 'TOGGLE RELIEF VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.relief_valve.on_clicked(partial(self._on_toggle_button_click, title="Change Safety Relief Valve", prompt="Toggle relief valve position.", addr=203))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.relief_valve_ax.add_patch(rectangle)

        # Outlet valve button
        self.outlet_valve_ax = self.fig.add_axes(BTN_POS['outlet_btn'])

        # Create the button with hover effect
        self.outlet_valve = Button(self.outlet_valve_ax, 'TOGGLE OUTLET VALVE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.outlet_valve.on_clicked(partial(self._on_toggle_button_click, title="Change Outlet Valve", prompt="Toggle outlet valve position.", addr=204))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.outlet_valve_ax.add_patch(rectangle)

        # Mixer button
        self.mixer_valve_ax = self.fig.add_axes(BTN_POS['mixer_btn'])

        # Create the button with hover effect
        self.mixer_valve = Button(self.mixer_valve_ax, 'TOGGLE TANK MIXER', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.mixer_valve.on_clicked(partial(self._on_toggle_button_click, title="Change Mixer Status", prompt="Toggle mixer operation.", addr=202))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.mixer_valve_ax.add_patch(rectangle)

        # Heater button
        self.heater_ax = self.fig.add_axes(BTN_POS['heater_btn'])

        # Create the button with hover effect
        self.heater = Button(self.heater_ax, 'SET HEATER SETTING', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.heater.on_clicked(partial(self._on_button_click_set_value, title="Change Heater Setting", prompt="Set heater output.", addr=236))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.heater_ax.add_patch(rectangle)

        # Auto mode button
        self.auto_button_ax = self.fig.add_axes(BTN_POS['auto_btn'])

        # Create the button with hover effect
        self.auto_button = Button(self.auto_button_ax, 'TOGGLE AUTO MODE', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.auto_button.on_clicked(partial(self._on_toggle_button_click, title="Change Auto Mode", prompt="Toggle auto mode.", addr=205))

        # Add the rectangle
        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.auto_button_ax.add_patch(rectangle)

        # Add button to show system overview
        self.show_drawing_button_ax = self.fig.add_axes(BTN_POS['show_drawing_btn'])
        self.show_drawing_button = Button(self.show_drawing_button_ax, 'SHOW SYSTEM', color=HPHMI.dark_gray, hovercolor=HPHMI.dark_green)
        self.show_drawing_button.on_clicked(self.show_image_popup)

        rectangle = plt.Rectangle(BTN_RECT_BORDER['start'], *BTN_RECT_BORDER['size'], 
                                  facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=BTN_RECT_BORDER['line_width'])
        self.show_drawing_button_ax.add_patch(rectangle)

        # Create faceplate zone
        rect = RECT['faceplate_zone']

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

        # Create misc operations rectangle
        rect = RECT['misc_operations']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Create manual actions zone
        rect = RECT['manual_actions']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # Create info rectangle
        rect = RECT['info_zone']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.dark_gray, linewidth=1, clip_on=False)
        )

        # For 'MISC OPERATIONS'
        rect = RECT['misc_operations']
        center_x = rect[0] + rect[2] / 2
        y_placement = TEXT_PLACEMENT['misc_operations'][1]

        self.desc_text = self.ax.text(center_x, y_placement, "MISC OPERATIONS", weight='bold', ha='center',
                        va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # For 'MANUAL ACTIONS'
        rect = RECT['manual_actions']
        center_x = rect[0] + rect[2] / 2
        y_placement = TEXT_PLACEMENT['manual_actions'][1]

        self.desc_text = self.ax.text(center_x, y_placement, "MANUAL ACTIONS", weight='bold', ha='center',
                        va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # For 'Static Info Zone'
        rect = RECT['info_zone']
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 + TEXT_PLACEMENT['info_zone'][1]

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
                if INPUT_LOW_LIMIT <= user_input <= INPUT_HIGH_LIMIT:
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
        self.dialog_window = tk.Toplevel(self.canvas._tkcanvas.master)
        self.dialog_window.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}+{DIALOG_X_POSITION}+{DIALOG_Y_POSITION}")
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
        self.dialog_window = tk.Toplevel(self.canvas._tkcanvas.master)
        self.dialog_window.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}+{DIALOG_X_POSITION}+{DIALOG_Y_POSITION}")
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
        error_window = tk.Toplevel(self.canvas._tkcanvas.master)
        error_window.geometry(f"{DIALOG_WIDTH}x{DIALOG_HEIGHT}+{DIALOG_X_POSITION}+{DIALOG_Y_POSITION}")
        error_window.title("ERROR")

        label = tk.Label(error_window, text=message)
        label.pack(pady=15)

        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy, width=12)
        ok_button.pack(pady=10)


    def close_window(self):
        self.result = None
        self.dialog_window.destroy()


    def show_image_popup(self, event):
        # Create a top-level window
        self.popup = tk.Toplevel()
        self.popup.title("Chemical Process Line Schematic")
        self.popup.geometry(f"{POPUP_WIDTH}x{POPUP_HEIGHT}")

        # Load and display the image
        image = Image.open("assets/Chemical_process_overview.PNG")
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(self.popup, image=photo)
        label.image = photo  # Keep a reference to avoid garbage collection
        label.pack()

        # Create labels for displaying numbers on the image
        self.value_labels = {
            "powder_inlet_valve": tk.Label(self.popup, text="Load", bg=HPHMI.gray, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "liquid_inlet_valve": tk.Label(self.popup, text="Load", bg=HPHMI.gray, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "powder_prop_valve": tk.Label(self.popup, text="Load", bg=HPHMI.gray, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "liquid_prop_valve": tk.Label(self.popup, text="Load", bg=HPHMI.gray, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "powder_feed_tank": tk.Label(self.popup, text="Load", bg=HPHMI.gray, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "liquid_feed_tank": tk.Label(self.popup, text="Load", bg=HPHMI.white, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "generator_voltage": tk.Label(self.popup, text="Load", bg=HPHMI.white, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "grid_power": tk.Label(self.popup, text="Load", bg=HPHMI.white, fg=HPHMI.dark_blue,
                                font=("Arial", 14, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
            "bearing_temperature": tk.Label(self.popup, text="Load", bg=HPHMI.white, fg=HPHMI.dark_blue,
                                font=("Arial", 12, "bold"), highlightbackground=HPHMI.dark_gray,
                                highlightcolor=HPHMI.dark_gray, highlightthickness=2, padx=6, pady=4),
        }
        
        # Position the labels on the image
        self.value_labels["powder_inlet_valve"].place(relx=0.275, rely=0.18, anchor="center")
        self.value_labels["liquid_inlet_valve"].place(relx=0.275, rely=0.775, anchor="center")
        self.value_labels["powder_prop_valve"].place(relx=0.37, rely=0.395, anchor="center")
        self.value_labels["liquid_prop_valve"].place(relx=0.37, rely=0.775, anchor="center")
        self.value_labels["powder_feed_tank"].place(relx=0.18, rely=0.175, anchor="center")
        self.value_labels["liquid_feed_tank"].place(relx=0.18, rely=0.61, anchor="center")
        self.value_labels["generator_voltage"].place(relx=0.31, rely=0.11, anchor="center")
        self.value_labels["grid_power"].place(relx=0.91, rely=0.39, anchor="center")
        self.value_labels["bearing_temperature"].place(relx=0.27, rely=0.39, anchor="center")

        # Add a close button
        close_button = tk.Button(self.popup, text="Close Window", command=self.popup.destroy, 
                                 font=("Arial", 12), padx=25, pady=5)
        close_button.place(relx=0.5, rely=0.95, anchor="center")


    def update_labels(self, water_in, exc_sw, tr_sw, grid_sw, turb_speed, bear_temp, gen_vol, grid_pwr):
        # Ensure that the update occurs only if the popup window is open and visible
        if hasattr(self, 'popup') and self.popup.winfo_exists() and self.popup.winfo_viewable():
            if water_in:
                self.value_labels['powder_inlet_valve']['text'] = "OPEN"
                self.value_labels['powder_inlet_valve']['bg'] = HPHMI.white
            else:
                self.value_labels['powder_inlet_valve']['text'] = "CLOSED"
                self.value_labels['powder_inlet_valve']['bg'] = HPHMI.dark_gray

            if water_in:
                self.value_labels['liquid_inlet_valve']['text'] = "OPEN"
                self.value_labels['liquid_inlet_valve']['bg'] = HPHMI.white
            else:
                self.value_labels['liquid_inlet_valve']['text'] = "CLOSED"
                self.value_labels['liquid_inlet_valve']['bg'] = HPHMI.dark_gray

            if exc_sw:
                self.value_labels['excite_breaker']['text'] = "ON"
                self.value_labels['excite_breaker']['bg'] = HPHMI.white
            else:
                self.value_labels['excite_breaker']['text'] = "OFF"
                self.value_labels['excite_breaker']['bg'] = HPHMI.dark_gray

            if tr_sw:
                self.value_labels['transformer_breaker_left']['text'] = "ON"
                self.value_labels['transformer_breaker_left']['bg'] = HPHMI.white
                self.value_labels['transformer_breaker_right']['text'] = "ON"
                self.value_labels['transformer_breaker_right']['bg'] = HPHMI.white
            else:
                self.value_labels['transformer_breaker_left']['text'] = "OFF"
                self.value_labels['transformer_breaker_left']['bg'] = HPHMI.dark_gray
                self.value_labels['transformer_breaker_right']['text'] = "OFF"
                self.value_labels['transformer_breaker_right']['bg'] = HPHMI.dark_gray

            if grid_sw:
                self.value_labels['grid_breaker']['text'] = "ON"
                self.value_labels['grid_breaker']['bg'] = HPHMI.white
            else:
                self.value_labels['grid_breaker']['text'] = "OFF"
                self.value_labels['grid_breaker']['bg'] = HPHMI.dark_gray

            self.value_labels['turbine_speed']['text'] = turb_speed
            self.value_labels['generator_voltage']['text'] = gen_vol
            self.value_labels["grid_power"]['text'] = grid_pwr
            self.value_labels["bearing_temperature"]['text'] = str(bear_temp) + "°C"
            
