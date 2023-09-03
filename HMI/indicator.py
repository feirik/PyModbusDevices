import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle

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
        self.fig.patch.set_facecolor('#D5D5D5')
        self.ax.set_facecolor('#D5D5D5')

        # Remove axis labels and ticks
        self.ax.axis('off')

        # Create a description box
        rect = [0.022, 0.885, 0.954, 0.07]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Control Status", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create a enable output description box
        rect = [0.022, 0.815, 0.32, 0.07]

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "ENABLE OUTPUT", weight='bold', ha='center',
                                      va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)


        # Create a enable output dynamic box
        rect = [0.022, 0.745, 0.32, 0.07]

        self.en_output_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.en_output_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)


        # Create a enable override description box
        rect = [0.505, 0.815, 0.32, 0.07]

        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.desc_text = self.ax.text(center_x, center_y, "ENABLE OVERRIDE", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)


        # Create a enable override dynamic box
        rect = [0.505, 0.745, 0.32, 0.07]

        self.en_ovverride_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2

        self.en_override_text = self.ax.text(center_x, center_y, "Loading...", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)


        # Create filler box
        rect = [0.825, 0.745, 0.151, 0.14]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        # Create filler box
        rect = [0.342, 0.745, 0.163, 0.14]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#4A4A4A', linewidth=0.5, clip_on=False)
        )

        # Add an outline box around the entire figure
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])


    def update_status(self, enable_output, enable_override):
        """Update the status of both boxes based on the coil statuses."""
        
        # Update 'enable_output' box and text
        if enable_output:
            self.en_output_box.set_facecolor("#FFFFFF")
            self.en_output_text.set_text("ON")
            self.en_output_text.set_color("#0000D7")
        else:
            self.en_output_box.set_facecolor("#999999")
            self.en_output_text.set_text("OFF")
            self.en_output_text.set_color("#0000D7")

        # Update 'enable_override' box and text
        if enable_override:
            self.en_ovverride_box.set_facecolor("#FFFFFF")
            self.en_override_text.set_text("ON")
            self.en_override_text.set_color("#0000D7")
        else:
            self.en_ovverride_box.set_facecolor("#999999")
            self.en_override_text.set_text("OFF")
            self.en_override_text.set_color("#0000D7")

        self.canvas.draw()
