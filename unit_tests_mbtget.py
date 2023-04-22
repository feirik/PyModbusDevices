import unittest
import subprocess
import threading
import time
from modbus_voltage_regulator import ModbusServer

class ModbusServerTestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate the ModbusServer class
        self.server = ModbusServer('127.0.0.1', 0)
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.start()


    def test_write_to_holding_register_2(self):
        # Select a holding register index within the allowed range
        register_index = 2

        # Set a test value for the holding register
        test_value = 12

        # Get the port number that was assigned
        port = self.server.socket.getsockname()[1]

        # Run the command
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        # Read the value from the holding register
        register_value = self.server.holding_registers[register_index]

        self.assertEqual(test_value, register_value)

        self.server.stop()

        # Run a command to stop listening loop
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

    def test_write_to_holding_register_200(self):
        register_index = 200
        test_value = 12

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])
    

    def test_write_large_value_to_holding_register(self):
        register_index = 200
        test_value = 4000

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_to_holding_register_65535(self):
        register_index = 65535
        test_value = 12

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w6", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_disable_output_coil_0(self):
        register_index = 0
        test_value = 0

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        # Sleep to let read loop update
        time.sleep(1)

        # Verify that voltage output was set to 0
        self.assertEqual(0, self.server.holding_registers[1])

        self.server.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_1(self):
        register_index = 1
        test_value = 1

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_200(self):
        register_index = 200
        test_value = 1

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_write_1_to_coil_65535(self):
        register_index = 65535
        test_value = 1

        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_enable_override_coil_1(self):
        register_index = 1
        test_value = 1

        # Enable override coil
        port = self.server.socket.getsockname()[1]
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        # Verify that set point can be overridden past max limit
        override_value = 280
        set_point_index = 2
        time.sleep(1)

        subprocess.run(["mbtget", "-w6", str(override_value), "-a", str(set_point_index), "-p", str(port), "127.0.0.1"])

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(override_value, set_point_register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])
        
        
    def test_max_limit_set_point(self):
        MAX_SET_POINT = 235

        port = self.server.socket.getsockname()[1]

        # Verify that set point cannot be overridden above max limit
        override_value = 280
        set_point_index = 2

        subprocess.run(["mbtget", "-w6", str(override_value), "-a", str(set_point_index), "-p", str(port), "127.0.0.1"])

        time.sleep(1)

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(MAX_SET_POINT, set_point_register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", "0", "-a", str(set_point_index), "-p", str(port), "127.0.0.1"])


    def test_min_limit_set_point(self):
        MIN_SET_POINT = 225

        port = self.server.socket.getsockname()[1]

        # Verify that set point cannot be overridden below minimum limit
        override_value = 80
        set_point_index = 2

        subprocess.run(["mbtget", "-w6", str(override_value), "-a", str(set_point_index), "-p", str(port), "127.0.0.1"])

        time.sleep(1)

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(MIN_SET_POINT, set_point_register_value)

        self.server.stop()
        subprocess.run(["mbtget", "-w5", "0", "-a", str(set_point_index), "-p", str(port), "127.0.0.1"])


if __name__ == '__main__':
    unittest.main()