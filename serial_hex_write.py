import struct
import serial
import binascii
from PyCRC.CRCCCITT import CRCCCITT

# def write_frame(self, frame, response=Nne):
    # writes a frame to the trax
    # frame is a list of byte values in decimal
    # the byte count and crc are both uint16 and
    # are transmitted in Big Endian.
    # Response is the frameID of the expected response packet

    # don't forget the byte count and crc (2 bytes each)
frame = (1,)
num_of_bytes = len(frame) + 4

byte_count = struct.pack(">H", num_of_bytes) # Big Endian
print '%s' % (byte_count)

byte_string = struct.pack("%dB" % len(frame), *frame)
print (byte_string)

# the checksum includes the bytecount
# crc = struct.pack(">H", self.CRCCCITT(byte_count + byte_string))
crc = struct.pack(">H", CRCCCITT().calculate(byte_count + byte_string))
print (crc)

print (byte_count + byte_string + crc)

    # self.port.write(byte_count + byte_string + crc)

    # if response is not None:
    #     f = self.read_frame()
    #     if ord(f[0]) != response:
    #         print "ERROR: expected frameID of %d but got %d" % (response, \
    #                                                             ord(f[0]))
    #         return False
    #     else:
    #         print "Successfully got response of frameID %d" % response,
    #         print "from request with frameID %d" % frame[0]

    # return True

# def read_frame(self):
    # returns one frame from without the byte count and checksum
    # by default the trax return data in Big Endian
#   byte_count_packet = self.read(2)
#     if byte_count_packet:  # only if it didn't timeout
#         byte_count = struct.unpack(">H", byte_count_packet)[0]
#         #print "Byte_count:", byte_count
#         # byte count includes 2 byte checksum and 2 byte byte count
#         frame = self.read(byte_count - 4)
#         checksum = struct.unpack(">H", self.read(2))[0]  # 2 byte checksum
#         our_checksum = self.checksum(byte_count_packet + frame)
#         if checksum != our_checksum:
#             print "Error: Checksum FAIL!"

#         return frame
#     else:
#         print "Timed out on byte count packet: no data received from TRAX"
#         sys.exit(0)

# def read(self, n0):
#     if not n
#         return self.port.read()
#     else:
#         return self.port.read(n)

# ser = serial.Serial(
#     port='/dev/ttyO5',
#     baudrate=38400,
#     parity=serial.PARITY_NNE,
#     stopbits=serial.STOPBITS_ONE,
#     bytesize=serial.EIGHTBITS
# )

# ser.write('\x00\x05\x01\xEF\xD4')
# s = (ser.read(3))[2]
# s = ser.seek(2) #read 3rd byte
# print binascii.b2a(s) #convert bin to ascii


