import serial
import struct

class ibus_encode:
    def __init__(self, uart):
        # Pre allocate a buffer for the transactions
        self._buffer = bytearray(32)
        self._uart = uart

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

    def write(self, values):
        assert len(values) <= 14
        if min(values) < 1000 or max(values) > 2000:
            print(f"Error: Values must be in the range 1000 to 2000")
            return False
        # Put the 0x20, 0x40 prefix and the 14 shorts being transmitted into the packet
        struct.pack_into("<BBHHHHHHHHHHHHHH", self._buffer, 0, 0x20, 0x40, *values)
        self.calc_cksum()
        uart.write(self._buffer)
        return True


# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
    
    uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
    ibus = ibus_encode(uart)
    value = 1000
    while True:
        # Send 14 values in the range 1000 to 2000 in an ibus packet.
        values = [value] * 14
        value += 1
        ibus.write(values)