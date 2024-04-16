# Contents
[Modbus Voltage Regulator](#modbus-voltage-regulator)
[Modbus Chemical Process Line](#modbus-chemical-process-line)


## Modbus Voltage Regulator

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

You can run unit tests by navigating to the project directory and executing the following command:

```shell
python3 -m unittest unit_tests.py
```

Unit tests for various read and write operations are included. The tests are using the client in `../Client/pymbtget.py` for interacting with the server.

## Modbus Chemical Process Line

This Python script simulates a Modbus TCP slave device that mimics a chemical processing system. The system is controlled via Modbus TCP/IP and involves various dynamic elements like valves, mixers, heaters, and sensors to simulate real-world chemical production scenarios.

# Modbus Holding Registers
- Ad 230: POWDER_TANK_LEVEL - Level of powder in the feeder tank.
- Ad 231: PROPORTIONAL_POWDER_FEED - Controls the feed rate of the powder.
- Ad 232: LIQUID_TANK_LEVEL - Level of liquid in the feeder tank.
- Ad 233: PROPORTIONAL_LIQUID_FEED - Controls the feed rate of the liquid.
- Ad 234: INTERMEDIATE_SLURRY_LEVEL - Combined level of powder and liquid in the mixer.
- Ad 235: PROCESSED_PRODUCT_LEVEL - Level of the finished product in the tank.
- Ad 236: HEATER - Temperature control for the mixing tank.
- Ad 237: MIX_TANK_PRESSURE - Pressure inside the mixing tank.
- Ad 238: TANK_TEMP_LOWER - Lower temperature in the tank.
- Ad 239: TANK_TEMP_UPPER - Upper temperature in the tank.
- Ad 240: POWDER_MIXING_VOLUME - Volume of powder being mixed.
- Ad 241: LIQUID_MIXING_VOLUME - Volume of liquid being mixed.
- Ad 242: PROD_FLOW - Flow rate of the product being output.
- Ad 243: PROD_FLOW_EST_MINUTE - Estimated flow per minute of the product.

# Modbus Coils
- Ad 200: POWDER_INLET - Controls the opening/closing of the powder inlet valve.
- Ad 201: LIQUID_INLET - Controls the opening/closing of the liquid inlet valve.
- Ad 202: MIXER - Turns the mixer on or off.
- Ad 203: SAFETY_RELIEF_VALVE - Manages the safety relief valve to release pressure.
- Ad 204: OUTLET_VALVE - Controls the outlet valve for tapping the processed product.
- Ad 205: AUTO_CONTROL_ENABLE - Enables automatic control of the process.

# Command Line Arguments

When running the modbus_chemical_process.py script, you can specify the following options:

--host: Host IP address to bind the server (default 127.0.0.1).
-p, --port: Port number for the server (default 11502).
-d, --debug: Enables detailed debug output to trace operations and values.

``python3 modbus_voltage_regulator.py --host 192.168.1.101 --port 502 -d``

This command will start the simulator on the specified IP and port with debugging enabled.

# Manual interaction

You can use the pymbtget.py script to control the server over CLI, such as:
```
python3 pymbtget.py -w5 1 -a 200 -p 502 192.168.1.101 # Open powder inlet valve
python3 pymbtget.py -w5 1 -a 201 -p 502 192.168.1.101 # Open liquid inlet valve
python3 pymbtget.py -w5 1 -a 202 -p 502 192.168.1.101 # Turn on mixer
python3 pymbtget.py -w5 1 -a 205 -p 502 192.168.1.101 # Enable automatic control

python3 pymbtget.py -w6 100 -a 231 -p 502 192.168.1.101 # Set proportional powder feed rate
python3 pymbtget.py -w6 100 -a 233 -p 502 192.168.1.101 # Set proportional liquid feed rate

python3 pymbtget.py -w6 100 -a 236 -p 502 192.168.1.101 # Set heater temperature
```