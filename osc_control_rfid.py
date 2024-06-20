import time
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from pythonosc import udp_client, osc_message_builder
import neopixel
import socket

# Initialize I2C bus and PN532
i2c = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with RFID tags
pn532.SAM_configuration()

# Define OSC client with retry mechanism
args = {"ip": "shine.local", "port": 5005}
max_retries = 5
retry_delay = 5
client = None

for attempt in range(max_retries):
    try:
        client = udp_client.SimpleUDPClient(args["ip"], args["port"])
        # Test connection
        client.send_message("/test", 1.0)
        print(f"Connected to OSC server on {args['ip']}:{args['port']}")
        break
    except (socket.gaierror, ConnectionRefusedError):
        print(f"Failed to connect to OSC server. Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)
else:
    print("Could not connect to OSC server. Continuing without OSC server.")

# Define GPIO pin for the NeoPixel data line
PIXEL_PIN = board.D18  # Assuming data line is connected to GPIO 18

# Define the number of pixels (24 for your ring, 48 for two rings)
NUM_PIXELS = 48

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5)

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

# LED animation functions
def shine_light_effect(delay=0.01, steps=5, ring=1):
    max_brightness = 220  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = dim_white
        pixels.show()
        time.sleep(delay)
    steps = 2
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = dim_white
        pixels.show()
        time.sleep(delay)

def fadein_light_effect(delay=0.02, steps=10, ring=1):
    max_brightness = 10  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = dim_white
        pixels.show()
        time.sleep(delay)

def fadeout_light_effect(delay=0.02, steps=10, ring=1):
    max_brightness = 10  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = dim_white
        pixels.show()
        time.sleep(delay)

def move_light_effect(delay=0.02, ring=1):
    white = (127, 127, 127)  # Warm white color at 50% intensity
    dim_white = (10, 10, 10)  # Warm white color at 50% intensity

    # Turn off all pixels in the ring
    start_index = (ring - 1) * NUM_PIXELS // 2
    for i in range(start_index, start_index + NUM_PIXELS // 2):
        pixels[i] = dim_white
    pixels.show()

    # Sequence to light up two LEDs radially opposite each other
    for i in range(NUM_PIXELS // 4):
        opposite_index = i + NUM_PIXELS // 4

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

class BreathingEffect(threading.Thread):
    def __init__(self, delay=0.02, steps=50, ring=1):
        super().__init__()
        self.delay = delay
        self.steps = steps
        self.ring = ring
        self.breath_depth = 30  # Maximum brightness level
        self.stop_event = threading.Event()
        self.daemon = True

    def run(self):
        while not self.stop_event.is_set():
            for step in range(self.steps + 1):
                if self.stop_event.is_set():
                    break
                intensity = int(self.breath_depth * step / self.steps)
                dim_color = (intensity, int(.1*intensity), int(.1*intensity))
                start_index = (self.ring - 1) * NUM_PIXELS // 2
                for i in range(start_index, start_index + NUM_PIXELS // 2, 1):  # Use every other LED
                    pixels[i] = dim_color
                pixels.show()
                time.sleep(self.delay)
            for step in range(self.steps + 1):
                if self.stop_event.is_set():
                    break
                intensity = int(self.breath_depth * (self.steps - step) / self.steps)
                dim_color = (intensity, int(.1*intensity), int(.1*intensity))
                start_index = (self.ring - 1) * NUM_PIXELS // 2
                for i in range(start_index, start_index + NUM_PIXELS // 2, 1):  # Use every other LED
                    pixels[i] = dim_color
                pixels.show()
                time.sleep(self.delay)

    def stop(self):
        self.stop_event.set()
        self.join()

# Start breathing light effect in a separate thread for each ring
breathing_effect = BreathingEffect(delay=0.01, steps=15, ring=1)
breathing_effect.start()

# Function to send OSC message with error handling
def send_osc_message(address, value):
    try:
        client.send_message(address, value)
    except Exception as e:
        print(f"Error sending OSC message to {address}: {e}")

# Main loop
while True:
    start_time = time.time()
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        tag_key = detect_tag(uid)
        if tag_key is not None:
            print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
            if tag_key == 1 or tag_key == 3:  # Blue tag 1
                print("sent tag ", tag_key)
                send_osc_message("/4/multitoggle/2/1", 1.0)  # increase intensity
            elif tag_key == 2 or tag_key == 4:  # Blue tag 2
                send_osc_message("/4/multitoggle/2/2", 1.0)  # decrease intensity
            elif tag_key == 6 or tag_key == 7:
                print("crickets")
                send_osc_message("/4/multitoggle/2/3", 1.0)  # crickets
            elif tag_key == 5:
                print("mario")
                send_osc_message("/4/multitoggle/2/7", 1.0)  # mario

            # Stop the breathing effect
            breathing_effect.stop()

            # Run other light effects
            shine_light_effect(ring=1)
            tag_read_light_effect(ring=1)
            move_light_effect(ring=1)
            fadeout_light_effect(ring=1)

            # Restart the breathing effect
            breathing_effect = BreathingEffect(delay=0.01, steps=15, ring=1)
            breathing_effect.start()
        else:
            print(f"Unknown tag detected with UID: {uid}")
            uid_hex = " ".join(format(x, '02x') for x in uid)
            print(f"Tag UID: {[hex(byte) for byte in uid]}".replace("'", ""))  # print(f"Tag UID: {uid_hex}")
            send_osc_message("/4/multitoggle/2/8", 1.0)  # error
            fadeout_light_effect(ring=1)
    end_time = time.time()
    print(f"Main loop duration: {end_time - start_time} seconds")
    time.sleep(0.1)
