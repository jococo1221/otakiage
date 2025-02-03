import time
import board
import neopixel

# Define the number of pixels (24 for your ring)
NUM_PIXELS = 24

# Define GPIO pin for the NeoPixel data line
PIXEL_PIN = board.D18  # Assuming data line is connected to GPIO 18

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5)


def fadein_light_effect(delay=0.05, steps=10):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        pixels.fill(dim_white)
        pixels.show()
        time.sleep(delay)

def fadeout_light_effect(delay=0.05, steps=10):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        pixels.fill(dim_white)
        pixels.show()
        time.sleep(delay)
    


# Function to light two LEDs simultaneously, moving in a circle
def move_light_effect(delay=0.05):

    white = (127, 127, 127) # Warm white color at 50% intensity
    dim_white = (10, 10, 10) # Warm white color at 50% intensity

    # Turn off all pixels
    pixels.fill(dim_white)
    pixels.show()
    
    # Sequence to light up two LEDs radially opposite each other
    for i in range(NUM_PIXELS // 2):
        opposite_index = i + NUM_PIXELS // 2
        
        pixels[i] = white  
        pixels[opposite_index] = white 
        
        pixels.show()
        time.sleep(delay)
        
        pixels[i] = dim_white
        pixels[opposite_index] = dim_white
    
    # Ensure all LEDs are off before exiting the function
    pixels.show()

# Main program loop
while True:
    fadein_light_effect()
    move_light_effect()
    move_light_effect()
    fadeout_light_effect()
