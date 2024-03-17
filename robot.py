from ibus_encode import ibus_encode
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
        self._time_step = 1

        self._done = False
        self.calc_bias()
        self._run_mpu()
        self._gyro_bias = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        }
        self._gyro_sum = {
            'x': 0.0,
            'y': 0.0,
            'z': 0.0,
        }

    def calc_bias(self):
        for i in range(self._bias_samples):
            gyro_data = self._mpu.get_gyro_data()
            for axis, val in gyro_data.items():
                self._gyro_bias[axis] += val / self._bias_samples

    def _run_mpu(self):
        self._last_time = time.time()
        while True:
            time.sleep(self._increment)
            time_now = time.time()
            time_delta = time_now - self._last_time
            gyro_data = self._mpu.get_gyro_data()
            for axis in gyro_data.keys():
                gyro_data[axis] -= self._gyro_bias[axis]
                self._gyro_sum[axis] += self._gyro_data[axis] * time_delta


class Robot:
    def __init__(self):
        self._uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
        self._ibus = ibus_encode(self._uart)
        self._sensors = Sensors()

        # Current state
        self._state = {
            "speed": 0.0,
            "turn": 0.0,
            "strafe": 0.0,
        }
        # target state
        self._target_state = {
            "speed": None,
            "turn": None,
            "strafe": None,
        }
        # Position in a frame of reference based on starting point and heading
        # X forwards
        # Y Right
        # Orientation in degrees clockwise
        self._global_pos = {
            "x": 0.0,
            "y": 0.0,
            "orientation": 0.0,
        }
        self._servos = ServoKit(channels=16)

    def enable_motors(self):
        self._ibus.enable()

    def disable_motors(self):
        self._ibus.diable()

    def get_heading(self):
        return self._sensor.get_heading)

        def turn_to_heading(self, new_heading):
            self._target_heading = new_heading

    if __name__ == "__main__":
        robot = Robot()
        while True:
            print(f"Heading = {robot.get_heading()}")
