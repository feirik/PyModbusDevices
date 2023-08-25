import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

X_AXIS_OFFSET = 0.12
BAR_HEIGHT = 0.60
BAR_WIDTH = 0.04

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
        rect = [X_AXIS_OFFSET, 0.121, BAR_WIDTH, BAR_HEIGHT]
        self.voltage_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor='#999999', edgecolor='#4A4A4A', linewidth=1, clip_on=False)
        self.fig.patches.extend([self.voltage_outline])

        # Create a dummy inner bar (height 0 for now)
        self.dynamic_bar = Rectangle((X_AXIS_OFFSET, 0.121), BAR_WIDTH, 0, transform=self.fig.transFigure, 
                                     facecolor='#0000D7', edgecolor='none', linewidth=0.5, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar])

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

    def set_value(self, value):
        # Normalize value to range [0, 1]
        normalized_value = value  # Assuming value is already in the range [0, 1]

        rect_height = normalized_value * BAR_HEIGHT
        rect_y = 0.121

        self.dynamic_bar.set_height(rect_height)
        self.dynamic_bar.set_y(rect_y)

        self.canvas.draw()