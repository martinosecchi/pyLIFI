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

	def start(self):
		try:
			self.arduino = serial.Serial(self.serial_addr, 9600, timeout=1)
		except:
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
		except:
			return None

	def readline(self):
		try:
			return self.arduino.readline()
		except:
			return None

	def getline(self):
		try:
			return self.queue.get_nowait()
		except Queue.Empty:
			return None

	def run(self):
		if self.do_write:
			self.f = open("sample.txt", "w+")
			start = now()
		#skip until first, the set prev as the value
		print 'lifiRx, waiting first value..'
		prev = None
		while not prev and not self.do_exit.isSet():
			try:
				prev = self.arduino.readline()
			except:
				pass
		try:
			prev = float(prev.split(" ")[1])
		except:
			print " couldn't read, prev not set"
			return
		print 'lifiRx, receiving'
		while not self.do_exit.isSet():
			l = None
			value = None
			try:
				l = self.arduino.readline()
				value = float(l.split(" ")[1])
				time = l.split(" ")[0]
			except:
				pass

			if l and value:
				value = (value+prev)/2
				if self.do_write:
					self.f.write( time + " " + str(value) + "\n" )
					# self.f.write( time + " " + str(value - prev) + "\n") # differantial signal
				if self.do_buffer: 
					self.queue.put(time + " " + str(value))
			if value:
				prev = value
		
def main():
	global rx_addr
	rx = lifiRx(False, rx_addr, True)
	rx.start()
	cmd = ''
	while cmd != 'stop':
		cmd = raw_input('type stop to stop:')
	rx.stop()

if __name__ == '__main__':
	main()
		