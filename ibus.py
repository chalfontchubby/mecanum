import serial
import struct
import time
import threading

# Define which channels of the interface do what
SPEED_CHAN = 1
TURN_CHAN = 0
STRAFE_CHAN = 3
ENABLE_CHAN = 6
PASSTHROUGH_CHAN = 7
KNOB_1 = 4
KNOB_2 = 5

ENABLE_ON = 2000
ENABLE_OFF = 1000

ZERO_OFFSET = 1500

# Class to read from the uart assuming it is connected to a ibus reciever
# If that has the enable channel set high, then write the unmodified packet
# backout - assuming that tx is connected to a pico decoder
# Else write out a set of values set up from host software.

class Ibus:
    def __init__(self, uart, callback):
        # Pre allocate a buffer for the transactions
        self._out_buffer = bytearray(32)
        self._in_buffer = bytearray(30)

        self._uart = uart
        self._local_values = [1500] * 14
        self._input_values = [1500] * 14
        self.disable()
        self.write(self._local_values)
        self._ibus_thread = threading.Thread(target=self.run, daemon=True)
        self._ibus_thread.start();
        self._host_running = False
        self._callback = callback
        # Don't pass control to app until we have seen in_control false;
        # Prevents unexpected robot startup
        self._safe_startup = False
        # Allow 
        self._disable_passthrough = False
        
    def atexit(self):
        shutdown_values = [1500] * 14
        shutdown_values[ENABLE_CHAN] = ENABLE_OFF
        self.write(shutdown_values)
        print("Sent shutdown values")
        
    def read(self):
        byte = 0
        while True:
            # We could have seen a 0x20, 0x20 - so the last byte we read could be the start of the packet if the
            # first 0x20 was part of the previous checksum.
            if byte != 0x20:
                byte = self._uart.read(1)
            # We must start with a 0x20. If we don't get it - start again
            if byte !=  b'\x20':
                continue
            # Then we need a 0x40, else start again
            # 
            byte = self._uart.read(1)
            if byte != b'\x40':
                continue

            # We've seen a 0x20 and a 0x40 - now slurp the next 30 bytes ino the buffer and decode those.
            # We don't process the 0x2040, so have to remember to deal with it
            bytes_read = self._uart.readinto(self._in_buffer)
            if bytes_read != 30:
                continue

            # (0x20, 0x40) " @"
            # 14*16 bitvalues, little endian
            # 16 bit checksum equal to 0xffff minus all bytes except the checksum

            # Get a view of the memory as 8 bit values we can process more easily for the checksum
            byte_data = memoryview(self._in_buffer)
            
            # Checksum is 0xffff minus every byte except the checksum itself.
            # We stripped the 0x20, 0x40 off the front before we got here, so we start counting down from 0xffff - 0x20 - 40
            my_cksum = 0xffff - 0x20 - 0x40
            # Now we have the rest of the bytes, 32 of them less the 0x20 at the start, and the 2 bytes of checksum
            for i in range(28):
                my_cksum -= byte_data[i]

            *self._input_values, cksum = struct.unpack("<HHHHHHHHHHHHHHH", self._in_buffer)
            if cksum == my_cksum:
                return
            # 0x20, 0x40 can't appear bit packet. Neither checksum nor data can begin with 0x20 or 0x40

    def get_passthrough(self):
        return self._input_values[PASSTHROUGH_CHAN] < 1500

    def passthrough(self):
        self._uart.write(b'\x20\x40')
        self._uart.write(self._in_buffer)

    def get_input_values(self):
        return self._input_values

    def run(self):
        self._uart.reset_input_buffer()
        loops = 0
        last_time = time.time()
        while True:
            pre_read_time = time.time()
            if self._uart.in_waiting > 100:
                # There are a few packets in the input fifo - better jump 
                print("Uart catchup")
                self._uart.reset_input_buffer()

            self.read()
            time_now = time.time()
            delta_t = time_now - last_time
            last_time = time_now
            #print(f"{loops} {self.get_passthrough()} {self._host_running}")
            loops += 1
            if self.get_passthrough():
                # We have now seen the passthrough switch low - so can pass control to the app if needed
                self._safe_startup = True
                if self._host_running:
                    self._host_running = False
                    self._callback(self._host_running)
                self.passthrough()
                
            else:
                if not self._host_running and self._safe_startup:
                    self._host_running = True
                    self._callback(self._host_running)
                self.write(self._local_values)
            # ibus runs at about 7ms period - we can sleep most of that
            #ime.sleep(0.005)
    
    def set_cksum(self):
        # Calculate and insert the checksum into the last 32 bytes
        byte_data = memoryview(self._out_buffer)
        # Checksum is 0xffff minus the sum of the first 30 bytes
        # (i.e. upto but excluding the checksum).
        cksum = 0xffff - sum( byte_data[:30] )
        if cksum < 0:
            print(f"Error: {Cksum=} out of range") 
        byte_data[30] = cksum & 0xff
        byte_data[31] = (cksum >> 8) & 0xff

    def enable(self):
        self._local_values[ENABLE_CHAN] = ENABLE_ON
        
    def disable(self):
        self._local_values[ENABLE_CHAN] = ENABLE_OFF

    def write(self, values):
        assert len(values) <= 14
        if min(values) < 1000 or max(values) > 2000:
            print(f"Error: Values must be in the range 1000 to 2000")
            return False
        # Put the 0x20, 0x40 prefix and the 14 shorts being transmitted into the packet
        struct.pack_into("<BBHHHHHHHHHHHHHH", self._out_buffer, 0, 0x20, 0x40, *values)
        self.set_cksum()
        self._uart.write(self._out_buffer)
        return True

    # Update the motion parameters if not in passthrough
    # Values are in the range +/- 500
    def set_motion(self, speed, turn, strafe):
        self._local_values[SPEED_CHAN] = speed + ZERO_OFFSET
        self._local_values[TURN_CHAN] = turn + ZERO_OFFSET
        self._local_values[STRAFE_CHAN] = strafe + ZERO_OFFSET 

def callback(in_control):
    print(f"{in_control=}")

# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
    
    uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
    ibus = Ibus(uart, callback)
    time.sleep(30)
#    while True:
#        for turn in range(-500,500):
#            ibus.set_motion(0,turn,0)
#            time.sleep(1)
        
        
        
    
