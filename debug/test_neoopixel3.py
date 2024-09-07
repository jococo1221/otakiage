import time
import board
import neopixel

PIXEL_PIN = board.D18
NUM_PIXELS = 48
BRIGHTNESS = 0.2

def test_neopixels():
    print("Initializing NeoPixel strip...")
    try:
        pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS)
        print("NeoPixel strip initialized.")
        print("Testing NeoPixels...")
        pixels.fill((255, 0, 0))  # Set all pixels to red
        pixels.show()
        time.sleep(1)
        pixels.fill((0, 0, 0))  # Turn off all pixels
        pixels.show()
        print("NeoPixel test complete.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_neopixels()

