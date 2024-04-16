The background for the project is to create simulated Modbus TCP devices to generate network traffic and show operational technology (OT) process impacts for cybersecurity use cases.

This project contains a basic Python implementation of these parts:
* Modbus TCP Client
* Modbus TCP Server simulating a voltage regulator or a chemical process line
* Human-Machine Interface (HMI) using Modbus TCP client API for interacting with the Modbus TCP server

The Client implementation serves as a Python implementation to the Perl script mbtget, enabling users to connect to a Modbus server and perform various read and write operations. One of the servers simulate a Modbus voltage regulator for testing and understanding simple Modbus commands. The other server simulates a 

# Client
The Client directory contains the `pymbtget.py` script that acts as a Modbus TCP Client. This script can connect to a Modbus TCP Server and carry out various operations, including read and write tasks. Users can specify different command line arguments to determine the type of Modbus operation, the Modbus server's IP address, the data point to read/write, and more. The Client folder also includes unit tests and an API.

# Server
The Server directory includes a Python script `modbus_voltage_regulator.py` simulating a Modbus TCP slave device acting as a voltage regulator. The simulated device maintains specific holding registers and coils with different functionalities, such as input/output voltage and set point voltage. Users can specify the host IP address, port number, and debug information settings via command-line arguments while running this script. Additionally, this folder includes unit tests for testing the Modbus server functionality. Detailed information about the Server component is provided in its README file.

The `modbus_chemical_process.py` script simulates a Modbus TCP server designed to simulate a chemical processing system. This server mimics the behavior of various components such as inlet valves, mixers, and sensors by maintaining a set of Modbus coils and holding registers that represent the operational state of these components.

# HMI
The HMI is designed to provide an interactive GUI to be used with the ModbusTCP server. The HMI is implemented with few dependecies using Python with the help of the `matplotlib` and `Pillow` libraries for graphical components. The different HMI directories contains the primary script `main.py` that launches the HMI. Further details about the HMI component and its usage are available in the README file of the folders.