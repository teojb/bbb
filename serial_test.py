import Adafruit_BBIO.UART as UART
import serial

UART.setup("UART5")

ser = serial.Serial(port = "/dev/ttyO5", baudrate=9600)
ser.close()
ser.open()
if ser.isOpen():
	print "Serial is open!"
	ser.write("Hello World!")
ser.close()