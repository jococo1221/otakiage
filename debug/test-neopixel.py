import time
import board
import neopixel

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
