#!/usr/bin/env python3

import tkinter as tk
from hmi_view import HMIView
from hmi_controller import HMIController

def main():
    # Instantiate a Tkinter root window
    root = tk.Tk()

    # Set window title
    root.title("HMI - Modbus Voltage Regulator")

    # Set window size
    root.geometry("1024x768")

    # Instantiate view and controller
    view = HMIView(master=root)
    controller = HMIController(view=view)

    # Start the GUI event loop
    root.mainloop()

# Entry point for the application
if __name__ == "__main__":
    main()