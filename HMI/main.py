#!/usr/bin/env python3

import tkinter as tk
from hmi_view import HMIView
from hmi_controller import HMIController

WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = "HMI - Modbus Voltage Regulator"

def main():
    # Instantiate a Tkinter root window
    root = tk.Tk()

    # Set window title
    root.title(WINDOW_TITLE)

    # Set window size
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Instantiate view and controller
    view = HMIView(master=root)
    controller = HMIController(view=view)

    # Start the GUI event loop
    root.mainloop()

# Entry point for the application
if __name__ == "__main__":
    main()