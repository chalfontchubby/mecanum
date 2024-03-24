# Support for running code on shutdown - put the robot into a safe state
import atexit
import ibus
import serial
import time
import threading

try: 
    from adafruit_servokit import ServoKit
    HAS_SERVOKIT = True
except:
    HAS_SERVOKIT = False
    print("No servokit available. Please see pi_setup/readme.txt for setup if required")

try: 
    from mpu6050 import mpu6050
    HAS_MPU6050 = True
except:
    HAS_MPU6050 = False
    print("No mpu available. Please see pi_setup/readme.txt for setup if gro support is required")


import ctypes


def wrap_angle(angle):
     return ((angle + 360.0 + 180.0) % 360) - 180


class Sensors:
    def __init__(self):
        if not HAS_MPU6050:
            self._mpu = None
            return
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
        if not HAS_MPU6050:
            return
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
                    self._gyro_intergral[axis] = wrap_angle(self._gyro_intergral[axis] + gyro_data[axis] * time_delta)
                    
            self._last_time = time_now
            # Processing all this took some time - so the sleep should be a touch shorted to account for it
            sleep_time = self._last_time + self._time_step - time.time()
            
    def get_heading(self):
        return self._gyro_intergral["z"]

class Robot:
    def __init__(self, callback = None):
        atexit.register(self.atexit)
        self._callback_thread = None  
        self._control_callback = callback
        self._uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
        self._in_control = False
        self._ibus = ibus.Ibus(self._uart, self._set_in_control)
        
        self._sensors = Sensors()

        if HAS_SERVOKIT:
            self._servos = ServoKit(channels=16)
        self.reset_state()

        # Create a thread to handle any ongoing updates - moving towards a target etc
        self._pid_period = 0.05
        self._pid_thread = threading.Thread(target=self._pid_daemon, daemon=True)
        self._pid_thread.start()
    
    def atexit(self):
        print("Shut down the robot")
        self._ibus.atexit()
        

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
        if not HAS_MPU6050:
            print("No mpu available")
            return None
        return self._sensors.get_heading()
        

    def turn_to_heading(self, new_heading):
        if not HAS_MPU6050:
            print("No mpu available")
            return None
        self._target_state["heading"] = new_heading
    
    def set_control_callback(self, callback):
        self._control_callback = callback
    
    def _set_in_control(self, in_control):
        assert in_control != self._in_control
        self._in_control = in_control
        self.reset_state()
        print(f"{in_control=}")
        if self._control_callback is None:
            # No callback - the host application can run a loop and check if it has control
            return
        
        if in_control:
            assert self._callback_thread is None
            self._callback_thread = threading.Thread(target=self._control_callback, args=(self,), daemon=True)
            self._callback_thread.start()
        else :
            assert self._callback_thread
            self._callback_thread.join(3)
            time.sleep(0.5)
            assert not self._callback_thread.is_alive(), "Callback thread didn't exit when expected"
            self._callback_thread = None        

    def get_ibus_values(self):
        values = self._ibus.get_input_values()

        channel_names = [
            "turn_js",
            "speed_js",
            "throttle_js",
            "strafe_js",
            "knob1",
            "knob2",
            "swa",
            "swb",
            "swc",
            "swd"
        ]
        return dict(zip(channel_names, values))
        

    def get_in_control(self):
        return self._in_control

    def _pid_daemon(self):
        while True:
            # Initially only turn control
            if self._target_state["heading"] is not None:
                self._ibus.enable()
                heading_error = wrap_angle( self._target_state["heading"] - self.get_heading())
                print(f"{heading_error=}")
                if abs(heading_error) < 1:
                    self._target_state["heading"] = None
                    self._ibus.disable()

                turn = int(min(20, max(-20, -heading_error*20)))
                print(f"{turn=}")
                self._ibus.set_motion(0, turn ,0)
            time.sleep(0.1)
        pass
    

    def set_motion(self,speed, turn ,strafe):
        self._ibus.set_motion(speed, turn ,strafe)