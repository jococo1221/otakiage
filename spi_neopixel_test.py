import time
import board
import neopixel_spi as neopixel

# Number of LEDs in your strip
NUM_PIXELS = 24  # Change this based on your setup

# Define SPI for Raspberry Pi
spi = board.SPI()

# Define NeoPixel strip
pixels = neopixel.NeoPixel_SPI(
    spi, NUM_PIXELS, pixel_order=neopixel.GRB, auto_write=False
)

# Colors to cycle through
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue

print("Starting SPI NeoPixel test...")
while True:
    for color in COLORS:
        pixels.fill(color)  # Set all pixels to the current color
        pixels.show()  # Send data to LEDs
        print(f"Showing color: {color}")
        time.sleep(1)  # Wait 1 second
    
        print("Reinitializing and testing SPI NeoPixel...")
        pixels.deinit()  # Deinitialize the current NeoPixel object
        pixels = neopixel.NeoPixel_SPI(
        spi, NUM_PIXELS, pixel_order=neopixel.GRB, auto_write=False
        )



