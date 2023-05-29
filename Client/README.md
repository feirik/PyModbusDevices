# Modbus TCP Client Command Line in Python

This project presents a Python implementation of a the Perl script [mbtget](https://github.com/sourceperl/mbtget) with a command-line interface. This script connects to a Modbus server and performs various read and write operations based on user input.

## Command Line Arguments

The script supports the following command line arguments:

- `ip_address`: The IP address or hostname of the Modbus server.
- `-h`, `--help`: Show the help message.
- `-v`, `--version`: Show version.
- `-d`, `--dump`: Set dump mode (show tx/rx frame in hex).
- `-s`, `--script`: Set script mode (csv on stdout).
- `-r1` to `-r4`: Read bit(s) or word(s) using the respective Modbus function.
- `-w5`, `--write5`: Write a bit (Modbus function 5).
- `-w6`, `--write6`: Write a word (Modbus function 6).
- `-f`, `--float`: Read registers as floating point value.
- `-2c`, `--twos_complement`: Set 'two's complement' mode for register read.
- `--hex`: Show value in hex (default is decimal).
- `-u`, `--unit_id`: Set the Modbus "unit id".
- `-p`, `--port`: Set TCP port (default 502).
- `-a`, `--address`: Set Modbus address (default 0).
- `-n`, `--number`: Set number of values to read.
- `-t`, `--timeout`: Set timeout seconds (default is 5s).

## Running the Script

You can run the script with your desired command line arguments. Here's an example command:

```shell
python3 modbus_tcp_client.py 192.168.1.100 -p 502 -r3 -a 0 -n 5```

## Operation

The script first parses command line arguments. Depending on the arguments provided, it performs a read or write operation. Read operations can handle bits and words, and they can also interpret registers as floating point numbers or in two's complement format. Write operations can handle bits and words. For each read operation, the script prints the results to the console.

## Error handling

The script includes basic error handling. It prints an error message and exits if it encounters an issue during the Modbus operations.
