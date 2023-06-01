# Modbus TCP Client Command Line in Python

This project presents a Python implementation of a the Perl script [mbtget](https://github.com/sourceperl/mbtget) with a command-line interface. This script connects to a Modbus server and performs various read and write operations based on user input.

## Command Line Arguments

The script supports the following command line arguments:

- `ip_address`: The IP address or hostname of the Modbus server.
- `-h`, `--help`: Display the help message.
- `-v`, `--version`: Display the script version.
- `-d`, `--dump`: Enable dump mode (show tx/rx frame in hex).
- `-s`, `--script`: Enable script mode (csv on stdout).
- `-r1`, `--read1`: Read bit(s) using Modbus function 1 (Read Coils).
- `-r2`, `--read2`: Read bit(s) using Modbus function 2 (Read Discrete Inputs).
- `-r3`, `--read3`: Read word(s) using Modbus function 3 (Read Holding Registers).
- `-r4`, `--read4`: Read word(s) using Modbus function 4 (Read Input Registers).
- `-w5`, `--write5`: Write a single bit (Modbus function 5).
- `-w6`, `--write6`: Write a single word (Modbus function 6).
- `-f`, `--float`: Read registers as floating point value.
- `-2c`, `--twos_complement`: Enable 'two's complement' mode for register read.
- `--hex`: Display value in hex (default is decimal).
- `-u`, `--unit_id`: Set the Modbus "unit id".
- `-p`, `--port`: Set TCP port (default 502).
- `-a`, `--address`: Set Modbus address (default 0).
- `-n`, `--number`: Set number of values to read.
- `-t`, `--timeout`: Set timeout in seconds (default is 5s).

## Running the Script

You can run the script with your desired command line arguments. Here's an example command:

```shell
python3 pymbtget.py 192.168.1.100 -p 502 -r3 -a 0 -n 5```

In this command:

- `192.168.1.100` is the IP address of the Modbus TCP server you want to interact with.
- `-p 502` specifies the port on which the Modbus server is running. 502 is the default Modbus TCP port.
- `-r3` indicates that you want to perform a "Read Holding Registers" operation, which is function code 3 in the Modbus protocol.
- `-a 0` sets the starting address for the read operation to address 0.
- `-n 5` specifies the quantity of registers to read from the server, starting from the specified address. In this case, you'll read 5 registers.

This script allows you to read data from a Modbus server's holding registers. Holding registers are part of the Modbus server's data model, and they are often used to hold information like configuration settings or measurement data from connected sensors.

## Unit Tests

To run the unit tests, navigate to the client's folder and execute the following commands:

```shell
python3 ../Server/modbus_voltage_regulator.py&
python3 -m unittest unit_tests.py```

- The first command starts the Modbus server script `modbus_voltage_regulator.py` in the background. This script simulates a Modbus server for the purpose of testing.
- The second command runs the suite of unit tests defined in `unit_tests.py` using Python's built-in `unittest` module.
