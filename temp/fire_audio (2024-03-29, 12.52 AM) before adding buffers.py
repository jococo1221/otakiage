#-----LIGHTS


#ip_address="192.168.2.23"
#ip_address="192.168.238.45"
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

mic_influence_percentage=50
volume_percentage_last_measure=0


i2c_address=0x27
i2c_address2=0x26

# PCF8574 I2C-Bus Slave Address Map
#     SWITCH        PCF8574 I2C-Bus
# A2   A1   AO   Slave Address
# L    L    L    0x27
# L    L    H    0x26
# L    H    L    0x25
# L    H    H    0x24
# H    L    L    0x23
# H    L    H    0x22
# H    H    L    0x21
# H    H    H    0x20

target_intensity=initial_intensity

# Import deque class from collections module
from collections import deque

# Initialize deques to store previous values of ip1 to ip8
ip1_history = deque(maxlen=50)
ip2_history = deque(maxlen=50)
ip3_history = deque(maxlen=50)
ip4_history = deque(maxlen=50)
ip5_history = deque(maxlen=50)
ip6_history = deque(maxlen=50)
ip7_history = deque(maxlen=50)
ip8_history = deque(maxlen=50)

ip1=target_intensity
ip2=target_intensity
ip3=target_intensity
ip4=target_intensity

ip5=target_intensity
ip6=target_intensity
ip7=target_intensity
ip8=target_intensity

volume_percentage = 0
# ip1=target_intensity
# ip2=target_intensity
# ip3=target_intensity
# ip4=target_intensity

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

#print("Hikari - ", dt_string, " - ", ip_address)
#print(smbus.__file__)
#print(random.randrange(1, 10))

#----AUDIO


import numpy as np
import sounddevice as sd
import threading  # Import threading module

# Parameters
duration = 0.1  # Duration of each audio frame in seconds
sample_rate = 44100  # Change this to a supported sample rate
blocksize = 16*1024 #1024  # Buffer size

def estimate_volume(data):
    # Compute root mean square (RMS) of the audio signal
    rms = np.sqrt(np.mean(data**2))
    # Convert RMS to dB
    volume_db = 20 * np.log10(rms)
    # Map dB to a range (0, 100)
    volume = np.interp(volume_db, [-60, 0], [0, 100])
    return volume

def audio_processing():

    global volume_percentage
    while True:
        ip1_history.append(ip1)
        ip2_history.append(ip2)
        ip3_history.append(ip3)
        ip4_history.append(ip4)
        ip5_history.append(ip5)
        ip6_history.append(ip6)
        ip7_history.append(ip7)
        ip8_history.append(ip8)
        # Capture audio input
        data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, blocking=True)
        # Estimate volume level
        volume = estimate_volume(data.flatten())
        volume_percentage = int(volume)
        # Adjust LED intensity based on volume level
        # Your LED control logic here
        time.sleep(0.01)  # Sleep to avoid high CPU usage

# def main():
#     device_name = "USB PnP Sound Device"  # Replace with your microphone's name
#     with sd.InputStream(device=device_name, callback=callback, channels=1, samplerate=sample_rate, blocksize=blocksize):
#         while True:
#             pass
#
# def callback(indata, frames, time, status):
#     if status:
#         print(status)
#     volume = volume(indata.flatten())
#     print(f"Volume: {int(volume)}")
#
# if __name__ == "__main__":
#     main()








#----


def animate_intensity(intensity_input):
    
    
    intensity=intensity_input
    gap_to_center=(target_intensity-intensity_input)
    flare_random = random.randrange(0,100) 
    flare_intensity = .1*(random.randrange(0,flare_range*10)) 
    increment = .01*random.randrange(0,variability_range) 
    # print("intensity_input to animate: ", intensity_input)
    decrement = cooling_speed*(2*random.randrange(0,variability_range) - int(.1*gap_to_center*random.randrange(0,variability_range)))

    if (intensity-increment>min_value):
        intensity -= decrement 
    if (intensity+increment<max_value):
        intensity += increment 
    if (flare_frequency/10>=flare_random and intensity_input + flare_intensity < max_value):
        intensity += flare_intensity 
    #print(random.randrange(1,10))
    return intensity
    #--------

def prepare_hw_output(intensity_input):
    #this hardware's intensity is higer when zero and lower when 1
    hw_output=int(max_value-intensity_input)

    return hw_output



from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import asyncio
import argparse

def filter_handler(address, *args):
    #output the address and the value
    print(f"{address}: {args}")
    #print(args[1]) #this one throws an error

def osc_set_multitoggle(address, *args):
    global ip1
    global ip2
    global ip3
    global ip4
    global ip5
    global ip6
    global ip7
    global ip8
    #payload = str(address) + str(args[0])
    #print(payload)
    
    #when turned on
    if args[0]==1:
        target_value=max_value

    if args[0]==0:
        target_value=min_value
    
    if address=="/4/multitoggle/1/1": ip1=target_value
    if address=="/4/multitoggle/1/2": ip2=target_value
    if address=="/4/multitoggle/1/3": ip3=target_value
    if address=="/4/multitoggle/1/4": ip4=target_value
    if address=="/4/multitoggle/1/5": ip5=target_value
    if address=="/4/multitoggle/1/6": ip6=target_value
    if address=="/4/multitoggle/1/7": ip7=target_value
    if address=="/4/multitoggle/1/8": ip8=target_value
        #print(address)    
    #print(f"{address}: {args}")
    
    #if (address + )== "/4/multitoggle/1/1: (1.0,)"


def osc_set_intensity(unused_addr, args, parameter):
    #  print("[{0}] ~ {1}".format(args[0], parameter))
    global target_intensity
    global min_value
    global max_value
    target_intensity=parameter*max_value
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

def osc_set_mic_influence_percentage(unused_addr, args, parameter):
  global mic_influence_percentage
  mic_influence_percentage=int(parameter*100)
  #print("Mic influence: ", parameter)
  


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("--ip", default=ip_address, help="The ip to listen on")
    parser.add_argument("--port", type=int, default=5005, help="The port to listen on")
    args = parser.parse_args()

dispatcher = Dispatcher()


dispatcher.map("/1/fader5", osc_set_intensity, "Fader blue")
dispatcher.map("/1/fader1", osc_set_mic_influence_percentage, "Fader 1")
dispatcher.map("/1/fader2", osc_set_vivacity, "Fader 2")
dispatcher.map("/1/fader3", osc_set_flare, "Fader 3")
dispatcher.map("/1/fader4", osc_set_flare_freq, "Fader 4")

dispatcher.map("/4/multitoggle/*", osc_set_multitoggle) 

#optional show in terminal what fader is used
#dispatcher.map("/*/*", filter_handler)


async def loop():
    """Example main loop that only runs for 10 iterations before finishing"""
    global ip1
    global ip2
    global ip3
    global ip4

    global ip5
    global ip6
    global ip7
    global ip8  
    
    volume_percentage_last_measure=0
    
    #for i in range(10000):
    while True:    
        
        # Capture audio input
        # data = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=1, blocking=True)
        # Estimate volume level
        # volume = estimate_volume(data.flatten())
        # volume_factor = (100-volume) / 100
        # volume_factor = 1
        

        
        
        # ip1=volume_factor*animate_intensity(ip1)
        # intensity1=volume_factor*animate_intensity(ip1)

        audio_factor_crossfade=((mic_influence_percentage/100)*(volume_percentage/100) + (1-(mic_influence_percentage/100))*1)
        audio_factor_add=( 1 + 2*((mic_influence_percentage/100)*(volume_percentage/100)))
        audio_factor=audio_factor_add
        
        ip1=animate_intensity(ip1)
        intensity=ip1*audio_factor
        bus.write_byte_data(i2c_address, 0x80, prepare_hw_output(intensity))
        
        # ip2=ip2*(1+volume_percentage) #cumulative feedback
        ip2=animate_intensity(ip2)
        intensity=ip2*audio_factor
        #print("mic_influence_percentage: ",mic_influence_percentage," - volume_percentage:", volume_percentage)
        bus.write_byte_data(i2c_address, 0x81, prepare_hw_output(intensity))
        
        #ip3=animate_intensity(ip3*(.5 + mic_influence_percentage*volume_percentage))
        ip3=animate_intensity(ip3)           
        intensity=ip3*audio_factor
        bus.write_byte_data(i2c_address, 0x82, prepare_hw_output(intensity))
        
        ip4=animate_intensity(ip4)
        intensity=ip4*audio_factor
        bus.write_byte_data(i2c_address, 0x83, prepare_hw_output(intensity))

        #second controler
        ip5=animate_intensity(ip5)
        intensity=ip5*audio_factor
        bus.write_byte_data(i2c_address2, 0x80, prepare_hw_output(intensity))
        
        ip6=animate_intensity(ip6)
        intensity=ip6*audio_factor
        bus.write_byte_data(i2c_address2, 0x81, prepare_hw_output(intensity))
        
        ip7=animate_intensity(ip7)
        intensity=ip7*audio_factor
        bus.write_byte_data(i2c_address2, 0x82, prepare_hw_output(intensity))
        
        ip8=animate_intensity(ip8)
        intensity=ip8*audio_factor
        bus.write_byte_data(i2c_address2, 0x83, prepare_hw_output(intensity))


        #DEBUG only output the volume when there's a 10% change
        if volume_percentage > volume_percentage_last_measure*1.10:
        #if True:
            print(f"Volume: {int(volume_percentage/1)}, Mic influence: {int(mic_influence_percentage)}, ip8: {int(ip8)}, Intensity8: {int(intensity)}")
        
        volume_percentage_last_measure=volume_percentage
        
        #print(f"L{i}", end = '')
                
        await asyncio.sleep(interval)


async def init_main():
    
    # Change ('0.0.0.0', args.port) to ('0.0.0.0', args.port)
    server = AsyncIOOSCUDPServer(('0.0.0.0', args.port), dispatcher, asyncio.get_event_loop())
    transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    #
    # server = AsyncIOOSCUDPServer((args.ip, args.port), dispatcher, asyncio.get_event_loop())
    # transport, protocol = await server.create_serve_endpoint()  # Create datagram endpoint and start serving
    
    audio_thread = threading.Thread(target=audio_processing)
    audio_thread.start()
    
    await loop()  # Enter main loop of program
    
    transport.close()  # Clean up serve endpoint


asyncio.run(init_main())


