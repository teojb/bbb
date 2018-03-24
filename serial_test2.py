import serial

ser = serial.Serial('COM11', 9600,timeout=None, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS)
ser.isOpen()

print ser.portstr

x = ser.read(5) # It will be waiting till it receives data
print x

