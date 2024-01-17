class PWM:
    """
    Dummy micropython pwm support for debug on other platforms
    """

    def __init__(self, pin):
        self._pin = pin
        self._duty = None
        self._freq = 0

    def duty_u16(self, duty):
        print(f"duty_u16 pwm on pin {self._pin} = {duty}")
        self._duty = duty

    def freq(self, frequency):
        print(f"freq pwm on pin {self._pin} = {frequency}")
        self._freq = frequency

    def deinit(self):
        print(f"Deinit pwm on pin {self._pin}")
        self._freq = 0

    # Output a string representing the pwm. Called by print etc.
    def __str__(self):
        return f"Pwm ({self._pin}: Duty:{self._duty} Freq: {self._freq})"

class Pin:
    """
    Dummy micropython pwm support for debug on other platforms
    """
    IN = "in"
    OUT = "out"
    LOW = "low"
    HIGH = "high"
    UNKNOWN = "unknown"
    def __init__(self, pin_num, dir):
        self._pin_num = pin_num
        self._dir = dir
        self._val = Pin.UNKNOWN

        print(f"Init {self} ")

    def low(self):
        print(f"Set {self}")

    def low(self):
        self._val = Pin.LOW
        print(f"Set {self}")

    def high(self):
        self._val = Pin.HIGH
        print(f"Set {self}")
    def __str__(self):
        return f"Pin ({self._pin_num}:{self._dir} = {self._val})"