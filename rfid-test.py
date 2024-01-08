#!/usr/bin/env python
#template from: https://ozeki.hu/p_3023-how-to-setup-a-nfc-reader-on-raspberry-pi.html

import signal
import time
import sys

from pirc522 import RFID

run = True
#rdr = RFID(bus=0, device=0)  # Replace with the appropriate bus and device numbers

rdr = RFID()
util = rdr.util()
util.debug = True

class RFIDTag:
    def __init__(self, uid, message):
        self.uid = uid
        self.message = message

def detect_tag(uid):
    for key, rfid_tag in rfid_tags.items():
        if uid == rfid_tag.uid:
            return key, rfid_tag.message
    return None, f"Unknown tag detected with UID: [{', '.join([f'0x{hex(x)[2:].zfill(2)}' for x in uid])}]"


rfid_tags = {
    1: RFIDTag(uid=[0x09, 0x37, 0x1A, 0xE5, 0xC1], message="Blue tag 1"),
    2: RFIDTag(uid=[0xC9, 0x00, 0xFA, 0xB9, 0x8A], message="Blue tag 2"),
    3: RFIDTag(uid=[0x88, 0x04, 0xC3, 0x8A, 0xC5], message="Sticker 1"),
    4: RFIDTag(uid=[0x88, 0x04, 0xbb, 0x8a, 0xbd], message="Sticker 2"),
    5: RFIDTag(uid=[0x62, 0xbb, 0x09, 0x1a, 0xca], message="White card"),
}

def end_read(signal, frame):
    global run
    print("\nCtrl+C captured, ending read.")
    run = False
    rdr.cleanup()
    sys.exit()


signal.signal(signal.SIGINT, end_read)

print("Starting")
while run:
    (error, data) = rdr.request()
    if not error:
        print("\nDetected: " + format(data, "02x"))

    (error, uid) = rdr.anticoll()
    if not error:

        tag_found = False

        detected_uid=uid

        tag_key, tag_message = detect_tag(detected_uid)

        if tag_key is not None:
            print(f"Tag {tag_key} detected. {tag_message}")
            # Add the actions for tag detection here
        else:
            print(tag_message)       


print("Setting tag")
util.set_tag(uid)


print("\nAuthorizing")
# Try using authentication method A
util.auth(rdr.auth_a, [0x12, 0x34, 0x56, 0x78, 0x96, 0x92])
# Uncomment the line below if authentication method B is necessary
# util.auth(rdr.auth_b, [0x74, 0x00, 0x52, 0x35, 0x00, 0xFF])

print("\nReading")
# Adjust the block number based on your RFID card's structure
util.read_out(0)

print("\nDeauthorizing")
util.deauth()

time.sleep(1)