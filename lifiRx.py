#!/usr/bin/python
import threading
import time
import serial
import datetime

STX = bytearray([2])
ETX = bytearray([3])
rx_addr = '/dev/cu.usbmodem1411' #Yun

def now():
	return datetime.datetime.now()

def seconds(start):
	return (now() - start).total_seconds()


class lifiRx(threading.Thread):

	def __init__(self, addr, do_write=True):
		super(lifiRx, self).__init__()
		self.serial_addr = addr
		self.do_exit = threading.Event()
		self.arduino = None
		self.f = None
		self.do_write = do_write

	def start(self):
		try:
			self.arduino = serial.Serial(self.serial_addr, 9600, timeout=1)
		except:
			print 'could not connect, rx closing'
			self.stop()
		time.sleep(1)
		super(lifiRx, self).start()

	def stop(self):
		self.do_exit.set()
		time.sleep(1)
		if self.f:
			self.f.close()
		if self.arduino:
			self.arduino.close()

	def run(self):
		if self.do_write:
			self.f = open("sample.txt", "w+")
			start = now()
		#skip until first, the set prev as the value
		prev = None
		while not prev:
			try:
				prev = self.arduino.readline()
			except:
				pass
		prev = float(prev.split(" ")[1])

		while not self.do_exit.isSet():
			l = None
			value = None
			try:
				l = self.arduino.readline()
				value = float(l.split(" ")[1])
				time = l.split(" ")[0]
			except:
				pass
			if l and self.do_write:
				# print l,
				# self.f.write(l)
				value = (value+prev)/2
				self.f.write( time + " " + str(value) + "\n" )
				# self.f.write( time + " " + str(value - prev) + "\n") # differantial signal
			if value:
				prev = value

def main():
	global rx_addr
	rx = lifiRx(rx_addr)
	rx.start()
	cmd = ''
	while cmd != 'stop':
		cmd = raw_input('type stop to stop:')
	rx.stop()

if __name__ == '__main__':
	main()
		