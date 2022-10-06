#test for the camera connection
from periphery import Serial
from time import sleep
#test_string = "Je teste le port série 1 2 3 4 5"
#byte = bytes (test_string, 'utf-8')
port = "/dev/ttyS1"

serialPort = Serial(port, 9600)
print ("Port Série ", port, " ouvert pour le test :")
sequenceNumber = 1
#bytes_sent = serialPort.write(byte)
# for general commands (payload type 0100), command should be bytes
command = bytearray.fromhex("8101040003ff")
print(command)
length = len(command).to_bytes(2, 'big')
command = b"\x01\x00" + length + sequenceNumber.to_bytes(4, 'big') + command
print(command)
serialPort.write(command)
#data = sendRawCommand(self.ip, command, skipCompletion=skipCompletion) # TODO: deal with udp packets getting lost and sequence number desyncing (see manual)
sequenceNumber += 1



#PowerOff = bytearray.fromhex("8101040003ff")
#PowerOn = bytearray.fromhex("8101040002ff")
#serialPort.write(PowerOff)
#sleep(2)
#serialPort.write(PowerOn)
                            
loopback = serialPort.read(128, timeout = 0.5)
print (loopback)
print (loopback.decode('utf-8'))

serialPort.close()
