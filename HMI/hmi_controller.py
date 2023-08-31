import tkinter as tk
import os
import sys

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI
from dynamic_bar import DynamicBar
from graph import GraphView

IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1

class HMIController:
    def __init__(self, view):
        self.view = view

        # Initialize the Graph
        self.graph = GraphView(self.view)
        self.graph.canvas_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        # Link buttons to methods
        self.view.read_coil_button['command'] = self.read_coil
        self.view.write_coil_button['command'] = self.write_coil
        
        # Initialization for periodic reading of holding register
        self._after_id = self.view.after(1000, self.read_holding_register_periodically)

        self.dynamic_bar = DynamicBar(self.view)
        self.dynamic_bar.canvas_widget.grid(row=0, column=5, pady=20, padx=20)

        # Bind the window's close event
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Add buttons to select graph view types
        self.view.default_button = tk.Button(self.view, text="200-260V View", command=self.set_default_view)
        self.view.default_button.grid(row=15, column=5)

        self.view.low_button = tk.Button(self.view, text="100-140V View", command=self.set_low_view)
        self.view.low_button.grid(row=16, column=5)

        self.view.high_button = tk.Button(self.view, text="0-400V View", command=self.set_high_view)
        self.view.high_button.grid(row=17, column=5)


    def set_default_view(self):
        self.graph.set_view_type('default')

    def set_low_view(self):
        self.graph.set_view_type('low')

    def set_high_view(self):
        self.graph.set_view_type('high')
        

    def read_coil(self):
        try:
            # Get coil address from Entry field
            coil_address = int(self.view.coil_address_entry.get() or "100")

            # Create a new Modbus client for the operation
            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            
            # Use the updated single coil read method
            result = client.read_coil(coil_address)

            client.close()

            # Update GUI with result
            self.view.read_result_label['text'] = 'Read result: ' + str(result)
        except Exception as e:
            self.view.read_result_label['text'] = 'Error: ' + str(e)

    def write_coil(self):
        try:
            # Get coil address and value from Entry fields
            coil_address = int(self.view.coil_address_entry.get() or "100")
            coil_value = bool(int(self.view.coil_value_entry.get() or "0"))

            # Create a new Modbus client for the operation
            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)

            # Use Modbus client to write coil
            result = client.write_coil(coil_address, coil_value)

            client.close()

            # Update GUI with result
            self.view.write_result_label['text'] = 'Write result: ' + str(result)
        except Exception as e:
            self.view.write_result_label['text'] = 'Error: ' + str(e)


    # Method to read the holding register
    def read_holding_register_periodically(self):
        # First, we cancel any previous scheduling to ensure that we don't have multiple calls scheduled
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        
        try:
            # Create a new Modbus client for the operation
            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            
            in_voltage_value = client.read_holding_register(0) # Reading from address 0
            self.view.read_holding_result_label['text'] = str(in_voltage_value)
            client.close()

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            out_voltage_value = client.read_holding_register(1)
            client.close()

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            set_point = client.read_holding_register(2)
            client.close()

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            min_set_point = client.read_holding_register(3)
            client.close()

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            max_set_point = client.read_holding_register(4)
            client.close()

            self.dynamic_bar.set_value(min_set_point, max_set_point, set_point)

            # Update the graph with the new values
            self.graph.update_graph(in_voltage_value, out_voltage_value)

            # Save the after_id to cancel it later upon closing
            self._after_id = self.view.after(1000, self.read_holding_register_periodically)
            
        except Exception as e:
            self.view.read_holding_result_label['text'] = 'Error: ' + str(e)


    def on_closing(self):
        """Called when the Tkinter window is closing."""
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        self.view.master.quit()
        self.view.master.destroy()