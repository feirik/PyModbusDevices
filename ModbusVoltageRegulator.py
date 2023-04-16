import argparse
import socket
import struct
import threading
import random
import time

# Modbus holding registers
# ------------------------
# Ad 0: Input voltage - Varies randomly between 210 to 255
# Ad 1: Output voltage - +-1 of set point value
# Ad 2: Set point voltage
# Ad 3: Minimum value for set point (MIN)
# Ad 4: Maximum value for set point (MAX)
# The limit checks are only performed if enableOverride bit in self.coils[1] is set to 0

# Modbus coils
# ------------
# Ad 0: EnableOutput is used to enable the voltage output
# Ad 1: EnableOverride is used to allow the set point limits to be overridden

# Define the Modbus function codes
READ_COILS = 1
READ_DISCRETE_INPUTS = 2 # Not supported
READ_HOLDING_REGISTERS = 3
READ_INPUT_REGISTERS = 4 # Not supported
WRITE_SINGLE_COIL = 5
WRITE_SINGLE_REGISTER = 6
WRITE_MULTIPLE_COILS = 15 # Not supported
WRITE_MULTIPLE_REGISTERS = 16 # Not supported

class ModbusClient:
    def __init__(self, host, port, debug=False):
        self.debug = debug

        # Initialize the holding registers to all zeros
        self.holding_registers = [0] * 65536

        # Initialize Modbus registers to typical values for a 230V voltage regulator
        self.holding_registers[2] = 230
        self.holding_registers[3] = 225
        self.holding_registers[4] = 235

        # Initialize the coils to all zeros
        self.coils = [0] * 65536

        # Initialize output voltage to be enabled, override to be disabled
        self.coils[0] = 1
        self.coils[1] = 0

        # Create a socket and bind it to the specified host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))

        # Start a thread to update voltage generator
        self.update_thread = threading.Thread(target=self.update_voltage_regulator)
        self.update_thread.daemon = True
        self.update_thread.start()


    def update_voltage_regulator(self):
        while True:
            self.holding_registers[0] = random.randint(210, 255)

            # Get the set point from the set point holding register
            set_point = self.holding_registers[2]

            # If the set point is greater than the maximum set point and EnableOverride is not activated,
            # set the set point to the maximum set point
            if set_point > self.holding_registers[4] and not self.coils[1]:
                self.holding_registers[2] = self.holding_registers[4]
            # If the set point is less than the minimum set point and EnableOverride is not activated,
            # set the set point to the minimum set point
            elif set_point < self.holding_registers[3] and not self.coils[1]:
                self.holding_registers[2] = self.holding_registers[3]
            # Otherwise, use the current set point value
            else:
                self.holding_registers[2] = set_point
            
            # Let output voltage vary between +-1 of calculated set point
            variation = random.randint(-1, 1)
            new_value = max(0, set_point + variation)

            # If EnableOutput is set, use the new value as output, else set output to 0
            if self.coils[0]:
                self.holding_registers[1] = new_value
            else:
                self.holding_registers[1] = 0

            # Sleep for 1 second before executing the loop again
            time.sleep(1)
    

    def listen(self):
        # Listen for incoming connections
        self.socket.listen(1)
        
        while True:
            # Accept an incoming connection
            conn, addr = self.socket.accept()
            
            # Receive the request data
            request = conn.recv(1024)
            
            # If the request data is not empty, handle the request
            if len(request) > 0:
                response = self.handle_request(request)
                conn.sendall(response)
                
            # Close the connection
            conn.close()
    
    def handle_request(self, request):
        # Unpack the request data
        # The first 6 bytes are the transaction ID, protocol ID, and length, which are unpacked as ">HHH"
        # The next byte is the unit ID, and the following byte is the function code
        # The rest of the data is the function-specific data
        transaction_id, protocol_id, length = struct.unpack(">HHH", request[:6])
        unit_id = request[6]
        function_code = request[7]
        data = request[8:]
        
        if self.debug:
            print(f"Received request with transaction ID {transaction_id}, unit ID {unit_id}, function code {function_code}, and data {data}")
        
        if function_code == READ_COILS:
            if self.debug:
                print("Handling read coils request")

            # Unpack the coil address and coil count from the Modbus message data
            coil_address, coil_count = struct.unpack(">HH", data)

            # Pack the coil data into a byte array
            coil_data = bytearray()
            for i in range(coil_count):
                # Calculate the index of the current coil
                coil_index = coil_address + i

                # Calculate the index of the byte in the coils array that contains the current coil
                byte_index = coil_index // 8

                # Calculate the bit index of the current coil within the byte
                bit_index = coil_index % 8

                # Check if the current coil is set (i.e., if the corresponding bit is 1)
                if self.coils[byte_index] & (1 << bit_index):
                    coil_data.append(1)
                else:
                    coil_data.append(0)

            # Calculate the number of bytes needed to represent the coils, adding 7 to round up to the nearest byte
            byte_count = (coil_count + 7) // 8

            # Calculate the total response length in bytes by adding 3 bytes for the header and byte count
            response_length = 3 + byte_count

            # Pack the transaction ID, protocol ID, response length, unit ID, and function code into a struct
            response = struct.pack(">HHHBB", transaction_id, protocol_id, response_length, unit_id, function_code)
            
            # Pack the byte count into a struct and append it to the response
            response += struct.pack(">B", byte_count)

            # Create a list of zeros with length of coil_count to store the coil values
            coils = [0] * coil_count

            # Iterate through the range of coil_count
            for i in range(coil_count):
                # Calculate the index of the current coil
                coil_index = coil_address + i
                # If the coil value is 1, set the corresponding value in the coils list to 1, otherwise set it to 0
                if self.coils[coil_index] == 1:
                    coils[i] = 1
                else:
                    coils[i] = 0

            # Pack the coil values into a byte array
            coil_data = bytearray()
            # Iterate over each group of 8 coils (1 byte) in the coils list
            for i in range(coil_count // 8):
                byte_value = 0
                # Iterate over the 8 coils in the current byte
                for j in range(8):
                    # Get the value of the current coil (1 or 0) and shift it to the correct position in the byte
                    bit_value = coils[i * 8 + j]
                    byte_value |= bit_value << j
                coil_data.append(byte_value)

            # If the coil count is not evenly divisible by 8, calculate the remaining bits and add them to the byte array
            if coil_count % 8 != 0:
                byte_value = 0
                # Iterate over the remaining bits
                for i in range(coil_count % 8):
                    # Calculate the bit value and OR it with the byte value
                    bit_value = coils[len(coils) - (coil_count % 8) + i]
                    byte_value |= bit_value << i
                coil_data.append(byte_value)

            response += bytes(coil_data)
            
        elif function_code == READ_HOLDING_REGISTERS:
            if self.debug:
                print("Handling read holding registers request")
            
            starting_address, quantity = struct.unpack(">HH", data)

            # Pack the register data into a byte array
            register_data = bytearray()
            for i in range(quantity):
                register_index = starting_address + i
                value = self.holding_registers[register_index]
                register_data += struct.pack(">H", value)

            # Calculate the number of bytes required to store the register data and the response length
            byte_count = quantity * 2
            response_length = 3 + byte_count

            # Create the response packet with the transaction ID, protocol ID, response length, unit ID, and function code
            response = struct.pack(">HHHBB", transaction_id, protocol_id, response_length, unit_id, function_code)
            
            # Pack the byte count into the response packet
            response += struct.pack(">B", byte_count)
            response += bytes(register_data)

        elif function_code == WRITE_SINGLE_COIL:
            if self.debug:
                print("Handling write single coil request")
            # Unpack the coil address and value from the Modbus message data
            coil_address, coil_value = struct.unpack(">HH", data)

            # If the coil value is 0xFF00 (ON), set the corresponding coil in the self.coils array to 1
            # Otherwise, set the coil to 0
            if coil_value == 0xFF00:
                self.coils[coil_address] = 1
            else:
                self.coils[coil_address] = 0

            # Pack the response data
            response_length = 6
            response = struct.pack(">HHHBBH", transaction_id, protocol_id, response_length, unit_id, function_code, coil_address)
            response += struct.pack(">H", coil_value)

        elif function_code == WRITE_SINGLE_REGISTER:
            if self.debug:
                print("Handling write single register request")

            # Unpack the register address and value from the Modbus message data
            register_address, register_value = struct.unpack(">HH", data)

            # Write the register value to the registers list
            self.holding_registers[register_address] = register_value

            # Pack the response data
            response_length = 6
            response = struct.pack(">HHHBBHH", transaction_id, protocol_id, response_length, unit_id, function_code, register_address, register_value)

        else:
            # Unsupported function code
            if self.debug:
                print("Handling unsupported function code:", function_code)

            # Set the exception function code by OR'ing the received function code with 0x80
            exception_function_code = function_code | 0x80

            # Set the exception code to 0x01, indicating that an unsupported function was requested
            exception_code = 0x01

            # Build the response packet
            response = struct.pack(">HHHBB", transaction_id, protocol_id, 3, unit_id, exception_function_code)
            response += struct.pack(">B", exception_code)
        
        return response
    
    
    def start(self):
        self.listen()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host IP address')
    parser.add_argument('-p', '--port', type=int, default=11502, help='Port number')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable printing debug messages')

    args = parser.parse_args()

    print(f"Starting Modbus TCP device with hostip={args.host}, port={args.port}, debug printing={'on' if args.debug else 'off'}")

    client = ModbusClient(args.host, args.port, args.debug)
    client.start()
