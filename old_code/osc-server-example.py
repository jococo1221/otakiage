"""Small example OSC server

This program listens to several addresses, and prints some information about
received packets.
"""
import argparse
import math

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server

#-----LIGHTS-----

max_value=68
min_value=1
variability_range=24 #/100
stability=3
flare_range=5 #/10
flare_frequency=6 #/10
initial_intensity=30
interval=1/60 #seconds
cooling_speed=.02

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


def print_calculo(unused_addr, args, parameter):
#  print("[{0}] ~ {1}".format(args[0], parameter))
  print("El doble del fader es:", 2*parameter)

def print_volume_handler(unused_addr, args, volume):
  print("[{0}] ~ {1}".format(args[0], volume))

def print_compute_handler(unused_addr, args, volume):
  try:
    print("[{0}] ~ {1}".format(args[0], args[1](volume)))
  except ValueError: pass

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
#      default="127.0.0.1", help="The ip to listen on")
      default="192.168.2.17", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  dispatcher = Dispatcher()
  dispatcher.map("/1/*", print)
  dispatcher.map("/2/*", print)
  dispatcher.map("/3/*", print)
  dispatcher.map("/1/fader1", print_calculo, "Fader")
  dispatcher.map("/filter", print)
  dispatcher.map("/volume", print_volume_handler, "Volume")
  dispatcher.map("/logvolume", print_compute_handler, "Log volume", math.log)

  server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()
