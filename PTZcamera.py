import socket
import logging as log
from commands import *
from periphery import Serial
import time


log.basicConfig(format='%(asctime)s %(message)s')
log.addLevelName(5,"VERBOSE")
log.getLogger().setLevel("VERBOSE")

socket.setdefaulttimeout(3)

class Camera:
	
	sequenceNumber = 1 # starts at 1?
	panSpeed = 0x08 # reasonable default speed
	tiltSpeed = 0x08
	zoomSpeed = 0x02
	
	def __init__(self, name, ip, mac, netmask="255.255.255.0", gateway="0.0.0.0"):
		self.name = name
		self.ip = ip
		self.mac = mac # mac using dashes to seperate
		self.netmask = netmask
		self.gateway = gateway
		#self.resetSequenceNumber()
		
	def __str__(self):
		return f"{self.name}({self.mac}) {self.ip}"

	def setIP(self, ip=None, netmask=None, gateway=None, name=None):
		# name must be up to 8 alphanumeric characters (and blank)
		if not ip:
			ip = self.ip
		if not netmask:
			netmask = self.netmask
		if not gateway:
			gateway = self.gateway
		if not name:
			name = self.name
		command = (b"\x02MAC:"+bytes(self.mac, encoding="utf-8")+b"\xFFIPADR:"+bytes(ip, encoding="utf-8")+
					b"\xFFMASK:"+bytes(netmask, encoding="utf-8")+b"\xFFGATEWAY:"+bytes(gateway, encoding="utf-8")+
					b"\xFFNAME:"+bytes(name, encoding="utf-8")+b"\xFF\x03")
		#sock.sendto(command, (self.ip, 52380))
		sendRawCommand(self.ip, command, port=52380)

	def sendCommand(self, command, skipCompletion=False):
		# for general commands (payload type 0100), command should be bytes
		length = len(command).to_bytes(2, 'big')
		command = b"\x01\x00" + length + self.sequenceNumber.to_bytes(4, 'big') + command
		data = sendRawCommand(self.ip, command, skipCompletion=skipCompletion) # TODO: deal with udp packets getting lost and sequence number desyncing (see manual)
		self.sequenceNumber += 1
		return data

	def inquire(self, command):
		return self.sendCommand(command, skipCompletion=True) # no acknoledge message for a inquiry

	#def resetSequenceNumber(self):
		#self.sequenceNumber = 1
		#sendRawCommand(self.ip, bytearray.fromhex('02 00 00 01 00 00 00 01 01'), skipCompletion=True)

	def getZoomPos(self):
		data = self.inquire(Inquiry.ZoomPos)
		print((data[10] << 12) | (data[11] << 8) | (data[12] << 4) | data[13])
		return (data[10] << 12) | (data[11] << 8) | (data[12] << 4) | data[13]

	def setSpeed(self, zoomSpeed=-1):
		if zoomSpeed>0:
			self.zoomSpeed = zoomSpeed

	def home(self):
		self.sendCommand(Commands.PanTiltHome)
	def reset(self):
		self.sendCommand(Commands.PanTiltReset)
	def stop(self):
		self.sendCommand(Commands.PanTiltStop())
	def zoomIn(self):
		self.sendCommand(Commands.ZoomTeleVariable(self.zoomSpeed))
	def zoomOut(self):
		self.sendCommand(Commands.ZoomWideVariable(self.zoomSpeed))
	def zoomStop(self):
		self.sendCommand(Commands.ZoomStop)
	def zoomPos(self, pos):
		self.sendCommand(Commands.ZoomPos(pos))
	def storePreset(self, mem: int):
		if mem < 8:
			self.sendCommand(Commands.MemorySet(mem))
		else:
			raise IndexError("%d is not a valid memory preset 0-7" % (mem))
	def recallPreset(self, mem: int):
		if mem < 8:
			self.sendCommand(Commands.MemoryRecall(mem))
		else:
			raise IndexError("%d is not a valid memory preset 0-7" % (mem))

	def powerOn(self):
		self.sendCommand(Commands.PowerOn)
	def powerOff(self):
		self.sendCommand(Commands.PowerOff)


def sendRawCommand(ip, command, port=52381, skipCompletion=False):
	# this sends a command and waits for a response, note it does NOT calculate / use the sequence number
	# command should be a bytes object
	log.debug("Sending to %s: %r", ip, command)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.bind(("", port))
	s.sendto(command, (ip, port))

	def receive():
		data = s.recv(1024)
		log.log(5, "Received %r", data)
		if b"NAK" in data:
			log.error("Command failed with error: %r", data)
		if len(data) > 10:
			if data[8] == 0x90:
				# acknowledged / completion / error message
				if data[9] == 0x41:
					log.debug("Command acknowledged successfully")
				if data[9] == 0x51:
					log.debug("Command completed successfully")
				if (data[9] & 0xf0) == 0x60:
					log.error("Command failed with error: %r", data)
					error = {0x01: "Message length error", 0x02: "Syntax Error", 0x03: "Command buffer full", 0x04: "Command canceled", 0x05: "No socket", 0x41: "Command not executable"}
					log.error("Formatted: %s",error.get(data[10], "Unknown"))
		else:
			if data == b'\x02\x01\x00\x01\x00\x00\x00\x00\x01':
				log.debug("Successfully reset sequence number")
			else:
				log.error("Returned data was too short?")
		return data

	try:
		data = receive() # acknolwedge
		if skipCompletion:
			return data
		data = receive() # completion
		return data
	except socket.timeout:
		log.error("Sendrawcommand timeout to %s", ip)
		return None
	finally:
		s.close()

def discoverCameras():
	# UDP socket, enable broadcast, and socket reuse (hah if even that worked)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	s.settimeout(3)
	#port = Serial("/dev/ttyS1",9600)
	try:
		s.bind(("", 52381))

		discoverCmd = b"\x02ENQ:network\xFF\x33"
		log.debug("Sending discover...")
		s.sendto(discoverCmd, ('<broadcast>', 52381))
		cameras = []
		try:
			while True:
				raw, addr = s.recvfrom(1024)
				print("sent2 :" , raw)
				if raw == discoverCmd:
					continue
				data = raw.split(b'\xFF')
				name = data[7][5:].decode("utf-8")
				mac = data[0][5:].decode("utf-8")
				log.info("Found camera %s (%s) at IP %s", name, mac, addr[0])
				cameras.append(Camera(name, addr[0], mac))
		except socket.timeout:
			log.debug("End discover")
		if len(cameras) == 0:
			return None
		return cameras
	finally:
		s.close()

c = discoverCameras()

e = Camera("CAM1", "192.168.0.1", "")
print("camera 2 :", e)

d = Camera("CAM2", "192.168.0.13", "")
print("camera3 : ", d)

f = Camera("CAM3", "192.168.108.42", "")
print("camera3 : ", f)

#e.getZoomPos()
#d.getZoomPos()
f.getZoomPos()

#d.sendCommand(b"\x01\x00\x00\x06\x00\x00\x00\x01\x81\x01\x04\x00\x03\xff") 
#time.sleep(1)

#d.sendCommand(b"\x81\x01\x7e\x01\x18\x02\xff")
#c[0].setIP(name="LaurieC1")
#c[0].sendCommand(b"\x81\x01\x7e\x01\x5a\x02\xff") # lowest latency
#d.sendCommand(Commands.PanTiltUp())
#d.sendCommand(Commands.PanTiltAbs(0x3000,0,0x10,0x10))
#d.getPos()
