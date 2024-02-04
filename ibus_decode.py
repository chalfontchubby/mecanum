from machine import UART
import struct 

def read_ibus():
    def decode_packet(data):
        # ibus packet is 32 bytes, but we already read the first 0x20 byte so
        # we only get 31 here.
        
        # (0x20), 0x40
        # 14*16 bitvalues, little endian
        # 16 bit checksum equal to 0xffff minus all bytes except the checksum
        values = [0] * 14
        byte_data = memoryview(data)
        
        # We can exit early if the first byte of the buffer isn't the 0x40 we expect
        if byte_data[0] != 0x40:
            return None
        
        # Checksum is 0xffff - every byte except the checksum itself.
        # We stripped the 0x20 off the front becore we got here, so we start counting doen from 0xffff - 0x20
        my_cksum = 0xffff - 0x20
        # Now we have the rest of the bytes, 32 of them less the 0x20 at the start, and the 2 bytes of checksum
        for i in range(29):
            my_cksum -= byte_data[i]

        b,*values,cksum = struct.unpack("<BHHHHHHHHHHHHHHH",data)
        #
        my_cksum = 0xffff - 0x20 - b - sum( (a&0xff) + (a>>8&0xff) for a in values)
        if b != 0x40 or cksum != my_cksum :
            print("Fail")
            return None
        return values



    while True:
        uart.readinto(buffer,1)
        if buffer[0] == 0x20:
            # We've seen a 0x20 - now slurp the next 31 bytes ino the buffer and decode those.
            # We don't process the 0x20, so have to remember to deal with it
            uart.readinto(buffer)

            values = decode_packet(buffer)
            if values is not None:
                return values
            

# If we run this file on it's own, then it runs the loop below.
# Otherwise we can just import it and get the function above
if __name__ == "__main__":
        
    start_byte=bytearray(1)
    buffer=bytearray(31)

    uart = UART(0, 115200, timeout=1000) # uart1 tx-pin 4, rx-pin 5
    while True:
        values = read_ibus()
        if values is not None:
            print(" ".join(str(x) for x in values))
