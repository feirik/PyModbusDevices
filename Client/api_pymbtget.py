#!/usr/bin/env python3

from pymbtget import ModbusTCPClient

class ModbusTCPClientAPI:

    def __init__(self, ip_address, port, timeout, unit_id):
        self.client = ModbusTCPClient(ip_address, port=port, timeout=timeout)
        self.unit_id = unit_id
        self.client.connect()

    def read_coils(self, modbus_address, number_of_values):
        result = self.client.read_coils(modbus_address, number_of_values, unit=self.unit_id)
        return result

    def read_holding_registers(self, modbus_address, number_of_values):
        result = self.client.read_holding_registers(modbus_address, number_of_values, unit=self.unit_id)
        return result

    def write_coil(self, modbus_address, bit_value):
        result = self.client.write_coil(modbus_address, bit_value, unit=self.unit_id)
        return result

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
    modbus_address = 100  # Replace with your desired Modbus address
    number_of_values = 10  # Replace with your desired number of values to read
    bit_value = True  # Replace with your desired bit value to write
    word_value = 1235  # Replace with your desired word value to write

    # Read Coils
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_coils(modbus_address, number_of_values)
    print(f"Read Coils Result: {result}")
    modbus_client.close()

    # Read Holding Registers
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_holding_registers(modbus_address, number_of_values)
    print(f"Read Holding Registers Result: {result}")
    modbus_client.close()

    # Write Coil
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_coil(modbus_address, bit_value)
    print(f"Write Coil Result: {result}")
    modbus_client.close()

    # Write Register
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.write_register(modbus_address, word_value)
    print(f"Write Register Result: {result}")
    modbus_client.close()

    # Read Coils
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_coils(modbus_address, number_of_values)
    print(f"Read Coils Result: {result}")
    modbus_client.close()

    # Read Holding Registers
    modbus_client = ModbusTCPClientAPI(ip_address, port, timeout, unit_id)
    result = modbus_client.read_holding_registers(modbus_address, number_of_values)
    print(f"Read Holding Registers Result: {result}")
    modbus_client.close()


if __name__ == "__main__":
    main()