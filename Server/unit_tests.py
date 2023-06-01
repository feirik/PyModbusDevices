import unittest
import subprocess
import threading
import time
from modbus_voltage_regulator import ModbusServer

MIN_SET_POINT = 225
MAX_SET_POINT = 235
SET_POINT_230V = 230

CLIENT_PATH="../Client/pymbtget.py"

class ModbusServerTestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate the ModbusServer class
        self.server = ModbusServer('127.0.0.1', 0)
        self.server_thread = threading.Thread(target=self.server.start)
        self.server_thread.start()


    def run_command(self, command, test_value, register_index, port):
        subprocess.run(["python3", CLIENT_PATH, command, str(test_value), "-a", str(register_index), "-p", str(port), "127.0.0.1"])


    def test_holding_registers_initialization(self):
        # Test that the holding registers are initialized with the correct values upon instantiation
        self.assertEqual(self.server.holding_registers[2], SET_POINT_230V)
        self.assertEqual(self.server.holding_registers[3], MIN_SET_POINT)
        self.assertEqual(self.server.holding_registers[4], MAX_SET_POINT)

        # Test that the remaining holding registers are initialized to all zeros
        for register in self.server.holding_registers[5:]:
            self.assertEqual(register, 0)

        # Get the port number that was assigned
        port = self.server.socket.getsockname()[1]
        
        self.server.stop()

        # Run a command to stop listening loop
        self.run_command("-w6", 0, 0, port)


    def test_coils_initialization(self):
        # Test whether the outputEnabled coil is initialized to 1.
        self.assertEqual(self.server.coils[0], 1)

        # Test that the remaining coils are initialized to all zeros
        for coil in self.server.coils[1:]:
            self.assertEqual(coil, 0)

        # Get the port number that was assigned
        port = self.server.socket.getsockname()[1]
        
        self.server.stop()

        self.run_command("-w6", 0, 0, port)

    def test_write_to_holding_register_2(self):
        # Select a holding register index within the allowed range
        register_index = 2

        # Set a test value for the holding register
        test_value = 12

        # Get the port number that was assigned
        port = self.server.socket.getsockname()[1]

        # Run the command
        self.run_command("-w6", test_value, register_index, port)

        # Read the value from the holding register
        register_value = self.server.holding_registers[register_index]

        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_to_holding_register_200(self):
        register_index = 200
        test_value = 12

        port = self.server.socket.getsockname()[1]
        self.run_command("-w6", test_value, register_index, port)

        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_large_value_to_holding_register(self):
        register_index = 200
        test_value = 4000

        port = self.server.socket.getsockname()[1]
        self.run_command("-w6", test_value, register_index, port)

        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_to_holding_register_65535(self):
        register_index = 65535
        test_value = 12

        port = self.server.socket.getsockname()[1]
        self.run_command("-w6", test_value, register_index, port)
        
        register_value = self.server.holding_registers[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_disable_output_coil_0(self):
        register_index = 0
        test_value = 0

        port = self.server.socket.getsockname()[1]
        self.run_command("-w5", test_value, register_index, port)

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        # Sleep to let read loop update
        time.sleep(1)

        # Verify that voltage output was set to 0
        self.assertEqual(0, self.server.holding_registers[1])

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_1_to_coil_1(self):
        register_index = 1
        test_value = 1

        port = self.server.socket.getsockname()[1]
        self.run_command("-w5", test_value, register_index, port)
        
        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_1_to_coil_200(self):
        register_index = 200
        test_value = 1

        port = self.server.socket.getsockname()[1]
        self.run_command("-w5", test_value, register_index, port)

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_write_1_to_coil_65535(self):
        register_index = 65535
        test_value = 1

        port = self.server.socket.getsockname()[1]
        self.run_command("-w5", test_value, register_index, port)

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_enable_override_coil_1(self):
        register_index = 1
        test_value = 1

        # Enable override coil
        port = self.server.socket.getsockname()[1]
        self.run_command("-w5", test_value, register_index, port)

        register_value = self.server.coils[register_index]
        self.assertEqual(test_value, register_value)

        # Verify that set point can be overridden past max limit
        override_value = 280
        set_point_index = 2
        time.sleep(1)

        self.run_command("-w6", override_value, set_point_index, port)

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(override_value, set_point_register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)
        
    def test_max_limit_set_point(self):
        MAX_SET_POINT = 235

        port = self.server.socket.getsockname()[1]

        # Verify that set point cannot be overridden above max limit
        override_value = 280
        set_point_index = 2

        self.run_command("-w6", override_value, set_point_index, port)

        time.sleep(1)

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(MAX_SET_POINT, set_point_register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

    def test_min_limit_set_point(self):
        MIN_SET_POINT = 225

        port = self.server.socket.getsockname()[1]

        # Verify that set point cannot be overridden below minimum limit
        override_value = 80
        set_point_index = 2

        self.run_command("-w6", override_value, set_point_index, port)
        
        time.sleep(1)

        set_point_register_value = self.server.holding_registers[set_point_index]
        self.assertEqual(MIN_SET_POINT, set_point_register_value)

        self.server.stop()
        self.run_command("-w6", 0, 0, port)

if __name__ == '__main__':
    unittest.main()