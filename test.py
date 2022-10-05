# Test du port série
from periphery import Serial
test_string = "Je teste le port série 1 2 3 4 5"
byte = bytes (test_string, 'utf-8')
port = "/dev/ttyS0"

serialPort = Serial(port, 9600)
print ("Port Série ", port, " ouvert pour le test :")
bytes_sent = serialPort.write(byte)
print (byte_sent)
print ("Envoyé ", bytes_sent, " octets")
loopback = serialPort.read(bytes_sent, timeout = 0.5)
print (loopback.decode('utf-8'))
if loopback == byte:
  print ("Reçu ", len(loopback), "octets identiques. Le port", port, "fonctionne bien ! \n")
else:
  print ("Reçu des données incorrectes : ", loopback, " sur le port série ", port, " bouclé \n")
serialPort.close()

