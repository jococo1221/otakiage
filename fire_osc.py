#-----LIGHTS

ip_address="192.168.2.23"
max_value=68
min_value=1
initial_intensity=30
variability_range=24 #/100
max_var=50
min_var=5
stability=3
flare_range=5 #/10
max_flare=30
min_flare=5
flare_frequency=6 #/10
max_flare_freq=30
min_flare_freq=1
interval=1/60 #seconds
cooling_speed=.02

ip1=initial_intensity
ip2=initial_intensity
ip3=initial_intensity
ip4=initial_intensity
# ip1=initial_intensity
# ip2=initial_intensity
# ip3=initial_intensity
# ip4=initial_intensity

i0=max_value
#i0=int(i0h)
i1=min_value

import smbus
import time
import random

from datetime import datetime
# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d-%b-%Y %H:%M:%S")

# Get I2C bus
bus = smbus.SMBus(1)

print("Hikari - ", dt_string, " - ", ip_address)
#print(smbus.__file__)
#print(random.randrange(1, 10))

def define_intensity(intensity_input):
    intensity=intensity_input
    gap_to_center=(initial_intensity-intensity_input)
    flare_random = random.randrange(0,100) 
    flare_intensity = .1*(random.randrange(0,flare_range*10)) 
    increment = .01*random.randrange(0,variability_range) 
    decrement = cooling_speed*(2*random.randrange(0,variability_range) - int(.1*gap_to_center*random.randrange(0,variability_range)))

    if (intensity-increment>min_value):
        intensity -= decrement 
    if (intensity+increment<max_value):
        intensity += increment 
    if (flare_frequency/10>=flare_random and ip1 + flare_intensity < max_value):
        intensity += flare_intensity 
    #print(random.randrange(1,10))
    return intensity
    #--------



from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import argparse

#def filter_handler(address, *args):
    #print(f"{address}: {args}")
    #print(args[1])

def osc_set_intensity(unused_addr, args, parameter):
    #  print("[{0}] ~ {1}".format(args[0], parameter))
    global initial_intensity
    global min_value
    global max_value
    initial_intensity=parameter*max_value
  #print("El doble del fader es:", 2*parameter)

def osc_set_vivacity(unused_addr, args, parameter):
    global variability_range
    global max_var
    global min_var
    variability_range=int(min_var + parameter*(max_var-min_var))

def osc_set_flare(unused_addr, args, parameter):
    global flare_range
    global max_flare
    global min_flare
    flare_range=int(min_flare + parameter*(max_flare-min_flare))

def osc_set_flare_freq(unused_addr, args, parameter):
  global flare_frequency
  global max_flare_freq
  global min_flare_freq
  flare_frequency=int(max_flare_freq + parameter*(max_flare_freq-min_flare_freq))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default=ip_address, help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

dispatcher = Dispatcher()
#dispatcher.map("/1/fader*", filter_handler)
dispatcher.map("/1/fader5", osc_set_intensity, "Fader blue")
dispatcher.map("/1/fader1", osc_set_intensity, "Fader 1")
dispatcher.map("/1/fader2", osc_set_vivacity, "Fader 2")
dispatcher.map("/1/fader3", osc_set_flare, "Fader 3")
dispatcher.map("/1/fader4", osc_set_flare_freq, "Fader 4")


async def loop():
    """Example main loop that only runs for 10 iterations before finishing"""
    global ip1
    global ip2
    global ip3
    global ip4
    
    
    #for i in range(10000):
    while True:    
        ip1=define_intensity(ip1)
        bus.write_byte_data(0x27, 0x80, int(max_value-ip1))
        
        ip2=define_intensity(ip2)
        bus.write_byte_data(0x27, 0x81, int(max_value-ip2))
        
        ip3=define_intensity(ip3)
        bus.write_byte_data(0x27, 0x82, int(max_value-ip3))
        
        ip4=define_intensity(ip4)
        bus.write_byte_data(0x27, 0x83, int(max_value-ip4))
        
        #print(f"L{i}", end = '')
        await asyncio.sleep(interval)


async def init_main():
    server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    
    await loop()  # Enter main loop of program
    
    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())
