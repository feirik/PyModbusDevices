import unittest
from pymbtget import *

MODBUS_PORT = 10502

class ModbusTCPClientTestCase(unittest.TestCase):
    def setUp(self):
        # Instantiate the ModbusTCPClient class
        self.client = ModbusTCPClient('localhost', MODBUS_PORT)

    def test_initialization(self):
        # Test the server property is initialized correctly
        self.assertEqual(self.client.server, 'localhost')

        # Test the port property is initialized correctly
        self.assertEqual(self.client.port, MODBUS_PORT)

        # Test the default values of timeout and print_dump_data
        self.assertEqual(self.client.timeout, 5)
        self.assertEqual(self.client.print_debug, False)

    def test_transaction_id_initialization(self):
        # Test the transaction_id property is initialized to 0
        self.assertEqual(self.client.transaction_id, 0)

    def test_socket_initialization(self):
        # Test the socket property is initialized to None
        self.assertIsNone(self.client.sock)

    def test_check_bit_value(self):
        # Test that '0' returns 0
        self.assertEqual(check_bit_value('0'), 0)

        # Test that '1' returns 1
        self.assertEqual(check_bit_value('1'), 1)

        # Test that '2' raises an ArgumentTypeError
        with self.assertRaises(argparse.ArgumentTypeError):
            check_bit_value('2')

    def test_check_word_value(self):
        # Test that '0' returns 0
        self.assertEqual(check_word_value('0'), 0)

        # Test that '65535' returns 65535
        self.assertEqual(check_word_value('65535'), 65535)

        # Test that '0x100' returns 256
        self.assertEqual(check_word_value('0x100'), 256)

        # Test that '65536' raises an ArgumentTypeError
        with self.assertRaises(argparse.ArgumentTypeError):
            check_word_value('65536')

        # Test that '0x10000' raises an ArgumentTypeError
        with self.assertRaises(argparse.ArgumentTypeError):
            check_word_value('0x10000')

        # Test that non-numeric string raises an ArgumentTypeError
        with self.assertRaises(argparse.ArgumentTypeError):
            check_word_value('abc')

    def test_check_unit_id(self):
        self.assertEqual(check_unit_id('1'), 1)
        self.assertEqual(check_unit_id('255'), 255)
        self.assertEqual(check_unit_id('0x10'), 16)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_unit_id('0')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_unit_id('256')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_unit_id('0x100')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_unit_id('abc')

    def test_check_port_number(self):
        self.assertEqual(check_port_number('1'), 1)
        self.assertEqual(check_port_number('65535'), 65535)
        self.assertEqual(check_port_number('0x100'), 256)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_port_number('0')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_port_number('65536')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_port_number('0x10000')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_port_number('abc')

    def test_check_modbus_address(self):
        self.assertEqual(check_modbus_address('0'), 0)
        self.assertEqual(check_modbus_address('65535'), 65535)
        self.assertEqual(check_modbus_address('0x100'), 256)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_modbus_address('-1')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_modbus_address('65536')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_modbus_address('0x10000')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_modbus_address('abc')

    def test_check_number_of_values(self):
        self.assertEqual(check_number_of_values('1'), 1)
        self.assertEqual(check_number_of_values('125'), 125)
        self.assertEqual(check_number_of_values('0x7D'), 125)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_number_of_values('0')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_number_of_values('126')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_number_of_values('0x7E') # Test '0x7E' (126 in hex)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_number_of_values('abc')

    def test_check_timeout(self):
        self.assertEqual(check_timeout('1'), 1)
        self.assertEqual(check_timeout('119'), 119)

        with self.assertRaises(argparse.ArgumentTypeError):
            check_timeout('0')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_timeout('120')

        with self.assertRaises(argparse.ArgumentTypeError):
            check_timeout('abc')

    def test_check_ipv4_or_hostname(self):
        # Test valid IPv4 addresses
        self.assertEqual(check_ipv4_or_hostname('127.0.0.1'), '127.0.0.1')
        self.assertEqual(check_ipv4_or_hostname('255.255.255.255'), '255.255.255.255')

        # Test valid hostnames
        self.assertEqual(check_ipv4_or_hostname('localhost'), 'localhost')
        self.assertEqual(check_ipv4_or_hostname('test-server'), 'test-server')
        
        # Test invalid IPv4 addresses
        with self.assertRaises(argparse.ArgumentTypeError):
            check_ipv4_or_hostname('300.300.300.300')
            check_ipv4_or_hostname('256.255.255.255')

        # Test invalid hostnames
        with self.assertRaises(argparse.ArgumentTypeError):
            check_ipv4_or_hostname('localhost$')
            check_ipv4_or_hostname('-test-server')

if __name__ == '__main__':
    unittest.main()