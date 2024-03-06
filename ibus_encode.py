import serial
import struct

class ibus_encode:
    def __init__(self, uart):
        self._buffer = bytearray(32)
        self._uart = uart

    def calc_cksum(self):
        byte_data = memoryview(self._buffer)
        # Checksum is 0xffff minus every byte except the checksum itself.
        cksum = 0xffff
        # Now we have the rest of the bytes, 32 of them less the 0x20 at the start, and the 2 bytes of checksum
        for i in range(30):
            cksum -= byte_data[i]
        byte_data[30] = cksum & 0xff
        byte_data[31] = (cksum >> 8) & 0xff

    def write(self, values):
        assert len(values) <= 14
        struct.pack_into("<HHHHHHHHHHHHHHH", self._buffer, 0, 0x4020, *values)
        self.calc_cksum()
        print(self._buffer)
        uart.write(self._buffer)


# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
    
    uart = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=3.0)
    ibus = ibus_encode(uart)
    while True:
        values = [1507] * 14
        ibus.write(values)