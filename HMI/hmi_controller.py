import tkinter as tk
import sys
import os

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1
NUMBER_OF_COILS = 1

from Client.api_pymbtget import ModbusTCPClientAPI
class HMIController:
    def __init__(self, view):
        self.view = view

        # Link buttons to methods
        self.view.read_coil_button['command'] = self.read_coil
        self.view.write_coil_button['command'] = self.write_coil

    def read_coil(self):
        try:
            # Get coil address from Entry field
            coil_address = int(self.view.coil_address_entry.get())

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)

            result = client.read_coils(coil_address, NUMBER_OF_COILS)

            print("we're here read")

            client.close()

            # Update GUI with result
            self.view.read_result_label['text'] = 'Read result: ' + str(result)
        except Exception as e:
            self.view.read_result_label['text'] = 'Error: ' + str(e)

    def write_coil(self):
        try:
            # Get coil address and value from Entry fields
            coil_address = int(self.view.coil_address_entry.get())
            coil_value = bool(int(self.view.coil_value_entry.get()))

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)

            print("we're here")

            # Use Modbus client to write coil
            result = client.write_coil(coil_address, coil_value)

            client.close()

            # Update GUI with result
            self.view.write_result_label['text'] = 'Write result: ' + str(result)
        except Exception as e:
            self.view.write_result_label['text'] = 'Error: ' + str(e)