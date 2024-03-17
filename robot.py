import ibus
import serial
import time
import threading

from adafruit_servokit import ServoKit
from mpu6050 import mpu6050

class Sensors:
    def __init__(self):
        self._mpu = mpu6050(0x68)
        ## Don't want very fast response - set mpu bandwidth to 10 Hz
        self._mpu.set_filter_range(mpu6050.FILTER_BW_10)
        self._bias_samples = 200  # number of samples to measure to get the initial gyro bias
        self._time_step = 0.01
        # Flag to indicate we are not moving, so any sensor data can be used to work out
        # bias and drift etc.
        self._stationary = False
        
        self._done = False
        self._gyro_bias = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        }
        self._gyro_intergral = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        }
        self.calc_mpu_bias()
        self._mpu_thread = threading.Thread(target=self._mpu_daemon, daemon=True)
        self._mpu_thread.start();
        
    def calc_mpu_bias(self):
        for i in range(self._bias_samples):
            gyro_data = self._mpu.get_gyro_data()
            for axis, val in gyro_data.items():
                self._gyro_bias[axis] += val / self._bias_samples

    def _mpu_daemon(self):
        self._last_time = time.time()
        sleep_time = self._time_step
        while True:
            if sleep_time > 0:
                time.sleep(sleep_time)
            time_now = time.time()
            time_delta = time_now - self._last_time
            gyro_data = self._mpu.get_gyro_data()
            if self._stationary:
                for axis, val in gyro_data.items():
                    # low pass filter the bias
                    self._gyro_bias[axis] = (self._gyro_bias[axis] *
                        ( self._bias_samples - 1) + gyro_data[axis]) / self._bias_samples
                    gyro_data[axis] -= self._gyro_bias[axis]
            else: 
                for axis in gyro_data.keys():
                    gyro_data[axis] -= self._gyro_bias[axis]
                    self._gyro_intergral[axis] += gyro_data[axis] * time_delta
            self._last_time = time_now
            # Processing all this took some time - so the sleep should be a touch shorted to account for it
            sleep_time = self._last_time + self._time_step - time.time()
            
    def get_heading(self):
        return self._gyro_intergral["z"]

class Robot:
    def __init__(self):
        self._uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
        self._in_control = False
        self._ibus = ibus.Ibus(self._uart, self._set_in_control)
        self._sensors = Sensors()
        
        self._servos = ServoKit(channels=16)
        self._control_callback = None
        self.reset_state()
        self._pid_period = 0.05
        self._pid_thread = threading.Thread(target=self._pid_daemon, daemon=True)
        self._pid_thread.start()
        
    def reset_state(self):
        self._target_state = {
            "speed": None,
            "turn": None,
            "strafe": None,
            "heading": None
        }
        # Current state
        self._state = {
            "speed": 0.0,
            "turn": 0.0,
            "strafe": 0.0,
        }

    def enable_motors(self):
        self._ibus.enable()

    def disable_motors(self):
        self._ibus.diable()

    def get_heading(self):
        return self._sensors.get_heading()

    def turn_to_heading(self, new_heading):
        self._target_state["heading"] = new_heading
    
    def set_control_callback(self, callback):
        self._control_callback = callback
    
    def _set_in_control(self, in_control):
        self._in_control = in_control
        if in_control:
            # Clear any targets when we take over
            self.reset_state()
        print(f"{in_control=}")
        if self._control_callback is not None:
            self._control_callback(in_control)

    def get_in_control(self):
        return self._in_control

    def _pid_daemon(self):
        while True:
            print("pid daemon")
            # Initially only turn control
            if self._target_state["heading"] is not None:
                heading_error = self._target_state["heading"] - self.get_heading()
                print(f"{heading_error=}")
        pass
    
if __name__ == "__main__":
    robot = Robot()
    def control_callback(in_control):
        if in_control:
            robot.turn_to_heading(0)
            print("Taking Over")
    
    robot.set_control_callback(control_callback)
    
    while True:
        print(f"Heading = {robot.get_heading()}")
        time.sleep(1)
