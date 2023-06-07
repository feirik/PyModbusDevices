import tkinter as tk

class HMIView(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.configure(bg='#D5D5D5')
        self.grid()

        # Label for coil value to write
        self.coil_value_label = tk.Label(self, text="Enter Coil Value to Write:")
        self.coil_value_label.grid(row=0, column=0, sticky="W")
        
        # Entry field for coil value to write
        self.coil_value_entry = tk.Entry(self)
        self.coil_value_entry.grid(row=1, column=0, sticky="W")

        # Label for read coil result
        self.read_coil_label = tk.Label(self, text="Read Coil Result:")
        self.read_coil_label.grid(row=2, column=0, sticky="W")

        # Display labels for read results
        self.read_result_label = tk.Label(self, text="")
        self.read_result_label.grid(row=2, column=1, sticky="W")

        # Button to read coil
        self.read_coil_button = tk.Button(self, text="Read Coil")
        self.read_coil_button.grid(row=3, column=0, sticky="W")

        # Label for write coil result
        self.write_coil_label = tk.Label(self, text="Write Coil Result:")
        self.write_coil_label.grid(row=4, column=0, sticky="W")

        # Display labels for write results
        self.write_result_label = tk.Label(self, text="")
        self.write_result_label.grid(row=4, column=1, sticky="W")

        # Button to write coil
        self.write_coil_button = tk.Button(self, text="Write Coil")
        self.write_coil_button.grid(row=5, column=0, sticky="W")

        # Label for coil address to read/write
        self.coil_address_label = tk.Label(self, text="Enter Coil Address to Read/Write:")
        self.coil_address_label.grid(row=6, column=0, sticky="W")
        
        # Entry field for coil address to read/write
        self.coil_address_entry = tk.Entry(self)
        self.coil_address_entry.grid(row=7, column=0, sticky="W")
