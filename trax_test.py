#!/usr/bin/env python2

import sys
import struct
import signal
import math
import binascii
import serial
import time
import crc16
import logging
import Adafruit_BBIO.GPIO as GPIO
import Adafruit_BBIO.UART as UART

# frameID
kGetModInfo				= 0x01
kGetModInfoResp			= 0x02
kSetDataComponents		= 0x03
kGetData				= 0x04
kGetDataResp			= 0x05
kSetConfig				= 0x06
kGetConfig				= 0x07
kGetConfigResp			= 0x08
kSave					= 0x09
kStartCal				= 0x0A
kStopCal				= 0x0B
kSetFIRFilters			= 0x0C
kGetFIRFilters			= 0x0D
kGetFIRFiltersResp		= 0x0E
kPowerDown				= 0x0F
kSaveDone				= 0x10
kUserCalSampleCount		= 0x11
kUserCalScore			= 0x12
kSetConfigDone			= 0x13
kSetFIRFiltersDone		= 0x14
kStartContinuousMode	= 0x15
kStopContinuousMode		= 0x16
kPowerUpDone			= 0x17
kSetAcqParams			= 0x18
kGetAcqParams			= 0x19
kSetAcqParamsDone		= 0x1A
kSetAcqParamsResp		= 0x1B
kPowerDownDone			= 0x1C
kFactoryMageCoeff		= 0x1D
kFactoryMageCoeffDone	= 0x1E
kTakeUserCalSample		= 0x1F
kFactoryAccelCoeff		= 0x24
kFactoryAccelCoeffDone	= 0x25
kSetFunctionalMode		= 0x4F
kGetFunctionalMode		= 0x50
kGetFunctionalModeResp	= 0x51
kSetResetRef			= 0x6E
kSetMagTruthMethod		= 0x77
kGetMagTruthMethod		= 0x78
kGetMagTruthMethodResp	= 0x79

# configID
kDeclination			= 1
kTrueNorth				= 2
kMountingRef			= 10
kUserCalNumPoints		= 12
kUserCalAutoSampling	= 13
kHPRDuringCal			= 16

logger = logging.getLogger(__name__)

class trax(object):
	def __init__(self, port=None, timeout=5):
		if port is not None:
		# Use serial communication if serial_port name is provided.
		# Open the serial port at 38400 baud, 8N1.  Add a 5 second timeout
		# to prevent hanging if device is disconnected.
		self._serial = serial.Serial(port, 38400, timeout)

	def _serial_send(self, command, ack=True, max_attempts=5):
		# Send a serial command and automatically handle if it needs to be resent
		# because of a bus error.  If ack is True then an ackowledgement is
		# expected and only up to the maximum specified attempts will be made
		# to get a good acknowledgement (default is 5).  If ack is False then
		# no acknowledgement is expected (like when resetting the device).
		attempts = 0
		while True:
			# Flush any pending received data to get into a clean state.
			self._serial.flushInput()
			# Send the data.
			self._serial.write(command)
			logger.debug('Serial send: 0x{0}'.format(binascii.hexlify(command)))
			# Stop if no acknowledgment is expected.
			if not ack:
				return
			# Read acknowledgement response (2 bytes).
			resp = bytearray(self._serial.read(2))
			logger.debug('Serial receive: 0x{0}'.format(binascii.hexlify(resp)))
			if resp is None or len(resp) != 2:
				raise RuntimeError('Timeout waiting for serial acknowledge, is the BNO055 connected?')
			# Stop if there's no bus error (0xEE07 response) and return response bytes.
			if not (resp[0] == 0xEE and resp[1] == 0x07):
				return resp
			# Else there was a bus error so resend, as recommended in UART app
			# note at:
			#   http://ae-bst.resource.bosch.com/media/products/dokumente/bno055/BST-BNO055-AN012-00.pdf
			attempts += 1
			if attempts >=  max_attempts:
				raise RuntimeError('Exceeded maximum attempts to acknowledge serial command without bus error!')

	def _write_bytes(self, address, data, ack=True):
		# Build and send serial register write command.
		command = bytearray(4+len(data))
		command[0] = 0xAA  # Start byte
		command[1] = 0x00  # Write
		command[2] = address & 0xFF
		command[3] = len(data) & 0xFF
		command[4:] = map(lambda x: x & 0xFF, data)
		resp = self._serial_send(command, ack=ack)
		# Verify register write succeeded if there was an acknowledgement.
		if resp[0] != 0xEE and resp[1] != 0x01:
			raise RuntimeError('Register write error: 0x{0}'.format(binascii.hexlify(resp)))

	def _write_byte(self, address, value, ack=True):
		# Write an 8-bit value to the provided register address.  If ack is True
		# then expect an acknowledgement in serial mode, otherwise ignore any
		# acknowledgement (necessary when resetting the device).
		# Build and send serial register write command.
		command = bytearray(5)
		command[0] = 0xAA  # Start byte
		command[1] = 0x00  # Write
		command[2] = address & 0xFF
		command[3] = 1     # Length (1 byte)
		command[4] = value & 0xFF
		resp = self._serial_send(command, ack=ack)
		# Verify register write succeeded if there was an acknowledgement.
		if ack and resp[0] != 0xEE and resp[1] != 0x01:
			raise RuntimeError('Register write error: 0x{0}'.format(binascii.hexlify(resp)))

	def _read_bytes(self, address, length):
		# Build and send serial register read command.
		command = bytearray(4)
		command[0] = 0xAA  # Start byte
		command[1] = 0x01  # Read
		command[2] = address & 0xFF
		command[3] = length & 0xFF
		resp = self._serial_send(command)
		# Verify register read succeeded.
		if resp[0] != 0xBB:
			 raise RuntimeError('Register read error: 0x{0}'.format(binascii.hexlify(resp)))
		# Read the returned bytes.
		length = resp[1]
		resp = bytearray(self._serial.read(length))
		logger.debug('Received: 0x{0}'.format(binascii.hexlify(resp)))
		if resp is None or len(resp) != length:
			raise RuntimeError('Timeout waiting to read data, is the BNO055 connected?')
		return resp

	def _read_byte(self, address):
		return self._read_bytes(address, 1)[0]

	def _read_signed_byte(self, address):
		# Read an 8-bit signed value from the provided register address.
		data = self._read_byte(address)
		if data > 127:
			return data - 256
		else:
			return data

	def _config_mode(self):
		# Enter configuration mode.
		self.set_mode(kSetConfig)

	def _operation_mode(self):
		# Enter operation mode to read sensor data.
		self.set_mode(self._mode)

	def begin(self, mode=kStartContinuousMode):
		"""Initialize the Trax.  Must be called once before any other
        library functions.  Will return True if successfully initialized and False otherwise.
        """
		# Save the desired normal operation mode.
        self._mode = mode
		# Make sure we're in config mode
        self._config_mode()
        self._write_byte(kGetModInfo)
        # Check the chip ID
        version = self._read_byte(kGetModInfoResp)
		print ('Firmware Version:' + (version))
        logger.debug('Read chip ID: 0x{0:02X}'.format(version))

        # Set functional mode.
		''' mode = 0 for compass
            mode = 1 for ahrs '''
        self._write_byte(kSetFunctionalMode, 1)

        # Enter normal operation mode.
        self._operation_mode()
        return True

    def set_mode(self, mode):
        """Set acquisition mode to continuous or polled.
        """
        self._write_byte(kStartContinuousMode, mode & 0xFF)

        time.sleep(0.03)
