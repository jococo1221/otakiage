# This file tests basic functionality of the Hue Lights API
# User is kAMWBACAinuX1ptJK42lDBlXwUyhBWpBBqPem1Fu
# IP address is 192.168.21.111

# Import the necessary libraries
import requests
import json
import time


# Define the base URL for the API
base_url = "http://192.168.21.111/api/kAMWBACAinuX1ptJK42lDBlXwUyhBWpBBqPem1Fu"

# Define the URL for the lights
lights_url = base_url + "/lights"

# Define the URL for the groups
groups_url = base_url + "/groups"

# Define the URL for the scenes
scenes_url = base_url + "/scenes"

light_transition_url = base_url + "/lights/12/state"

# function to modify the state of a light
def modify_light_state(light_id, state, color, brightness, transition_time):
    light_url = base_url + "/lights/" + str(light_id) + "/state"
    light_data = {"on": state, "bri": brightness, "hue": color, "sat": 254, "transitiontime": transition_time}
    response = requests.put(light_url, data=json.dumps(light_data))
    print(response.text)



modify_light_state(12, True, 0, 254, 50)
time.sleep(5)
#transition to emerald green
modify_light_state(12, True, 30500, 254, 50)
time.sleep(5)
modify_light_state(12, True, 8402, 254, 50)
time.sleep(5)
modify_light_state(12, False, 0, 254, 10)

