import time
import threading
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from pythonosc import udp_client, osc_message_builder
import neopixel
from rpi_ws281x import PixelStrip, Color
import socket
import subprocess
import random
import os
import sys

#Get RFID tag data
DB_PATH = os.path.join(os.path.dirname(__file__), "rfid_tags.db")
from tag_store import TagStore
store = TagStore(DB_PATH)

admin_active = threading.Event()

import pygame

#external osc_safe.py
from osc_safe import OSCSafeClient
osc = OSCSafeClient(host="shine.local", port=5006, refresh_sec=0)  # set to IP for max reliability
osc.start()

# Initialize global variables
previous_tag_key = 0

debounce=0.1 # default debounce

# Preset parameters
pulse_intensity = .5


# Initialize I2C bus and PN532
i2c = busio.I2C(board.SCL, board.SDA)
# i2c = busio.I2C(scl=board.D24, sda=board.D23)  # Update `GP23` and `GP24` to match your pin definitions
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with RFID tags
pn532.SAM_configuration()

# Define OSC client with retry mechanism
args = {"ip": "shine.local", "port": 5006}
max_retries = 5
retry_delay = 5
client = None


# LED configuration for SPI-based NeoPixel control
LED_COUNT = 48           # Number of LED pixels (24 per ring, 2 rings)
LED_PIN = 10             # GPIO pin for SPI MOSI (must be GPIO 10 for SPI)
LED_FREQ_HZ = 800000     # LED signal frequency in hertz (800kHz typical)
LED_DMA = 10             # DMA channel to use for generating signal
LED_BRIGHTNESS = 128     # Brightness of LEDs (0-255)
LED_CHANNEL = 0          # Channel not used for SPI
NUM_PIXELS = 48

# Initialize NeoPixel strip using SPI
pixels = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, False, LED_BRIGHTNESS, LED_CHANNEL)
pixels.begin()  # Initialize the strip

# Helper function to set a pixel color
def set_pixel(index, color):
    r, g, b = color
    pixels.setPixelColor(index, Color(int(r), int(g), int(b)))

def show_pixels():
    pixels.show()

def play_sound(file_path, volume=1.0):
    # Check if pygame.mixer is initialized
    if not pygame.mixer.get_init():
        # subprocess.run(["bluetoothctl"], input="power on\nconnect 00:1B:B8:AE:05:4F\nexit\n", text=True)
        print("Trying to initialize pygame.mixer ...")
        # Check if PulseAudio is ready
        if os.path.exists("/run/user/1000/pulse/native"):
            try:
                pygame.mixer.init()
                print("pygame.mixer initialized.")
            except Exception as e:
                print(f"Failed to initialize pygame.mixer: {e}")
                return
        else:
            print("PulseAudio is not ready. Skipping sound.")
            return
    
    # Play the sound
    try:
        sound = pygame.mixer.Sound(file_path)
        sound.set_volume(volume)
        sound.play()
    except Exception as e:
        print(f"Failed to play sound: {e}")


def play_sound_in_thread(file_path, volume=1.0):
    threading.Thread(target=play_sound, args=(file_path, volume)).start()
  


# Function to detect RFID tag
def detect_tag(uid):
    row = store.get_by_uid(uid)
    if row:
        tag_key, _message, _function = row
        return tag_key
    return 999


# LED animation functions
def shine_light_effect(delay=0.01, steps=5, ring=1):
    max_brightness = 220  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            #pixels[i] = dim_white
            set_pixel(i, dim_white)
        show_pixels()
        time.sleep(delay)
    steps = 2
    for step in range(steps + 1):
        intensity = int(max_brightness * (steps - step) / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            #pixels[i] = dim_white
            set_pixel(i, dim_white)
        show_pixels()
        time.sleep(delay)

def fadein_light_effect(delay=0.02, steps=10, ring=1):
    max_brightness = pulse_intensity  # Maximum brightness level
    start_index = (ring - 1) * NUM_PIXELS // 2
    for step in range(steps + 1):
        intensity = int(max_brightness * step / steps)
        dim_white = (intensity, intensity, intensity)
        for i in range(start_index, start_index + NUM_PIXELS // 2):
            #pixels[i] = dim_white
            set_pixel(i, dim_white)
        show_pixels()
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
            #pixels[i] = colored_intensity
            set_pixel(i, colored_intensity)
        show_pixels()
        time.sleep(delay/2)

def le_set(color=(1, 1, 1)):
    ring=1
    max_brightness = 10  # Maximum brightness level
    intensity = max_brightness
    start_index = (ring - 1) * NUM_PIXELS // 2
    # Ensure the color values are normalized to 0-1 range
    r, g, b = color
    colored_intensity = (int(r * intensity), int(g * intensity), int(b * intensity))
    for i in range(start_index, start_index + NUM_PIXELS // 2):
        #pixels[i] = colored_intensity
        set_pixel(i, colored_intensity)
    show_pixels()


def move_light_effect(delay=0.02, ring=1):
    white = (127, 127, 127)  # Warm white color at 50% intensity
    dim_white = (10, 10, 10)  # Warm white color at 50% intensity

    # Turn off all pixels in the ring
    start_index = (ring - 1) * NUM_PIXELS // 2
    for i in range(start_index, start_index + NUM_PIXELS // 2):
        #pixels[i] = dim_white
        set_pixel(i, dim_white)     
    show_pixels()

    # Sequence to light up two LEDs radially opposite each other
    for i in range(NUM_PIXELS // 4):
        opposite_index = i + NUM_PIXELS // 4

        set_pixel(start_index + i, white)
        set_pixel(start_index + opposite_index, white)

        show_pixels()
        time.sleep(delay)

        set_pixel(start_index + i, dim_white)
        set_pixel(start_index + opposite_index, dim_white)

    # Ensure all LEDs are off before exiting the function
    show_pixels()

def tag_read_light_effect(ring=1):
    move_light_effect(ring=ring)



class PulseEffect(threading.Thread):
    global pulse_intensity

    def __init__(self, steps=50, ring=1):
        super().__init__()
        self.steps = steps * 6  # Adjusted for breathing effect
        self.ring = ring
        self.breath_depth = 30 * pulse_intensity  # Maximum brightness level
        self.stop_event = threading.Event()
        self.daemon = True

        self.current_intensity = [0] * NUM_PIXELS
        self.gamma = 2.0

    def run(self):
        """Main thread loop, runs the breathing effect."""
        while not self.stop_event.is_set():
            self.breathing_effect()

    def breathing_effect(self):
        """Implements a smooth breathing effect with gamma correction."""
        start_index = (self.ring - 1) * NUM_PIXELS // 2
        leds_to_update = NUM_PIXELS // 2  # Total number of LEDs in the ring

        cycle_duration = 2.0  # Duration for full brighten and dim cycle (seconds)
        step_duration = cycle_duration / (2 * self.steps)

        # Brighten
        for step in range(self.steps + 1):
            if self.stop_event.is_set():
                break
            target_intensity = int(self.breath_depth * step / self.steps)
            target_color = self.apply_gamma_correction(target_intensity)
            self.update_leds_weighted(target_intensity, target_color, start_index, leds_to_update)
            time.sleep(step_duration)

        # Dim
        for step in range(self.steps + 1):
            if self.stop_event.is_set():
                break
            target_intensity = int(self.breath_depth * (self.steps - step) / self.steps)
            target_color = self.apply_gamma_correction(target_intensity)
            self.update_leds_weighted(target_intensity, target_color, start_index, leds_to_update)
            time.sleep(step_duration)

    def apply_gamma_correction(self, intensity):
        """Applies gamma correction to smooth transitions."""
        adjusted_intensity = int((intensity / self.breath_depth) ** self.gamma * self.breath_depth)
        return self.cap_color_values(adjusted_intensity)

    def cap_color_values(self, value):
        """Cap color values to the range [0, 255]."""
        capped_value = min(max(0, value), 255)
        return (capped_value, int(0.1 * capped_value), int(0.1 * capped_value))

    def update_leds_weighted(self, target_intensity, target_color, start_index, leds_to_update):
        """Update LEDs based on the intensity differences."""
        gaps = [abs(target_intensity - self.current_intensity[i]) for i in range(start_index, start_index + leds_to_update)]
        total_gap = sum(gaps)

        if total_gap > 0:
            probabilities = [gap / total_gap for gap in gaps]
            num_leds_to_update = random.randint(6, leds_to_update) if target_intensity < 5 else random.randint(3, 6)
            selected_leds = random.choices(range(len(gaps)), probabilities, k=num_leds_to_update)

            for led_index in selected_leds:
                pixel_index = start_index + led_index
                set_pixel(pixel_index, target_color)
                self.current_intensity[pixel_index] = target_intensity

            show_pixels()

    def stop(self):
        """Stops the thread."""
        self.stop_event.set()
        self.join()


#f_ FEEDBACK

def f_ack():
    play_sound_in_thread("/home/pi/otakiage/drop.wav", 0.7)

def f_ack_av():
    play_sound_in_thread("/home/pi/otakiage/drop.wav", 0.7)
    fadeout_light_effect(color=(.5,.5,.5))


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
breathing_effect = PulseEffect(steps=15, ring=1)
breathing_effect.start()

# Add this flag at the top of your script (after breathing_effect is created)
breathing_effect_running = True

# Function to send OSC message with error handling
def send_osc_message(address, value):

    ok = osc.send(address, value)
    if not ok:
        f_silent_error()

    # # Previous approach
    # try:
    #     client.send_message(address, value)
    # except Exception as e:
    #     print(f"Error sending OSC message to {address}: {e}")
    #     f_silent_error()


def copy_tag_workflow():
    admin_active.set()
    try:
        # ▼ STOP BREATHING WHILE IN ADMIN
        global breathing_effect_running, breathing_effect
        if breathing_effect_running:
            try:
                breathing_effect.stop()
            except Exception as e:
                print("[Breathing] stop error:", e)
            breathing_effect_running = False
        # ▲

        f_ack_av()
        print(".....")
        time.sleep(3.0)  # debounce

        le_set(color=(0,0,.2))  # dim blue - admin indicator
        print("\n[CopyTag] Scan OLD tag within 15s...")
        old = pn532.read_passive_target(timeout=15.0)
        if not old:
            print("[CopyTag] Timeout waiting for OLD tag.")
            f_error(); return
        if not store.get_by_uid(old):
            print("[CopyTag] OLD tag not in DB.")
            f_error(); return

        f_ack_av()
        print(".")
        time.sleep(1.0)  # debounce

        
        print("[CopyTag] Now scan NEW tag within 15s...")
        le_set(color=(.2,.2,0))  # dim yellow - ready to copy indicator
        new = pn532.read_passive_target(timeout=15.0)
        if not new:
            print("[CopyTag] Timeout waiting for NEW tag.")
            f_error(); return
        if store.get_by_uid(new):
            print("[CopyTag] NEW tag already exists; abort.")
            f_error(); return

        old_key, new_key = store.copy_tag(old, new) or (None, None)
        if old_key is not None:
            print(f"[CopyTag] Copied {old_key} → {new_key}")
            le_set(color=(0,.2,0))  # dim green - success indicator
            f_ack()
            time.sleep(1.0)  # debounce
        else:
            print("[CopyTag] OLD tag lookup failed.")
            f_error()
    finally:
        # ▼ RESTART BREATHING AFTER ADMIN
        if not breathing_effect_running:
            breathing_effect = PulseEffect(steps=15, ring=1)
            breathing_effect.start()
            breathing_effect_running = True
        # ▲
        admin_active.clear()

def delete_tag_workflow():
    admin_active.set()
    try:
        global breathing_effect_running, breathing_effect
        if breathing_effect_running:
            try:
                breathing_effect.stop()
            except Exception as e:
                print("[Breathing] stop error:", e)
            breathing_effect_running = False

        # ack + debounce
        f_ack_av()
        print(".....")
        time.sleep(3.0)


        le_set(color=(0,0,.2))  # dim blue - admin indicator
        print("\n[DeleteTag] Scan tag within 15s...")
        uid = pn532.read_passive_target(timeout=15.0)
        if not uid:
            print("[DeleteTag] Timeout."); f_error(); return

        row = store.get_by_uid(uid)
        if not row:
            print("[DeleteTag] Not found."); f_error(); return

        tag_key, message, function = row
        print(f"[DeleteTag] Found tag_key={tag_key} ({function}) {message!r}")
        le_set(color=(0,.2,0))  # dim green - success indicator
        f_ack(); time.sleep(1.0)

        removed = store.delete_by_uid(uid)
        print("[DeleteTag] Deleted." if removed else "[DeleteTag] Nothing removed.")
        f_ack() if removed else f_error()
    finally:
        if not breathing_effect_running:
            breathing_effect = PulseEffect(steps=15, ring=1)
            breathing_effect.start()
            breathing_effect_running = True
        admin_active.clear()


def admin_keyboard():
    print("[Admin] Type 'c' then Enter to copy tag; 'd' to delete tag; 'r' to reload.")
    while True:
        try:
            line = input()
        except EOFError:
            time.sleep(0.2)
            continue
        if not line:
            continue
        s = line.strip().lower()

        # tolerate repeated letters like "cc", "dd"
        if "c" in s and set(s) <= {"c"}:
            print("[Admin] Copy mode…")
            copy_tag_workflow()
            continue
        if "d" in s and set(s) <= {"d"}:
            print("[Admin] Delete mode…")
            delete_tag_workflow()
            continue
        if s and s[0] == "r":
            print("[Admin] Reload not implemented; DB writes are live.")
            continue

        print(f"[Admin] Unknown command: {s!r}")



threading.Thread(target=admin_keyboard, daemon=True).start()

# Main loop
while True:

    if admin_active.is_set():
        time.sleep(0.05)
        continue

    tag_key = None
    start_time = time.time()
    uid = None
    uid = pn532.read_passive_target(timeout=0.5)
    # default color is white
    light_color = (0.5, 0.5, 0.5)
    if uid is not None:
        tag_key = detect_tag(uid)
        print(".", end="", flush=True)

        if previous_tag_key != tag_key:  # new tag detected, for tags that are "one time use" (not cumulative)
            dbrow = store.get_by_key(tag_key) if tag_key != 999 else None
            tag_message = dbrow[2] if dbrow else "Unknown tag"   # message
            tag_function = dbrow[3] if dbrow else "none"         # function

            print(f"Tag {tag_key} detected. {tag_message}. Previous tag: {previous_tag_key}")


            if tag_function == "increase_intensity":
                print("sent tag ", tag_key)
                send_osc_message("/4/multitoggle/2/1", 1.0)
                play_sound_in_thread("/home/pi/otakiage/fire_up_fd.wav", 0.9)
            elif tag_function == "decrease_intensity":
                play_sound_in_thread("/home/pi/otakiage/fire_down_fd2.wav", 0.6)
                send_osc_message("/4/multitoggle/2/2", 1.0)
            elif tag_function == "clock_half":
                a_pulse_intensity(1/2)
            elif tag_function == "clock_double":
                a_pulse_intensity(2)
            elif tag_function == "clock_point9":
                a_pulse_intensity(.9)
            elif tag_function == "darya":
                print("Darya")
                send_osc_message("/4/multitoggle/3/3", 1.0)
            elif tag_function == "mario":
                print("mario")
                send_osc_message("/4/multitoggle/2/7", 1.0)
            elif tag_function == "birds":
                print("birds")
                send_osc_message("/4/multitoggle/3/2", 1.0)
            elif tag_function == "restart_light":
                print("restart light")
                send_osc_message("/4/multitoggle/4/3", 1.0)
            elif tag_function == "prev_light":
                print("prev light")
                send_osc_message("/4/multitoggle/4/1", 1.0)
            elif tag_function == "next_light":
                print("next light")
                send_osc_message("/4/multitoggle/4/2", 1.0)
            elif tag_function == "wish":
                print("wish")
                send_osc_message("/4/multitoggle/5/1", 1.0)
            elif tag_function == "push1" and previous_tag_key != 31:
                send_osc_message("/2/push1", 1.0)
                play_sound_in_thread("/home/pi/otakiage/audio/fireworks5.wav", 0.5)
            elif tag_function == "push2" and previous_tag_key != 32:
                send_osc_message("/2/push2", 1.0)
                play_sound_in_thread("/home/pi/otakiage/audio/fireworks5.wav", 0.5)
            elif tag_function == "push3" and previous_tag_key != 33:
                send_osc_message("/2/push3", 1.0)
                play_sound_in_thread("/home/pi/otakiage/audio/fireworks5.wav", 0.5)
            elif tag_function == "push4" and previous_tag_key != 34:
                send_osc_message("/2/push4", 1.0)
                play_sound_in_thread("/home/pi/otakiage/audio/fireworks5.wav", 0.5)
            elif tag_function == "push16" and previous_tag_key != 35:
                print("Light - dummy moment")
                send_osc_message("/effects/fireworks", 1.0)
                ##send_osc_message("/2/push16", 1.0) #for now different than push
                ##play_sound_in_thread("/home/pi/otakiage/audio/fireworks5.wav", 0.5)
            elif tag_function == "oraculo":
                if tag_key == previous_tag_key:
                    print("repeated oraculo")
                    send_osc_message("/4/multitoggle/2/8", 1.0)
                else:
                    print("oraculo")
                    send_osc_message("/4/multitoggle/3/1", 1.0)
            elif tag_function == "copy_tag":
                print("copy tag command triggered")
                copy_tag_workflow()
            elif tag_function == "delete_tag":
                print("delete tag command triggered")
                delete_tag_workflow()
            elif tag_key == 999: # unknown tag
                light_color = (0, .5, .5)  # color is teal
                uid_hex = " ".join(format(x, '02x') for x in uid)
                print("unassigned tag UID:", uid_hex)
                # output in this format :     30: {"uid": [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], "message": "AVAILABLE"},
                uid_hex = " ".join(format(x, '02x') for x in uid)
                print(f"    {tag_key}: {{\"uid\": [{uid_hex}], \"message\": \"AVAILABLE\"}}")
            else: # known but unmanaged tag (not assigned in this loop)
                light_color = (0.5,0.3,0.0) #color is orange
                #known but unmanaged tag
                print("Known tag:", tag_key, "hex:", tag_key)

            # Stop the breathing effect
            if breathing_effect_running:
                breathing_effect.stop()
                breathing_effect_running = False

            # Run other light effects
            shine_light_effect(ring=1)
            tag_read_light_effect(ring=1)
            move_light_effect(ring=1)
            le_set(color=light_color)  #light color when a tag is held



    elif uid is None and previous_tag_key != tag_key: # tag removed
            print("]")
            fadeout_light_effect(ring=1)
            # Restart the breathing effect if not running
            if not breathing_effect_running:
                breathing_effect = PulseEffect(steps=15, ring=1)
                breathing_effect.start()
                breathing_effect_running = True
        

    previous_tag_key=tag_key

    end_time = time.time()
    #print(f"Main loop duration: {end_time - start_time} seconds")
    time.sleep(debounce)
