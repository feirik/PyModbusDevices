#!/usr/bin/env python3

import argparse
import socket
import struct
import threading
import random
import time

# Modbus coils
# ------------
# Ad 200: POWDER_INLET - Open/closed in series with proportional valve controlling flow
# Ad 201: LIQUID_INLET - Open/closed in series with proportional valve controlling flow
# Ad 202: MIXER - On/off turning on mixer in mixing tank required for processing the dry and liquid components
# Ad 203: SAFETY_RELIEF_VALVE - Open/closed relieving pressure
# Ad 204: OUTLET_VALVE - Open/closed tapping the mixing tank of processed product
# Ad 205: AUTO_CONTROL_ENABLE - Enable automatic and less productive control of the process

# Modbus holding registers
# ------------------------
# Ad 230: POWDER_TANK_LEVEL - Feeder tank for powder going into chemical process
# Ad 231: PROPORTIONAL_POWDER_FEED - Proportional valve from powder feeder tank
# Ad 232: LIQUID_TANK_LEVEL - Feeder tank for liquid going into chemical process
# Ad 233: PROPORTIONAL_LIQUID_FEED - Proportional valve from liquid feeder tank
# Ad 234: INTERMEDIATE_SLURRY_LEVEL - Sum of powder and liquid in mixer tank
# Ad 235: PROCESSED_PRODUCT_LEVEL - Sum of processed product in mixer tank
# Ad 236: HEATER - Controllable heater for heating the mixer tank
# Ad 237: MIX_TANK_PRESSURE - Pressure in upper part of tank containing air (kPa)
# Ad 238: TANK_TEMP_LOWER - Temperature in lower part of tank (celsius)
# Ad 239: TANK_TEMP_UPPER - Temperature in upper part of tank (celsius)
# Ad 240: POWDER_MIXING_VOLUME - Volume of powder component (liters)
# Ad 241: LIQUID_MIXING_VOLUME - Volume of liquid component (liters)
# Ad 242: PROD_FLOW - Current flow of finished product (l/s)
# Ad 243: PROD_FLOW_EST_MINUTE - Estimated flow of finished product (l/min)


# Define the Modbus function codes
READ_COILS = 1
READ_DISCRETE_INPUTS = 2 # Not supported
READ_HOLDING_REGISTERS = 3
READ_INPUT_REGISTERS = 4 # Not supported
WRITE_SINGLE_COIL = 5
WRITE_SINGLE_REGISTER = 6
WRITE_MULTIPLE_COILS = 15 # Not supported
WRITE_MULTIPLE_REGISTERS = 16 # Not supported

# Modbus constants
DEFAULT_PORT = 11502 # Test port
REGISTER_SIZE = 65536
MAX_REQUEST_SIZE = 1024
BYTE_SIZE = 8
BYTE_ROUND_UP = 7
REGISTER_BYTE_SIZE = 2
RESPONSE_HEADER_SIZE = 3

# Modbus coil addresses
POWDER_INLET_ADDR = 200
LIQUID_INLET_ADDR = 201
MIXER_ADDR = 202
SAFETY_RELIEF_VALVE_ADDR = 203
OUTLET_VALVE_ADDR = 204
AUTO_CONTROL_ENABLE = 205

# Modbus register addresses
POWDER_TANK_LEVEL_ADDR = 230
PROPORTIONAL_POWDER_FEED_ADDR = 231
LIQUID_TANK_LEVEL_ADDR = 232
PROPORTIONAL_LIQUID_FEED_ADDR = 233
INTERMEDIATE_SLURRY_LEVEL_ADDR = 234
PROCESSED_PRODUCT_LEVEL_ADDR = 235
HEATER_ADDR = 236
MIX_TANK_PRESSURE_ADDR = 237
TANK_TEMP_LOWER_ADDR = 238
TANK_TEMP_UPPER_ADDR = 239
POWDER_MIXING_VOLUME_ADDR = 240
LIQUID_MIXING_VOLUME_ADDR = 241
PROD_FLOW_ADDR = 242
PROD_FLOW_EST_MINUTE_ADDR = 243

# Valve constants
INLET_MAX_FLOW = 10  # Max flow rate in l/s
PROPORTIONAL_VALVE_INCREMENT = 1  # Increment per second for proportional valves
ON_OFF_VALVE_INCREMENT = 20  # Percentage increment per second for on/off valve
VALVE_MIN = 0 # Percentage
VALVE_MAX = 100 # Percentage

# Tank constants
POWDER_TANK_FILL_LIMIT = 300
LIQUID_TANK_FILL_LIMIT = 800
MAX_TANK_VOLUME = 10000  # Maximum volume of the mixing tank in liters
BASE_PRESSURE = 101 # kPa - Atmospheric pressure
PRESSURE_INCREASE_LOW = 0.2
PRESSURE_INCREASE_MEDIUM = 0.3
PRESSURE_INCREASE_HIGH = 0.4
PRESSURE_DECREASE = 0.2
RELEIF_PRESSURE_DECREASE = 5

# Constants for heater simulation
MAX_HEATER_TEMP = 160  # Max temperature at 100% heater setting
COOLING_RATE = 0.2 # How fast the tank cools down per second
HEATING_RATE = 0.4 # How fast the tank heats up per second
AMBIENT_TEMP = 20 # Ambient temperature

# Constants for chemical processing
MIN_REACTION_TEMP = 50
MAX_REACTION_TEMP = 160
BASE_CONVERSION_RATE = 0.2  # Base rate at MIN_REACTION_TEMP
MAX_CONVERSION_RATE = 10  # Max rate at MAX_REACTION_TEMP
REACTION_TEMPERATURE_INCREASE = 0.1

# Constants for enhanced reaction
ENHANCED_REACTION_TEMP_THRESHOLD = 110  # Temperature threshold for enhanced reaction chance
ENHANCED_REACTION_MULTIPLIER = 2 # Multiplier for how much more is processed in an enhanced reaction
EXTRA_HEAT_FROM_ENHANCED_REACTION = 0.6 # Additional temperature increase from an enhanced reaction

# Constants for outlet flow
MAX_OUTLET_FLOW = 25  # Max flow rate in l/s when outlet valve is open

# Error values
ERROR_REG = 9999
ERROR_COIL = 1
PRESSURE_ERROR_LIMIT = 400
POWDER_IGNITION_TEMPERATURE = 130
PRODUCT_MIX_ERROR_LEVEL = 20


class ModbusServer:
    def __init__(self, host, port, debug=False):
        self.debug = debug
        self.listening = False

        # Initialize the holding registers to all zeros
        self.holding_registers = [0] * REGISTER_SIZE

        # Valve positions
        self.powder_inlet = 0
        self.powder_inlet_prop = 0
        self.liquid_inlet = 0
        self.liquid_inlet_prop = 0
        self.outlet_valve_position = 0

        # Tank levels
        self.powder_tank_level = 900 # Start at 900l
        self.liquid_tank_level = 900 # Start at 900l
        self.powder_mix_tank_level = 0
        self.liquid_mix_tank_level = 0
        self.processed_mix_tank_level = 0

        # Inlet flows
        self.powder_inlet_flow = 0
        self.liquid_inlet_flow = 0

        # Outlet flow
        self.product_outlet_flow = 0
        self.product_outlet_flow_history = []

        # Temperatures
        self.temperature_upper = 20 # Start at ambient temperature
        self.temperature_lower = 20 # Start at ambient temperature
        self.upper_temp_history = [20] * 10 # Use historical value for delay - Start at ambient temperature
        self.lower_temp_history = [20] * 10 # Use historical value for delay - Start at ambient temperature

        # Pressure
        self.tank_pressure = 101 # kPa - Start at atmospheric pressure

        # Error boolean indicating process is malfunctioning
        self.process_error = False

        # Initialize Modbus registers to typical startup values
        self.holding_registers[POWDER_TANK_LEVEL_ADDR] = 900 # Start at 900l
        self.holding_registers[PROPORTIONAL_POWDER_FEED_ADDR] = 0
        self.holding_registers[LIQUID_TANK_LEVEL_ADDR] = 900 # Start at 900l
        self.holding_registers[PROPORTIONAL_LIQUID_FEED_ADDR] = 0
        self.holding_registers[INTERMEDIATE_SLURRY_LEVEL_ADDR] = 0
        self.holding_registers[PROCESSED_PRODUCT_LEVEL_ADDR] = 0
        self.holding_registers[HEATER_ADDR] = 0
        self.holding_registers[MIX_TANK_PRESSURE_ADDR] = 101 # kPa - Start at atmospheric pressure
        self.holding_registers[TANK_TEMP_LOWER_ADDR] = 20 # Start at ambient temperature
        self.holding_registers[TANK_TEMP_UPPER_ADDR] = 20 # Start at ambient temperature
        self.holding_registers[POWDER_MIXING_VOLUME_ADDR] = 0
        self.holding_registers[LIQUID_MIXING_VOLUME_ADDR] = 0
        self.holding_registers[PROD_FLOW_ADDR] = 0
        self.holding_registers[PROD_FLOW_EST_MINUTE_ADDR] = 0

        # Initialize the coils to all zeros
        self.coils = [0] * REGISTER_SIZE

        # Initialize process control coils to off (0)
        self.coils[POWDER_INLET_ADDR] = 0
        self.coils[LIQUID_INLET_ADDR] = 0
        self.coils[MIXER_ADDR] = 0
        self.coils[SAFETY_RELIEF_VALVE_ADDR] = 0
        self.coils[OUTLET_VALVE_ADDR] = 0
        self.coils[AUTO_CONTROL_ENABLE] = 0

        # Create a socket and bind it to the specified host and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))

        # Start a thread to simulate data
        self.simulation_thread = threading.Thread(target=self.simulate_data)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()


    def simulate_data(self):
        while True:
            if self.coils[AUTO_CONTROL_ENABLE] == 1:
                # Simulate process sequences if automatic control is enabled
                process_sequence_thread = threading.Thread(target=self.auto_control)
                process_sequence_thread.start()

            # Update simulation data for various parameters
            self.update_inlet_valve_positions()
            self.update_inlet_flows()
            self.update_temperature_from_heater()
            self.process_chemicals()
            self.update_outlet_flow()
            self.update_tank_pressure()
            self.update_registers()

            # Overwrite values if process is malfunctioning
            if self.process_error:
                self.set_error_values()

            time.sleep(1)  # Simulate data update every second


    def auto_control(self):
        self.coils[POWDER_INLET_ADDR] = 1
        self.coils[LIQUID_INLET_ADDR] = 1
        self.coils[MIXER_ADDR] = 1

        # Control valves if below 1400l of each component, or above 1600l
        if self.powder_mix_tank_level < 1400:
            self.holding_registers[PROPORTIONAL_POWDER_FEED_ADDR] = 50

        if self.powder_mix_tank_level > 1600:
            self.holding_registers[PROPORTIONAL_POWDER_FEED_ADDR] = 0

        if self.liquid_mix_tank_level < 1400:
            self.holding_registers[PROPORTIONAL_LIQUID_FEED_ADDR] = 50

        if self.liquid_mix_tank_level > 1600:
            self.holding_registers[PROPORTIONAL_LIQUID_FEED_ADDR] = 0

        # If we have filled up the mixing tank with both components, start the heater gently
        if self.powder_mix_tank_level > 1000 and self.liquid_mix_tank_level > 1000:
            self.holding_registers[HEATER_ADDR] = 40

        # Open outlet if we have over 2000l of finished product in tank, close if below 1700l
        if self.processed_mix_tank_level > 2000:
            self.coils[OUTLET_VALVE_ADDR] = 1

        if self.processed_mix_tank_level < 1700:
            self.coils[OUTLET_VALVE_ADDR] = 0

        # Check for overpressure
        if self.tank_pressure > 200:
            self.coils[SAFETY_RELIEF_VALVE_ADDR] = 1
        else:
            self.coils[SAFETY_RELIEF_VALVE_ADDR] = 0


    def update_inlet_valve_positions(self):
        # Update powder inlet valve position
        if self.coils[POWDER_INLET_ADDR] == 1 and self.powder_inlet < VALVE_MAX:
            self.powder_inlet += ON_OFF_VALVE_INCREMENT
            self.powder_inlet = min(self.powder_inlet, VALVE_MAX)  # Ensure valve position does not exceed max
        elif self.coils[POWDER_INLET_ADDR] == 0 and self.powder_inlet > VALVE_MIN:
            self.powder_inlet -= ON_OFF_VALVE_INCREMENT
            self.powder_inlet = max(self.powder_inlet, VALVE_MIN)  # Ensure valve position does not go below min

        # Update proportional powder feed valve position
        target_prop_powder = self.holding_registers[PROPORTIONAL_POWDER_FEED_ADDR]
        if self.powder_inlet_prop < target_prop_powder:
            self.powder_inlet_prop += PROPORTIONAL_VALVE_INCREMENT
            self.powder_inlet_prop = min(self.powder_inlet_prop, target_prop_powder)
        elif self.powder_inlet_prop > target_prop_powder:
            self.powder_inlet_prop -= PROPORTIONAL_VALVE_INCREMENT
            self.powder_inlet_prop = max(self.powder_inlet_prop, target_prop_powder)

        # Update liquid inlet valve position
        if self.coils[LIQUID_INLET_ADDR] == 1 and self.liquid_inlet < VALVE_MAX:
            self.liquid_inlet += ON_OFF_VALVE_INCREMENT
            self.liquid_inlet = min(self.liquid_inlet, VALVE_MAX)
        elif self.coils[LIQUID_INLET_ADDR] == 0 and self.liquid_inlet > VALVE_MIN:
            self.liquid_inlet -= ON_OFF_VALVE_INCREMENT
            self.liquid_inlet = max(self.liquid_inlet, VALVE_MIN)

        # Update proportional liquid feed valve position
        target_prop_liquid = self.holding_registers[PROPORTIONAL_LIQUID_FEED_ADDR]
        if self.liquid_inlet_prop < target_prop_liquid:
            self.liquid_inlet_prop += PROPORTIONAL_VALVE_INCREMENT
            self.liquid_inlet_prop = min(self.liquid_inlet_prop, target_prop_liquid)
        elif self.liquid_inlet_prop > target_prop_liquid:
            self.liquid_inlet_prop -= PROPORTIONAL_VALVE_INCREMENT
            self.liquid_inlet_prop = max(self.liquid_inlet_prop, target_prop_liquid)


    def update_inlet_flows(self):
        self.powder_inlet_flow = min(self.powder_inlet, self.powder_inlet_prop) / 100 * INLET_MAX_FLOW
        self.liquid_inlet_flow = min(self.liquid_inlet, self.liquid_inlet_prop) / 100 * INLET_MAX_FLOW

        # Subtract the calculated flow from the respective tank levels
        self.powder_tank_level -= self.powder_inlet_flow
        self.liquid_tank_level -= self.liquid_inlet_flow

        # Add the calculated flow to the respective mixing volumes
        self.powder_mix_tank_level += self.powder_inlet_flow
        self.liquid_mix_tank_level += self.liquid_inlet_flow

        # Powder level is manually filled below fill limit - Simulating manual filling process
        if self.powder_tank_level < POWDER_TANK_FILL_LIMIT:
            refill_powder = random.randint(400, 600)
            self.powder_tank_level += refill_powder

        # Liquid level is kept around fill limit - Simulating automatic fill process from another part of plant
        if self.liquid_tank_level < LIQUID_TANK_FILL_LIMIT:
            self.liquid_tank_level = random.randint(LIQUID_TANK_FILL_LIMIT - 3, LIQUID_TANK_FILL_LIMIT)


    def update_temperature_from_heater(self):
        # Heater settings (as a percentage)
        heater_setting = self.holding_registers[HEATER_ADDR] / 100

        # Linear interpolation for target temperature based on heater setting
        # This will create a straight line between 0% (AMBIENT_TEMP) and 100% (MAX_HEATER_TEMP)
        target_temperature = heater_setting * (MAX_HEATER_TEMP - AMBIENT_TEMP) + AMBIENT_TEMP

        # Get the temperatures from 10 seconds ago to introduce delay in regulation
        delayed_upper_temp = self.upper_temp_history.pop(0)  # Remove the oldest value
        delayed_lower_temp = self.lower_temp_history.pop(0)  # Remove the oldest value

        # Update the temperature history lists with the latest values
        self.upper_temp_history.append(self.temperature_upper)
        self.lower_temp_history.append(self.temperature_lower)

        # Heating process
        # Only increase temperature if below target, else allow cooling
        if delayed_lower_temp < target_temperature:
            self.temperature_lower += HEATING_RATE
            self.temperature_upper += HEATING_RATE
        else:
            self.temperature_lower = max(self.temperature_lower - COOLING_RATE, AMBIENT_TEMP)
            self.temperature_upper = max(self.temperature_upper - COOLING_RATE, AMBIENT_TEMP)


    def process_chemicals(self):
        # Get the current mixer status and temperature
        mixer_on = self.coils[MIXER_ADDR]
        current_temp = self.temperature_lower

        # Calculate the current conversion rate based on temperature
        if current_temp < MIN_REACTION_TEMP:
            conversion_rate = 0  # No reaction if below minimum temperature
        else:
            # Interpolate conversion rate based on current temperature
            conversion_rate = (BASE_CONVERSION_RATE + 
                              (current_temp - MIN_REACTION_TEMP) / 
                              (MAX_REACTION_TEMP - MIN_REACTION_TEMP) * 
                              (MAX_CONVERSION_RATE - BASE_CONVERSION_RATE))

        # Check if the mixer is on and the temperature is sufficient for reaction
        if mixer_on == 1 and current_temp >= MIN_REACTION_TEMP:
            # Determine if an enhanced reaction occurs (25% chance when temp > 110)
            is_enhanced_reaction = current_temp > ENHANCED_REACTION_TEMP_THRESHOLD and random.random() < 0.25

            # Calculate how much chemical is processed from powder and liquid
            # Enhance the rate if there's an enhanced reaction
            if is_enhanced_reaction:
                reaction_multiplier = ENHANCED_REACTION_MULTIPLIER
            else:
                reaction_multiplier = 1

            processed_powder = min(self.powder_mix_tank_level, conversion_rate * reaction_multiplier)
            processed_liquid = min(self.liquid_mix_tank_level, conversion_rate * reaction_multiplier)

            # Subtract the processed amount from the mixing volumes
            self.powder_mix_tank_level -= processed_powder
            self.liquid_mix_tank_level -= processed_liquid

            # Add the processed amount to the product level
            self.processed_mix_tank_level += (processed_powder + processed_liquid)

            # Reaction process increases temperature, more so if enhanced
            if is_enhanced_reaction:
                temperature_increase = REACTION_TEMPERATURE_INCREASE + EXTRA_HEAT_FROM_ENHANCED_REACTION
            else:
                temperature_increase = REACTION_TEMPERATURE_INCREASE
 
            self.temperature_lower += temperature_increase
            self.temperature_upper += temperature_increase

            # Ensure the mixing volumes don't drop below zero
            self.powder_mix_tank_level = max(self.powder_mix_tank_level, 0)
            self.liquid_mix_tank_level = max(self.liquid_mix_tank_level, 0)

        # Check if tank operations result in malfunctioning
        tank_level = self.powder_mix_tank_level + self.liquid_mix_tank_level + self.processed_mix_tank_level

        # Error if mixing tank is overfilled
        if tank_level > MAX_TANK_VOLUME:
            self.process_error = True

        # Error if outlet valve tries to empty unprocessed liquid
        if self.processed_mix_tank_level <= PRODUCT_MIX_ERROR_LEVEL and self.outlet_valve_position != 0:
            self.process_error = True

        # Error if powder is fed into mixing tank during high temperature, with safety releif valve open
        if self.coils[SAFETY_RELIEF_VALVE_ADDR] == 1:
            if self.powder_inlet_flow != 0 and self.temperature_upper > POWDER_IGNITION_TEMPERATURE:
                self.process_error = True
    

    def update_outlet_flow(self):
        # Update outlet valve position based on the coil status
        if self.coils[OUTLET_VALVE_ADDR] == 1 and self.outlet_valve_position < VALVE_MAX:
            # Open the valve if it's not fully open
            self.outlet_valve_position += ON_OFF_VALVE_INCREMENT
            self.outlet_valve_position = min(self.outlet_valve_position, VALVE_MAX)
        elif self.coils[OUTLET_VALVE_ADDR] == 0 and self.outlet_valve_position > VALVE_MIN:
            # Close the valve if it's not fully closed
            self.outlet_valve_position -= ON_OFF_VALVE_INCREMENT
            self.outlet_valve_position = max(self.outlet_valve_position, VALVE_MIN)

        # Determine the outlet flow based on valve position
        if self.outlet_valve_position > 0:
            # If the valve is open, calculate flow rate based on valve position
            effective_outlet_flow = (self.outlet_valve_position / VALVE_MAX) * MAX_OUTLET_FLOW
            self.product_outlet_flow = min(self.processed_mix_tank_level, effective_outlet_flow)
        else:
            # If valve is closed, there is no outlet flow
            self.product_outlet_flow = 0

        # Update the outlet flow history
        self.product_outlet_flow_history.append(self.product_outlet_flow)
        # Ensure the list does not exceed 60 entries
        if len(self.product_outlet_flow_history) > 60:
            self.product_outlet_flow_history.pop(0)

        # Subtract the outlet flow from the processed mix tank level
        self.processed_mix_tank_level -= self.product_outlet_flow

        # Ensure the processed mix tank level doesn't drop below zero
        self.processed_mix_tank_level = max(self.processed_mix_tank_level, 0)


    def get_average_outlet_flow_per_minute(self):
        # Return the average flow rate from the history
        if self.product_outlet_flow_history:
            return (sum(self.product_outlet_flow_history) / len(self.product_outlet_flow_history)) * 60
        else:
            return 0


    def update_tank_pressure(self):
        # Calculate the current total volume in the mixing tank
        current_volume = self.powder_mix_tank_level + self.liquid_mix_tank_level + self.processed_mix_tank_level

        # Calculate the tank's fill percentage
        fill_percentage = (current_volume / MAX_TANK_VOLUME) * 100

        pressure_change_rate = 0

        # Determine the pressure change rate based on the temperature
        if self.temperature_upper > 50:
            if self.temperature_upper < 80:
                pressure_change_rate = PRESSURE_INCREASE_LOW
            elif self.temperature_upper < 120:
                pressure_change_rate = PRESSURE_INCREASE_MEDIUM
            else:
                pressure_change_rate = PRESSURE_INCREASE_HIGH

        # Increase pressure more quickly if tank is very full
        if fill_percentage > 50:
            pressure_scaling_factor = 1 + ((fill_percentage / 50) ** 2)
        else:
            pressure_scaling_factor = 1

        # Apply the pressure change rate only if the tank is more than 50% full
        if fill_percentage > 50:
            self.tank_pressure += pressure_change_rate * pressure_scaling_factor
        else:
            # Decrease the pressure if the tank is not more than 50% full
            self.tank_pressure -= PRESSURE_DECREASE

        # Rapidly decrease pressure if pressure relief valve is open
        if self.coils[SAFETY_RELIEF_VALVE_ADDR] == 1:
            self.tank_pressure -= RELEIF_PRESSURE_DECREASE

        # Ensure pressure doesn't fall below atmospheric pressure
        self.tank_pressure = max(self.tank_pressure, BASE_PRESSURE)

        if self.tank_pressure > PRESSURE_ERROR_LIMIT:
            self.process_error = True


    def update_registers(self):
        # Update registers with integers based on process values
        self.holding_registers[POWDER_TANK_LEVEL_ADDR] = int(self.powder_tank_level)
        self.holding_registers[LIQUID_TANK_LEVEL_ADDR] = int(self.liquid_tank_level)
        self.holding_registers[POWDER_MIXING_VOLUME_ADDR] = int(self.powder_mix_tank_level)
        self.holding_registers[LIQUID_MIXING_VOLUME_ADDR] = int(self.liquid_mix_tank_level)
        self.holding_registers[PROCESSED_PRODUCT_LEVEL_ADDR] = int(self.processed_mix_tank_level)
        self.holding_registers[INTERMEDIATE_SLURRY_LEVEL_ADDR] = int(self.powder_mix_tank_level + self.liquid_mix_tank_level)
        self.holding_registers[TANK_TEMP_UPPER_ADDR] = round(self.temperature_upper)
        self.holding_registers[TANK_TEMP_LOWER_ADDR] = round(self.temperature_lower)
        self.holding_registers[PROD_FLOW_ADDR] = int(self.product_outlet_flow)
        self.holding_registers[PROD_FLOW_EST_MINUTE_ADDR] = round(self.get_average_outlet_flow_per_minute())
        self.holding_registers[MIX_TANK_PRESSURE_ADDR] = round(self.tank_pressure)

    
    def set_error_values(self):
        self.holding_registers[POWDER_TANK_LEVEL_ADDR] = ERROR_REG
        self.holding_registers[PROPORTIONAL_POWDER_FEED_ADDR] = ERROR_REG
        self.holding_registers[LIQUID_TANK_LEVEL_ADDR] = ERROR_REG
        self.holding_registers[PROPORTIONAL_LIQUID_FEED_ADDR] = ERROR_REG
        self.holding_registers[INTERMEDIATE_SLURRY_LEVEL_ADDR] = ERROR_REG
        self.holding_registers[PROCESSED_PRODUCT_LEVEL_ADDR] = ERROR_REG
        self.holding_registers[HEATER_ADDR] = ERROR_REG
        self.holding_registers[MIX_TANK_PRESSURE_ADDR] = ERROR_REG
        self.holding_registers[TANK_TEMP_LOWER_ADDR] = ERROR_REG
        self.holding_registers[TANK_TEMP_UPPER_ADDR] = ERROR_REG
        self.holding_registers[POWDER_MIXING_VOLUME_ADDR] = ERROR_REG
        self.holding_registers[LIQUID_MIXING_VOLUME_ADDR] = ERROR_REG
        self.holding_registers[PROD_FLOW_ADDR] = ERROR_REG
        self.holding_registers[PROD_FLOW_EST_MINUTE_ADDR] = ERROR_REG

        self.coils[POWDER_INLET_ADDR] = ERROR_COIL
        self.coils[LIQUID_INLET_ADDR] = ERROR_COIL
        self.coils[MIXER_ADDR] = ERROR_COIL
        self.coils[SAFETY_RELIEF_VALVE_ADDR] = ERROR_COIL
        self.coils[OUTLET_VALVE_ADDR] = ERROR_COIL


    def listen(self):
        self.listening = True

        # Listen for incoming connections
        self.socket.listen(1)
        
        while self.listening:
            # Accept an incoming connection
            conn, addr = self.socket.accept()
            
            # Receive the request data
            request = conn.recv(MAX_REQUEST_SIZE)
            
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
                byte_index = coil_index // BYTE_SIZE

                # Calculate the bit index of the current coil within the byte
                bit_index = coil_index % BYTE_SIZE

                # Check if the current coil is set (i.e., if the corresponding bit is 1)
                if self.coils[byte_index] & (1 << bit_index):
                    coil_data.append(1)
                else:
                    coil_data.append(0)

            # Calculate the number of bytes needed to represent the coils, adding 7 to round up to the nearest byte
            byte_count = (coil_count + BYTE_ROUND_UP) // BYTE_SIZE

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
            for i in range(coil_count // BYTE_SIZE):
                byte_value = 0
                # Iterate over the 8 coils in the current byte
                for j in range(BYTE_SIZE):
                    # Get the value of the current coil (1 or 0) and shift it to the correct position in the byte
                    bit_value = coils[i * BYTE_SIZE + j]
                    byte_value |= bit_value << j
                coil_data.append(byte_value)

            # If the coil count is not evenly divisible by 8, calculate the remaining bits and add them to the byte array
            if coil_count % BYTE_SIZE != 0:
                byte_value = 0
                # Iterate over the remaining bits
                for i in range(coil_count % BYTE_SIZE):
                    # Calculate the bit value and OR it with the byte value
                    bit_value = coils[len(coils) - (coil_count % BYTE_SIZE) + i]
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
            byte_count = quantity * REGISTER_BYTE_SIZE
            response_length = RESPONSE_HEADER_SIZE + byte_count

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

            print("Wrote " + str(register_value) + " to addr: " + str(register_address))

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

    def stop(self):
        self.listening = False


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host IP address')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help='Port number')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable printing debug messages')

    args = parser.parse_args()

    print(f"Starting Modbus TCP device with hostip={args.host}, port={args.port}, debug printing={'on' if args.debug else 'off'}")

    server = ModbusServer(args.host, args.port, args.debug)
    server.start()
