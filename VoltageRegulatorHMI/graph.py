import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from colors import HPHMI

VIEW_RANGES = {
    'default': {'limits': (200, 260), 'labels': (201, 258), 'y_pos_label': 216},
    'low': {'limits': (100, 140), 'labels': (101, 139), 'y_pos_label': 110.6},
    'high': {'limits': (0, 400), 'labels': (8, 390), 'y_pos_label': 110},
}

BAR_OUTLINES = {
    'in_voltage': {
        'x': 0.9439,
        'y': 0.121,
        'width': 0.015,
        'height': 0.832
    },
    'out_voltage': {
        'x': 0.96,
        'y': 0.121,
        'width': 0.015,
        'height': 0.832
    }
}

# Constantts for dynamic bars
BASE_Y = 0.121
BAR_SCALE = 0.832
UPPER_BOUNDARY = 0.953

class GraphView:
    def __init__(self, master):
        """Initialize the Matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=(5, 3.2))
        self.view_type = 'default'
        self.master = master
        self.setup_view(master)

        self.data_in = []
        self.data_out = []
        self.average_voltage_array = []


    def set_view_type(self, view_type):
        """Set the view type and update the graph accordingly."""
        if view_type in VIEW_RANGES:
            self.view_type = view_type
            self.setup_view(self.master)  # Use the stored master here
        else:
            raise ValueError(f"Invalid view type: {view_type}")

    
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
        self.fig.patch.set_facecolor(HPHMI.gray)

        # Set the axis background color
        self.ax.set_facecolor(HPHMI.gray)
        
        # Set consistent intervals for the X and Y axes
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds

        y_min, y_max = VIEW_RANGES[self.view_type]['limits']
        self.ax.set_ylim(y_min, y_max)

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color(HPHMI.dark_green)
        xticks[-1].set_weight('bold')
        
        # Input voltage label
        self.ax.set_ylabel("0\nVoltage\nIn (V)", rotation=0, labelpad=20, va='center', 
                    bbox=dict(facecolor='none', edgecolor=HPHMI.dark_blue, boxstyle='square', linewidth=2))
        
        # Output voltage label
        voltage_out_label_text = f"0\nVoltage\nOut (V)"
        x_position = -5.72
        y_position = VIEW_RANGES[self.view_type]['y_pos_label']
        self.ax.text(x_position, y_position, voltage_out_label_text, 
            rotation=0, ha='center', va='center',
            bbox=dict(facecolor='none', edgecolor=HPHMI.brown, boxstyle='square', linewidth=2))

        # Hide y-axis tick lables
        self.ax.set_yticklabels([])

        # Manually add the y-labels at desired positions
        label_min, label_max = VIEW_RANGES[self.view_type]['labels']
        y_label_min = self.ax.text(-1.5, label_min, str(y_min), ha='right', va='center')
        y_label_max = self.ax.text(-1.5, label_max, str(y_max), ha='right', va='center')

        # Format the y-labels
        y_label_min.set_color(HPHMI.dark_green)
        y_label_min.set_weight('bold')
        y_label_max.set_color(HPHMI.dark_green)
        y_label_max.set_weight('bold')

        # Outline bar for in_voltage
        voltage_in_outline = self.create_rectangle(BAR_OUTLINES['in_voltage']['x'], 
                                                   BAR_OUTLINES['in_voltage']['y'], 
                                                   BAR_OUTLINES['in_voltage']['width'], 
                                                   BAR_OUTLINES['in_voltage']['height'], 
                                                   HPHMI.gray, HPHMI.dark_gray, 1)

        
        # Outline bar for out_voltage
        voltage_out_outline = self.create_rectangle(BAR_OUTLINES['out_voltage']['x'], 
                                                    BAR_OUTLINES['out_voltage']['y'], 
                                                    BAR_OUTLINES['out_voltage']['width'], 
                                                    BAR_OUTLINES['out_voltage']['height'], 
                                                    HPHMI.gray, HPHMI.dark_gray, 1)

        self.fig.patches.extend([voltage_in_outline, voltage_out_outline])

        plt.setp(self.ax.spines.values(), color=HPHMI.dark_gray)

        # Use faint grid lines
        self.ax.grid(color=HPHMI.dark_gray, linestyle='--', linewidth=0.5, alpha=1)

        # Embed the Matplotlib figure into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, columnspan=4, rowspan=8, pady=20, padx=20)

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor=HPHMI.dark_gray, linewidth=2, clip_on=False)
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
        y_axis_min, y_axis_max = VIEW_RANGES[self.view_type]['limits']
        self.ax.set_ylim(y_axis_min, y_axis_max)
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
        rect_y_in = BASE_Y + normalized_min_in * BAR_SCALE

        rect_height_out = normalized_max_out - normalized_min_out
        rect_y_out = BASE_Y + normalized_min_out * BAR_SCALE

        # For the in_voltage dynamic bar, check bar is not below the lower boundary
        rect_y_in = max(BASE_Y, rect_y_in)

        # If the top of the dynamic bar exceeds the upper boundary, adjust the height and base
        if rect_y_in + rect_height_in * BAR_SCALE > UPPER_BOUNDARY:
            overflow = (rect_y_in + rect_height_in * BAR_SCALE) - UPPER_BOUNDARY
            rect_height_in -= overflow / BAR_SCALE
            rect_y_in += overflow

        # For the out_voltage dynamic bar, check bar is not below the lower boundary
        rect_y_out = max(BASE_Y, rect_y_out)

        # If the top of the dynamic bar exceeds the upper boundary, adjust the height and base
        if rect_y_out + rect_height_out * BAR_SCALE > UPPER_BOUNDARY:
            overflow = (rect_y_out + rect_height_out * BAR_SCALE) - UPPER_BOUNDARY
            rect_height_out -= overflow / BAR_SCALE
            rect_y_out += overflow

        # Update the Matplotlib plot
        self.ax.cla()
        
        # Plot the data
        self.ax.plot(self.data_in, "-o", color=HPHMI.dark_blue, markersize=1)
        self.ax.plot(self.data_out, "-o", color=HPHMI.brown, markersize=1)

        # Label the axes
        voltage_in_label_text = f"{round(avg_in_value, 1)}\nVoltage\nIn (V)"
        self.ax.set_ylabel(voltage_in_label_text, rotation=0, labelpad=20, va='center', 
                    bbox=dict(facecolor='none', edgecolor=HPHMI.dark_blue, boxstyle='square', linewidth=2))

        # Output voltage label
        voltage_out_label_text = f"{voltage_out}\nVoltage\nOut (V)"
        x_position = -5.72
        y_position = VIEW_RANGES[self.view_type]['y_pos_label']
        self.ax.text(x_position, y_position, voltage_out_label_text, 
            rotation=0, ha='center', va='center',
            bbox=dict(facecolor='none', edgecolor=HPHMI.brown, boxstyle='square', linewidth=2))

        # Hide y-axis tick lables
        self.ax.set_yticklabels([])

        # Manually add the y-labels at desired positions
        label_min, label_max = VIEW_RANGES[self.view_type]['labels']
        y_label_min = self.ax.text(-1.5, label_min, str(y_axis_min), ha='right', va='center')
        y_label_max = self.ax.text(-1.5, label_max, str(y_axis_max), ha='right', va='center')

        # Format the y-labels
        y_label_min.set_color(HPHMI.dark_green)
        y_label_min.set_weight('bold')
        y_label_max.set_color(HPHMI.dark_green)
        y_label_max.set_weight('bold')

        # Set x-ticks to represent elapsed time
        self.ax.set_xticks([0, 15, 30, 45, 60])
        self.ax.set_xticklabels(['-60','-45', '-30', '-15', '60s'])

        # Set rightmost x-tick to describe the x-axis
        xticks = self.ax.get_xticklabels()
        xticks[-1].set_color(HPHMI.dark_green)
        xticks[-1].set_weight('bold')

        # Outline bar for in_voltage
        voltage_in_outline = self.create_rectangle(BAR_OUTLINES['in_voltage']['x'], 
                                                BAR_OUTLINES['in_voltage']['y'], 
                                                BAR_OUTLINES['in_voltage']['width'], 
                                                BAR_OUTLINES['in_voltage']['height'], 
                                                HPHMI.gray, HPHMI.dark_gray, 1)

        # Inner bar representing the input voltage data range
        voltage_in_bar = self.create_rectangle(BAR_OUTLINES['in_voltage']['x'], 
                                               rect_y_in, 
                                               BAR_OUTLINES['in_voltage']['width'], 
                                               rect_height_in * BAR_OUTLINES['in_voltage']['height'], 
                                               HPHMI.dark_blue, 'none', 0.5)

        # Outline bar for out_voltage
        voltage_out_outline = self.create_rectangle(BAR_OUTLINES['out_voltage']['x'], 
                                                    BAR_OUTLINES['out_voltage']['y'], 
                                                    BAR_OUTLINES['out_voltage']['width'], 
                                                    BAR_OUTLINES['out_voltage']['height'], 
                                                    HPHMI.gray, HPHMI.dark_gray, 1)

        # Inner bar representing the output voltage data range
        voltage_out_bar = self.create_rectangle(BAR_OUTLINES['out_voltage']['x'], 
                                                rect_y_out, 
                                                BAR_OUTLINES['out_voltage']['width'], 
                                                rect_height_out * BAR_OUTLINES['out_voltage']['height'], 
                                                HPHMI.brown, 'none', 0.5)
        
        self.fig.patches.extend([voltage_in_outline, voltage_in_bar, voltage_out_outline, voltage_out_bar])

        # Set the axes labels and grid
        self.ax.set_xlim(0, 60)  # Fixed at 60 seconds
        y_min, y_max = VIEW_RANGES[self.view_type]['limits']
        self.ax.set_ylim(y_min, y_max)  # Use dynamic voltage range from VIEW_RANGES
        self.ax.grid(color=HPHMI.dark_gray, linestyle='--', linewidth=0.5, alpha=1)
        self.fig.tight_layout()
        self.canvas.draw()
