#!/usr/bin/env python
#template from: https://ozeki.hu/p_3023-how-to-setup-a-nfc-reader-on-raspberry-pi.html

import signal
import time
import sys
#sys.path.insert(0, '/usr/lib/python3/dist-packages/pirc522')

from pirc522 import RFID

run = True
#rdr = RFID(bus=0, device=0)  # Replace with the appropriate bus and device numbers

rdr = RFID()
util = rdr.util()
util.debug = True

tag1 = [0x09, 0x37, 0x1A, 0xE5, 0xC1]  # Replace with the UID of tag1 09,37,1a,e5,c1
tag2 = [0xC9, 0x00, 0xFA, 0xB9, 0x8A]  # Replace with the UID of tag2 c9,00,fa,b9,8a

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
        #print("Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," +
        #		str(uid[2]) + "," + str(uid[3]))

        uid_hex = [hex(x)[2:].zfill(2) for x in uid]
        print("Card read UID: " + ",".join(uid_hex))

        if uid == tag1:
            print("Tag 1 detected. Outputting Message1")
            # Add the actions for tag1 detection here
        elif uid == tag2:
            print("Tag 2 detected. Outputting Message2")
            # Add the actions for tag2 detection here
        else:
            print("Unknown tag detected")


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