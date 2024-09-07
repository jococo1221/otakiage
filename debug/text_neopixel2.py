import time
import board
import neopixel

# Function to initialize NeoPixel strip
def initialize_neopixel(pin, num_pixels, brightness):
    try:
        print("Initializing NeoPixel strip...")
        pixels = neopixel.NeoPixel(pin, num_pixels, brightness=brightness)
        print("NeoPixel strip initialized.")
        return pixels
    except Exception as e:
        print(f"Error initializing NeoPixel strip: {e}")
        return None

# Function to test NeoPixels
def test_neopixels(pixels):
    if pixels is None:
        print("NeoPixel strip not initialized. Skipping test.")
        return

    try:
        print("Testing NeoPixels...")
        pixels.fill((255, 0, 0))  # Set all pixels to red
        pixels.show()
        time.sleep(1)
        pixels.fill((0, 0, 0))  # Turn off all pixels
        pixels.show()
        print("NeoPixel test complete.")
    except Exception as e:
        print(f"Error during NeoPixel test: {e}")

# Main execution
def main():
    PIXEL_PIN = board.D18  # Define the GPIO pin for NeoPixel data
    NUM_PIXELS = 48  # Define the number of pixels
    BRIGHTNESS = 0.2  # Set brightness (lower value for safety)
    
    pixels = initialize_neopixel(PIXEL_PIN, NUM_PIXELS, BRIGHTNESS)
    test_neopixels(pixels)

if __name__ == "__main__":
    main()
