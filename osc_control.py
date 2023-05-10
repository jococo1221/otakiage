import RPi.GPIO as GPIO	
import subprocess
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Este da positivo mientras el boton esta apretado. 
#El boton esta conectado a tierra y al pin 23, asi que FALSE pasa cuando le aprietas
#GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)

INPUT_SUBIR = 23
GPIO.setup(INPUT_SUBIR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
INPUT_BAJAR = 24
GPIO.setup(INPUT_BAJAR, GPIO.IN, pull_up_down=GPIO.PUD_UP)



LED_RED = 17
GPIO.setup(LED_RED, GPIO.OUT)
LED_YELLOW = 27
GPIO.setup(LED_YELLOW, GPIO.OUT)
LED_GREEN = 22
GPIO.setup(LED_GREEN, GPIO.OUT)


"""Small example OSC client

This program sends 10 random values between 0.0 and 1.0 to the /filter address,
waiting for 1 seconds between each value.
"""
import argparse
import random
import time

from pythonosc import udp_client
print("otakiage")

def led(led_name):
    #turn YELLOW led ON
    if led_name=="green":
        GPIO.output(LED_GREEN, GPIO.HIGH)
    else:
        GPIO.output(LED_GREEN, GPIO.LOW)
    if led_name=="yellow":
        GPIO.output(LED_YELLOW, GPIO.HIGH) 
    else:
        GPIO.output(LED_YELLOW, GPIO.LOW)
    if led_name=="red":
        GPIO.output(LED_RED, GPIO.HIGH) 
    else:
        GPIO.output(LED_RED, GPIO.LOW)
    if led_name=="black":
        GPIO.output(LED_GREEN, GPIO.LOW)
        GPIO.output(LED_YELLOW, GPIO.LOW)
        GPIO.output(LED_RED, GPIO.LOW)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="192.168.2.23" ,
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)
  
  intensidad = .3
  x = 100
  
  while True: 
    #for x in range(10):
    #print (x)
    
    intensidad = round(intensidad, 1)
    if GPIO.input(INPUT_SUBIR) == False:   
      #value=random.random()
      if (intensidad + .1) <= 1:
          intensidad += .1
      value = intensidad
      client.send_message("/1/fader5", value )
      led("green")
    if GPIO.input(INPUT_BAJAR) == False:   
      #value=random.random()
      if (intensidad - .1) >= 0 and (intensidad - .1) <= 1:
          intensidad -= .1
      value = intensidad
      client.send_message("/1/fader5", value )
      led("red")
    print(intensidad)
    x += 1
    time.sleep(.1)
    if x >= 50:
        led("yellow")
        time.sleep(.1)
        x=0
    led("black")
    
    
