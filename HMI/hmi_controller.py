import tkinter as tk
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI

IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1

class HMIController:
    def __init__(self, view):
        self.view = view
        self.data = []  # Store data for plotting

        # Set up the Matplotlib figure and axis for the graph
        self.setup_graph_view()

        # Link buttons to methods
        self.view.read_coil_button['command'] = self.read_coil
        self.view.write_coil_button['command'] = self.write_coil
        
        # Initialization for periodic reading of holding register
        self._after_id = self.view.after(1000, self.read_holding_register_periodically)

        # Bind the window's close event
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.average_voltage_array = []
        self.timestamps = []  # Store timestamps for plotting

    def setup_graph_view(self):
        """Initialize the Matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=(5, 4))

        # Set the figure background color
        self.fig.patch.set_facecolor('#F3F3F3')

        # Set the axis background color
        self.ax.set_facecolor('#F3F3F3')
        
        # Set consistent intervals for the X and Y axes
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        self.ax.set_ylim(200, 260)  # Voltage range from 200 to 260
        
        # Assuming the normal range is 220 to 240
        self.ax.axhspan(220, 240, color='green', alpha=0.1, label='Normal Range')

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color('darkgreen')
        xticks[-1].set_weight('bold')
        
        # Label the axes
        self.ax.set_ylabel("0\nVoltage\nIn (V)", rotation=0, labelpad=20, va='center', 
                       bbox=dict(facecolor='none', edgecolor='blue', boxstyle='square', linewidth=2))
        
        self.ax.set_yticklabels([])

        # Use faint grid lines
        self.ax.grid(alpha=0.2)

        # Embed the Matplotlib figure into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.view)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=10, column=0, columnspan=2, pady=20)

        self.fig.tight_layout()

    def update_graph(self, value):
        """Update the Matplotlib plot with the new reading."""
        # Append the new value to the data list
        self.data.append(value)

        # If more than 60 data points, drop the oldest one
        if len(self.data) > 60:
            self.data.pop(0)

        # Update the Matplotlib plot
        self.ax.cla()
        
        # Re-shade the normal operating range after clearing the axis
        self.ax.axhspan(220, 240, color='green', alpha=0.1, label='Normal Range')
        
        # Handle the visual for outlier data
        color = 'blue'
        
        # Plot the data
        self.ax.plot(self.data, "-o", color=color, markersize=1)

        # Label the axes
        y_label_text = f"{round(value, 1)}\nVoltage\nIn (V)"
        self.ax.set_ylabel(y_label_text, rotation=0, labelpad=20, va='center', 
                       bbox=dict(facecolor='none', edgecolor='blue', boxstyle='square', linewidth=2))

        self.ax.set_yticklabels([])

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color('darkgreen')
        xticks[-1].set_weight('bold')
        
        # Set the axes labels and grid
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        self.ax.set_ylim(200, 260)  # Voltage range from 200 to 260
        self.ax.grid(alpha=0.2)
        self.fig.tight_layout()
        self.canvas.draw()
    

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


    def compute_average_voltage(self):
        return sum(self.average_voltage_array) / len(self.average_voltage_array)


    # Method to read the holding register
    def read_holding_register_periodically(self):
        # First, we cancel any previous scheduling to ensure that we don't have multiple calls scheduled
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        
        try:
            # Create a new Modbus client for the operation
            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            
            value = client.read_holding_register(0) # Reading from address 0
            self.view.read_holding_result_label['text'] = str(value)

            # Add the new reading to the list and ensure it only contains the last 5 readings
            self.average_voltage_array.append(value)
            if len(self.average_voltage_array) > 5:
                self.average_voltage_array.pop(0)
            
            # Compute the average of the last 5 readings
            avg_value = self.compute_average_voltage()

            # Update the graph with the new value
            self.update_graph(avg_value)

            # Save the after_id to cancel it later upon closing
            self._after_id = self.view.after(1000, self.read_holding_register_periodically)
            
            client.close()
        except Exception as e:
            self.view.read_holding_result_label['text'] = 'Error: ' + str(e)

    def on_closing(self):
        """Called when the Tkinter window is closing."""
        if hasattr(self, '_after_id'):
            self.view.after_cancel(self._after_id)
        self.view.master.quit()
        self.view.master.destroy()