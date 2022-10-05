#test for the camera connection
from periphery import Serial
#test_string = "Je teste le port série 1 2 3 4 5"
#byte = bytes (test_string, 'utf-8')
port = "/dev/ttyS1"

serialPort = Serial(port, 9600)
print ("Port Série ", port, " ouvert pour le test :")
#bytes_sent = serialPort.write(byte)

loopback = serialPort.read(128, timeout = 0.5)

print (loopback.decode('utf-8'))

serialPort.close()
