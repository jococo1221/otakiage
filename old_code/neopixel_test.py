import time
from rpi_ws281x import PixelStrip, Color

# LED configuration:
LED_COUNT = 24          # Number of LED pixels.
LED_PIN = 18           # GPIO pin connected to the pixels (must support PWM).
LED_FREQ_HZ = 800000   # LED signal frequency in hertz (usually 800kHz).
LED_DMA = 10           # DMA channel to use for generating signal (try 10).
LED_BRIGHTNESS = 255   # Brightness of the LEDs (0-255).
LED_INVERT = False     # True to invert the signal (when using NPN transistor level shift).
LED_CHANNEL = 0        # Set to 1 for GPIOs 13, 19, 41, 45, or 53.

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

def color_wipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)

def theater_chase(strip, color, wait_ms=50, iterations=10):
    """Create a theater chase effect."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw a rainbow that fades across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

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
            print("Theater chase: White")
            theater_chase(strip, Color(127, 127, 127))  # White theater chase
            print("Rainbow animation")
            rainbow(strip)
    except KeyboardInterrupt:
        print("Exiting. Turning off LEDs...")
        color_wipe(strip, Color(0, 0, 0))  # Turn off LEDs
