import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.patches import Polygon
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from colors import HPHMI

# Used for all bars
Y_AXIS_OFFSET = 0.121
BAR_HEIGHT = 0.60
BAR_WIDTH = 0.024
Y_AXIS_CENTER = 0.398

# Individual per bar
BAR1_X_AXIS_OFFSET = 0.06
BAR2_X_AXIS_OFFSET = 0.21
BAR3_X_AXIS_OFFSET = 0.37
BAR4_X_AXIS_OFFSET = 0.54
BAR5_X_AXIS_OFFSET = 0.71
BAR6_X_AXIS_OFFSET = 0.86

# Total bar start and end, min and max for dynamic inner bar
BAR1_START = 0
BAR1_END = 160
BAR1_MIN = 20
BAR1_MAX = 120

BAR2_START = 0
BAR2_END = 100
BAR2_MIN = 20
BAR2_MAX = 80

BAR3_START = 0
BAR3_END = 300
BAR3_MIN = 100
BAR3_MAX = 250

BAR4_START = 0
BAR4_END = 2500
BAR4_MIN = 750
BAR4_MAX = 2000

BAR5_START = 0
BAR5_END = 2500
BAR5_MIN = 750
BAR5_MAX = 2000

BAR6_START = 0
BAR6_END = 1500
BAR6_MIN = 250
BAR6_MAX = 1250

class DynamicBar:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(figsize=(7, 3.2))
        
        # Initial setup
        self._setup_view()

        # Embed the widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()

    def _setup_view(self):
        self.ax.axis('off')
        self.fig.patch.set_facecolor(HPHMI.gray)  # Set figure background color

        # Place the first static text at the top left with bold weight and color #4A4A4A
        self.ax.text(-0.13, 1.11, "Mixing Tank Control", ha='left', va='top', fontsize=11, weight='bold', color='#4A4A4A', transform=self.ax.transAxes)

        # Place bar texts
        self.ax.text(-0.13, 1.02, "Tank temp", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)
        self.ax.text(0.08, 1.02, "Heater", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)
        self.ax.text(0.24, 1.02, "Mix pressure", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)
        self.ax.text(0.48, 1.02, "Powder vol", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)
        self.ax.text(0.70, 1.02, "Liquid vol", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)
        self.ax.text(0.90, 1.02, "Prod flow", ha='left', va='top', fontsize=11, color=HPHMI.darker_gray, transform=self.ax.transAxes)

        # Create the outline bar 1
        rect = [BAR1_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar1_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar1_outline])

        # Create the outline bar 2
        rect = [BAR2_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar2_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar2_outline])

        # Create the outline bar 3
        rect = [BAR3_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar3_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar3_outline])

        # Create the outline bar 4
        rect = [BAR4_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar4_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar4_outline])

        # Create the outline bar 5
        rect = [BAR5_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar5_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar5_outline])

        # Create the outline bar 6
        rect = [BAR6_X_AXIS_OFFSET, Y_AXIS_OFFSET, BAR_WIDTH, BAR_HEIGHT]
        self.bar6_outline = Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                                         facecolor=HPHMI.dark_gray, edgecolor=HPHMI.darker_gray, linewidth=1, clip_on=False)
        self.fig.patches.extend([self.bar6_outline])

        # Create a dynamic inner bar 1
        self.dynamic_bar1 = Rectangle((BAR1_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar1])

        # Create a dynamic inner bar 2
        self.dynamic_bar2 = Rectangle((BAR2_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar2])

        # Create a dynamic inner bar 3
        self.dynamic_bar3 = Rectangle((BAR3_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar3])

        # Create a dynamic inner bar 4
        self.dynamic_bar4 = Rectangle((BAR4_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar4])

        # Create a dynamic inner bar 5
        self.dynamic_bar5 = Rectangle((BAR5_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar5])

        # Create a dynamic inner bar 6
        self.dynamic_bar6 = Rectangle((BAR6_X_AXIS_OFFSET + 0.0021, Y_AXIS_OFFSET), BAR_WIDTH - 0.0025, 0, transform=self.fig.transFigure, 
                                     facecolor=HPHMI.light_blue, edgecolor=HPHMI.darker_gray, linewidth=0.3, clip_on=False)
        self.fig.patches.extend([self.dynamic_bar6])

        # Create square indicator bar 1
        self.square_size = 0.017
        self.square_indicator1 = Rectangle((BAR1_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator1])

        # Create square indicator bar 2
        self.square_indicator2 = Rectangle((BAR2_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator2])

        # Create square indicator bar 3
        self.square_indicator3 = Rectangle((BAR3_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator3])

        # Create square indicator bar 4
        self.square_indicator4 = Rectangle((BAR4_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator4])

        # Create square indicator bar 5
        self.square_indicator5 = Rectangle((BAR5_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator5])

        # Create square indicator bar 6
        self.square_indicator6 = Rectangle((BAR6_X_AXIS_OFFSET + 0.0136, Y_AXIS_CENTER), 
                                          self.square_size, self.square_size, angle=45, transform=self.fig.transFigure, 
                                          facecolor=HPHMI.darker_gray, edgecolor='none', clip_on=False)
        self.fig.patches.extend([self.square_indicator6])

        # Create a triangle indicator using a Polygon
        triangle_base_size = 0.055
        triangle_height = 0.09

        triangle_x = BAR1_X_AXIS_OFFSET + 0.013
        triangle_y = Y_AXIS_CENTER + 0.34

        triangle_vertices = [(triangle_x, triangle_y), 
                            (triangle_x - triangle_base_size/2, triangle_y + triangle_height), 
                            (triangle_x + triangle_base_size/2, triangle_y + triangle_height)]

        self.warning_triangle_bar1 = Polygon(triangle_vertices, transform=self.fig.transFigure, 
                                        visible=False, facecolor=HPHMI.red, edgecolor=HPHMI.black, linewidth=1.5, clip_on=False)
        self.fig.patches.extend([self.warning_triangle_bar1])

        triangle_x = BAR3_X_AXIS_OFFSET + 0.013

        triangle_vertices = [(triangle_x, triangle_y), 
                            (triangle_x - triangle_base_size/2, triangle_y + triangle_height), 
                            (triangle_x + triangle_base_size/2, triangle_y + triangle_height)]

        self.warning_triangle_bar3 = Polygon(triangle_vertices, transform=self.fig.transFigure, 
                                        visible=False, facecolor=HPHMI.red, edgecolor=HPHMI.black, linewidth=1.5, clip_on=False)
        self.fig.patches.extend([self.warning_triangle_bar3])

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor=HPHMI.dark_gray, linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        # Initialize dynamic numbers below the outline bar with a placeholder
        self.dynamic_number1 = self.ax.text(BAR1_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')

        self.dynamic_number2 = self.ax.text(BAR2_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')

        self.dynamic_number3 = self.ax.text(BAR3_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')

        self.dynamic_number4 = self.ax.text(BAR4_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')

        self.dynamic_number5 = self.ax.text(BAR5_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')

        self.dynamic_number6 = self.ax.text(BAR6_X_AXIS_OFFSET + BAR_WIDTH/2, Y_AXIS_OFFSET - 0.0275, '0', 
                                   ha='center', va='top', fontsize=10, color=HPHMI.dark_blue, 
                                   transform=self.fig.transFigure, weight='bold')


    def update_bars(self, tank_temp, heater, pressure, powder_vol, liquid_vol, prod_flow):
        self._set_value(BAR1_MIN, BAR1_MAX, tank_temp, self.dynamic_bar1, self.square_indicator1, self.dynamic_number1, BAR1_START, BAR1_END)
        self._set_value(BAR2_MIN, BAR2_MAX, heater, self.dynamic_bar2, self.square_indicator2, self.dynamic_number2, BAR2_START, BAR2_END)
        self._set_value(BAR3_MIN, BAR3_MAX, pressure, self.dynamic_bar3, self.square_indicator3, self.dynamic_number3, BAR3_START, BAR3_END)
        self._set_value(BAR4_MIN, BAR4_MAX, powder_vol, self.dynamic_bar4, self.square_indicator4, self.dynamic_number4, BAR4_START, BAR4_END)
        self._set_value(BAR5_MIN, BAR5_MAX, liquid_vol, self.dynamic_bar5, self.square_indicator5, self.dynamic_number5, BAR5_START, BAR5_END)
        self._set_value(BAR6_MIN, BAR6_MAX, prod_flow, self.dynamic_bar6, self.square_indicator6, self.dynamic_number6, BAR6_START, BAR6_END)

        self._display_warning(BAR1_MIN, BAR1_MAX, tank_temp, self.warning_triangle_bar1)
        self._display_warning(BAR3_MIN, BAR3_MAX, pressure, self.warning_triangle_bar3)

        # Redraw canvas with changes
        self.canvas.draw()


    def _set_value(self, min_set_point, max_set_point, set_point, bar, square, number, start, end):
        # Calculate the start and end of the bar based on the set points
        bar_start = start
        bar_end = end
        bar_range = bar_end - bar_start

        # Normalize values based on the dynamic starting point and range
        normalized_min = (min_set_point - bar_start) / bar_range
        normalized_max = (max_set_point - bar_start) / bar_range
        normalized_set_point = (set_point - bar_start) / bar_range

        # Calculate the position and height of the dynamic bar
        dynamic_bar_start = Y_AXIS_OFFSET + normalized_min * BAR_HEIGHT
        dynamic_bar_height = (normalized_max - normalized_min) * BAR_HEIGHT

        # Set the position and height of the dynamic bar
        bar.set_y(dynamic_bar_start)
        bar.set_height(dynamic_bar_height)

        # Update the y position of the square indicator
        square_y_position = Y_AXIS_OFFSET + normalized_set_point * BAR_HEIGHT - (self.square_size / 2) - 0.007
        
        # Make sure the indicator is not set outside area of bar
        square_y_position = max(0.11, min(0.705, square_y_position))
        square.set_y(square_y_position)

        # Update dynamic number
        number.set_text(str(set_point))


    def _display_warning(self, min_set_point, max_set_point, set_point, triangle):
        # Check if set_point is out of bounds and display warning triangle
        if set_point < min_set_point or set_point > max_set_point:
            # Value needs to be different from 0 to show warning
            if set_point > 1.0:
                triangle.set_visible(True)
        else:
            triangle.set_visible(False)
