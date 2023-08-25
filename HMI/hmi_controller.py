import tkinter as tk
import os
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Add the parent directory of this script to the system path to allow importing modules from there
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Client.api_pymbtget import ModbusTCPClientAPI
from dynamic_bar import DynamicBar

IP_ADDRESS = "127.0.0.1"
SERVER_PORT = 11502
TIMEOUT = 5
UNIT_ID = 1

class HMIController:
    def __init__(self, view):
        self.view = view
        self.data_in = []  # Store data for plotting
        self.data_out = []

        # Set up the Matplotlib figure and axis for the graph
        self.setup_graph_view()

        # Link buttons to methods
        self.view.read_coil_button['command'] = self.read_coil
        self.view.write_coil_button['command'] = self.write_coil
        
        # Initialization for periodic reading of holding register
        self._after_id = self.view.after(1000, self.read_holding_register_periodically)

        self.dynamic_bar = DynamicBar(self.view)
        self.dynamic_bar.canvas_widget.grid(row=0, column=5, pady=20, padx=20)

        # Bind the window's close event
        self.view.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.average_voltage_array = []
        self.timestamps = []  # Store timestamps for plotting

    def setup_graph_view(self):
        """Initialize the Matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=(5, 3.2))

        # Set the figure background color
        self.fig.patch.set_facecolor('#D5D5D5')

        # Set the axis background color
        self.ax.set_facecolor('#D5D5D5')
        
        # Set consistent intervals for the X and Y axes
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        self.ax.set_ylim(200, 260)  # Voltage range from 200 to 260

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color('darkgreen')
        xticks[-1].set_weight('bold')
        
        # Input voltage label
        self.ax.set_ylabel("0\nVoltage\nIn (V)", rotation=0, labelpad=20, va='center', 
                       bbox=dict(facecolor='none', edgecolor='#0000D7', boxstyle='square', linewidth=2))
        
        # Output voltage label
        voltage_out_label_text = f"0\nVoltage\nOut (V)"
        x_position = -5.72
        y_position = 216
        self.ax.text(x_position, y_position, voltage_out_label_text, 
            rotation=0, ha='center', va='center',
            bbox=dict(facecolor='none', edgecolor='#CC6600', boxstyle='square', linewidth=2))

        self.ax.set_yticklabels([])

        # Manually add the y-labels at desired positions
        y_label_200 = self.ax.text(-1.5, 201, '200', ha='right', va='center')
        y_label_260 = self.ax.text(-1.5, 258, '260', ha='right', va='center')

        # Format the y-labels
        y_label_200.set_color('#008000')
        y_label_200.set_weight('bold')
        y_label_260.set_color('#008000')
        y_label_260.set_weight('bold')

        # Outline bar for in_voltage
        # x, y, width, height
        rect = [0.9439, 0.121, 0.015, 0.832]  # Adjust these values as needed
        voltage_in_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)

        # Outline bar for out_voltage
        # x, y, width, height
        rect = [0.96, 0.121, 0.015, 0.832]  # Adjust these values as needed
        voltage_out_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)

        self.fig.patches.extend([voltage_in_outline, voltage_out_outline])

        plt.setp(self.ax.spines.values(), color='#999999')

        # Use faint grid lines
        self.ax.grid(color='#999999', linestyle='--', linewidth=0.5, alpha=1)

        # Embed the Matplotlib figure into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.view)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        self.fig.tight_layout()


    def update_graph(self, voltage_in, voltage_out):
        """Update the Matplotlib plot with the new reading."""
        # Append the new voltage_in value to the data list
        self.data_in.append(voltage_in)
        self.data_out.append(voltage_out)

        # If more than 60 data points, drop the oldest one
        if len(self.data_in) > 60:
            self.data_in.pop(0)
        if len(self.data_out) > 60:
            self.data_out.pop(0)

        # Find the minimum and maximum values
        voltage_in_min = min(self.data_in)
        voltage_in_max = max(self.data_in)
        voltage_out_min = min(self.data_out)
        voltage_out_max = max(self.data_out)

        # Normalize these values according to the y-axis range
        y_axis_min = 200
        y_axis_max = 260
        y_range = y_axis_max - y_axis_min

        normalized_min_in = (voltage_in_min - y_axis_min) / y_range
        normalized_max_in = (voltage_in_max - y_axis_min) / y_range

        normalized_min_out = (voltage_out_min - y_axis_min) / y_range
        normalized_max_out = (voltage_out_max - y_axis_min) / y_range

        # Use the normalized values to set the height and starting point of the colored rectangle
        rect_height_in = normalized_max_in - normalized_min_in
        rect_y_in = 0.121 + normalized_min_in * 0.832  # Adjust starting point based on minimum value

        rect_height_out = normalized_max_out - normalized_min_out
        rect_y_out = 0.121 + normalized_min_out * 0.832  # Adjust starting point based on minimum value

        # Update the Matplotlib plot
        self.ax.cla()
        
        # Plot the data
        self.ax.plot(self.data_in, "-o", color='#0000D7', markersize=1)
        self.ax.plot(self.data_out, "-o", color='#CC6600', markersize=1)

        # Label the axes
        voltage_in_label_text = f"{round(voltage_in, 1)}\nVoltage\nIn (V)"
        self.ax.set_ylabel(voltage_in_label_text, rotation=0, labelpad=20, va='center', 
                       bbox=dict(facecolor='none', edgecolor='#0000D7', boxstyle='square', linewidth=2))

        # Output voltage label
        voltage_out_label_text = f"{voltage_out}\nVoltage\nOut (V)"
        x_position = -5.72
        y_position = 216
        self.ax.text(x_position, y_position, voltage_out_label_text, 
            rotation=0, ha='center', va='center',
            bbox=dict(facecolor='none', edgecolor='#CC6600', boxstyle='square', linewidth=2))

        self.ax.set_yticklabels([])

        # Manually add the y-labels at desired positions
        y_label_200 = self.ax.text(-1.5, 201, '200', ha='right', va='center')
        y_label_260 = self.ax.text(-1.5, 258, '260', ha='right', va='center')

        # Format the y-labels
        y_label_200.set_color('#008000')
        y_label_200.set_weight('bold')
        y_label_260.set_color('#008000')
        y_label_260.set_weight('bold')

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])
        # Set rightmost x-tick to describe the x-axis
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color('#008000')
        xticks[-1].set_weight('bold')

        # Outline bar for in_voltage
        # x, y, width, height
        rect = [0.9439, 0.121, 0.015, 0.832]
        voltage_in_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        
        self.fig.patches.extend([voltage_in_outline])

        # Inner bar representing the input voltage data range
        voltage_in_bar = Rectangle((0.9439, rect_y_in), 0.015, rect_height_in * 0.832, transform=self.fig.transFigure, 
                        facecolor='#0000D7', edgecolor='none', linewidth=0.5, clip_on=False)

        self.fig.patches.extend([voltage_in_outline, voltage_in_bar])

        # Outline bar for out_voltage
        # x, y, width, height
        rect = [0.96, 0.121, 0.015, 0.832]
        voltage_out_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)

        # Inner bar representing the output voltage data range
        voltage_out_bar = Rectangle((0.96, rect_y_out), 0.015, rect_height_out * 0.832, transform=self.fig.transFigure, 
                        facecolor='#CC6600', edgecolor='none', linewidth=0.5, clip_on=False)

        self.fig.patches.extend([voltage_out_outline, voltage_out_bar])

        plt.setp(self.ax.spines.values(), color='#999999')

        # Set the axes labels and grid
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        self.ax.set_ylim(200, 260)  # Voltage range from 200 to 260
        self.ax.grid(color='#999999', linestyle='--', linewidth=0.5, alpha=1)
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
            
            in_voltage_value = client.read_holding_register(0) # Reading from address 0
            self.view.read_holding_result_label['text'] = str(in_voltage_value)

            client.close()

            # Add the new reading to the list and ensure it only contains the last 5 readings
            self.average_voltage_array.append(in_voltage_value)
            if len(self.average_voltage_array) > 5:
                self.average_voltage_array.pop(0)
            
            # Compute the average of the last 5 readings
            avg_in_value = self.compute_average_voltage()

            client = ModbusTCPClientAPI(IP_ADDRESS, SERVER_PORT, TIMEOUT, UNIT_ID)
            out_voltage_value = client.read_holding_register(1)

            client.close()

            normalized_value = (in_voltage_value - 200) / 60  # Example normalization logic, modify as needed
            self.dynamic_bar.set_value(normalized_value)

            # Update the graph with the new value
            self.update_graph(avg_in_value, out_voltage_value)

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
