#!/usr/bin/env python3

import argparse
import socket
import random
import struct
import sys
import re
import ipaddress
from enum import Enum

# Constants
VERSION = '0.0.1'

# Modbus/TCP Parameters
MODBUS_PORT = 10502
# Function codes
READ_COILS = 0x01
READ_DISCRETE_INPUTS = 0x02
READ_HOLDING_REGISTERS = 0x03
READ_INPUT_REGISTERS = 0x04
WRITE_SINGLE_COIL = 0x05
WRITE_SINGLE_REGISTER = 0x06
# Exception codes
EXP_ILLEGAL_FUNCTION = 0x01
EXP_DATA_ADDRESS = 0x02
EXP_DATA_VALUE = 0x03
EXP_SLAVE_DEVICE_FAILURE = 0x04
EXP_ACKNOWLEDGE = 0x05
EXP_SLAVE_DEVICE_BUSY = 0x06
EXP_MEMORY_PARITY_ERROR = 0x08
EXP_GATEWAY_PATH_UNAVAILABLE = 0x0A
EXP_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B

# Default values
opt_server = 'localhost'
opt_server_port = MODBUS_PORT
opt_function = READ_HOLDING_REGISTERS
opt_unit_id = 1
opt_modbus_address = 0
opt_number_of_values = 1
opt_timeout = 5
opt_word_value = 0
opt_bit_value = 0

# Function codes dictionary
function_codes = {
    READ_COILS: 'read coils',
    READ_DISCRETE_INPUTS: 'read discrete inputs',
    READ_HOLDING_REGISTERS: 'read holding registers',
    READ_INPUT_REGISTERS: 'read input registers',
    WRITE_SINGLE_COIL: 'write single coil',
    WRITE_SINGLE_REGISTER: 'write single register'
}

# Exception codes dictionary
exception_codes = {
    EXP_ILLEGAL_FUNCTION: 'illegal function',
    EXP_DATA_ADDRESS: 'data address',
    EXP_DATA_VALUE: 'data value',
    EXP_SLAVE_DEVICE_FAILURE: 'slave device failure',
    EXP_ACKNOWLEDGE: 'acknowledge',
    EXP_SLAVE_DEVICE_BUSY: 'slave device busy',
    EXP_MEMORY_PARITY_ERROR: 'memory parity error',
    EXP_GATEWAY_PATH_UNAVAILABLE: 'gateway path unavailable',
    EXP_GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND: 'gateway target device failed to respond'
}

class ModbusTCPClient:
    def __init__(self, server, port=502, timeout=5):
        self.server = server
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.transaction_id = 0

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.server, self.port))

    def close(self):
        if self.sock is not None:
            self.sock.close()

    def send_request(self, function_code, address, quantity_or_value, unit_id):
        transaction_id = random.randint(0, 65535)
        protocol_id = 0
        length = 6

        if function_code in [READ_COILS, READ_DISCRETE_INPUTS, READ_HOLDING_REGISTERS, READ_INPUT_REGISTERS, WRITE_SINGLE_REGISTER]:
            tx_buffer = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, address, quantity_or_value)
        elif function_code == WRITE_SINGLE_COIL:
            bit_value = 0xFF00 if quantity_or_value == 1 else 0x0000
            tx_buffer = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, address, bit_value)

        self.sock.send(tx_buffer)


    def receive_response(self):
        response_header = self.sock.recv(7)
        transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", response_header)

        # Receive the response body
        response_body = self.sock.recv(length - 1)

        function_code = response_body[0]

        if function_code == WRITE_SINGLE_REGISTER:
            register_address, register_value = struct.unpack(">HH", response_body[1:])
            byte_count = 4  # 2 bytes for address and 2 bytes for value
            response_data = (register_address, register_value)
        elif function_code == WRITE_SINGLE_COIL:
            output_address, output_value = struct.unpack(">HH", response_body[1:])
            byte_count = 4  # 2 bytes for address and 2 bytes for value
            response_data = (output_address, output_value)
        elif function_code == READ_COILS or function_code == READ_DISCRETE_INPUTS:
            byte_count = response_body[1]
            data = response_body[2:]
            response_data = [format(b, '08b') for b in data]
        elif function_code == READ_INPUT_REGISTERS or function_code == READ_HOLDING_REGISTERS:
            byte_count, *response_data = struct.unpack(">B" + "H" * ((length - 3) // 2), response_body[1:])
        else:
            raise ValueError(f"Unsupported function code: {function_code}")
        
        # Process and return the response
        return transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data


    def send_and_receive(self, function_code, modbus_address, value=None, unit_id=1):
        self.send_request(function_code, modbus_address, value, unit_id=1)
        return self.receive_response()

    def read_coils(self, address, count, unit=1):
        response = self.send_and_receive(READ_COILS, address, count, unit)
        return self.parse_bit_response(response)

    def read_discrete_inputs(self, address, count, unit=1):
        response = self.send_and_receive(READ_DISCRETE_INPUTS, address, count, unit)
        return self.parse_bit_response(response)

    def read_holding_registers(self, address, count, unit=1):
        response = self.send_and_receive(READ_HOLDING_REGISTERS, address, count, unit)
        print(response)
        return self.parse_word_response(response)

    def read_input_registers(self, address, count, unit=1):
        response = self.send_and_receive(READ_INPUT_REGISTERS, address, count, unit)
        return self.parse_word_response(response)

    def write_coil(self, address, value, unit=1):
        response = self.send_and_receive(WRITE_SINGLE_COIL, address, value, unit)
        return self.parse_write_bit_response(response, value)

    def write_register(self, address, value, unit=1):
        response = self.send_and_receive(WRITE_SINGLE_REGISTER, address, value, unit)
        return self.parse_write_word_response(response, value)

    def parse_bit_response(self, response):
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response

        # Unpack the coil values from the response data and convert to boolean
        coil_values_bool = [bool(int(bit)) for data_byte in response_data for bit in data_byte[::-1]]

        # Convert boolean values to integers
        coil_values_int = [int(value) for value in coil_values_bool]

        # Convert values to uppercase hex string format
        trans_id_hex_values = [f"{(transaction_id >> 8) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
        protocol_id_hex_values = [f"{(protocol_id >> 8) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
        length_hex_values = [f"{(length >> 8) & 0xFF:02X}", f"{length & 0xFF:02X}"]
        unit_id_hex = f"{unit_id:02X}"
        function_code_hex = f"{function_code:02X}"
        byte_count_hex = f"{byte_count:02X}"
        data_hex_values = [f"{int(value, 2):02X}" for value in response_data]  # Convert binary strings to integers before formatting

        # Join header and data hex values
        formatted_hex = " ".join(["[" + " ".join(trans_id_hex_values + protocol_id_hex_values + length_hex_values + [unit_id_hex]) + "]"] + [function_code_hex, byte_count_hex] + data_hex_values)
        print(f"Rx\n{formatted_hex}")

        return coil_values_int


    def parse_word_response(self, response):
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response

        # Unpack the register values from the response data
        register_values = response_data

        # Convert values to uppercase hex string format
        trans_id_hex_values = [f"{(transaction_id >> 8) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
        protocol_id_hex_values = [f"{(protocol_id >> 8) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
        length_hex_values = [f"{(length >> 8) & 0xFF:02X}", f"{length & 0xFF:02X}"]
        unit_id_hex = f"{unit_id:02X}"
        function_code_hex = f"{function_code:02X}"
        byte_count_hex = f"{byte_count:02X}"
        data_hex_values = [f"{(value >> 8) & 0xFF:02X} {value & 0xFF:02X}" for value in register_values]

        # Join header and data hex values
        formatted_hex = " ".join(["[" + " ".join(trans_id_hex_values + protocol_id_hex_values + length_hex_values + [unit_id_hex]) + "]"] + [function_code_hex, byte_count_hex] + data_hex_values)
        print(f"Rx\n{formatted_hex}")

        return response_data


    def parse_write_bit_response(self, response, expected_value):
        # Unpack the response data
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response
        address, value = response_data

        # Check if the response value matches the expected value
        expected_output_value = 0xFF00 if expected_value == 1 else 0x0000
        result = value == expected_output_value

        # Convert values to uppercase hex string format
        trans_id_hex_values = [f"{(transaction_id >> 8) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
        protocol_id_hex_values = [f"{(protocol_id >> 8) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
        length_hex_values = [f"{(length >> 8) & 0xFF:02X}", f"{length & 0xFF:02X}"]
        unit_id_hex = f"{unit_id:02X}"
        function_code_hex = f"{function_code:02X}"
        address_hex_values = [f"{(address >> 8) & 0xFF:02X}", f"{address & 0xFF:02X}"]
        value_hex_values = [f"{(value >> 8) & 0xFF:02X}", f"{value & 0xFF:02X}"]

        # Join header and data hex values
        formatted_hex = " ".join(["[" + " ".join(trans_id_hex_values + protocol_id_hex_values + length_hex_values + [unit_id_hex]) + "]"] + [function_code_hex] + address_hex_values + value_hex_values)
        print(f"Rx\n{formatted_hex}")

        return result


    def parse_write_word_response(self, response, expected_value):
        # Unpack the response data
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response
        address, value = response_data

        # Check if the response value matches the expected value
        result = value == expected_value

        # Convert values to uppercase hex string format
        trans_id_hex_values = [f"{(transaction_id >> 8) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
        protocol_id_hex_values = [f"{(protocol_id >> 8) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
        length_hex_values = [f"{(length >> 8) & 0xFF:02X}", f"{length & 0xFF:02X}"]
        unit_id_hex = f"{unit_id:02X}"
        function_code_hex = f"{function_code:02X}"
        address_hex_values = [f"{(address >> 8) & 0xFF:02X}", f"{address & 0xFF:02X}"]
        value_hex_values = [f"{(value >> 8) & 0xFF:02X}", f"{value & 0xFF:02X}"]

        # Join header and data hex values
        formatted_hex = " ".join(["[" + " ".join(trans_id_hex_values + protocol_id_hex_values + length_hex_values + [unit_id_hex]) + "]"] + [function_code_hex] + address_hex_values + value_hex_values)
        print(f"Rx\n{formatted_hex}")

        return result



# Argument code below
def check_bit_value(value):
    if value == '0' or value == '1':
        return int(value)
    else:
        raise argparse.ArgumentTypeError("bit_value must be 0 or 1")

def check_word_value(value):
    decimal_pattern = re.compile(r'^\d{1,5}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,4}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 0 <= int_value <= 65535:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, 16)
        if 0 <= int_value <= 65535:
            return int_value

    raise argparse.ArgumentTypeError("word_value must be between 0 and 65535, either in decimal or hexadecimal format")


def check_unit_id(value):
    decimal_pattern = re.compile(r'^\d{1,3}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,2}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= 255:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, 16)
        if 1 <= int_value <= 255:
            return int_value

    raise argparse.ArgumentTypeError("unit_id must be between 1 and 255, either in decimal or hexadecimal format")


def check_port_number(value):
    decimal_pattern = re.compile(r'^\d{1,5}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,4}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= 65535:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, 16)
        if 1 <= int_value <= 65535:
            return int_value

    raise argparse.ArgumentTypeError("port_number must be between 1 and 65535, either in decimal or hexadecimal format")


def check_modbus_address(value):
    decimal_pattern = re.compile(r'^\d{1,5}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,4}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 0 <= int_value <= 65535:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, 16)
        if 0 <= int_value <= 65535:
            return int_value

    raise argparse.ArgumentTypeError("modbus_address must be between 0 and 65535, either in decimal or hexadecimal format")


def check_number_of_values(value):
    decimal_pattern = re.compile(r'^\d{1,3}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,2}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= 125:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, 16)
        if 1 <= int_value <= 125:
            return int_value

    raise argparse.ArgumentTypeError("value_number must be between 1 and 125, either in decimal or hexadecimal format")


def check_timeout(value):
    pattern = re.compile(r'^\d{1,3}$')

    if pattern.match(value):
        int_value = int(value)
        if 0 < int_value < 120:
            return int_value

    raise argparse.ArgumentTypeError("timeout must be a positive integer less than 120 seconds")


def check_ipv4_or_hostname(value):
    ipv4_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    hostname_pattern = re.compile(r'^[a-z][a-z0-9\.\-]+$')

    if ipv4_pattern.match(value) or hostname_pattern.match(value):
        return value

    raise argparse.ArgumentTypeError("Invalid IPv4 address or hostname")


# Command-line arguments parsing
parser = argparse.ArgumentParser(description='Client ModBus / TCP command line', add_help=False)
parser.add_argument('-h', '--help', action='store_true', help='show this help message')
parser.add_argument('-v', '--version', action='store_true', help='show version')
parser.add_argument('-d', '--dump', action='store_true', help='set dump mode (show tx/rx frame in hex)')
parser.add_argument('-s', '--script', action='store_true', help='set script mode (csv on stdout)')
parser.add_argument('-r1', '--read1', action='store_true', help='read bit(s) (function 1)')
parser.add_argument('-r2', '--read2', action='store_true', help='read bit(s) (function 2)')
parser.add_argument('-r3', '--read3', action='store_true', help='read word(s) (function 3)')
parser.add_argument('-r4', '--read4', action='store_true', help='read word(s) (function 4)')
parser.add_argument('-w5', '--write5', metavar='bit_value', type=check_bit_value, help='write a bit (function 5)')
parser.add_argument('-w6', '--write6', metavar='word_value', type=check_word_value, help='write a word (function 6)')
parser.add_argument('-f', '--float', action='store_true', help='set floating point value')
parser.add_argument('-2c', '--twos_complement', action='store_true', help="set 'two's complement' mode for register read")
parser.add_argument('--hex', action='store_true', help='show value in hex (default is decimal)')
parser.add_argument('-u', '--unit_id', metavar='unit_id', type=int, help='set the modbus "unit id"')
parser.add_argument('-p', '--port', metavar='port_number', type=check_port_number, help='set TCP port (default 502)')
parser.add_argument('-a', '--address', metavar='modbus_address', type=check_modbus_address, help='set modbus address (default 0)')
parser.add_argument('-n', '--number', metavar='value_number', type=check_number_of_values, help='number of values to read')
parser.add_argument('-t', '--timeout', metavar='timeout', type=check_timeout, help='set timeout seconds (default is 5s)')
#parser.add_argument('--host', metavar='server_address', action='store_true', type=check_ipv4_or_hostname, help='set the IPv4 address or hostname of the server')

args = parser.parse_args()

if args.help:
    parser.print_help()
    sys.exit()

if args.version:
    print(VERSION)
    sys.exit()

if args.dump:
    opt_dump_mode = True

if args.script:
    opt_script_mode = True

if args.read1:
    opt_function = READ_COILS

if args.read2:
    opt_function = READ_DISCRETE_INPUTS

if args.read3:
    opt_function = READ_HOLDING_REGISTERS

if args.read4:
    opt_function = READ_INPUT_REGISTERS

if args.write5 is not None:
    opt_function = WRITE_SINGLE_COIL
    opt_bit_value = args.write5

if args.write6 is not None:
    opt_function = WRITE_SINGLE_REGISTER
    opt_word_value = args.write6

if args.float:
    opt_float = True

if args.twos_complement:
    opt_twos_complement = True

if args.hex:
    opt_hex = True

if args.unit_id is not None:
    opt_unit_id = args.unit_id

if args.port is not None:
    opt_server_port = args.port

if args.address is not None:
    opt_modbus_address = args.address

if args.number is not None:
    opt_number_of_values = args.number

if args.timeout is not None:
    opt_timeout = args.timeout

#if args.server_address is not None:
#    opt_server = args.server_address


# Modbus client initialization
client = ModbusTCPClient(opt_server, port=opt_server_port, timeout=opt_timeout)
client.connect()

try:
    if opt_function == READ_COILS:
        result = client.read_coils(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
        print("Register values:", result[:opt_number_of_values])
    elif opt_function == READ_DISCRETE_INPUTS:
        result = client.read_discrete_inputs(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
    elif opt_function == READ_HOLDING_REGISTERS:
        result = client.read_holding_registers(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
        print("Register values:", result[:opt_number_of_values])
    elif opt_function == READ_INPUT_REGISTERS:
        result = client.read_input_registers(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
    elif opt_function == WRITE_SINGLE_COIL:
        result = client.write_coil(opt_modbus_address, opt_bit_value, unit=opt_unit_id)

        if result:
            print("bit write ok")
        else:
            print("bit write failed")
        
    elif opt_function == WRITE_SINGLE_REGISTER:
        result = client.write_register(opt_modbus_address, opt_word_value, unit=opt_unit_id)

        if result:
            print("word write ok")
        else:
            print("word write failed")

    

    # if result.isError():
    #     print("Error:", exception_codes[result.exception_code])
    # else:
    #     if opt_function in (READ_COILS, READ_DISCRETE_INPUTS):
    #         if opt_script_mode:
    #             print(','.join([str(int(bit)) for bit in result.bits]))
    #         else:
    #             print("Bit values:", [int(bit) for bit in result.bits])
    #     elif opt_function in (READ_HOLDING_REGISTERS, READ_INPUT_REGISTERS):
    #         if opt_float:
    #             values = [decode_float32(result.registers[i:i+2]) for i in range(0, len(result.registers), 2)]
    #         elif opt_twos_complement:
    #             values = [twos_complement_to_int(reg) for reg in result.registers]
    #         else:
    #             values = result.registers

    #         if opt_script_mode:
    #             print(','.join([str(value) for value in values]))
    #         else:
    #             print("Register values:", values)

except Exception as e:
    print("Error:", str(e))

client.close()