import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
from colors import HPHMI

RECT = {
    'control_status': [0.022, 0.885, 0.954, 0.07],
    'powder_inlet_desc': [0.022, 0.815, 0.32, 0.07],
    'powder_inlet_dynamic': [0.022, 0.745, 0.32, 0.07],
    'liquid_inlet_desc': [0.505, 0.815, 0.32, 0.07],
    'liquid_inlet_dynamic': [0.505, 0.745, 0.32, 0.07],
    'filler_box_right': [0.825, 0.465, 0.151, 0.42],
    'filler_box_left': [0.342, 0.465, 0.163, 0.42],
    'mixer_desc': [0.022, 0.675, 0.32, 0.07],
    'mixer_dynamic': [0.022, 0.605, 0.32, 0.07],
    'relief_valve_desc': [0.505, 0.675, 0.32, 0.07],
    'relief_valve_dynamic': [0.505, 0.605, 0.32, 0.07],
    'outlet_valve_desc': [0.022, 0.535, 0.32, 0.07],
    'outlet_valve_dynamic': [0.022, 0.465, 0.32, 0.07],
    'auto_control_desc': [0.505, 0.535, 0.32, 0.07],
    'auto_control_dynamic': [0.505, 0.465, 0.32, 0.07],
}

class Indicator:
    def __init__(self, master):
        """Initialize the Matplotlib figure and axis."""
        self.fig, self.ax = plt.subplots(figsize=(5, 3.2))
        self.master = master
        
        # Setup the initial view
        self.setup_view()
        
        # Embed the Matplotlib figure into the Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=9, columnspan=4, rowspan=8, column=0, pady=20, padx=20)


    def setup_view(self):
        """Setup the Matplotlib figure and axis."""
        # Set the figure and axis background color
        self.fig.patch.set_facecolor(HPHMI.gray)
        self.ax.set_facecolor(HPHMI.gray)

        # Remove axis labels and ticks
        self.ax.axis('off')

        # Create a description box
        rect = RECT['control_status']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Control Status", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create a powder inlet description box
        rect = RECT['powder_inlet_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "POWDER INLET", weight='bold', ha='center',
                                      va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a powder inlet dynamic box
        rect = RECT['powder_inlet_dynamic']

        self.powder_inlet_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.powder_inlet_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a liquid_inlet description box
        rect = RECT['liquid_inlet_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "LIQUID INLET", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a liquid_inlet dynamic box
        rect = RECT['liquid_inlet_dynamic']

        self.liquid_inlet_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.liquid_inlet_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create filler box right
        rect = RECT['filler_box_right']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        # Create filler box left
        rect = RECT['filler_box_left']

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor=HPHMI.dark_gray, linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])


        # Create a mixer description box
        rect = RECT['mixer_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "MIXER", weight='bold', ha='center',
                                      va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a mixer dynamic box
        rect = RECT['mixer_dynamic']

        self.mixer_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.mixer_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a relief_valve description box
        rect = RECT['relief_valve_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "RELIEF VALVE", weight='bold', ha='center',
                                      va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a relief_valve dynamic box
        rect = RECT['relief_valve_dynamic']

        self.relief_valve_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.relief_valve_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


        # Create a outlet_valve description box
        rect = RECT['outlet_valve_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "OUTLET VALVE", weight='bold', ha='center',
                                      va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create a outlet_valve dynamic box
        rect = RECT['outlet_valve_dynamic']

        self.outlet_valve_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.outlet_valve_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create a auto_control description box
        rect = RECT['auto_control_desc']

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "AUTO MODE", weight='bold', ha='center',
                                      va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)

        # Create a auto_control dynamic box
        rect = RECT['auto_control_dynamic']

        self.auto_control_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor=HPHMI.gray, edgecolor=HPHMI.darker_gray, linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.auto_control_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color=HPHMI.darker_gray, transform=self.fig.transFigure)


    def update_status(self, powder_in, liquid_in, mixer, relief_valve, outlet_valve, auto_mode):
        """Update the status of boxes based on the read statuses."""

        if powder_in:
            self.powder_inlet_box.set_facecolor(HPHMI.white)
            self.powder_inlet_text.set_text("OPEN")
            self.powder_inlet_text.set_color(HPHMI.dark_blue)
        else:
            self.powder_inlet_box.set_facecolor(HPHMI.dark_gray)
            self.powder_inlet_text.set_text("CLOSED")
            self.powder_inlet_text.set_color(HPHMI.dark_blue)

        if liquid_in:
            self.liquid_inlet_box.set_facecolor(HPHMI.white)
            self.liquid_inlet_text.set_text("OPEN")
            self.liquid_inlet_text.set_color(HPHMI.dark_blue)
        else:
            self.liquid_inlet_box.set_facecolor(HPHMI.dark_gray)
            self.liquid_inlet_text.set_text("CLOSED")
            self.liquid_inlet_text.set_color(HPHMI.dark_blue)

        if mixer:
            self.mixer_box.set_facecolor(HPHMI.white)
            self.mixer_text.set_text("ON")
            self.mixer_text.set_color(HPHMI.dark_blue)
        else:
            self.mixer_box.set_facecolor(HPHMI.dark_gray)
            self.mixer_text.set_text("OFF")
            self.mixer_text.set_color(HPHMI.dark_blue)

        if relief_valve:
            self.relief_valve_box.set_facecolor(HPHMI.white)
            self.relief_valve_text.set_text("OPEN")
            self.relief_valve_text.set_color(HPHMI.dark_blue)
        else:
            self.relief_valve_box.set_facecolor(HPHMI.dark_gray)
            self.relief_valve_text.set_text("CLOSED")
            self.relief_valve_text.set_color(HPHMI.dark_blue)

        if outlet_valve:
            self.outlet_valve_box.set_facecolor(HPHMI.white)
            self.outlet_valve_text.set_text("OPEN")
            self.outlet_valve_text.set_color(HPHMI.dark_blue)
        else:
            self.outlet_valve_box.set_facecolor(HPHMI.dark_gray)
            self.outlet_valve_text.set_text("CLOSED")
            self.outlet_valve_text.set_color(HPHMI.dark_blue)

        if auto_mode:
            self.auto_control_box.set_facecolor(HPHMI.white)
            self.auto_control_text.set_text("ACTIVE")
            self.auto_control_text.set_color(HPHMI.dark_blue)
        else:
            self.auto_control_box.set_facecolor(HPHMI.dark_gray)
            self.auto_control_text.set_text("INACTIVE")
            self.auto_control_text.set_color(HPHMI.dark_blue)

        self.canvas.draw()
