import tkinter as tk
import os
import sys

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI

from dynamic_bar import DynamicBar
from graph import GraphView
from indicator import Indicator
from button import ButtonView

READ_INTERVAL_MS = 1000

# Define constants for dynamic bar layout
DYNAMIC_BAR_ROW = 0
DYNAMIC_BAR_COLUMN = 5
DYNAMIC_BAR_COLUMN_SPAN = 4
DYNAMIC_BAR_ROW_SPAN = 8
DYNAMIC_BAR_PAD_Y = 20
DYNAMIC_BAR_PAD_X = 20

# Define constants for the button view layout
BUTTON_VIEW_ROW = 9
BUTTON_VIEW_COLUMN = 5
BUTTON_VIEW_COLUMN_SPAN = 4
BUTTON_VIEW_ROW_SPAN = 8
BUTTON_VIEW_PAD_Y = 20
BUTTON_VIEW_PAD_X = 20

class HMIController:
    def __init__(self, view, host, port, timeout, unit_id):
        self.view = view
        self.host = host
        self.port = port
        self.timeout = timeout
        self.unit_id = unit_id

        # Initialize the Graph
        self.graph = GraphView(self.view)
        self.graph.canvas_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
        
        # Initialization for periodic reading of holding register
        self._after_id = self.view.after(READ_INTERVAL_MS, self.read_holding_register_periodically)

        self.dynamic_bar = DynamicBar(self.view)
        self.dynamic_bar.canvas_widget.grid(row=DYNAMIC_BAR_ROW, 
                                            column=DYNAMIC_BAR_COLUMN, 
                                            columnspan=DYNAMIC_BAR_COLUMN_SPAN, 
                                            rowspan=DYNAMIC_BAR_ROW_SPAN, 
                                            pady=DYNAMIC_BAR_PAD_Y, 
                                            padx=DYNAMIC_BAR_PAD_X)

        self.indicator = Indicator(self.view)

        self.button_view = ButtonView(self.view, self)
        self.button_view.canvas_widget.grid(row=BUTTON_VIEW_ROW, 
                                            column=BUTTON_VIEW_COLUMN, 
                                            columnspan=BUTTON_VIEW_COLUMN_SPAN, 
                                            rowspan=BUTTON_VIEW_ROW_SPAN, 
                                            pady=BUTTON_VIEW_PAD_Y, 
                                            padx=BUTTON_VIEW_PAD_X)

        # Bind the window's close event
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def set_default_view(self, event=None):
        self.graph.set_view_type('default')

    def set_low_view(self, event=None):
        self.graph.set_view_type('low')

    def set_high_view(self, event=None):
        self.graph.set_view_type('high')


    def write_register(self, addr, value):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        result = client.write_register(addr, value)
        client.close()
        return result

    def read_coil(self, addr):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        current_value = client.read_coil(addr)
        client.close()
        return current_value

    def write_coil(self, addr, value):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        result = client.write_coil(addr, value)
        client.close()
        return result

    def read_holding_register_periodically(self):
        # First, we cancel any previous scheduling to ensure that we don't have multiple calls scheduled
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)

        try:
            # Read input voltage
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            in_voltage_value = client.read_holding_register(0)
            client.close()

            # Read output voltage
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            out_voltage_value = client.read_holding_register(1)
            client.close()

            # Update the graph with input and output voltage values
            self.graph.update_graph(in_voltage_value, out_voltage_value)

            # Read set point
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            set_point = client.read_holding_register(2)
            client.close()

            # Read minimum set point limit
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            min_set_point = client.read_holding_register(3)
            client.close()

            # Read maximum set point limit
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            max_set_point = client.read_holding_register(4)
            client.close()

            # Update the dynamic bar with read values
            self.dynamic_bar.set_value(min_set_point, max_set_point, set_point)

            # Read enable output coil status
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            enable_output = client.read_coil(0)
            client.close()

            # Read enable override coil status
            client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
            enable_override = client.read_coil(1)
            client.close()

            # Update indicator statuses with read coil values
            self.indicator.update_status(enable_output, enable_override)

            # Save the after_id to cancel it later upon closing
            self._after_id = self.view.after(READ_INTERVAL_MS, self.read_holding_register_periodically)

        except Exception as e:
            print('Error:', e)


    def on_closing(self):
        """Called when the Tkinter window is closing."""
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        self.view.master.quit()
        self.view.master.destroy()