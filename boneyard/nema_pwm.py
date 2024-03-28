###
# If we are running on micro python, we should be able in import the machine classes
try:
    from machine import Pin, PWM

except ImportError:
    # That failed.... We are not running on a pico so include some dummy classes so we can debug on other platforms
    print("No micropython support found. ")
    from dummy_machine import Pin, PWM


import time

# Duty is parts per 1<<16
DUTY = 1<<15

verbose = True

# Set some global scale factor for motor speed to pwm frequency
MOTOR_SPEED = 64000
# Duty cycle is 16 bit, so this should give 50% duty cycle
# A4988 requires 1us pulse width. At 10kHz, 50% gives 0.5 / 10e4 = 50us
DUTY = 1<<15

def debug(str):
    if verbose:
        print(str)
            

class Stepper:
    """
    Handles  A4988 hardware driver for bipolar stepper motors
    """
    enable_pin = None
    step_size_pins = [None] * 3
    instances = []
        
    def __init__(self, dir_pin, step_pin, name=None):
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.pwm = PWM(self.step_pin)
        self.pwm.duty_u16(DUTY)
        self.pwm.deinit()
        print(f"Dir dpin {dir_pin}")
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.dir = 0
        self.count = 0
        self.speed = 0
        Stepper.instances.append(self)
        self.MIN_SPEED = 25   
        
        self.MAX_ACCEL = 500   
        self.steps = 0
        self.name=name if name else ""
        self.step_pin.low()


            
    # class methods control all the instances in the class rather than
    # just one.
    @classmethod
    # Define which pin is the enable for all motors
    def set_enable_pin(cls, pin):
        debug(f"Set enable pin to {pin}")
        cls.enable_pin = Pin(pin, Pin.OUT)
        
    @classmethod
    def set_step_size_pins(cls, pin0, pin1, pin2):
        debug(f"Set step size pins to {pin0}:{pin1}:{pin2}")
        cls.step_size_pins = [Pin(pin0, Pin.OUT), Pin(pin1, Pin.OUT), Pin(pin2, Pin.OUT)]
     
    @classmethod
    # Enable all the motors
    def enable(cls):
        debug(f"Enable")
        cls.enable_pin.low()

        
    @classmethod
    # Disable all the motors
    def kill(cls):
        debug(f"Disable")
        cls.enable_pin.high()

    @classmethod
    def stop_all(cls):
        debug(f"Stop all")
        for stepper in cls.instances:
            stepper.set_speed(0)
    
    # 0 = full_step
	# 1 = 1/2 step
    # 2 = 1/4 step
    # etc
    @classmethod
    def set_step_size(cls, step_size):
        assert step_size >= 0 and step_size <= 7
        for bit in range(3):
            cls.step_size_pins[bit].value(1 & (step_size >> bit))
    

    def set_speed(self, speed_in):
        needs_start = self.speed == 0
        self.speed = speed_in
        debug(f"{self.name} Speed set to {self.speed}")
        # set direction
        if self.speed> self.MIN_SPEED:
            self.dir = 1
            self.dir_pin.high()
            print("dir high")
        elif self.speed < -self.MIN_SPEED:
            self.dir = -1
            self.dir_pin.low()
            print("Dir low")
                  
        if abs(self.speed) < self.MIN_SPEED:
            debug(f"{self.name} Below minimum speed - stop")
            self.dir = 0
            self.pwm.deinit()
            self.speed = 0
        else :
            if needs_start:
                debug("Start")
                self.pwm = PWM(self.step_pin)
                self.pwm.duty_u16(DUTY)

            self.pwm.freq(abs(self.speed))
        debug(f"{self.name} Speed:{self.speed} dir:{self.dir}")
            
    def request_speed(self, speed_in):
        self.set_speed(max([self.speed - self.MAX_ACCEL, min([self.speed + self.MAX_ACCEL , speed_in])]))     
            
    def get_speed(self):
        return self.speed
    
def calc_motor_speeds(velocities) :
    setup = {
        "FORE": [
             1, -1,
             1, -1
        ],
        "LEFT": [
             1,  1,
            -1, -1
        ],
        "CLOCK": [
             1,  1,
             1,  1
        ]
    }
    # Speed of each of the 4 motors is the sum of the velocity in that direction * it's motor direction
    # returns a list of 4 motor speeds
    return [MOTOR_SPEED * sum(setup[dir][i] * velocities[dir] for dir in velocities.keys() ) for i in range (4)]

def main():
    
    Stepper.set_enable_pin(6)
    Stepper.set_step_size_pins(7, 8, 9)

    motors = [Stepper(11,10, name="FL"),
              Stepper(17,16, name="FR"),
              Stepper(20,21, name="BL"),
              Stepper(18,29, name="BR")]


    Stepper.enable()
    Stepper.set_step_size(5)

    # How fast do we go in each of 3 directions
    velocities= {"FORE": 1, "LEFT": 0, "CLOCK": 0}

    # Convert those to 4 motor speeds
    speeds = calc_motor_speeds(velocities)
    print(f"{velocities} -> {speeds}")
    for j in range(500):
        for i in range(4):
            motors[i].request_speed(speeds[i])
        time.sleep(0.1)
    Stepper.stop_all()

    
        
    time.sleep(5)

    #print(f"Stepped {motor1.steps}")
    Stepper.kill()

if __name__ == "__main__":
    main()