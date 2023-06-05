This project contains a basic Python implementation of these parts:
* Modbus TCP Client
* Modbus TCP Server simulating a voltage regulator. 

The Client implementation serves as a Python implementation to the Perl script mbtget, enabling users to connect to a Modbus server and perform various read and write operations. The Server component simulates a Modbus voltage regulator for testing and understanding simple Modbus commands.

# Client
The Client directory contains the `pymbtget.py` script that acts as a Modbus TCP Client. This script can connect to a Modbus TCP Server and carry out various operations, including read and write tasks. Users can specify different command line arguments to determine the type of Modbus operation, the Modbus server's IP address, the data point to read/write, and more. The Client folder also includes unit tests for testing the client functionality. More details are provided in the README file in its directory.

# Server
The Server directory includes a Python script `modbus_voltage_regulator.py` simulating a Modbus TCP slave device acting as a voltage regulator. The simulated device maintains specific holding registers and coils with different functionalities, such as input/output voltage and set point voltage. Users can specify the host IP address, port number, and debug information settings via command-line arguments while running this script. Additionally, this folder includes unit tests for testing the Modbus server functionality. Detailed information about the Server component is provided in its README file.