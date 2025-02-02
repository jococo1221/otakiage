import requests
import json
import evdev
import time
import os

# Define the base URL for the API
base_url = "http://192.168.21.111/api/kAMWBACAinuX1ptJK42lDBlXwUyhBWpBBqPem1Fu"
light_transition_url = base_url + "/lights/12/state"

# Function to modify the state of a light
def modify_light_state(light_id, state, color, brightness, transition_time):
    light_url = f"{base_url}/lights/{light_id}/state"
    light_data = {"on": state, "bri": brightness, "hue": color, "sat": 254, "transitiontime": transition_time}
    response = requests.put(light_url, data=json.dumps(light_data))
    print(response.text)


def wait_for_button():

    # Add a 1 second pause
    time.sleep(1)

    device_path = "/dev/input/event3"  # Replace with the actual event device
    # check if the device exists and is readable using evdev
    is_bluetooth_controller_ready = os.access(device_path, os.R_OK) or os.access(device_path, os.W_OK)

    # Keep checking until the device is ready
    while not is_bluetooth_controller_ready:
        print(f"Error: Device {device_path} not found or not readable.")
        time.sleep(5)
        is_bluetooth_controller_ready = os.access(device_path, os.R_OK) or os.access(device_path, os.W_OK)
 
    try:
        device = evdev.InputDevice(device_path)
        print(f"Listening for input on {device_path}...")

        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                key_event = evdev.categorize(event)
                print(f"Key event detected: {key_event.keycode}, value: {event.value}")

                # Check if the key is BTN_WEST and pressed (value == 1)
                if ("BTN_WEST" in key_event.keycode or "KEY_MUTE" in key_event.keycode) and event.value == 1:
                    print("-----Clicker ppressed! Continuing script...")
                    #play sound
                    os.system("aplay /home/pi/otakiage/drop.wav")
                    break  # Exit the loop to continue script execution
                else:
                    print("-----No match - key_event.code= ", key_event.keycode, " and event.value= ", event.value)
    except FileNotFoundError:
        print(f"Error: Device {device_path} not found.")
    except Exception as e:
        print(f"Unexpected error: {e}")


# Main sequence
# Loop forever

while True:
    modify_light_state(12, True, 0, 254, 50)
    wait_for_button()  # Instead of time.sleep()

    modify_light_state(12, True, 30500, 254, 50)
    wait_for_button()

    modify_light_state(12, True, 8402, 254, 50)
    wait_for_button()

    modify_light_state(12, False, 0, 254, 10)
    wait_for_button()
