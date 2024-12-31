from smbus2 import SMBus, i2c_msg
import time

# Define the I2C bus and PN532 address
I2C_BUS_NUMBER = 11  # Change if using a different software I2C bus
PN532_I2C_ADDRESS = 0x24  # Default I2C address of PN532

# PN532 Commands
COMMAND_GET_FIRMWARE_VERSION = [0xD4, 0x02]
COMMAND_SAM_CONFIGURATION = [0xD4, 0x14, 0x01, 0x14, 0x01]

def write_command(bus, address, command):
    """Send a command to the PN532 over I2C."""
    bus.write_i2c_block_data(address, 0x00, command)  # Write to the device

def read_response(bus, address, length):
    """Read the response from the PN532."""
    msg = i2c_msg.read(address, length)
    bus.i2c_rdwr(msg)
    return list(msg)

def check_ack(response):
    """Check if the PN532 sent an ACK (0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00)."""
    ack = [0x00, 0x00, 0xFF, 0x00, 0xFF, 0x00]
    return response[:6] == ack

def main():
    try:
        with SMBus(I2C_BUS_NUMBER) as bus:
            print("Initializing PN532...")

            # Step 1: Get Firmware Version
            print("Sending Get Firmware Version command...")
            write_command(bus, PN532_I2C_ADDRESS, COMMAND_GET_FIRMWARE_VERSION)
            time.sleep(0.1)  # Small delay to let the PN532 process the command
            
            # Read response (firmware version)
            response = read_response(bus, PN532_I2C_ADDRESS, 12)  # Adjust length if needed
            print(f"Firmware Version Response: {response}")
            if not check_ack(response):
                print("ACK not received after Get Firmware Version command.")
                return

            # Step 2: Configure SAM
            print("Sending SAM Configuration command...")
            write_command(bus, PN532_I2C_ADDRESS, COMMAND_SAM_CONFIGURATION)
            time.sleep(0.1)  # Small delay to let the PN532 process the command
            
            # Read response (acknowledgment for SAM Configuration)
            response = read_response(bus, PN532_I2C_ADDRESS, 8)  # Adjust length if needed
            print(f"SAM Configuration Response: {response}")
            if not check_ack(response):
                print("ACK not received after SAM Configuration command.")
                return

            print("PN532 is initialized and responding correctly!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
