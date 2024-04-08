#from machine import I2C
#from machine import Pin, PWM
from smbus import SMBus


from time import sleep

import math

from math import *
class I2Cmux:
    # TCA9548A
    def __init__(self, smbus, address=0x70):
        self._smbus = smbus
        self._address = address
        
    def switch(self, channels):
        #self._i2c.writeto(0x70, b'\xff')
        self._smbus.write_byte_data(self._address, 0, channels)
  
i2c = SMBus(1)  # Create a new I2C bus

mux = I2Cmux(i2c)
mux.switch(3)
    
num_laser=2
laser_addr = 116
                        
laser_start = 0xB0;
#while True:

calib_count = 200
offsets = [0 , 12 ]
spacing = 90
alpha = math.radians(10)
extra = spacing / math.sin(alpha/2) / 2

while True:
    dists = [0,0]
    mux.switch(3)
    i2c.write_byte_data(laser_addr, 0x10, laser_start)
        
    sleep(0.04)
    for laser_num in range(num_laser):
        mux.switch(1<<laser_num)
        range1 = i2c.read_byte_data(laser_addr, 2)
        range2 = i2c.read_byte_data(laser_addr, 3)
        dists[laser_num] =  (range1 << 8) + range2 - offsets[laser_num]

    b = dists[0] + extra
    c = dists[1] + extra
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(alpha))
    b_smaller = ( b < c)
    if b_smaller: 
        beta = math.asin(math.sin(alpha) * b / a)
        gamma = math.pi - (alpha + beta)
    else:
        gamma = math.asin(math.sin(alpha) * c / a)
        beta = math.pi - (alpha + gamma)
    print(f"{a=} {math.degrees(beta)=} {math.degrees(gamma)=} {85 - math.degrees(gamma)=}")
    diff = (dists[1] - dists[0]) / 2
    diff = max(-32,min(32,diff))
