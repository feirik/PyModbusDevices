import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GraphView:
    def __init__(self, master):
        """Initialize the Matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=(5, 3.2))
        self.setup_view(master)

        self.data_in = []
        self.data_out = []
        self.average_voltage_array = []

    
    def compute_average_voltage(self, voltage_value):
        """Computes the average of the last 5 readings."""
        self.average_voltage_array.append(voltage_value)
        if len(self.average_voltage_array) > 5:
            self.average_voltage_array.pop(0)
        return sum(self.average_voltage_array) / len(self.average_voltage_array)


    def create_rectangle(self, x, y, width, height, facecolor, edgecolor, linewidth, transform=None, clip_on=False):
        """Utility function to create a rectangle with given parameters."""
        return Rectangle((x, y), width, height, transform=transform or self.fig.transFigure, 
                        facecolor=facecolor, edgecolor=edgecolor, linewidth=linewidth, clip_on=clip_on)


    def setup_view(self, master):
        """Setup the Matplotlib figure and axis."""
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
        xticks[-1].set_color('#008000')
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
        voltage_in_outline = self.create_rectangle(0.9439, 0.121, 0.015, 0.832, '#D5D5D5', '#999999', 1)
        self.fig.patches.extend([voltage_in_outline])

        # Outline bar for out_voltage
        voltage_out_outline = self.create_rectangle(0.96, 0.121, 0.015, 0.832, '#D5D5D5', '#999999', 1)
        self.fig.patches.extend([voltage_out_outline])

        self.fig.patches.extend([voltage_in_outline, voltage_out_outline])

        plt.setp(self.ax.spines.values(), color='#999999')

        # Use faint grid lines
        self.ax.grid(color='#999999', linestyle='--', linewidth=0.5, alpha=1)

        # Embed the Matplotlib figure into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=2, pady=20, padx=20)

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        self.fig.tight_layout()


    def update_graph(self, voltage_in, voltage_out):
        """Updates the graph with the provided voltage readings."""
        avg_in_value = self.compute_average_voltage(voltage_in)
        
        self.data_in.append(avg_in_value)
        self.data_out.append(voltage_out)

        # Ensure only the last 60 readings are kept
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

        # Clamp normalized values between 0 and 1
        normalized_min_in = min(max(normalized_min_in, 0), 1)
        normalized_max_in = min(max(normalized_max_in, 0), 1)

        normalized_min_out = min(max(normalized_min_out, 0), 1)
        normalized_max_out = min(max(normalized_max_out, 0), 1)

        # Use the normalized values to set the height and starting point of the colored rectangle
        rect_height_in = normalized_max_in - normalized_min_in
        rect_y_in = 0.121 + normalized_min_in * 0.832  # Adjust starting point based on minimum value

        rect_height_out = normalized_max_out - normalized_min_out
        rect_y_out = 0.121 + normalized_min_out * 0.832  # Adjust starting point based on minimum value

        # For the in_voltage dynamic bar

        # Ensure the base of the bar is not below the lower boundary
        rect_y_in = max(0.121, rect_y_in)

        # If the top of the dynamic bar exceeds the upper boundary, adjust the height and base
        if rect_y_in + rect_height_in * 0.832 > 0.953:
            overflow = (rect_y_in + rect_height_in * 0.832) - 0.953
            rect_height_in -= overflow / 0.832
            rect_y_in += overflow

        # For the out_voltage dynamic bar

        # Ensure the base of the bar is not below the lower boundary
        rect_y_out = max(0.121, rect_y_out)

        # If the top of the dynamic bar exceeds the upper boundary, adjust the height and base
        if rect_y_out + rect_height_out * 0.832 > 0.953:
            overflow = (rect_y_out + rect_height_out * 0.832) - 0.953
            rect_height_out -= overflow / 0.832
            rect_y_out += overflow

        # Update the Matplotlib plot
        self.ax.cla()
        
        # Plot the data
        self.ax.plot(self.data_in, "-o", color='#0000D7', markersize=1)
        self.ax.plot(self.data_out, "-o", color='#CC6600', markersize=1)

        # Label the axes
        voltage_in_label_text = f"{round(avg_in_value, 1)}\nVoltage\nIn (V)"
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
        voltage_in_outline = self.create_rectangle(0.9439, 0.121, 0.015, 0.832, '#D5D5D5', '#999999', 1)
        self.fig.patches.extend([voltage_in_outline])

        # Inner bar representing the input voltage data range
        voltage_in_bar = self.create_rectangle(0.9439, rect_y_in, 0.015, rect_height_in * 0.832, '#0000D7', 'none', 0.5)
        self.fig.patches.extend([voltage_in_bar])

        # Outline bar for out_voltage
        voltage_out_outline = self.create_rectangle(0.96, 0.121, 0.015, 0.832, '#D5D5D5', '#999999', 1)
        
        # Inner bar representing the output voltage data range
        voltage_out_bar = self.create_rectangle(0.96, rect_y_out, 0.015, rect_height_out * 0.832, '#CC6600', 'none', 0.5)

        self.fig.patches.extend([voltage_out_outline, voltage_out_bar])

        plt.setp(self.ax.spines.values(), color='#999999')

        # Set the axes labels and grid
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        self.ax.set_ylim(200, 260)  # Voltage range from 200 to 260
        self.ax.grid(color='#999999', linestyle='--', linewidth=0.5, alpha=1)
        self.fig.tight_layout()
        self.canvas.draw()
