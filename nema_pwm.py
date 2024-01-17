from machine import Timer, Pin, PWM
import time

verbose = True
def debug(str):
    if verbose:
        print(str)
            

class Stepper:
    """
    Handles  A4988 hardware driver for bipolar stepper motors
    """
    enable_pin = None
    instances = []
    
    def __init__(self, dir_pin, step_pin, name=None):
        self.step_pin = Pin(step_pin, Pin.OUT)
        self.pwm = PWM(self.step_pin)
        self.pwm.duty_u16(1000)
        self.pwm.deinit()
        
        self.dir_pin = Pin(dir_pin, Pin.OUT)
        self.dir = 0
        self.count = 0
        self.speed = 0
        Stepper.instances.append(self)
        self.MIN_SPEED = 25   
        
        self.MAX_ACCEL = 5000   
        self.MAX_SPEED = 5000  
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
    # Enable all the motors
    def enable(cls):
        debug(f"Enable")
        cls.enable_pin.high()
        
    @classmethod
    # Disable all the motors
    def kill(cls):
        debug(f"Disable")
        cls.enable_pin.low()

    @classmethod
    def stop_all(cls):
        debug(f"Stop all")
        for stepper in cls.instances:
            stepper.set_speed(0)
        
    def set_speed(self, speed_in):
        needs_start = self.speed == 0
        self.speed = speed_in
        debug(f"{self.name} Speed set to {self.speed}")
        # set direction
        if self.speed> self.MIN_SPEED:
            self.dir = 1
            self.dir_pin.high()
        elif self.speed < -self.MIN_SPEED:
            self.dir = -1
            self.dir_pin.low()
            
        if abs(self.speed) < self.MIN_SPEED:
            debug("{self.name} Below minimum speed - stop")
            self.dir = 0
            self.pwm.deinit()
            self.speed = 0
        else :
            if needs_start:
                Debug("Start")
                self.pwm = PWM(self.step_pin)
                self.pwm.duty_u16(1000)

            self.pwm.freq(abs(self.speed))
        debug(f"{self.name} Speed {speed} dir {self.dir}")
            
    def request_speed(self, speed_in):
        self.set_speed(max([self.speed - self.MAX_ACCEL, min([self.speed + self.MAX_ACCEL , speed_in])]))     
            
    def get_speed(self):
        return self.speed
    


def main():
    
    Stepper.set_enable_pin(14)
    
    motor1 = Stepper(17,16)
    motor2 = Stepper(19,18)

    motor1.name = "one"
    motor2.name = "two"

    Stepper.enable()

    for j in range (5):
        for i in range (10):
            print(f"Loop {i}")
            motor1.request_speed(5000*i)
            motor2.request_speed(-5000)
            time.sleep(1)
        Stepper.stop_all()
    
        
    time.sleep(5)

    #print(f"Stepped {motor1.steps}")
    Stepper.kill()

#def issr(t):
#    global motor1, motor2
#    motor1.do_step()
 #   motor2.do_step()

if __name__ == "__main__":

        
    #tim = Timer(-1,period=timer_period, callback=issr)

    main()