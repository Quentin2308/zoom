# Test du port série
from periphery import Serial
test_string = b"Je teste le port série 1 2 3 4 5"
port = "/dev/ttyS0"
try:
  serialPort = Serial(port, 9600)
  print ("Port Série ", port, " ouvert pour le test :")
  bytes_sent = serialPort.write(test_string)
  print ("Envoyé ", bytes_sent, " octets")
  loopback = serialPort.read(128,0.5)
  if loopback == test_string:
    print ("Reçu ", len(loopback), "octets identiques. Le port", port, "fonctionne bien ! \n")
  else:
    print ("Reçu des données incorrectes : ", loopback, " sur le port série ", port, " bouclé \n")
  serialPort.close()
except IOError:
  print ("Erreur sur ", port, "\n")
