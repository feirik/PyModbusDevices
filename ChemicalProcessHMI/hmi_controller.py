import tkinter as tk
import os
import sys
import threading
import time

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI

from dynamic_bar import DynamicBar
from graph import GraphView
from indicator import Indicator
from button import ButtonView

# Update constants
READ_INTERVAL_MS = 1000
DELAY_TIME=0.05

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

# Modbus coil addresses
POWDER_INLET_ADDR = 200
LIQUID_INLET_ADDR = 201
MIXER_ADDR = 202
SAFETY_RELIEF_VALVE_ADDR = 203
OUTLET_VALVE_ADDR = 204
AUTO_CONTROL_ENABLE = 205

# Modbus register addresses
POWDER_TANK_LEVEL_ADDR = 230
PROPORTIONAL_POWDER_FEED_ADDR = 231
LIQUID_TANK_LEVEL_ADDR = 232
PROPORTIONAL_LIQUID_FEED_ADDR = 233
INTERMEDIATE_SLURRY_LEVEL_ADDR = 234
PROCESSED_PRODUCT_LEVEL_ADDR = 235
HEATER_ADDR = 236
MIX_TANK_PRESSURE_ADDR = 237
TANK_TEMP_LOWER_ADDR = 238
TANK_TEMP_UPPER_ADDR = 239
POWDER_MIXING_VOLUME_ADDR = 240
LIQUID_MIXING_VOLUME_ADDR = 241
PROD_FLOW_ADDR = 242
PROD_FLOW_EST_MINUTE_ADDR = 243

# Modbus constants for chemical process
NUMBER_OF_COILS = 6
NUMBER_OF_REGISTERS = 14


class HMIController:
    def __init__(self, view, host, port, timeout, unit_id, os):
        self.view = view
        self.host = host
        self.port = port
        self.timeout = timeout
        self.unit_id = unit_id
        self.os = os

        # Store state of read values
        self.data = None

        # Initialize the Graph
        self.graph = GraphView(self.view)
        self.graph.canvas_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=20)
        
        # Initialization for periodic reading of holding register
        self._after_id = self.view.after(READ_INTERVAL_MS, self.read_data_periodically)

        self.dynamic_bar = DynamicBar(self.view)
        self.dynamic_bar.canvas_widget.grid(row=DYNAMIC_BAR_ROW, 
                                            column=DYNAMIC_BAR_COLUMN, 
                                            columnspan=DYNAMIC_BAR_COLUMN_SPAN, 
                                            rowspan=DYNAMIC_BAR_ROW_SPAN, 
                                            pady=DYNAMIC_BAR_PAD_Y, 
                                            padx=DYNAMIC_BAR_PAD_X)

        self.indicator = Indicator(self.view)

        self.button_view = ButtonView(self.view, self, self.os)
        self.button_view.canvas_widget.grid(row=BUTTON_VIEW_ROW, 
                                            column=BUTTON_VIEW_COLUMN, 
                                            columnspan=BUTTON_VIEW_COLUMN_SPAN, 
                                            rowspan=BUTTON_VIEW_ROW_SPAN, 
                                            pady=BUTTON_VIEW_PAD_Y, 
                                            padx=BUTTON_VIEW_PAD_X)

        # Bind the window's close event
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_closing)


    def write_register(self, addr, value):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        result = client.write_register(addr, value)
        client.close()
        return result


    def write_coil(self, addr, value):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        result = client.write_coil(addr, value)
        client.close()
        return result


    def read_coil(self, addr):
        client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
        current_value = client.read_coil(addr)
        client.close()
        return current_value


    def get_current_value(self, addr):
        return self.data[addr]


    def fetch_data_threaded(self, callback):
        def run():
            try:
                data = {}

                client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
                coils_array = client.read_multiple_coils(POWDER_INLET_ADDR, NUMBER_OF_COILS)
                client.close()

                # Map the coils values to their corresponding addresses
                if coils_array:
                    for i, value in enumerate(coils_array):
                        address = POWDER_INLET_ADDR + i
                        data[address] = value

                # Short delay to ensure sending and receiving is finished
                time.sleep(DELAY_TIME)

                client = ModbusTCPClientAPI(self.host, self.port, self.timeout, self.unit_id)
                register_array = client.read_multiple_holding_registers(POWDER_TANK_LEVEL_ADDR, NUMBER_OF_REGISTERS)
                client.close()

                # Map the register values to their corresponding addresses
                if register_array:
                    for i, value in enumerate(register_array):
                        address = POWDER_TANK_LEVEL_ADDR + i
                        data[address] = value


                self.view.after(0, callback, data)  # Schedule the callback on the main thread
            except Exception as e:
                print(f"Error fetching data in background thread: {e}")
        
        # Start the background thread
        threading.Thread(target=run, daemon=True).start()


    def process_fetched_data(self, data):
        if data:
            self.data = data  # Update the data attribute on the main thread
        else:
            print("No data received or data fetch failed.")


    def read_data_periodically(self):
        # First, we cancel any previous scheduling to ensure that we don't have multiple calls scheduled
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)

        # Start the data fetching process in a separate thread
        self.fetch_data_threaded(self.process_fetched_data)

        if self.data:
            self.graph.update_graph(self.data[INTERMEDIATE_SLURRY_LEVEL_ADDR], self.data[PROCESSED_PRODUCT_LEVEL_ADDR])

            # Temp Heater Pressure PowderMix LiquidMix

            tank_temp = self.data[TANK_TEMP_UPPER_ADDR]
            heater = self.data[HEATER_ADDR]
            pressure = self.data[MIX_TANK_PRESSURE_ADDR]
            powder_vol = self.data[POWDER_MIXING_VOLUME_ADDR]
            liquid_vol = self.data[LIQUID_MIXING_VOLUME_ADDR]
            prod_flow = self.data[PROD_FLOW_EST_MINUTE_ADDR]

            self.dynamic_bar.update_bars(tank_temp, heater, pressure, powder_vol, liquid_vol, prod_flow)

            powder_in = self.data[POWDER_INLET_ADDR]
            liquid_in = self.data[LIQUID_INLET_ADDR]
            mixer = self.data[MIXER_ADDR]
            relief_valve = self.data[SAFETY_RELIEF_VALVE_ADDR]
            outlet_valve = self.data[OUTLET_VALVE_ADDR]
            auto_mode = self.data[AUTO_CONTROL_ENABLE]

            self.indicator.update_status(powder_in, liquid_in, mixer, relief_valve, outlet_valve, auto_mode)
            self.button_view.update_labels(self.data)

        # Save the after_id to cancel it later upon closing
        self._after_id = self.view.after(READ_INTERVAL_MS, self.read_data_periodically)


    def on_closing(self):
        """Called when the Tkinter window is closing."""
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        self.view.master.quit()
        self.view.master.destroy()