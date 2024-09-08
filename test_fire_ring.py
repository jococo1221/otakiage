import time
import random
import math
from rpi_ws281x import PixelStrip, Color

# LED strip configuration
LED_PIN = 18         # GPIO pin connected to the strip (18 is PWM).
NUM_LEDS = 20        # Number of LEDs in the ring
BRIGHTNESS = 255     # Max brightness
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0

# Fire simulation parameters
COOLING = 30         # How much the air cools as it rises
SPARKING = 90       # Chance (out of 255) a new spark will be added
FRAMES_PER_SECOND = 20

# Color palettes
PALETTES = {
    'default': [(0, 0, 0), (255, 0, 0), (255, 255, 0), (255, 255, 255)],  # Black -> Red -> Yellow -> White
    'custom': [(0, 0, 0), (50, 0, 0), (100, 100, 50), (255, 255, 255)],  # Black -> Red -> Yellow -> White
    'blue_fire': [(0, 0, 0), (0, 0, 255), (0, 255, 255), (255, 255, 255)],  # Black -> Blue -> Aqua -> White
    'simple_fire': [(0, 0, 0), (255, 0, 0), (255, 255, 255)],  # Black -> Red -> White
}

# Choose active palette here
active_palette_name = 'custom'
active_palette = PALETTES[active_palette_name]

# Create PixelStrip object
strip = PixelStrip(NUM_LEDS, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, BRIGHTNESS, LED_CHANNEL)
strip.begin()

# Helper function to convert RGB to 32-bit color
def color(r, g, b):
    return Color(r, g, b)

def color_from_palette(heat, palette):
    # Map heat value (0-255) to the palette index
    palette_size = len(palette) - 1
    index = min(int((heat / 255) * palette_size), palette_size)
    return palette[index]

def fire_simulation():
    heat = [0] * NUM_LEDS

    while True:
        # Step 1: Cool down every cell a little
        for i in range(NUM_LEDS):
            cooling = random.randint(0, (COOLING * 10 // NUM_LEDS) + 2)
            heat[i] = max(0, heat[i] - cooling)

        # Step 2: Heat from each cell drifts 'up' and diffuses a little
        for k in range(NUM_LEDS - 1, 2, -1):
            heat[k] = (heat[k - 1] + heat[k - 2] + heat[k - 2]) // 3

        # Step 3: Randomly ignite new 'sparks' near the bottom
        if random.randint(0, 255) < SPARKING:
            y = random.randint(0, 7)
            heat[y] = min(255, heat[y] + random.randint(160, 255))

        # Step 4: Map from heat cells to LED colors
        for j in range(NUM_LEDS):
            color_value = color_from_palette(heat[j], active_palette)
            r, g, b = color_value
            strip.setPixelColor(j, color(r, g, b))

        strip.show()
        time.sleep(1 / FRAMES_PER_SECOND)

if __name__ == "__main__":
    try:
        fire_simulation()
    except KeyboardInterrupt:
        # Gracefully shut down the LED strip on exit
        for i in range(NUM_LEDS):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
