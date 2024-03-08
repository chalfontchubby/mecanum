from adafruit_servokit import ServoKit
from mpu6050 import mpu6050

import time

# for atan2
import math

kit = ServoKit(channels=16)
sensor = mpu6050(0x68)

## Don't want very fast response - set bandwidth to 19 Hz
sensor.set_filter_range(mpu6050.FILTER_BW_10)
dir = 0
gyro_bias= {
    'x': 0.0,
    'y': 0.0,
    'z': 0.0,
    }
gyro_sum= {
    'x': 0.0,
    'y': 0.0,
    'z': 0.0,
    }
            
SAMPLES = 1000
for i in range(SAMPLES):
    gyro_data = sensor.get_gyro_data()
    for axis, val in gyro_data.items():
        gyro_bias[axis] += val / SAMPLES
last_time = time.time()        
while True:
    time_now = time.time()
    delta_t = time_now - last_time
    last_time = time_now
    acc_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    angle_x = max(0,min(180,math.degrees(math.atan2(acc_data['x'], acc_data['z'])) + 90))
    angle_y = max(0,min(180,math.degrees(math.atan2(acc_data['y'], acc_data['z'])) + 90))
    #print(angle_x, angle_y)
    for axis in gyro_data.keys():    
        gyro_data[axis] -= gyro_bias[axis] 
        gyro_sum[axis] += gyro_data[axis] * delta_t                                      
    print(gyro_sum )

    kit.servo[0].angle = angle_x
    kit.servo[1].angle = angle_y
