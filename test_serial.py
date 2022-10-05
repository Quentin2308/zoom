from periphery import Serial

# Open /dev/ttyUSB0 with baudrate 115200, and defaults of 8N1, no flow control
serial = Serial("/dev/ttyS0", 9600)

serial.write(b"Hello World!")

# Read up to 128 bytes with 500ms timeout
buf = serial.read(100, 2)
print("read {:d} bytes: {:s}".format(len(buf), buf.decode('utf-8')))

serial.close()
