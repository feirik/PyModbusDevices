#!/usr/bin/env python3

import argparse
import socket
import random
import struct
import sys
import re

# Constants
VERSION = '0.1.0'

# Modbus/TCP Parameters
MODBUS_PORT = 502

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
opt_hex = False
opt_script_mode = False
opt_float = False
opt_2c = False
opt_debug_mode = False
opt_modbus_address = 0
opt_number_of_values = 1
opt_timeout = 5
opt_word_value = 0
opt_bit_value = 0

# Constants
MAX_TRANSACTION_ID = 65535
MODBUS_REQUEST_LENGTH = 6
BYTE_SHIFT = 8
COIL_ON = 0xFF00
COIL_OFF = 0x0000
RESPONSE_HEADER_LENGTH = 7
EXCEPTION_FC_BASE = 0x80
WRITE_SINGLE_BYTE_COUNT = 4
READ_HDR_SIZE = 3
REG_SIZE = 2
MAX_UINT8 = 255
MAX_UINT16 = 65535
HEX_BASE = 16
MAX_REGISTERS_PER_READ = 125
MAX_TIMEOUT = 120
SIGN_BIT_POSITION = 15

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
    def __init__(self, server, port=MODBUS_PORT, timeout=5, print_debug=False):
        self.server = server
        self.port = port
        self.timeout = timeout
        self.sock = None
        self.transaction_id = 0
        self.print_debug = print_debug


    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.server, self.port))


    def close(self):
        if self.sock is not None:
            self.sock.close()


    def send_request(self, function_code, address, quantity_or_value, unit_id):
        transaction_id = random.randint(0, MAX_TRANSACTION_ID)
        protocol_id = 0
        length = MODBUS_REQUEST_LENGTH

        if function_code in [READ_COILS, READ_DISCRETE_INPUTS, READ_HOLDING_REGISTERS, READ_INPUT_REGISTERS, WRITE_SINGLE_REGISTER]:
            # Packs the Modbus Application Header (MBAP) and Protocol Data Unit (PDU) fields into a bytes object in big endian format
            # The ">HHHBBHH" format specifies the byte sizes for each field
            tx_buffer = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, address, quantity_or_value)
            # Hexadecimal representation of high and low bytes of `quantity_or_value` for debug printing
            quant_or_val_hex = [f"{(quantity_or_value >> BYTE_SHIFT) & 0xFF:02X}", f"{quantity_or_value & 0xFF:02X}"]
        elif function_code == WRITE_SINGLE_COIL:
            bit_value = COIL_ON if quantity_or_value == 1 else COIL_OFF
            tx_buffer = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, address, bit_value)
            quant_or_val_hex = [f"{(bit_value >> BYTE_SHIFT) & 0xFF:02X}", f"{bit_value & 0xFF:02X}"]

        if self.print_debug:
            # Convert values to uppercase hex string format
            tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
            proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
            len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
            unit_hex = f"{unit_id:02X}"
            func_hex = f"{function_code:02X}"
            addr_hex = [f"{(address >> BYTE_SHIFT) & 0xFF:02X}", f"{address & 0xFF:02X}"]

            # Join header and data hex values
            formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex] + addr_hex + quant_or_val_hex)
            print(f"Tx\n{formatted_hex}\n")

        self.sock.send(tx_buffer)


    def receive_response(self):
        response_header = self.sock.recv(RESPONSE_HEADER_LENGTH)
        # Unpacks the response header into transaction_id, protocol_id, length, and unit_id using big endian format
        transaction_id, protocol_id, length, unit_id = struct.unpack(">HHHB", response_header)

        # Receive the response body, 'length - 1' as unit_id byte already read in the header
        response_body = self.sock.recv(length - 1)
        function_code = response_body[0]

        # Handle Modbus TCP exceptions
        if function_code >= EXCEPTION_FC_BASE:
            exception_code = response_body[1]
            exception_msg = exception_codes.get(exception_code, f"unknown exception code {exception_code}")

            if self.print_debug:
                tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
                proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
                len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
                unit_hex = f"{unit_id:02X}"
                func_hex = f"{function_code:02X}"
                except_hex = f"{exception_code:02X}"

                formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex, except_hex])
                print(f"Rx\n{formatted_hex}\n")

            raise ValueError(f"Sent function code {function_code - EXCEPTION_FC_BASE}, received exception code {exception_code}: {exception_msg}")

        if function_code == WRITE_SINGLE_REGISTER:
            register_address, register_value = struct.unpack(">HH", response_body[1:])
            # 2 bytes for address and 2 bytes for value
            byte_count = WRITE_SINGLE_BYTE_COUNT
            response_data = (register_address, register_value)
        elif function_code == WRITE_SINGLE_COIL:
            output_address, output_value = struct.unpack(">HH", response_body[1:])
            # 2 bytes for address and 2 bytes for value
            byte_count = WRITE_SINGLE_BYTE_COUNT
            response_data = (output_address, output_value)
        elif function_code == READ_COILS or function_code == READ_DISCRETE_INPUTS:
            byte_count = response_body[1]
            data = response_body[2:]
            # Convert each byte in data to its binary representation
            response_data = [format(b, '08b') for b in data]
        elif function_code == READ_INPUT_REGISTERS or function_code == READ_HOLDING_REGISTERS:
            # Unpack the byte count and the response data from the response body, omitting the function code
            byte_count, *response_data = struct.unpack(">B" + "H" * ((length - READ_HDR_SIZE) // REG_SIZE), response_body[1:])
        else:
            raise ValueError(f"Received unsupported function code: {function_code}")
        
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

        if self.print_debug:
            tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
            proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
            len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
            unit_hex = f"{unit_id:02X}"
            func_hex = f"{function_code:02X}"
            byte_count_hex = f"{byte_count:02X}"
            data_hex_values = [f"{int(value, 2):02X}" for value in response_data]  # Convert binary strings to integers before formatting

            formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex, byte_count_hex] + data_hex_values)
            print(f"Rx\n{formatted_hex}\n")

        return coil_values_int


    def parse_word_response(self, response):
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response

        # Unpack the register values from the response data
        register_values = response_data
        
        if self.print_debug:
            tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
            proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
            len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
            unit_hex = f"{unit_id:02X}"
            func_hex = f"{function_code:02X}"
            byte_count_hex = f"{byte_count:02X}"
            data_hex_values = [f"{(value >> BYTE_SHIFT) & 0xFF:02X} {value & 0xFF:02X}" for value in register_values]

            formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex, byte_count_hex] + data_hex_values)
            print(f"Rx\n{formatted_hex}\n")

        return response_data


    def parse_write_bit_response(self, response, expected_value):
        # Unpack the response data
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response
        address, value = response_data

        # Check if the response value matches the expected value
        expected_output_value = COIL_ON if expected_value == 1 else COIL_OFF

        if value == expected_output_value:
            result = True
        else:
            result = False

        if self.print_debug:
            # Convert values to uppercase hex string format
            tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
            proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
            len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
            unit_hex = f"{unit_id:02X}"
            func_hex = f"{function_code:02X}"
            addr_hex = [f"{(address >> BYTE_SHIFT) & 0xFF:02X}", f"{address & 0xFF:02X}"]
            value_hex = [f"{(value >> BYTE_SHIFT) & 0xFF:02X}", f"{value & 0xFF:02X}"]

            # Join header and data hex values
            formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex] + addr_hex + value_hex)
            print(f"Rx\n{formatted_hex}\n")

        return result


    def parse_write_word_response(self, response, expected_value):
        # Unpack the response data
        transaction_id, protocol_id, length, unit_id, function_code, byte_count, response_data = response
        address, value = response_data

        # Check if the response value matches the expected value
        if value == expected_value:
            result = True
        else:
            result = False

        if self.print_debug:
            # Convert values to uppercase hex string format
            tra_hex = [f"{(transaction_id >> BYTE_SHIFT) & 0xFF:02X}", f"{transaction_id & 0xFF:02X}"]
            proto_hex = [f"{(protocol_id >> BYTE_SHIFT) & 0xFF:02X}", f"{protocol_id & 0xFF:02X}"]
            len_hex = [f"{(length >> BYTE_SHIFT) & 0xFF:02X}", f"{length & 0xFF:02X}"]
            unit_hex = f"{unit_id:02X}"
            func_hex = f"{function_code:02X}"
            addr_hex = [f"{(address >> BYTE_SHIFT) & 0xFF:02X}", f"{address & 0xFF:02X}"]
            value_hex = [f"{(value >> BYTE_SHIFT) & 0xFF:02X}", f"{value & 0xFF:02X}"]

            # Join header and data hex values
            formatted_hex = " ".join(["[" + " ".join(tra_hex + proto_hex + len_hex + [unit_hex]) + "]"] + [func_hex] + addr_hex + value_hex)
            print(f"Rx\n{formatted_hex}\n")

        return result


def print_register_values(result, modbus_address, number_of_values, script_mode=False, print_as_hex=False, print_float=False, two_comp=False):
    if script_mode:
        # Creating a semicolon-separated string of values from the result list
        csv_values = ";".join([f"{value:05}" for value in result[:number_of_values]])
        print(csv_values + ";")
    else:
        print("Values:")
        if print_float:
            # Combine every two consecutive registers to create 32-bit floats
            float_result = [struct.unpack('!f', struct.pack('!HH', result[i], result[i+1]))[0] for i in range(0, len(result), 2)]
            # Looping through float results, printing each value with its index and modbus address
            for i, value in enumerate(float_result, start=1):
                value_str = f"{value:.6f}"
                print(f"{i:3} (ad {modbus_address + (i - 1) * 2:05}): {value_str}")
        else:
            # Looping through results printing the index, modbus address and value
            for i, value in enumerate(result[:number_of_values], start=1):
                if two_comp and not print_as_hex:
                    value = value - (value & (2 ** SIGN_BIT_POSITION)) * 2
                if print_as_hex:
                    value_str = f"{value:04X}"
                else:
                    value_str = f"{value:5}"
                print(f"{i:3} (ad {modbus_address + i - 1:05}): {value_str}")


# Argument parsing support functions
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
        if 0 <= int_value <= MAX_UINT16:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, HEX_BASE)
        if 0 <= int_value <= MAX_UINT16:
            return int_value

    raise argparse.ArgumentTypeError("word_value must be between 0 and 65535, either in decimal or hexadecimal format")


def check_unit_id(value):
    decimal_pattern = re.compile(r'^\d{1,3}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,2}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= MAX_UINT8:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, HEX_BASE)
        if 1 <= int_value <= MAX_UINT8:
            return int_value

    raise argparse.ArgumentTypeError("unit_id must be between 1 and 255, either in decimal or hexadecimal format")


def check_port_number(value):
    decimal_pattern = re.compile(r'^\d{1,5}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,4}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= MAX_UINT16:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, HEX_BASE)
        if 1 <= int_value <= MAX_UINT16:
            return int_value

    raise argparse.ArgumentTypeError("port_number must be between 1 and 65535, either in decimal or hexadecimal format")


def check_modbus_address(value):
    decimal_pattern = re.compile(r'^\d{1,5}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,4}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 0 <= int_value <= MAX_UINT16:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, HEX_BASE)
        if 0 <= int_value <= MAX_UINT16:
            return int_value

    raise argparse.ArgumentTypeError("modbus_address must be between 0 and 65535, either in decimal or hexadecimal format")


def check_number_of_values(value):
    decimal_pattern = re.compile(r'^\d{1,3}$')
    hex_pattern = re.compile(r'^0x[a-fA-F0-9]{1,2}$')

    if decimal_pattern.match(value):
        int_value = int(value)
        if 1 <= int_value <= MAX_REGISTERS_PER_READ:
            return int_value
    elif hex_pattern.match(value):
        int_value = int(value, HEX_BASE)
        if 1 <= int_value <= MAX_REGISTERS_PER_READ:
            return int_value

    raise argparse.ArgumentTypeError("value_number must be between 1 and 125, either in decimal or hexadecimal format")


def check_timeout(value):
    pattern = re.compile(r'^\d{1,3}$')

    if pattern.match(value):
        int_value = int(value)
        if 0 < int_value < MAX_TIMEOUT:
            return int_value

    raise argparse.ArgumentTypeError("timeout must be a positive integer less than 120 seconds")


def check_ipv4_or_hostname(value):
    ipv4_pattern = re.compile(r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
    hostname_pattern = re.compile(r'^[a-z][a-z0-9\.\-]+$')

    if ipv4_pattern.match(value) or hostname_pattern.match(value):
        return value

    raise argparse.ArgumentTypeError("Invalid IPv4 address or hostname")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Client ModBus / TCP command line', add_help=False)
    parser.add_argument('ip_address', type=check_ipv4_or_hostname, help='IP address or hostname of the Modbus server', nargs='?', default=opt_server)
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
    parser.add_argument('-f', '--float', action='store_true', help='read registers as floating point value')
    parser.add_argument('-2c', '--twos_complement', action='store_true', help="set 'two's complement' mode for register read")
    parser.add_argument('--hex', action='store_true', help='show value in hex (default is decimal)')
    parser.add_argument('-u', '--unit_id', metavar='unit_id', type=int, help='set the modbus "unit id"')
    parser.add_argument('-p', '--port', metavar='port_number', type=check_port_number, help='set TCP port (default 502)')
    parser.add_argument('-a', '--address', metavar='modbus_address', type=check_modbus_address, help='set modbus address (default 0)')
    parser.add_argument('-n', '--number', metavar='value_number', type=check_number_of_values, help='number of values to read')
    parser.add_argument('-t', '--timeout', metavar='timeout', type=check_timeout, help='set timeout seconds (default is 5s)')

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit()

    if args.version:
        print(VERSION)
        sys.exit()

    if args.dump:
        opt_debug_mode = True

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

    if args.twos_complement:
        opt_2c = True

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

    if args.float:
        opt_float = True
        # Reading float requires 2 registers to be read per output value
        opt_number_of_values *= 2

    if args.timeout is not None:
        opt_timeout = args.timeout

    if args.ip_address is not None:
        opt_server = args.ip_address

    # Modbus client initialization
    client = ModbusTCPClient(opt_server, port=opt_server_port, timeout=opt_timeout, print_debug=opt_debug_mode)
    client.connect()

    try:
        if opt_function == READ_COILS:
            result = client.read_coils(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
            print_register_values(result, opt_modbus_address, opt_number_of_values, opt_script_mode, opt_hex)

        elif opt_function == READ_DISCRETE_INPUTS:
            result = client.read_discrete_inputs(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
            print_register_values(result, opt_modbus_address, opt_number_of_values, opt_script_mode, opt_hex)

        elif opt_function == READ_HOLDING_REGISTERS:
            result = client.read_holding_registers(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
            print_register_values(result, opt_modbus_address, opt_number_of_values, opt_script_mode, opt_hex, opt_float, opt_2c)
            
        elif opt_function == READ_INPUT_REGISTERS:
            result = client.read_input_registers(opt_modbus_address, opt_number_of_values, unit=opt_unit_id)
            print_register_values(result, opt_modbus_address, opt_number_of_values, opt_script_mode, opt_hex, opt_float, opt_2c)

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

    except Exception as e:
        print("Error:", str(e))

    client.close()