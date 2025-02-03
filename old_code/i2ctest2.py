
max_value=120
min_value=0
variability_range=28 #/100
stability=3
flare_range=5 #/10
flare_frequency=10 #/10
initial_intensity=max_value-10
interval=1/1 #seconds

ip1=initial_intensity
ip2=initial_intensity
ip3=initial_intensity
ip4=initial_intensity

i0=max_value
#i0=int(i0h)
i1=min_value

import smbus
import time
import random


# Get I2C bus
bus = smbus.SMBus(1)

#print(random.randrange(1, 10))

def define_intensity(intensity_input):
    intensity=intensity_input
    return intensity

  
while True: # i < 10000:
    # device address 0x27
    # select channel 0x80 1st channel, 0x81 2nd channel ... 0x83 4th channel
    # dimming level - 0 fully open, 100 fully closed (71 decimal)
    
#     ip1=define_intensity(ip1)
#     bus.write_byte_data(0x27, 0x80, int(max_value-ip1))
#
#     ip2=define_intensity(ip2)
#     bus.write_byte_data(0x27, 0x81, int(max_value-ip2))
#
#     ip3=define_intensity(ip3)
#     bus.write_byte_data(0x27, 0x82, int(max_value-ip3))
#
#     ip4=define_intensity(ip4)
#     bus.write_byte_data(0x27, 0x83, int(max_value-ip4))
#
#     time.sleep (interval)
#     i += 1
#     print("intensity=",(ip1)," max value=",max_value)
#     print("value written to bus=",int(max_value-ip1))
#     print("i=",i)
#
#
# bus.write_byte_data(0x27, 0x80, 0x00)
# time.sleep (.3)
# bus.write_byte_data(0x27, 0x80, i0)
# time.sleep (.3)
# bus.write_byte_data(0x27, 0x80, 0x00)
# time.sleep (.3)
# bus.write_byte_data(0x27, 0x80, i0)

    i=i0
    while i > i1:
    	bus.write_byte_data(0x27, 0x80, i)
    	time.sleep (.05)
    	i -= 1
    	print(i)

    i=i1
    while i < i0:
    	bus.write_byte_data(0x27, 0x80, i)
    	time.sleep (.05)
    	i += 1
    	print(i)


