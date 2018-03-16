import trax_test
import Adafruit_BBIO.UART as UART
import serial

UART.setup("UART5")
ser = serial.Serial(port = "/dev/ttyO5", baudrate = 38400, timeout = 5)
ser.close()
ser.open()

t = trax_test.trax(ser)

version = t.get_version()
print "Firmware Ver: " + str(version)