import serial

s = serial.Serial('COM22', 9600,timeout=None, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)

s.write("hello")