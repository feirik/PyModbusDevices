import tkinter as tk
import sys
import os

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1

from Client.api_pymbtget import ModbusTCPClientAPI

class HMIController:
    def __init__(self, view):
        self.view = view

        # Link buttons to methods
        self.view.read_coil_button['command'] = self.read_coil
        self.view.write_coil_button['command'] = self.write_coil
        
        # Initialization for periodic reading of holding register
        self.read_holding_register_periodically()

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
        try:
            # Create a new Modbus client for the operation
            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            
            value = client.read_holding_register(0) # Reading from address 0
            self.view.read_holding_result_label['text'] = str(value)
            
            client.close()
        except Exception as e:
            self.view.read_holding_result_label['text'] = 'Error: ' + str(e)
        # Schedule the function to run again after 1 second
        self.view.after(1000, self.read_holding_register_periodically)
