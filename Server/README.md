This is a Python implementation of a Modbus TCP slave device simulating a voltage regulator. The voltage regulator is inspired by the no longer supported ModbusPal project written in Java.

# Modbus Holding Registers
The following holding registers are implemented in the simulated voltage regulator:

- Ad 0: Input voltage - Varies randomly between 210 to 255
- Ad 1: Output voltage - +-1 of set point value
- Ad 2: Set point voltage
- Ad 3: Minimum value for set point (MIN)
- Ad 4: Maximum value for set point (MAX)

The limit checks are only performed if EnableOverride is disabled.

# Modbus Coils
The following coils are implemented in the simulator:

- Ad 0: EnableOutput is used to enable the voltage output
- Ad 1: EnableOverride is used to allow the set point limits to be overridden

# Command Line Arguments

The following command line arguments are available when running the Modbus TCP device script:

* `--host`: the host IP address (default is `127.0.0.1`)
* `-p`, `--port`: the port number (default is `11502`)
* `-d`, `--debug`: enable printing of debug messages (default is `off`)

# Starting the Simulator

To start the simulator, run the program with the desired command line arguments. For example, to start the simulator on a specific IP address and port with debugging information enabled, run the following command:

``python3 modbus_voltage_regulator.py --host 192.168.1.100 --port 502 -d``

The program will print out the IP address, port, and debug information settings to the console. The simulator will then listen for incoming Modbus TCP requests on the specified IP address and port.

# Unit Tests

To execute the unit tests for this project, you need to run the `unit_tests.py` file. This script contains a comprehensive suite of tests, including basic functionality tests as well as tests for the Modbus server's read and write capabilities.

You can run these tests by navigating to the project directory and executing the following command:

```shell
python3 -m unittest unit_tests.py
```

Upon execution, this command will run all the tests defined in the unit_tests.py file and display the results in the console. If any test fails, you'll see an error message detailing the nature of the failure. Conversely, if all tests pass, you'll see a message indicating successful completion of all tests. The tests are using the client in `../Client/pymbtget.py` for interacting with the server.
