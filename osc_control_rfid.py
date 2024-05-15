import time
import RPi.GPIO as GPIO
from pythonosc import udp_client
from pirc522 import RFID

# Initialize GPIO
GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

# Define RFID reader
rdr = RFID()
util = rdr.util()
util.debug = True

# Define OSC client
args = {"ip": "192.168.2.23", "port": 5005}
client = udp_client.SimpleUDPClient(args["ip"], args["port"])

# Define RFID tags
rfid_tags = {
    1: {"uid": [0x23, 0xa8, 0x18, 0xf7, 0x64], "message": "Blue tag 1"},
    2: {"uid": [0xC9, 0x00, 0xFA, 0xB9, 0x8A], "message": "Blue tag 2"},
    3: {"uid": [0x88, 0x04, 0xC3, 0x8A, 0xC5], "message": "Sticker 1"},
    4: {"uid": [0x88, 0x04, 0xbb, 0x8a, 0xbd], "message": "Sticker 2"},
    5: {"uid": [0x88, 0x04, 0x47, 0xc8, 0x03], "message": "It'sa me"},
    6: {"uid": [0xb3, 0xc2, 0x00, 0xfd, 0x8c], "message": "White card"},
}

# Function to detect RFID tag
def detect_tag(uid):
    for tag_key, tag_data in rfid_tags.items():
        if uid == tag_data["uid"]:
            return tag_key
    return None

# Main loop
intensidad = 0.3
x = 100
while True:
    intensidad = round(intensidad, 1)
    (error, data) = rdr.request()
    #if not error:
        #print("no error")        
    (error, uid) = rdr.anticoll()
    if not error:
        tag_key = detect_tag(uid)
        print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
        
        if tag_key is not None:
            if (tag_key == 1 or tag_key == 3) :  # Blue tag 1, increase intensity
                if (intensidad + 0.1) <= 1:
                    intensidad += 0.1
                value = intensidad
                client.send_message("/1/fader5", value)
            elif (tag_key == 2 or tag_key == 4):  # Blue tag 2, decrease intensity
                if (intensidad - 0.1) >= 0 and (intensidad - 0.1) <= 1:
                    intensidad -= 0.1
                value = intensidad
                client.send_message("/1/fader5", value)
        print(intensidad)
        x += 1
        time.sleep(0.1)
