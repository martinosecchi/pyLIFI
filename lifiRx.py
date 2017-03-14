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
		self.arduino.readline() # skip first, usually it's partial
		while not self.do_exit.isSet():
			l = None
			try:
				l = self.arduino.readline()
			except:
				pass
			if l and self.do_write:
				# print l,
				# self.f.write(l)
				self.f.write(l)

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
		