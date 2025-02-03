import board
import busio
from adafruit_pn532.i2c import PN532_I2C

# Initialize I2C and PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=True)

print("Looking for PN532...")
version = pn532.firmware_version
print(f"PN532 Firmware Version: {version}")

print("Waiting for RFID tag...")
while True:
    uid = pn532.read_passive_target(timeout=1.0)
    if uid:
        print(f"Tag detected! UID: {uid}")
