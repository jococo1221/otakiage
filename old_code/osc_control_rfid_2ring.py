import time
import board
import busio
import threading
from digitalio import DigitalInOut
from adafruit_pn532.i2c import PN532_I2C
from pythonosc import udp_client
import neopixel

# Initialize I2C bus and PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with RFID tags
pn532.SAM_configuration()

# Define OSC client
args = {"ip": "shine.local", "port": 5005}
client = udp_client.SimpleUDPClient(args["ip"], args["port"])

# Define GPIO pin for the NeoPixel data line
PIXEL_PIN = board.D18  # Assuming data line is connected to GPIO 18

# Define the number of pixels per ring
NUM_PIXELS_PER_RING = 24
NUM_RINGS = 1  # Set this to 1 for debugging single ring

# Initialize NeoPixel strip for two rings
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS_PER_RING * NUM_RINGS, brightness=0.5)

# Define RFID tags
rfid_tags = {
    1: {"uid": [0x23, 0xa8, 0x18, 0xf7, 0x64], "message": "Blue tag 1"},
    2: {"uid": [0xC9, 0x00, 0xFA, 0xB9, 0x8A], "message": "Blue tag 2"},
    3: {"uid": [0x4, 0x79, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Sticker 1"},
    4: {"uid": [0x04, 0xbb, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Sticker 2"},
    5: {"uid": [0x04, 0x47, 0xc8, 0xd2, 0x56, 0x49, 0x81], "message": "It'sa me"},
    6: {"uid": [0xb3, 0xc2, 0x00, 0xfd, 0x8c], "message": "White card"},
    7: {"uid": [0x04, 0x20, 0xee, 0x1a, 0x5c, 0x15, 0x90], "message": "Ticket"},
}

# Function to detect RFID tag
def detect_tag(uid):
    for tag_key, tag_data in rfid_tags.items():
        if uid == bytearray(tag_data["uid"]):
            return tag_key
    return None

# Helper function to set pixels for a specific ring
def set_pixels_for_ring(color, ring):
    start_index = (ring - 1) * NUM_PIXELS_PER_RING
    end_index = ring * NUM_PIXELS_PER_RING
    for i in range(start_index, end_index):
        pixels[i] = color

# LED animation functions with ring parameter
def fadein_light_effect(delay=0.02, steps=10, ring=1):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        set_pixels_for_ring(dim_white, ring)
        pixels.show()
        time.sleep(delay)

def fadeout_light_effect(delay=0.02, steps=10, ring=1):
    max_brightness = 10  # Maximum brightness level
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        set_pixels_for_ring(dim_white, ring)
        pixels.show()
        time.sleep(delay)

def move_light_effect(delay=0.02, ring=1):
    white = (127, 127, 127)  # Warm white color at 50% intensity
    dim_white = (10, 10, 10)  # Warm white color at 50% intensity

    # Turn off all pixels in the ring
    set_pixels_for_ring(dim_white, ring)
    pixels.show()

    # Sequence to light up two LEDs radially opposite each other
    for i in range(NUM_PIXELS_PER_RING // 2):
        start_index = (ring - 1) * NUM_PIXELS_PER_RING
        opposite_index = i + NUM_PIXELS_PER_RING // 2

        pixels[start_index + i] = white
        pixels[start_index + opposite_index] = white

        pixels.show()
        time.sleep(delay)

        pixels[start_index + i] = dim_white
        pixels[start_index + opposite_index] = dim_white

    # Ensure all LEDs are off before exiting the function
    pixels.show()

def tag_read_light_effect(ring=1):
    move_light_effect(ring=ring)

def breathing_light_effect(delay=0.02, steps=50, ring=1):
    breath_depth = 30  # Maximum brightness level
    while True:
        for step in range(steps + 1):
            intensity = int(breath_depth * step / steps)
            dim_color = (intensity, int(.1*intensity), int(.1*intensity))
            set_pixels_for_ring(dim_color, ring)
            pixels.show()
            time.sleep(delay)
        for step in range(steps + 1):
            intensity = int(breath_depth * (steps - step) / steps)
            dim_color = (intensity, int(.1*intensity), int(.1*intensity))
            set_pixels_for_ring(dim_color, ring)
            pixels.show()
            time.sleep(delay)

# Start breathing light effect in a separate thread for each ring
breathing_thread_1 = threading.Thread(target=breathing_light_effect, args=(0.02, 50, 1))
breathing_thread_1.daemon = True
breathing_thread_1.start()

# breathing_thread_2 = threading.Thread(target=breathing_light_effect, args=(0.02, 50, 2))
# breathing_thread_2.daemon = True
# breathing_thread_2.start()

# Main loop
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        tag_key = detect_tag(uid)
        if tag_key is not None:
            print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
            if tag_key == 1 or tag_key == 3:  # Blue tag 1
                print("sent tag ", tag_key)
                client.send_message("/4/multitoggle/2/1", 1.0)  # increase intensity
            elif tag_key == 2 or tag_key == 4:  # Blue tag 2
                client.send_message("/4/multitoggle/2/2", 1.0)  # decrease intensity
            elif tag_key == 6 or tag_key == 7:
                print("crickets")
                client.send_message("/4/multitoggle/2/3", 1.0)  # crickets
            elif tag_key == 5:
                print("mario")
                client.send_message("/4/multitoggle/2/7", 1.0)  # mario
            fadein_light_effect(ring=1)
            tag_read_light_effect(ring=1)
            move_light_effect(ring=1)
            fadeout_light_effect(ring=1)
        else:
            print(f"Unknown tag detected with UID: {uid}")
            uid_hex = " ".join(format(x, '02x') for x in uid)
            print(f"Tag UID: {[hex(byte) for byte in uid]}".replace("'", ""))  # print(f"Tag UID: {uid_hex}")
            client.send_message("/4/multitoggle/2/8", 1.0)  # error
            fadeout_light_effect(ring=1)
    time.sleep(0.1)
