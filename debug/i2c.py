import board
import busio
from adafruit_pn532.i2c import PN532_I2C

# Initialize I2C bus and PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with RFID tags
pn532.SAM_configuration()

# Attempt to read a tag
uid = pn532.read_passive_target(timeout=0.5)
if uid:
    print(f"Tag detected: {uid}")
else:
    print("No tag detected")
