import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import pygame
import neopixel

# Initialize I2C bus and PN532
print("Initializing I2C bus and PN532...")
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()
print("I2C and PN532 initialized.")

# Initialize Pygame mixer
print("Initializing Pygame mixer...")
pygame.mixer.init()
print("Pygame mixer initialized.")

def play_sound(file_path, volume=1.0):
    print(f"Playing sound: {file_path}")
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play()

play_sound("/home/pi/otakiage/drop.wav", 0.5)

# Initialize NeoPixel strip
print("Initializing NeoPixel strip...")
PIXEL_PIN = board.D18
NUM_PIXELS = 48
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5)
print("NeoPixel strip initialized.")

def test_neopixels():
    print("Testing NeoPixels...")
    pixels.fill((255, 0, 0))
    pixels.show()
    time.sleep(1)
    pixels.fill((0, 0, 0))
    pixels.show()
    print("NeoPixel test complete.")

test_neopixels()

# Main loop
while True:
    print("Reading RFID tag...")
    uid = pn532.read_passive_target(timeout=0.5)
    if uid:
        print(f"Tag detected: {uid}")
        play_sound("/home/pi/otakiage/drop.wav", 0.5)
        test_neopixels()
    else:
        print("No tag detected.")
    time.sleep(0.1)
