import board
import busio
from adafruit_pn532.i2c import PN532_I2C

# Initialize I2C bus and PN532
print("Initializing I2C bus and PN532...")
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()
print("I2C and PN532 initialized.")
