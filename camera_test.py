#test for the camera connection
from periphery import Serial
from time import sleep
#test_string = "Je teste le port série 1 2 3 4 5"
#byte = bytes (test_string, 'utf-8')
port = "/dev/ttyS1"

serialPort = Serial(port, 9600)
print ("Port Série ", port, " ouvert pour le test :")
#bytes_sent = serialPort.write(byte)
PowerOff = bytearray.fromhex("8101040003ff")
PowerOn = bytearray.fromhex("8101040002ff")
serialPort.write(PowerOff)
sleep(2)
serialPort.write(PowerOn)
                            
loopback = serialPort.read(128, timeout = 0.5)

print (loopback.decode('utf-8'))

serialPort.close()
