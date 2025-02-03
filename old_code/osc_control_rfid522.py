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
args = {"ip": "shine.local", "port": 5005}
client = udp_client.SimpleUDPClient(args["ip"], args["port"])

# Define RFID tags
rfid_tags = {
    1: {"uid": [0x23, 0xa8, 0x18, 0xf7, 0x64], "message": "Blue tag 1"},
    2: {"uid": [0xC9, 0x00, 0xFA, 0xB9, 0x8A], "message": "Blue tag 2"},
    3: {"uid": [0x88, 0x04, 0xC3, 0x8A, 0xC5], "message": "Sticker 1"},
    4: {"uid": [0x88, 0x04, 0xbb, 0x8a, 0xbd], "message": "Sticker 2"},
    5: {"uid": [0x88, 0x04, 0x47, 0xc8, 0x03], "message": "It'sa me"},
    6: {"uid": [0xb3, 0xc2, 0x00, 0xfd, 0x8c], "message": "White card"},
    7: {"uid": [136, 4, 32, 238, 66], "message": "Ticket"},
}

# Function to detect RFID tag
def detect_tag(uid):
    for tag_key, tag_data in rfid_tags.items():
        if uid == tag_data["uid"]:
            return tag_key
    return None

# Main loop
while True:
    (error, data) = rdr.request()
    (error, uid) = rdr.anticoll()
    if not error:
        tag_key = detect_tag(uid)
        if tag_key is not None:
            print(f"Tag {tag_key} detected. {rfid_tags[tag_key]['message']}")
            if tag_key == 1 or tag_key == 3:  # Blue tag 1
                print("sent tag ", tag_key)
                client.send_message("/4/multitoggle/2/1", 1.0) #increase intensity
            elif tag_key == 2 or tag_key == 4:  # Blue tag 2
                client.send_message("/4/multitoggle/2/2", 1.0) #decrease intensity 
            elif tag_key == 6 or tag_key == 7:
                print("crickets")
                client.send_message("/4/multitoggle/2/3", 1.0) #crickets
            elif tag_key == 5:
                print("mario")
                client.send_message("/4/multitoggle/2/7", 1.0) #mario
        else:
            print(f"Unknown tag detected with UID: {uid}")
    time.sleep(0.1)
