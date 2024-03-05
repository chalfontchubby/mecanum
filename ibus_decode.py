from machine import UART
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
        struct.pack_into("<HHHHHHHHHHHHHHH", self.buffer, 0, 0x4020, *values)
        calc_cksum()

=

class ibus_interface:
    def __init__(self, uart):
        self._buffer = bytearray(30)
        self._uart = uart

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
            self._uart.readinto(self._buffer)

            # (0x20, 0x40) " @"
            # 14*16 bitvalues, little endian
            # 16 bit checksum equal to 0xffff minus all bytes except the checksum

            # Get a view of the memory as 8 bit values we can process more easily for the checksum
            byte_data = memoryview(self._buffer)
            
            # Checksum is 0xffff minus every byte except the checksum itself.
            # We stripped the 0x20, 0x40 off the front before we got here, so we start counting doen from 0xffff - 0x20 - 40
            my_cksum = 0xffff - 0x20 - 0x40
            # Now we have the rest of the bytes, 32 of them less the 0x20 at the start, and the 2 bytes of checksum
            for i in range(28):
                my_cksum -= byte_data[i]

            values = [0] * 14
            *values, cksum = struct.unpack("<HHHHHHHHHHHHHHH", self._buffer)
            if cksum == my_cksum:
                return values
            # 0x20, 0x40 can't appear bit packet. Neither checksum nor data can begin with 0x20 or 0x40


# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
        
    uart = UART(0, 115200, timeout=1000) # uart1 tx-pin 4, rx-pin 5
    ibus = ibus_interface(uart)
    while True:
        values = ibus.read()
        if values is not None:
            print(" ".join(str(x) for x in values))
