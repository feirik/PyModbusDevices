#!/usr/bin/env python3

from .pymbtget import ModbusTCPClient

"""
The ModbusTCPClientAPI class initializes a ModbusTCPClient object, connects to the server,
and sets the Modbus unit ID for subsequent operations. It takes the following parameters:

ip_address (str ip format): The IP address of the Modbus server to connect to.

port (int): The port number the client will use to connect to the Modbus server.

timeout (int): The maximum amount of time (in seconds) to wait for a response from the server before giving up.

unit_id (int): The Modbus unit ID to be used by the client.

"""
class ModbusTCPClientAPI:
    def __init__(self, ip_address, port, timeout, unit_id):
        self.client = ModbusTCPClient(ip_address, port=port, timeout=timeout)
        self.unit_id = unit_id
        self.client.connect()

    """
    Reads the state of a specific coil on the Modbus device.

    modbus_address (int): The address of the coil to read.

    returns (bool): The state of the coil read (True for ON, False for OFF).
    """
    def read_coil(self, modbus_address):
        result = self.client.read_coils(modbus_address, 1, unit=self.unit_id)
        return result[0]

    """
    Reads the state of specific coils on the Modbus device.

    modbus_address (int): The address of the first coil to read.

    number_of_values (int): The number of coils to read.

    returns (list of bool): An array of boolean values representing the state of each coil read.
    """
    def read_multiple_coils(self, modbus_address, number_of_values):
        result = self.client.read_coils(modbus_address, number_of_values, unit=self.unit_id)
        return result[:number_of_values]

    """
    Reads the content of a specific holding register on the Modbus device.

    modbus_address (int): The address of the holding register to read.

    returns (int): The value of the holding register read.
    """
    def read_holding_register(self, modbus_address):
        result = self.client.read_holding_registers(modbus_address, 1, unit=self.unit_id)
        return result[0]

    """
    Reads the content of specific holding registers on the Modbus device.

    modbus_address (int): The address of the first holding register to read.

    number_of_values (int): The number of holding registers to read.

    returns (list of int): An array of integer values representing the content of each holding register read.
    """
    def read_multiple_holding_registers(self, modbus_address, number_of_values):
        result = self.client.read_holding_registers(modbus_address, number_of_values, unit=self.unit_id)
        return result

    """
    Writes a binary value to a specific coil on the Modbus device.

    modbus_address (int): The address of the coil to write to.

    bit_value (bool): The binary value to write to the coil.

    returns (bool): A boolean indicating whether the write operation was successful.
    """
    def write_coil(self, modbus_address, bit_value):
        result = self.client.write_coil(modbus_address, bit_value, unit=self.unit_id)
        return result

    """
    Writes an integer value to a specific holding register on the Modbus device.

    modbus_address (int): The address of the holding register to write to.

    word_value (int): The integer value to write to the holding register.

    returns (bool): A boolean indicating whether the write operation was successful.
    """
    def write_register(self, modbus_address, word_value):
        result = self.client.write_register(modbus_address, word_value, unit=self.unit_id)
        return result

    def close(self):
        self.client.close()


def main():
    ip_address = "127.0.0.1"
    port = 11502
    timeout = 5
    unit_id = 1
    modbus_single_reg_address = 0
    modbus_address = 100
    number_of_values = 10
    bit_value_before = False
    word_value_before = 1234 
    bit_value_after = True
    word_value_after = 2468

    # Write Coil initial value
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_coil(modbus_address, bit_value_before)
    print(f"Intial write - Write Coil Result: {result}")
    modbus_client.close()

    # Write Register initial value
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_register(modbus_address, word_value_before)
    print(f"Intial write - Write Register Result: {result}")
    modbus_client.close()

    # Read Coils
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_multiple_coils(modbus_address, number_of_values)
    print(f"Intial read - Read Coils Result: {result}")
    modbus_client.close()

    # Read Holding Registers
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_multiple_holding_registers(modbus_address, number_of_values)
    print(f"Intial read - Read Holding Registers Result: {result}")
    modbus_client.close()

    # Write Coil
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_coil(modbus_address, bit_value_after)
    print(f"Updated write - Write Coil Result: {result}")
    modbus_client.close()

    # Write Register
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_register(modbus_address, word_value_after)
    print(f"Updated write - Write Register Result: {result}")
    modbus_client.close()

    # Read Coils
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_multiple_coils(modbus_address, number_of_values)
    print(f"Updated read - Read Coils Result: {result}")
    modbus_client.close()

    # Read Holding Registers
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_multiple_holding_registers(modbus_address, number_of_values)
    print(f"Updated read - Read Holding Registers Result: {result}")
    modbus_client.close()

    # Read Holding Registers
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_holding_register(modbus_single_reg_address)
    print(f"Read changing variable - Read Holding Register Result: {result}")
    modbus_client.close()

    # Read single coil
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_coil(modbus_address)
    print(f"Read single value - Read Coil Result: {result}")
    modbus_client.close()

if __name__ == "__main__":
    main()
    