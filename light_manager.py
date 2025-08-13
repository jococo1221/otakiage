# filepath: /home/pi/otakiage/light_manager.py 
import requests
import json

# Define the base URL for the API
base_url = "http://192.168.21.111/api/kAMWBACAinuX1ptJK42lDBlXwUyhBWpBBqPem1Fu"

# Function to modify the state of a light
def modify_light_state(light_id, state, color, brightness, transition_time):
    light_url = f"{base_url}/lights/{light_id}/state"
    light_data = {"on": state, "bri": brightness, "hue": color, "sat": 254, "transitiontime": transition_time}
    response = requests.put(light_url, data=json.dumps(light_data))
    print(response.text)

# Function to modify the state of a group of lights
def modify_group_state(group_id, state, color, brightness, transition_time):
    group_url = f"{base_url}/groups/{group_id}/action"
    group_data = {"on": state, "bri": brightness, "hue": color, "sat": 254, "transitiontime": transition_time}
    response = requests.put(group_url, data=json.dumps(group_data))
    print(response.text)

# Function to display all groups of lights
def display_groups():
    groups_url = f"{base_url}/groups"
    response = requests.get(groups_url)
    print(response.text)