import unittest
import subprocess
import threading
from modbus_voltage_regulator import ModbusClient

class ModbusClientTestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate the ModbusClient class
        self.client = ModbusClient('127.0.0.1', 0)
        self.client_thread = threading.Thread(target=self.client.start)
        self.client_thread.start()


    def test_write_to_holding_register_2(self):
        # Select a holding register index within the allowed range
        register_index = 2

        # Set a test value for the holding register
        test_value = 12

        # Get the port number that was assigned
        port = self.client.socket.getsockname()[1]

        # Run the command
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        # Read the value from the holding register
        register_value = self.client.holding_registers[register_index]

        self.assertEqual(test_value, register_value)

        self.client.stop()

        # Run a command to stop listening loop
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

    def test_write_to_holding_register_200(self):
        register_index = 200
        test_value = 12

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])
    

    def test_write_large_value_to_holding_register(self):
        register_index = 200
        test_value = 4000

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_to_holding_register_65535(self):
        register_index = 65535
        test_value = 12

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_0_to_coil_0(self):
        register_index = 0
        test_value = 0

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_1(self):
        register_index = 1
        test_value = 1

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_200(self):
        register_index = 200
        test_value = 1

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_65535(self):
        register_index = 65535
        test_value = 1

        port = self.client.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.client.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.client.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


if __name__ == '__main__':
    unittest.main()