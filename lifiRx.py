#!/usr/bin/python
import threading
import time
import serial
import datetime
import Queue

STX = "1010101010100110" #bytearray([2])
ETX = "1010101010100101" #bytearray([3])
rx_addr = '/dev/cu.usbmodem1411' #Yun

def now():
	return datetime.datetime.now()

def seconds(start):
	return (now() - start).total_seconds()


class lifiRx(threading.Thread):

	def __init__(self, buff=True, addr=rx_addr, write=False):
		super(lifiRx, self).__init__()
		self.serial_addr = addr
		self.do_exit = threading.Event()
		self.arduino = None
		self.f = None
		self.do_write = write
		self.do_buffer = buff
		self.queue = Queue.Queue()
		self.stopped = False

	def connect(self):
		try:
			self.arduino = serial.Serial(self.serial_addr, 9600, timeout=1)
		except serial.SerialException, AttributeError:
			print 'could not connect, rx closing'
			self.stop()

	def start(self):
		try:
			self.arduino = serial.Serial(self.serial_addr, 9600, timeout=1)
		except serial.SerialException, AttributeError:
			print 'could not connect, rx closing'
			self.stop()
		time.sleep(1)
		super(lifiRx, self).start()

	def stop(self):
		print 'closing rx'
		self.do_exit.set()
		time.sleep(1)
		if self.f:
			self.f.close()
		if self.arduino:
			self.arduino.close()
		self.stopped = True

	def read(self):
		try:
			return self.arduino.read()
		except serial.SerialException, AttributeError:
			return None

	def readline(self):
		try:
			return self.arduino.readline()
		except serial.SerialException, AttributeError:
			return None

	def getbuffered(self):
		try:
			return self.queue.get_nowait()
		except Queue.Empty:
			return None

	def run(self):
		if self.do_write:
			self.f = open("sample.txt", "w+")
		print 'lifiRx waiting for sensory data..'
		try:
			while not self.do_exit.isSet() and not self.arduino.readline():
				pass
		except serial.SerialException, AttributeError:
			print 'lifiRx problem when testing reception'
			self.stop()
		print 'lifiRx receiving'
		while not self.do_exit.isSet():
			l = None
			try:
				l = self.arduino.readline()
			except serial.SerialException:
				print e
				
			if l :
				if self.do_write:
					self.f.write(l)
				if self.do_buffer: 
					self.queue.put(l)

		
def main():
	global rx_addr
	rx = lifiRx(buff=False, write=True)
	rx.start()
	cmd = ''
	while cmd != 'stop':
		cmd = raw_input('type stop to stop:')
	rx.stop()

if __name__ == '__main__':
	main()
		