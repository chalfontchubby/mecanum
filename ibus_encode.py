import serial
import struct
import time

# Define which channels of the interface do what
SPEED_CHAN = 1
TURN_CHAN = 0
STRAFE_CHAN = 3
ENABLE_CHAN = 6

ENABLE_ON = 2000
ENABLE_OFF = 1000
SPEED_MULT = 300
TURN_MULT = 300
STRAFE_MULT = 300

ZERO_OFFSET = 1500

class ibus_encode:
    def __init__(self, uart):
        # Pre allocate a buffer for the transactions
        self._buffer = bytearray(32)
        self._uart = uart
        self._values = [1500] * 14
        self.disable()
        
    def calc_cksum(self):
        # Calculate and insert the checksum into the last 32 bytes
        byte_data = memoryview(self._buffer)
        # Checksum is 0xffff minus the sum of the first 30 bytes
        # (i.e. upto but excluding the checksum).
        cksum = 0xffff - sum( byte_data[:30] )
        if cksum < 0:
            print(f"Error: {Cksum=} out of range") 
        byte_data[30] = cksum & 0xff
        byte_data[31] = (cksum >> 8) & 0xff

    def enable(self):
        self._values[ENABLE_CHAN] = ENABLE_ON
        self.write(self._values)
        
    def disable(self):
        self._values[ENABLE_CHAN] = ENABLE_OFF
        self.write(self._values)

    def write(self, values):
        assert len(values) <= 14
        if min(values) < 1000 or max(values) > 2000:
            print(f"Error: Values must be in the range 1000 to 2000")
            return False
        # Put the 0x20, 0x40 prefix and the 14 shorts being transmitted into the packet
        struct.pack_into("<BBHHHHHHHHHHHHHH", self._buffer, 0, 0x20, 0x40, *values)
        self.calc_cksum()
        self._uart.write(self._buffer)
        return True

    def move(self, speed, turn, strafe):
        self._values[SPEED_CHAN] = int(SPEED_MULT * speed) + ZERO_OFFSET
        self._values[TURN_CHAN] = int(TURN_MULT * turn) +ZERO_OFFSET
        self._values[STRAFE_CHAN] = int(STRAFE_MULT * strafe) +ZERO_OFFSET
        print(self._values)
        self.write(self._values)


    # This does the same, but takes a time argument and steadily changes the values
    # to avoid sudden jerks the robot can't cope with
    def accel(self, speed, turn, strafe, duration):
        # Convert the old values to floats so we don't get rounding problems
        # when we calculate the steps
        last_speed = float(self._values[SPEED_CHAN])
        last_turn = float(self._values[TURN_CHAN])
        last_strafe = float(self._values[STRAFE_CHAN])
        
        target_speed = (SPEED_MULT * speed) + ZERO_OFFSET
        target_turn = (TURN_MULT * turn) +ZERO_OFFSET
        target_strafe = (STRAFE_MULT * strafe) +ZERO_OFFSET
        
        # How long is each step of the process going to take.
        # Smaller makes the acceleration smoother
        step_duration = 0.05
        steps = int(duration / step_duration)
        print(f"{steps=}")
        speed_step = (target_speed - last_speed) / steps
        turn_step = (target_turn - last_turn) / steps
        strafe_step = (target_strafe - last_strafe) / steps
        
        for step in range(steps):
            # Update the values
            last_speed += speed_step
            last_turn += turn_step
            last_strafe += strafe_step
            self._values[SPEED_CHAN] = int(last_speed)
            self._values[TURN_CHAN] = int(last_turn)
            self._values[STRAFE_CHAN] = int(last_strafe)
            print(self._values)
            self.write(self._values)
            time.sleep(step_duration)

# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
    
    uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
    ibus = ibus_encode(uart)
    value = 1000
    script = [
        # dir, rotate, strafe, duration
        [0.1, 0.0, 0.0, 1],
        [0.0, 0.1, 0.0, 1],
        [0.0, 0.0, 0.1, 1],
        [0.0, 0.0, 0.0, 1],
        [-0.1, 0.0, 0.0, 1],
    ]
    ibus.enable()
    
    for (speed, turn, strafe, duration) in script:
        print(f"{speed=}, {turn=}, {strafe=}, {duration=}")
        ibus.move(speed, turn, strafe)
        time.sleep(duration)
    ibus.disable()
        # Send 14 values in the range 1000 to 2000 in an ibus packet.
        #values = [value] * 14
        #value += 1
        #ibus.write(values)