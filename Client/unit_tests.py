import unittest
import time
import subprocess
import re
from pymbtget import *
from unittest.mock import patch
from io import StringIO

MODBUS_TEST_PORT = 11502
REG_TEST_VALUE = 1234
COIL_TEST_VALUE = True
TEST_ADDRESS = 100

class ModbusTCPClientTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize Modbus server to test values
        cls.client = ModbusTCPClient('localhost', MODBUS_TEST_PORT)

        try:
            # Attempt to connect to server
            cls.client.connect()
        except Exception as e:
            raise ConnectionError(f"Unable to connect to Modbus server at localhost:{MODBUS_TEST_PORT}. Error: {str(e)}")

        try:
            # Init register
            cls.client.write_register(TEST_ADDRESS, REG_TEST_VALUE)
            cls.client.close()

            # Attempt to connect again
            cls.client.connect()
        except Exception as e:
            raise ConnectionError(f"Unable to connect to Modbus server at localhost:{MODBUS_TEST_PORT}. Error: {str(e)}")

        try:
            # Init coil
            cls.client.write_coil(TEST_ADDRESS, COIL_TEST_VALUE)
            cls.client.close()
        except Exception as e:
            raise Exception(f"Failed to write coil to address {TEST_ADDRESS} on Modbus server at localhost:{MODBUS_TEST_PORT}. Error: {str(e)}")


    def setUp(self):
        # Instantiate the ModbusTCPClient class
        self.client = ModbusTCPClient('localhost', MODBUS_TEST_PORT)


    def test_initialization(self):
        # Test the server property is initialized correctly
        self.assertEqual(self.client.server, 'localhost')

        # Test the port property is initialized correctly
        self.assertEqual(self.client.port, MODBUS_TEST_PORT)

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


    # This decorator is used to replace the standard output (sys.stdout) with a StringIO object for the duration of the test
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_register_values(self, mock_stdout):
        # Define the input parameters for the print_register_values function
        result = [12345, 23456, 34567]
        modbus_address = 100
        number_of_values = 3
        script_mode = False
        print_as_hex = False
        print_float = False
        two_comp = False

        # Call the function with the defined parameters
        print_register_values(result, modbus_address, number_of_values, script_mode, print_as_hex, print_float, two_comp)

        # Define the expected output. The values should be the decimal representation of the input values
        expected_output = (
            r"Values:1\(ad00100\):123452\(ad00101\):234563\(ad00102\):34567"
        )

        # Remove white space
        actual_output = re.sub(r'\s', '', mock_stdout.getvalue())

        # Check that the actual output matches the expected output
        self.assertTrue(re.match(expected_output, actual_output))


    @patch('sys.stdout', new_callable=StringIO)
    def test_print_register_values_as_hex(self, mock_stdout):
        # Define the input parameters for the print_register_values function
        result = [12345, 23456, 34567]
        modbus_address = 100
        number_of_values = 3
        script_mode = False
        print_as_hex = True
        print_float = False
        two_comp = False

        # Call the function with the defined parameters
        print_register_values(result, modbus_address, number_of_values, script_mode, print_as_hex, print_float, two_comp)

        # Define the expected output. The values should be the hexadecimal representation of the input values
        expected_output = (
            r"Values:1\(ad00100\):30392\(ad00101\):5BA03\(ad00102\):8707"
        )

        # Remove white space
        actual_output = re.sub(r'\s', '', mock_stdout.getvalue())

        # Check that the actual output matches the expected output
        self.assertTrue(re.match(expected_output, actual_output))


    def test_modbus_client_read_holding_registers(self):
        client = ModbusTCPClient('localhost', port=MODBUS_TEST_PORT)

        try:
            client.connect()

            # Reading one register starting at address 100
            result = client.read_holding_registers(TEST_ADDRESS, 1)  # reading one register starting at address 100
            assert result == [REG_TEST_VALUE], 'Unexpected read result'
        finally:
            client.close()


    def test_modbus_client_read_coils(self):
        client = ModbusTCPClient('localhost', port=MODBUS_TEST_PORT)

        try:
            client.connect()

            result = client.read_coils(TEST_ADDRESS, 1)
            
            # Convert the 1 or 0 to boolean
            coil_status = bool(result[0])

            assert coil_status == COIL_TEST_VALUE, 'Unexpected read result'

        finally:
            # Close the connection
            client.close()


    def test_modbus_client_read_discrete_inputs_unsupported(self):
        client = ModbusTCPClient('localhost', port=MODBUS_TEST_PORT)

        try:
            client.connect()

            # Try to read discrete inputs which is not supported by server
            client.read_discrete_inputs(TEST_ADDRESS, 1)

            # If an exception is not raised by this point, fail the test
            self.fail('Expected function code exception but none was raised')

        except ValueError as e:
            # Check the error message matches what we expect
            expected_msg = f'Sent function code 2, received exception code 1: illegal function'
            self.assertEqual(str(e), expected_msg, 'Unexpected exception message')

        finally:
            client.close()


    def test_modbus_client_read_input_registers_unsupported(self):
        client = ModbusTCPClient('localhost', port=MODBUS_TEST_PORT)

        try:
            client.connect()
            client.read_input_registers(TEST_ADDRESS, 1)
            self.fail('Expected function code exception but none was raised')

        except ValueError as e:
            # Check the error message matches what we expect
            expected_msg = f'Sent function code 4, received exception code 1: illegal function'
            self.assertEqual(str(e), expected_msg, 'Unexpected exception message')

        finally:
            client.close()


    def test_server_read_holding_registers_debug(self):
        command = ["python3", "pymbtget.py", "127.0.0.1", "-r3", "-a", "100", "-n", "10", "-p", "11502", "-d"]
        result = subprocess.run(command, text=True, capture_output=True)

        '''
        Pattern:
        1. 'Tx' indicates a transmission, with hexadecimal values for the protocol details.
        2. The values after 'Tx' indicate the Modbus request sent (reading multiple registers).
        3. 'Rx' signifies a reception, similar to 'Tx' but with response data.
        4. The hexadecimal values after 'Rx' are the register values returned.
        5. 'Values:' shows the human-readable register numbers, addresses, and their corresponding values.
        '''
        expected_output = (
            r"Tx\[\w+\]03\d+64\d+0A"
            r"Rx\[\w+\]03\d+04D2\d+"
            r"Values:1\(ad00100\):12342\(ad00101\):\d3\(ad00102\):\d4\(ad00103\):\d5"
            r"\(ad00104\):\d6\(ad00105\):\d7\(ad00106\):\d8\(ad00107\):\d9\(ad00108\):\d10\(ad00109\):0"
        )

        # Remove white space
        actual_output = re.sub(r'\s', '', result.stdout)

        # Assert the actual output matches the expected output using regex
        self.assertTrue(re.match(expected_output, actual_output))


    def test_server_read_coils_debug(self):
        command = ["python3", "pymbtget.py", "127.0.0.1", "-r1", "-a", "100", "-n", "10", "-p", "11502", "-d"]
        result = subprocess.run(command, text=True, capture_output=True)

        '''
        Pattern:
        1. 'Tx' indicates a transmission, with hexadecimal values for the protocol details.
        2. The values after 'Tx' indicate the Modbus request sent (reading multiple coils).
        3. 'Rx' signifies a reception, similar to 'Tx' but with response data.
        4. The hexadecimal values after 'Rx' are the coil values returned.
        5. 'Values:' shows the human-readable coil numbers, addresses, and their corresponding values.
        '''
        expected_output = (
        r"Tx\[\w+\]01\d+64\d+0A"
        r"Rx\[\w+\]0102\d+00"
        r"Values:1\(ad00100\):\d2\(ad00101\):\d3\(ad00102\):\d4\(ad00103\):\d5"
        r"\(ad00104\):\d6\(ad00105\):\d7\(ad00106\):\d8\(ad00107\):\d9\(ad00108\):\d10\(ad00109\):0"
        )

        actual_output = re.sub(r'\s', '', result.stdout)

        self.assertTrue(re.match(expected_output, actual_output))


    def test_server_write_holding_register_debug(self):
        command = ["python3", "pymbtget.py", "-w6", "1234", "-a", "100", "-p", "11502", "-d"]
        result = subprocess.run(command, text=True, capture_output=True)

        '''
        Pattern:
        1. 'Tx' indicates a transmission, with hexadecimal values for the protocol details.
        2. The values after 'Tx' indicate the Modbus request sent (writing to a single register).
        3. 'Rx' signifies a reception, similar to 'Tx' but with response data.
        4. The hexadecimal values after 'Rx' are the confirmation of the write request.
        5. 'word write ok' message indicates that the write operation was successful.
        '''
        expected_output = (
            r"Tx\[\w+\]06\d+64\d+D2"
            r"Rx\[\w+\]06\d+64\d+D2"
            r"wordwriteok"
        )

        actual_output = re.sub(r'\s', '', result.stdout)

        self.assertTrue(re.match(expected_output, actual_output))


    def test_server_write_single_coil_debug(self):
        command = ["python3", "pymbtget.py", "-w5", "1", "-a", "100", "-p", "11502", "-d"]
        result = subprocess.run(command, text=True, capture_output=True)

        '''
        Pattern:
        1. 'Tx' indicates a transmission, with hexadecimal values for the protocol details.
        2. The values after 'Tx' indicate the Modbus request sent (writing to a single coil).
        3. 'Rx' signifies a reception, similar to 'Tx' but with response data.
        4. The hexadecimal values after 'Rx' are the confirmation of the write request.
        5. 'bit write ok' message indicates that the write operation was successful.
        '''
        expected_output = (
            r"Tx\[\w+\]05\d+64FF00"
            r"Rx\[\w+\]05\d+64FF00"
            r"bitwriteok"
        )

        actual_output = re.sub(r'\s', '', result.stdout)

        self.assertTrue(re.match(expected_output, actual_output))


    def test_server_read_input_registers_exception(self):
        command = ["python3", "pymbtget.py", "-r4", "-a", "100", "-p", "11502", "-d"]
        result = subprocess.run(command, text=True, capture_output=True)

        '''
        Pattern:
        1. 'Tx' indicates a transmission, with hexadecimal values for the protocol details.
        2. The values after 'Tx' indicate the Modbus request sent (attempting to read input registers).
        3. 'Rx' signifies a reception, similar to 'Tx' but contains exception code in this case.
        4. 'Error:' indicates that an error message is following.
        5. The error message describes the mismatch between the sent function code and the received exception code.
        '''
        expected_output = (
            r"Tx\[\w+\]04\d+64\d+01"
            r"Rx\[\w+\]8401"
            r"Error:Sentfunctioncode4,receivedexceptioncode1:illegalfunction"
        )

        actual_output = re.sub(r'\s', '', result.stdout)

        self.assertTrue(re.match(expected_output, actual_output))


if __name__ == '__main__':
    unittest.main()