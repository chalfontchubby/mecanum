from machine import I2C
from time import sleep, ticks_ms
from machine import Pin, PWM
import math

import ustruct
from math import *
class I2Cmux:
    # TCA9548A
    def __init__(self, i2c, address=0x70):
        self._i2c = i2c
        self._address = address
        
    def switch(self, channels):
        #self._i2c.writeto(0x70, b'\xff')
        self._i2c.writeto(self._address, channels)
        



i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
mux = I2Cmux(i2c)
mux.switch(b'\x03')
    
print(i2c.scan())
num_laser=2
laser_addr = 116
            
p15 = machine.Pin(15)            
pwm15 = machine.PWM(p15)  
            
buf1 = bytearray(1)                # Pre-allocated buffers for reads: allows reads to
buf2 = bytearray(2)                # be done in interrupt handlers

buf1[0] = 0xB0;
#while True:

selections = [b'\x01', b'\x02']
start_time =  ticks_ms()
calib_count = 200
offsets = [0 , 12 ]
spacing = 90
alpha = math.radians(10)
extra = spacing / math.sin(alpha/2) / 2
print(f"{extra=}")

sleep(2)
while True:
    dists = [0,0]
    mux.switch(b'\x03')
    i2c.writeto_mem(laser_addr, 0x10, buf1)
        
    sleep(0.04)
    time =  ticks_ms()
    for laser_num in range(num_laser):
        mux.switch(selections[laser_num])
        i2c.readfrom_mem_into(laser_addr, 0x02, buf2)
        # unpack?
        dists[laser_num] = buf2[0] * 0x100 + buf2[1] - offsets[laser_num]
 #   if calib_count > 0:
 #       calib_count -= 1
 #       if calib_count == 0 :
 #           offsets[0] = dists[0]
 #           offsets[1] = dists[1]
 #           print ("Snap", offsets)
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

    print(calib_count, dists, dists[0] - dists[1], " " * int(diff + 32) , "*")
end_time =  ticks_ms()
print(f"Delta = {end_time - start_time}")
