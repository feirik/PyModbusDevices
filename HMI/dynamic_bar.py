import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

X_AXIS_OFFSET = 0.08
Y_AXIS_OFFSET = 0.121
BAR_HEIGHT = 0.60
BAR_WIDTH = 0.04
Y_AXIS_CENTER = 0.398

class DynamicBar:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(figsize=(4.4, 3.2))
        
        # Initial setup
        self._setup_view()

        # Embed the widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()

    def _setup_view(self):
        self.ax.axis('off')
        self.fig.patch.set_facecolor('#D5D5D5')  # Set figure background color

        # Place the first static text at the top left with bold weight and color #4A4A4A
        self.ax.text(-0.13, 1.11, "Voltage Control", ha='left', va='top', fontsize=11, weight='bold', color='#4A4A4A', transform=self.ax.transAxes)

        # Place the second static text at the top left with color #4A4A4A
        self.ax.text(-0.13, 1.02, "Set point", ha='left', va='top', fontsize=11, color='#4A4A4A', transform=self.ax.transAxes)

        # Create the outline bar for voltage
        rect = [X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.voltage_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor='#999999', edgecolor='#4A4A4A', linewidth=1, clip_on=False)
        self.fig.patches.extend([self.voltage_outline])

        # Create a dynamic inner bar
        self.dynamic_bar = Rectangle((X_AXIS_OFFSET + 0.0024, Y_AXIS_OFFSET), BAR_WIDTH - 0.003, 0, transform=self.fig.transFigure, 
                                     facecolor='#BBE0E3', edgecolor='#4A4A4A', linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar])

        # Create a square indicator rotated by 45 degrees (appearing as a diamond) inside the bar
        self.square_size = 0.032
        self.square_indicator = Rectangle((X_AXIS_OFFSET + 0.022, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor='#4A4A4A', edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator])

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])


    def set_value(self, min_set_point, max_set_point, set_point):
        # Calculate the start and end of the bar based on the set points
        bar_start = max(min_set_point - 10, 0)  # Ensure bar_start is 0 or larger
        bar_end = max_set_point + 10
        bar_range = bar_end - bar_start

        # Normalize values based on the dynamic starting point and range
        normalized_min = (min_set_point - bar_start) / bar_range
        normalized_max = (max_set_point - bar_start) / bar_range
        normalized_set_point = (set_point - bar_start) / bar_range

        # Calculate the position and height of the dynamic bar
        dynamic_bar_start = Y_AXIS_OFFSET + normalized_min * BAR_HEIGHT
        dynamic_bar_height = (normalized_max - normalized_min) * BAR_HEIGHT

        # Set the position and height of the dynamic bar
        self.dynamic_bar.set_y(dynamic_bar_start)
        self.dynamic_bar.set_height(dynamic_bar_height)

        # Update the y position of the square indicator
        square_y_position = Y_AXIS_OFFSET + normalized_set_point * BAR_HEIGHT - (self.square_size / 2) - 0.007
        
        # Make sure the indicator is not set outside area of bar
        square_y_position = max(0.098, min(0.698, square_y_position))
        self.square_indicator.set_y(square_y_position)

        # Redraw the canvas to reflect the changes
        self.canvas.draw()
    