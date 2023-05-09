
max_value=68
min_value=1
variability_range=28 #/100
stability=3
flare_range=5 #/10
flare_frequency=10 #/10
initial_intensity=30
interval=1/60 #seconds

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

print(121)
#print(random.randrange(1, 10))

def define_intensity(intensity_input):
    intensity=intensity_input
    gap_to_center=(initial_intensity-intensity_input)
    flare_random = random.randrange(0,100) 
    flare_intensity = .1*(random.randrange(0,flare_range*10)) 
    increment = .01*random.randrange(0,variability_range) 
    decrement = .02*(2*random.randrange(0,variability_range) - int(.1*gap_to_center*random.randrange(0,variability_range)))

    if (intensity-increment>min_value):
        intensity -= decrement 
    if (intensity+increment<max_value):
        intensity += increment 
    if (flare_frequency/10>=flare_random and ip1 + flare_intensity < max_value):
        intensity += flare_intensity 
    #print(random.randrange(1,10))
    return intensity

  
i=0
while True: # i < 10000:
    # device address 0x27
    # select channel 0x80 1st channel, 0x81 2nd channel ... 0x83 4th channel
    # dimming level - 0 fully open, 100 fully closed (71 decimal)
    
    ip1=define_intensity(ip1)
    bus.write_byte_data(0x27, 0x80, int(max_value-ip1))

    ip2=define_intensity(ip2)
    bus.write_byte_data(0x27, 0x81, int(max_value-ip2))

    ip3=define_intensity(ip3)
    bus.write_byte_data(0x27, 0x82, int(max_value-ip3))

    ip4=define_intensity(ip4)
    bus.write_byte_data(0x27, 0x83, int(max_value-ip4))
  
    time.sleep (interval)
    i += 1

bus.write_byte_data(0x27, 0x80, 0x00)
time.sleep (.3)
bus.write_byte_data(0x27, 0x80, i0)
time.sleep (.3)
bus.write_byte_data(0x27, 0x80, 0x00)
time.sleep (.3)
bus.write_byte_data(0x27, 0x80, i0)

i=i0
while i > i1:
	bus.write_byte_data(0x27, 0x80, i)
	time.sleep (.05)
	i -= 1

i=i1
while i < i0:
	bus.write_byte_data(0x27, 0x80, i)
	time.sleep (.05)
	i += 1
	print(i)


