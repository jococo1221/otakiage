i0=70
#i0=int(i0h)
i1=1

import smbus
import time



# Get I2C bus
bus = smbus.SMBus(1)
# bus.beginTrasmission(0x27)dev
# PCA9531 address, 0x60(96)
# Select frequency prescaler 0 register, 0x01(01)
#		0x4B(75)	Period of blink = 0.5 sec

# device address 0x27
# select channel 0x80 1st channel, 0x81 2nd channel ... 0x83 4th channel
# dimming level - 0 fully open, 100 fully closed (71 decimal)
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



# PCA9531 address, 0x60(96)
# Select pulse width modulation 0 register, 0x02(02)
#		0x80(128)	Duty cycle = 50
#bus.write_byte_data(0x60, 0x02, 0x80)

# PCA9531 address, 0x60(96)
# Select LED selector register, 0x05(05)
#		0xAA(170)	Output set to Blinking at PWM0
#bus.write_byte_data(0x60, 0x05, 0xAA)

# PCA9531 address, 0x60(96)
# Select LED selector register, 0x06(06)
#		0xAA(170)	Output set to Blinking at PWM0
#bus.write_byte_data(0x60, 0x06, 0xAA)
