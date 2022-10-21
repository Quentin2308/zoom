#test for the camera connection
from periphery import Serial
from time import sleep

port = "/dev/ttyS1"

inquiry = bytearray.fromhex("883001FF")
toto3 = inquiry[0:23]
print (toto3)
toto4 = int.from_bytes(toto3, byteorder="big") 
#print (toto4)
toto5 = bin(toto4)[2::]
#print (toto5)
#print (len(toto5))
toto6 = ba.bitarray(toto5)

serialPort = Serial(port, 9600, databits=8, stopbits=1)
print ("Port Série ", port, " ouvert pour le test :")
#sequenceNumber = 1

print(inquiry)

bytes_sent = serialPort.write(inquiry)
# for general commands (payload type 0100), command should be bytes
#command = bytearray.fromhex("8101040003ff")

#length = len(inquiry).to_bytes(2, 'big')
#print ("longueur = ", length)

#command = b"\x01\x00" + length + sequenceNumber.to_bytes(4, 'big') + inquiry
#print(command)

serialPort.write(command)
#sequenceNumber += 1

#data = sendRawCommand(self.ip, command, skipCompletion=skipCompletion) # TODO: deal with udp packets getting lost and sequence number desyncing (see manual)
#PowerOff = bytearray.fromhex("8101040003ff")
#PowerOn = bytearray.fromhex("8101040002ff")
#serialPort.write(PowerOff)
#sleep(2)
#serialPort.write(PowerOn)
                            
loopback = serialPort.read(128, timeout = 0.5)
print (loopback)
print (loopback.decode('utf-8'))

serialPort.close()
