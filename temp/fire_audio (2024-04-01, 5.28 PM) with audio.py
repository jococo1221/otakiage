#-----LIGHTS


#ip_address="192.168.2.23"
#ip_address="192.168.238.45"
max_value=68
min_value=1
initial_intensity=5

target_intensity=initial_intensity

variability_range=10 #/100

max_var=50
min_var=5
stability=3

#replaced by snap
flare_range=5 #/10
max_flare=30
min_flare=5

snap_range=.07
max_snap=.20
min_snap=.01

flare_frequency=6 #/10
max_flare_freq=30
min_flare_freq=1
interval=1/60 #seconds
cooling_speed=.01

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
buffer_size=3

ip1_history = deque([0] * buffer_size, maxlen=buffer_size)
ip1_history = deque([0] * buffer_size, maxlen=buffer_size)
ip2_history = deque([0] * buffer_size, maxlen=buffer_size)
ip3_history = deque([0] * buffer_size, maxlen=buffer_size)
ip4_history = deque([0] * buffer_size, maxlen=buffer_size)
ip5_history = deque([0] * buffer_size, maxlen=buffer_size)
ip6_history = deque([0] * buffer_size, maxlen=buffer_size)
ip7_history = deque([0] * buffer_size, maxlen=buffer_size)
ip8_history = deque([0] * buffer_size, maxlen=buffer_size)

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

def randomize_intensity(intensity_input, audio_factor):
    
    increment = (.1*random.randrange(-variability_range,variability_range) + 2*(audio_factor-1))
    print("audio factor: ", audio_factor, " increment:", increment)

    
    calculated_intensity= intensity_input+increment

    return calculated_intensity
    


def animate_intensity(intensity_input, feedback_prev, audio_factor):
    
    # range_values=max_value-min_value
    
    intensity_with_feedback=intensity_input+feedback_prev
    
    gap=(intensity_input-target_intensity)

    calculated_intensity=intensity_input-gap*snap_range
    
    output_intensity=calculated_intensity*.2 + feedback_prev*.8
    
    output_intensity
    if(output_intensity<=min_value):
        output_intensity=min_value
    
    # max_increment=max_value-intensity_input
    # max_decrement=intensity_input-min_value
    #
    # pull_to_target=(target_intensity-intensity_input)*(random.randrange(0,flare_range*10))
    

    return output_intensity
    #--------

def animate_intensity_old(intensity_input, feedback_prev, audio_factor):
    
    
    flux_intensity=(.8*intensity_input+.5*feedback_prev+.2*audio_factor)
    gap_to_center=(target_intensity-flux_intensity)
    
    flare_random = random.randrange(0,100) 
    flare_intensity = .1*(random.randrange(0,flare_range*10)) 

    increment = gap_to_center*(.01*random.randrange(0,variability_range))
    #random decrement, proportional to cooling parameter and distance to center
    decrement = cooling_speed*(2*random.randrange(0,variability_range) - int(.1*gap_to_center*random.randrange(0,variability_range)))

    
    if (flux_intensity-increment>min_value):
        flux_intensity -= decrement 
    if (flux_intensity+increment<max_value):
        flux_intensity += increment 
    #flares, random, and only when it won't overflow
    if (flare_frequency/10>=flare_random and intensity_input + flare_intensity < max_value):
        flux_intensity += flare_intensity 
    #print(random.randrange(1,10))
    return flux_intensity
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
    print("target_intensity: ", target_intensity)
  #print("El doble del fader es:", 2*parameter)

def osc_set_vivacity(unused_addr, args, parameter):
    global variability_range
    global max_var
    global min_var
    variability_range=int(min_var + parameter*(max_var-min_var))
    print("variability_range: ", variability_range)

#replaced by snap
def osc_set_flare(unused_addr, args, parameter):
    global flare_range
    global max_flare
    global min_flare
    flare_range=int(min_flare + parameter*(max_flare-min_flare))


def osc_set_snap(unused_addr, args, parameter):
    global snap_range
    global max_snap
    global min_snap
    snap_range=float(min_snap + parameter*(max_snap-min_snap))
    print("snap_range: ", snap_range)


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
dispatcher.map("/1/fader3", osc_set_snap, "Fader 3")
dispatcher.map("/1/fader4", osc_set_flare_freq, "Fader 4")

dispatcher.map("/4/multitoggle/*", osc_set_multitoggle) 

#optional show in terminal what fader is used
dispatcher.map("/*/*", filter_handler)


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


        # osc fader crossfades (not working very well)
        audio_factor_crossfade=((mic_influence_percentage/100)*(volume_percentage/100) + (1-(mic_influence_percentage/100))*1)
        # fader adds
        audio_factor_add=( 1 + 2*((mic_influence_percentage/100)*(volume_percentage/100)*2))
        audio_factor=audio_factor_add
        
        ip1=randomize_intensity(ip1, audio_factor)
        ip1=animate_intensity(ip1, ip1, audio_factor)
        intensity=ip1
        bus.write_byte_data(i2c_address, 0x80, prepare_hw_output(intensity))
        
        feedback_lag=1
        
        # ip2=ip2*(1+volume_percentage) #cumulative feedback
        ip2=randomize_intensity(ip2, audio_factor)
        ip2=animate_intensity(ip2, ip1_history[feedback_lag], audio_factor)
        intensity=ip2
        #print("mic_influence_percentage: ",mic_influence_percentage," - volume_percentage:", volume_percentage)
        bus.write_byte_data(i2c_address, 0x81, prepare_hw_output(intensity))
        
        #ip3=animate_intensity(ip3*(.5 + mic_influence_percentage*volume_percentage))
        ip3=randomize_intensity(ip3, audio_factor)
        ip3=animate_intensity(ip3, ip2_history[feedback_lag], audio_factor)           
        intensity=ip3
        bus.write_byte_data(i2c_address, 0x82, prepare_hw_output(intensity))
        
        ip4=animate_intensity(ip4, ip3_history[feedback_lag], audio_factor)
        intensity=ip4
        bus.write_byte_data(i2c_address, 0x83, prepare_hw_output(intensity))

        #second controler
        ip5=animate_intensity(ip5, ip4_history[feedback_lag], audio_factor)
        intensity=ip5
        bus.write_byte_data(i2c_address2, 0x80, prepare_hw_output(intensity))
        
        ip6=animate_intensity(ip6, ip5_history[feedback_lag], audio_factor)
        intensity=ip6
        bus.write_byte_data(i2c_address2, 0x81, prepare_hw_output(intensity))
        
        ip7=animate_intensity(ip7, ip6_history[feedback_lag], audio_factor)
        intensity=ip7
        bus.write_byte_data(i2c_address2, 0x82, prepare_hw_output(intensity))
        
        ip8=animate_intensity(ip8, ip7_history[feedback_lag], audio_factor)
        intensity=ip8
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


