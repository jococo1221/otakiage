# pip install rpi_ws281x adafruit-circuitpython-neopixel

import time
import board
import neopixel

# Configuration
LED_COUNT = 24        # Number of LED pixels in your strip
LED_PIN = board.D18   # GPIO pin connected to the pixels (18 is default for GPIO.BCM)
LED_BRIGHTNESS = 0.2  # Set brightness from 0 to 1 (optional)

# Initialize the neopixel object
pixels = neopixel.NeoPixel(LED_PIN, LED_COUNT, brightness=LED_BRIGHTNESS, auto_write=False)

# Define colors (in RGB format)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

# Function to set all LEDs to a specific color
def set_all_pixels(color):
    pixels.fill(color)
    pixels.show()

# Function to cycle through colors
def color_cycle():
    colors = [RED, GREEN, BLUE, WHITE]
    for color in colors:
        set_all_pixels(color)
        time.sleep(1)

# Main loop
if __name__ == "__main__":
    try:
        while True:
            color_cycle()

    except KeyboardInterrupt:
        # Cleanup and turn off LEDs on exit
        pixels.fill(OFF)
        pixels.show()
