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

            normalized_value = (in_voltage_value - 200) / 60  # Example normalization logic, modify as needed
            self.dynamic_bar.set_value(normalized_value)

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