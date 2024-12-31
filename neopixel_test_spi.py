import time
from rpi_ws281x import PixelStrip, Color

# LED configuration:
LED_COUNT = 24          # Number of LED pixels.
LED_PIN = 10            # GPIO pin for SPI MOSI (must be 10 for SPI control).
LED_FREQ_HZ = 800000    # LED signal frequency in hertz (usually 800kHz).
LED_DMA = 10            # DMA channel to use for generating signal.
LED_BRIGHTNESS = 255    # Brightness of the LEDs (0-255).
LED_CHANNEL = 0         # Channel not required for SPI.

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, False, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def color_wipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

if __name__ == "__main__":
    try:
        print("Press Ctrl-C to quit.")
        while True:
            print("Color wipe: Red")
            color_wipe(strip, Color(255, 0, 0))  # Red wipe
            print("Color wipe: Green")
            color_wipe(strip, Color(0, 255, 0))  # Green wipe
            print("Color wipe: Blue")
            color_wipe(strip, Color(0, 0, 255))  # Blue wipe
    except KeyboardInterrupt:
        print("Exiting. Turning off LEDs...")
        color_wipe(strip, Color(0, 0, 0))  # Turn off LEDs
