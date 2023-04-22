import unittest
from modbus_voltage_regulator import ModbusServer

MIN_SET_POINT = 225
MAX_SET_POINT = 235
SET_POINT_230V = 230

class ModbusServerTestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate the ModbusServer class and initialize the holding registers and coils
        self.server = ModbusServer('localhost', 0)

    def test_holding_registers_initialization(self):
        # Test that the holding registers are initialized with the correct values upon instantiation
        self.assertEqual(self.server.holding_registers[2], SET_POINT_230V)
        self.assertEqual(self.server.holding_registers[3], MIN_SET_POINT)
        self.assertEqual(self.server.holding_registers[4], MAX_SET_POINT)

        # Test that the remaining holding registers are initialized to all zeros
        for register in self.server.holding_registers[5:]:
            self.assertEqual(register, 0)

    def test_coils_initialization(self):
        # Test whether the outputEnabled coil is initialized to 1.
        self.assertEqual(self.server.coils[0], 1)

        # Test that the remaining coils are initialized to all zeros
        for coil in self.server.coils[1:]:
            self.assertEqual(coil, 0)

if __name__ == '__main__':
    unittest.main()