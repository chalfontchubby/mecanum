from machine import I2C
from time import sleep
from machine import Pin

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
devices = set(i2c.scan())
laser_addr = 116
print(devices)
            
buf1 = bytearray(1)                # Pre-allocated buffers for reads: allows reads to
buf2 = bytearray(2)                # be done in interrupt handlers

buf1[0] = 0xB0;
while True:
    i2c.writeto_mem(laser_addr, 0x10, buf1)
    sleep(0.05)
    i2c.readfrom_mem_into(laser_addr, 0x02, buf2);
    distance = buf2[0] * 0x100 + buf2[1] - 17;
    print(f"distance={distance}mm");
    sleep(0.01);