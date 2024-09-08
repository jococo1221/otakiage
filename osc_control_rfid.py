import time
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from pythonosc import udp_client, osc_message_builder
import neopixel
import socket
import random

import pygame
pygame.mixer.init()

# Preset parameters
pulse_intensity = .5


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


# Define GPIO pin for the NeoPixel data line
PIXEL_PIN = board.D18  # Assuming data line is connected to GPIO 18

# Define the number of pixels (24 for your ring, 48 for two rings)
NUM_PIXELS = 48

# Initialize NeoPixel strip
pixels = neopixel.NeoPixel(PIXEL_PIN, NUM_PIXELS, brightness=0.5)

def play_sound(file_path, volume=1.0):
    sound = pygame.mixer.Sound(file_path)
    sound.set_volume(volume)
    sound.play()

def play_sound_in_thread(file_path, volume=1.0):
    threading.Thread(target=play_sound, args=(file_path, volume)).start()

# Define RFID tags
rfid_tags = {
    1: {"uid": [0x23, 0xa8, 0x18, 0xf7, 0x64], "message": "Blue tag 1"},
    2: {"uid": [0xC9, 0x00, 0xFA, 0xB9, 0x8A], "message": "Blue tag 2"},
    3: {"uid": [0x4, 0x79, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Fuego"},
    4: {"uid": [0x04, 0xbb, 0x8a, 0xea, 0xd1, 0x64, 0x80], "message": "Sticker 2"},
    5: {"uid": [0x04, 0x47, 0xc8, 0xd2, 0x56, 0x49, 0x81], "message": "It'sa me"},
    6: {"uid": [0x04, 0xe4, 0xa0, 0x65, 0x5f, 0x61, 0x80], "message": "."},
    7: {"uid": [0x04, 0x23, 0x83, 0x32, 0x4f, 0x61, 0x80], "message": "Darya"},
    8: {"uid": [0x4, 0x69, 0xcf, 0x35, 0x4f, 0x61, 0x80], "message": "Bird"},
    9: {"uid": [0x4, 0x9a, 0xd8, 0x65, 0x5f, 0x61, 0x80], "message": "Oracle"},
    10: {"uid": [0x4, 0x1e, 0xc2, 0x65, 0x5f, 0x61, 0x80], "message": "Oracle"},
    11: {"uid": [0x4, 0x49, 0xbe, 0x54, 0x6f, 0x61, 0x80], "message": "Oracle"},
    12: {"uid": [0x4, 0x94, 0xd8, 0x65, 0x5f, 0x61, 0x80], "message": "Oracle"},
    13: {"uid": [0x04, 0xd7, 0xab, 0x65, 0x5f, 0x61, 0x80], "message": "."},
    14: {"uid": [0x04, 0xa6, 0x31, 0x4f, 0x6f, 0x61, 0x80], "message": "."},
    15: {"uid": [0x04, 0xeb, 0xc3, 0x67, 0x5f, 0x61, 0x80], "message": "."},
    16: {"uid": [0x04, 0xa6, 0x8d, 0x32, 0x4f, 0x61, 0x80], "message": "."},
    17: {"uid": [0x04, 0xfd, 0x14, 0x54, 0x6f, 0x61, 0x80], "message": "."},
    18: {"uid": [0x04, 0x2b, 0x43, 0x66, 0x5f, 0x61, 0x80], "message": "."},
    19: {"uid": [0x04, 0xa4, 0xe9, 0x65, 0x5f, 0x61, 0x80], "message": "."},
    20: {"uid": [0x04, 0x87, 0x71, 0x4e, 0x6f, 0x61, 0x80], "message": "Agua"},
    21: {"uid": [0x04, 0xa1, 0x57, 0xc6, 0x79, 0x00, 0x00], "message": "Black clock 1"},
    22: {"uid": [0x04, 0xa0, 0x57, 0xc6, 0x79, 0x00, 0x00], "message": "Black clock 2"},  
    23: {"uid": [0x04, 0x9e, 0x57, 0xc6, 0x79, 0x00, 0x00], "message": "Small step"},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # : {"uid": , "message": ""},
    # 7: {"uid": [0x04, 0x20, 0xee, 0x1a, 0x5c, 0x15, 0x90], "message": "Ticket"},
    # : {"uid": [0xb3, 0xc2,  0x00, 0xfd, 0x8c], "message": "White card"},
    1000: {"uid": [0x04, 0x90, 0x57, 0xc6, 0x79, 0x00, 0x00], "message": "Dummy, without comma"}    
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
    max_brightness = pulse_intensity  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = dim_white
        pixels.show()
        time.sleep(delay)

def fadeout_light_effect(delay=0.02, steps=10, ring=1, color=(1, 1, 1)):
    max_brightness = 10  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2

    # Ensure the color values are normalized to 0-1 range
    r, g, b = color

    for step in range(steps + 1):
        intensity = (max_brightness * (steps - step) / steps)
        colored_intensity = (int(r * intensity), int(g * intensity), int(b * intensity))
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            pixels[i] = colored_intensity
        pixels.show()
        time.sleep(delay)

def le_set(color=(1, 1, 1)):
    ring=1
    max_brightness = 10  # Maximum brightness level
    intensity = max_brightness
    start_index = (ring - 1) * NUM_PIXELS // 2
    # Ensure the color values are normalized to 0-1 range
    r, g, b = color
    colored_intensity = (int(r * intensity), int(g * intensity), int(b * intensity))
    for i in range(start_index, start_index + NUM_PIXELS // 2):
        pixels[i] = colored_intensity
    pixels.show()


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



class PulseEffect(threading.Thread):
    global pulse_intensity

    def __init__(self, delay=0.02, steps=50, ring=1):
        super().__init__()
        bconversion_factor = 6  # Adjusted to handle more frequent updates
        self.bdelay = delay / bconversion_factor
        self.bsteps = steps * bconversion_factor

        cconversion_factor = 4
        self.cdelay = delay / cconversion_factor
        self.csteps = steps * cconversion_factor

        self.ring = ring
        self.breath_depth = 30 * pulse_intensity  # Maximum brightness level
        self.stop_event = threading.Event()
        self.daemon = True

        self.current_intensity = [0] * NUM_PIXELS
        self.gamma = 2.0

    def run(self):
        while not self.stop_event.is_set():
            if pulse_intensity < 0.01:
                self.coal_effect()
            else:
                self.breathing_effect()

    def breathing_effect(self):
        """This function implements the standard breathing effect with weighted LED updates and gamma correction."""
        start_index = (self.ring - 1) * NUM_PIXELS // 2
        leds_to_update = NUM_PIXELS // 2  # Total number of LEDs in the ring

        cycle_duration = 2.0  # Duration for a full brighten and dim cycle (seconds)
        step_duration = cycle_duration / (2 * self.bsteps)  # Duration per step

        # Brighten
        start_time = time.time()
        for step in range(self.bsteps + 1):
            if self.stop_event.is_set():
                break
            target_intensity = int(self.breath_depth * step / self.bsteps)
            target_color = self.apply_gamma_correction(target_intensity)

            self.update_leds_weighted(target_intensity, target_color, start_index, leds_to_update)

            # Wait for the next step
            elapsed_time = time.time() - start_time
            sleep_time = step_duration - elapsed_time % step_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Dim
        start_time = time.time()
        for step in range(self.bsteps + 1):
            if self.stop_event.is_set():
                break
            target_intensity = int(self.breath_depth * (self.bsteps - step) / self.bsteps)
            target_color = self.apply_gamma_correction(target_intensity)

            self.update_leds_weighted(target_intensity, target_color, start_index, leds_to_update)

            # Wait for the next step
            elapsed_time = time.time() - start_time
            sleep_time = step_duration - elapsed_time % step_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

    def apply_gamma_correction(self, intensity):
        """Applies gamma correction to smooth the transition for small values."""
        adjusted_intensity = int((intensity / self.breath_depth) ** self.gamma * self.breath_depth)
        return self.cap_color_values(adjusted_intensity)

    def cap_color_values(self, value):
        """Cap the color values to 255."""
        capped_value = min(max(0, value), 255)
        return (capped_value, int(0.1 * capped_value), int(0.1 * capped_value))

    def update_leds_weighted(self, target_intensity, target_color, start_index, leds_to_update):
        """Update LEDs based on weighted probabilities where dimmer LEDs are more likely to be updated."""
        gaps = []
        for i in range(start_index, start_index + leds_to_update):
            gap = abs(target_intensity - self.current_intensity[i])
            gaps.append(gap)

        total_gap = sum(gaps)

        if total_gap > 0:
            probabilities = [gap / total_gap for gap in gaps]

            num_leds_to_update = random.randint(6, leds_to_update) if target_intensity < 5 else random.randint(3, 6)

            selected_leds = random.choices(range(len(gaps)), probabilities, k=num_leds_to_update)

            for led_index in selected_leds:
                pixel_index = start_index + led_index
                pixels[pixel_index] = target_color
                self.current_intensity[pixel_index] = target_intensity

            pixels.show()

    def coal_effect(self):
        """This function implements the 'cross' effect for pulse_intensity < 0.4."""
        
        start_index = (self.ring - 1) * NUM_PIXELS // 2
        cross_leds = [0, NUM_PIXELS // 8, NUM_PIXELS // 4, 3 * NUM_PIXELS // 8]  # 4 evenly spaced LEDs

        cycle_duration = 2.0  # Duration for a full brighten and dim cycle (seconds)
        step_duration = cycle_duration / (2 * self.csteps)  # Duration per step

        # Brighten
        start_time = time.time()
        for step in range(self.csteps + 1):
            if self.stop_event.is_set():
                break
            intensity = int(self.breath_depth * step / self.csteps)
            dim_color = self.cap_color_values(intensity)

            for i in cross_leds:
                pixels[start_index + i] = dim_color
            pixels.show()

            # Wait for the next step
            elapsed_time = time.time() - start_time
            sleep_time = step_duration - elapsed_time % step_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Dim
        start_time = time.time()
        for step in range(self.csteps + 1):
            if self.stop_event.is_set():
                break
            intensity = int(self.breath_depth * (self.csteps - step) / self.csteps)
            dim_color = self.cap_color_values(intensity)

            for i in cross_leds:
                pixels[start_index + i] = dim_color
            pixels.show()

            # Wait for the next step
            elapsed_time = time.time() - start_time
            sleep_time = step_duration - elapsed_time % step_duration
            if sleep_time > 0:
                time.sleep(sleep_time)

    def stop(self):
        self.stop_event.set()
        self.join()

#f_ FEEDBACK

def f_ack():
    play_sound_in_thread("/home/pi/otakiage/drop.wav", 0.7)

def f_error():
    play_sound_in_thread("/home/pi/otakiage/drop.wav", 0.7)
    time.sleep(0.2)
    play_sound_in_thread("/home/pi/otakiage/drop.wav", 0.7)

def f_silent_error():
    fadeout_light_effect(color=(.2,.2,1))


#a_ ACTIONS

def a_pulse_intensity(p_factor):    
    global pulse_intensity
    max_pi=50
    min_pi=.1
    if(pulse_intensity<min_pi):
        #deal with zero value
        pulse_intensity=min_pi*p_factor
    
    if(pulse_intensity*p_factor>min_pi and pulse_intensity*p_factor<max_pi):
        #normal
        pulse_intensity = (pulse_intensity)*p_factor
        f_ack()
    elif(pulse_intensity*p_factor>=max_pi):
        #top cap
        pulse_intensity = max_pi
        f_error()
    elif(pulse_intensity*p_factor<=min_pi):
        #lower cap
        pulse_intensity = 0
        f_error()
    else:
        f_error()
    
    print("pulse intensity x ", p_factor," = ", pulse_intensity)    


#MAIN PROGRAM

#set blue color while trying to connect
le_set(color=(0,0,.5))

for attempt in range(max_retries):
    try:
        client = udp_client.SimpleUDPClient(args["ip"], args["port"])
        # Test connection
        client.send_message("/test", 1.0)
        print(f"Connected to OSC server on {args['ip']}:{args['port']}")

        #Connected - set black color
        le_set(color=(0,0,0))

        break
    except (socket.gaierror, ConnectionRefusedError):
        print(f"Failed to connect to OSC server. Retrying in {retry_delay} seconds...")
        f_silent_error()
        le_set(color=(0,0,.5))
        time.sleep(retry_delay)
else:
    print("Could not connect to OSC server. Continuing without OSC server.")


# Start breathing light effect in a separate thread for each ring
breathing_effect = PulseEffect(delay=0.01, steps=15, ring=1)
breathing_effect.start()

# Function to send OSC message with error handling
def send_osc_message(address, value):
    try:
        client.send_message(address, value)
    except Exception as e:
        print(f"Error sending OSC message to {address}: {e}")
        f_silent_error()

# Main loop

previous_tag=0 #initialize
while True:
    start_time = time.time()
    uid = pn532.read_passive_target(timeout=0.5)
    if uid is not None:
        tag_key = detect_tag(uid)
        if tag_key is not None:
            print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
            if tag_key == 1 or tag_key == 3:  # Fuego
                print("sent tag ", tag_key)
                send_osc_message("/4/multitoggle/2/1", 1.0)  # increase intensity
                play_sound_in_thread("/home/pi/otakiage/fire_up_fd.wav", 0.9)
            elif tag_key == 2 or tag_key == 4 or tag_key == 20 :  # Agua
                play_sound_in_thread("/home/pi/otakiage/fire_down_fd.wav", 0.7)
                send_osc_message("/4/multitoggle/2/2", 1.0)  # decrease intensity
            elif tag_key == 21:  # Clock 1
                a_pulse_intensity(1/2)
            elif tag_key == 22:  # Clock 2
                a_pulse_intensity(2)
            elif tag_key == 23:  #
                a_pulse_intensity(.9)
            elif tag_key == 6 :
                print("Darya")
                send_osc_message("/4/multitoggle/3/3", 1.0)
            elif tag_key == 7:
                print("Darya")
                send_osc_message("/4/multitoggle/3/3", 1.0)
            elif tag_key == 5:
                print("mario")
                send_osc_message("/4/multitoggle/2/7", 1.0)  # mario
            elif tag_key == 8:
                print("birds")
                send_osc_message("/4/multitoggle/3/2", 1.0)
            elif tag_key in {9, 10, 11, 12,13, 14, 15, 16, 17, 18, 19}:
                if tag_key==previous_tag:
                    print("repeated oraculo")
                    send_osc_message("/4/multitoggle/2/8", 1.0)  # error
                else:
                    print("oraculo")
                    send_osc_message("/4/multitoggle/3/1", 1.0) #play random message
            else:
                print("unassigned tag:", tag_key)
                send_osc_message("/4/multitoggle/2/8", 1.0)  # error
            previous_tag=tag_key


            # Stop the breathing effect
            breathing_effect.stop()

            # Run other light effects
            shine_light_effect(ring=1)
            tag_read_light_effect(ring=1)
            move_light_effect(ring=1)
            fadeout_light_effect(ring=1)

            # Restart the breathing effect
            breathing_effect = PulseEffect(delay=0.01, steps=15, ring=1)
            breathing_effect.start()
        else:
            uid_hex = " ".join(format(x, '02x') for x in uid)
            #print(f"Tag UID: {[hex(byte) for byte in uid]}".replace("'", ""))  # print(f"Tag UID: {uid_hex}")
            uid_hex = ", ".join(f"0x{byte:02x}" for byte in uid)
            print(f': {{"uid": [{uid_hex}], "message": "."}},')
            send_osc_message("/4/multitoggle/2/8", 1.0)  # error
            fadeout_light_effect(ring=1)
    end_time = time.time()
    #print(f"Main loop duration: {end_time - start_time} seconds")
    time.sleep(0.1)
