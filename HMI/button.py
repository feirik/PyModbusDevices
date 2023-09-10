import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.widgets import Button
from matplotlib.patches import Rectangle
import tkinter as tk


class CustomInputDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, x, y, width=225, height=106):
        super().__init__(parent)
        self.geometry(f"{width}x{height}+{x}+{y}")  # Set both position and dimensions
        self.title(title)

        self.label = tk.Label(self, text=prompt)
        self.label.pack(pady=5)

        self.entry = tk.Entry(self)
        self.entry.pack(pady=0)

        self.button_frame = tk.Frame(self)  # Create a frame for the buttons
        self.button_frame.pack(pady=10)

        self.submit_button = tk.Button(self.button_frame, text="Apply", command=self.submit)
        self.submit_button.grid(row=0, column=0, padx=5)

        self.cancel_button = tk.Button(self.button_frame, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=0, column=1, padx=5)

        self.result = None

    def submit(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()


class ButtonView:
    def __init__(self, master):
        self.fig, self.ax = plt.subplots(figsize=(4.4, 3.2))
        
        # Hide the default axis
        self.ax.axis('off')
        
        # Style attributes
        self.fig.patch.set_facecolor('#D5D5D5')  # Set figure background color
        outline_box = Rectangle((0, 0), 1, 1, transform=self.fig.transFigure, 
                                facecolor='none', edgecolor='#999999', linewidth=2, clip_on=False)
        self.fig.patches.extend([outline_box])

        # Initial setup
        self._setup_view()

        # Embed the widget
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas_widget = self.canvas.get_tk_widget()
        
    def _setup_view(self):

        self.button_ax = self.fig.add_axes([0.1, 0.75, 0.3, 0.12])
        
        # Create the button with hover effect
        self.button = Button(self.button_ax, 'UPDATE\nSET POINT', color='#999999', hovercolor='#008000')
        self.button.on_clicked(self._on_button_click)

        # Give it a thick border (You can adjust the rectangle's linewidth for the desired thickness)
        # Here, the rectangle is slightly smaller than the full button
        inset_ratio = 0.03  # 5% inset for the rectangle
        rectangle = plt.Rectangle((inset_ratio, inset_ratio), 1 - 2*inset_ratio, 1 - 2*inset_ratio, 
                                  facecolor='#D5D5D5', edgecolor='#999999', linewidth=1.5)
        self.button_ax.add_patch(rectangle)

        # # Define an area (l, b, w, h) in the bottom right for the button
        # button_ax = self.fig.add_axes([0.1, 0.75, 0.3, 0.12])

        # # Give it a thick border (You can adjust the rectangle's linewidth for the desired thickness)
        # rectangle = plt.Rectangle((0, 0), 1, 1, facecolor='#D5D5D5', edgecolor='#999999', linewidth=3.5)
        # button_ax.add_patch(rectangle)

        # # Create the button
        # self.button = Button(button_ax, 'UPDATE\nSET POINT', color='#999999', hovercolor='#FFFFFF')
        # self.button.on_clicked(self._on_button_click)



        # Create faceplate zone
        rect = [0.465, 0.52, 0.51, 0.433]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Reserved Faceplate Zone\n", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create reserved information block
        rect = [0.465, 0.045, 0.31, 0.40]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        center_y = rect[1] + rect[3] / 2 - 0.02

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, center_y, "Set View", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

        # Create manual actions zone
        rect = [0.028, 0.045, 0.41, 0.907]

        # Add the rectangle to the axis instead of the figure
        self.description_box = self.ax.add_patch(
            Rectangle((rect[0], rect[1]), rect[2], rect[3], transform=self.fig.transFigure, 
                    facecolor='#D5D5D5', edgecolor='#999999', linewidth=1, clip_on=False)
        )

        # Calculate the center of the rectangle
        center_x = rect[0] + rect[2] / 2
        y_placement = 0.91

        # Add text to the rectangle
        self.desc_text = self.ax.text(center_x, y_placement, "MANUAL ACTIONS", weight='bold', ha='center',
                         va='center', fontsize=10, color='#4A4A4A', transform=self.fig.transFigure)

    def _on_button_click(self, event):
        # Get the top-left corner of the widget
        x = self.canvas._tkcanvas.winfo_rootx()
        y = self.canvas._tkcanvas.winfo_rooty()

        # Get the dimensions of the widget
        width = self.canvas._tkcanvas.winfo_width()
        height = self.canvas._tkcanvas.winfo_height()

        # Calculate the position for the popup to appear adjacent to the bottom-right corner of the widget
        x = 815
        y = 514

        print(f"x: {x}, y: {y}")  # Debug print for coordinates

        # Display the custom input dialog
        dialog = CustomInputDialog(self.canvas._tkcanvas.master, "Update Value", "Enter value:", x, y)
        self.canvas._tkcanvas.master.wait_window(dialog)  # Wait until dialog is closed
        user_input = dialog.result

        if user_input is not None:
            print(user_input)

