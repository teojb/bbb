import sys
import struct
import signal
import math
import binascii
import serial
import time
import crc16
from PyCRC.CRCCCITT import CRCCCITT
#import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART
#import shm

UART.setup("UART5")
UART.setup("UART2")
UART.setup("UART4")
UART.setup("UART1")

kGetModInfo				= 1 #0x01
kGetModInfoResp			= 0x02 #0x02
kPowerUpDone			= 0x17



class trax_ahrs:

	def __init__ (self, port):
	    self.port = serial.Serial(port="/dev/ttyO5", baudrate=38400, timeout=5, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
	    self.port.close()
	    self.port.open()

	# def write_frame(self, frame, response=None):
	# 	num_of_bytes = len(frame) + 4
	# 	byte_count = struct.pack(">H", num_of_bytes) # Big Endian
	# 	byte_string = struct.pack("%dB" % len(frame), *frame)
	# 	crc = struct.pack(">H", CRCCCITT().calculate(byte_count + byte_string))
	# 	self.port.write(byte_count + byte_string + crc)
	# 	#f = self.read_frame()

		#return True

	# def read_frame(self):
	# 	byte_count_packet = self.read(2)
	# 	if byte_count_packet:  # only if it didn't timeout
	# 		byte_count = struct.unpack(">H", byte_count_packet)[0]
	# 		frame = self.read(byte_count - 4)
	# 		checksum = struct.unpack(">H", self.read(2))[0]  # 2 byte checksum
	# 		our_checksum = self.checksum(byte_count_packet + frame)
	# 		if checksum != our_checksum:
	# 			print "Error: Checksum FAIL!"

	# 		return frame

	def read(self, n=0):
		if not n:
			return self.port.read()
		else:
			return self.port.read(n)

	def checksum(self, byte_string):
		return CRCCCITT.calculate(byte_string)

	def get_version(self):
		#self.write_frame((1,))
		#print str(b'\x00\x05'b'\x01'b'\xef\xd4')
		# self.port.write(b'\x00\x05'b'\x01'b'\xEF\xD4')
		self.port.write('\x00\x05\x01\xEF\xD4')
		# input = '000501EFD4'
		# self.port.write(input.decode("hex"))
		#self.port.write((bytes([0x00])+bytes([0x05])+bytes([0x01])+bytes([0xEF])+bytes([0xD4])))
		#print ("packet: %s%s%s" % (byte_count, byte_string, crc))
		# f = self.read_frame()
		f = self.read.port.read(11)
		print (f)
		#if ord(f[0]) == binascii.b2a_hex(kGetModInfoResp)
		# if ord(f[0]) == 02:
		# 	print "Got Response"
		# else:
		# 	print "No Response"
		# ModInfo = struct.unpack(">BII", f)
		# type = ModInfo[1]
		# revision = ModInfo[2]
		# print "Firmware Version: %d %d" % (type, revision)

ser = serial.Serial(port="/dev/ttyO5", baudrate=38400, timeout=5, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
ser.close()
ser.open()
t = trax_ahrs(ser)
t.get_version()
