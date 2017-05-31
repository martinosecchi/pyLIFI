#!/usr/bin/python
import threading
import time
import serial
import Queue

STX = bytearray([2])
ETX = bytearray([3])
tx_addr = '/dev/cu.usbserial-DA0147XE' #RedBoard


class lifiTx(threading.Thread):
	def __init__(self, address=tx_addr):
		super(lifiTx, self).__init__()
		self.arduino = None
		self.serial_addr = address
		self.do_exit = threading.Event()
		self.queue = Queue.Queue()

	def start(self):
		try:
			self.arduino = serial.Serial(self.serial_addr,9600, timeout=1)
		except:
			print 'could not connect, tx closing'
			self.stop()
		time.sleep(1)
		super(lifiTx, self).start()

	def stop(self):
		print 'closing tx'
		self.do_exit.set()
		time.sleep(1)
		if self.arduino and not self.arduino.closed:
			self.arduino.write(bytearray(['0']))
			self.arduino.close()

	def send(self, msg):
		self.queue.put(msg)

	def enlight(self, msg):
		self.arduino.write(STX)
		self.arduino.write(bytearray([len(msg)])) # send also length
		for b in msg:
			self.arduino.write(bytearray(b)) #send 1 char at a time, as bytes
		self.arduino.write(ETX)

		# allow ETX to get predicted by switching state one more time:
		self.arduino.write(bytearray('0'))
		self.arduino.write(bytearray('0')) # for good measure
		self.arduino.write(bytearray('1'))
	def check(self):
		return self.arduino.readline()

	def run(self):
		while(not self.do_exit.isSet()):
			try:
				msg = self.queue.get(timeout=1)
			except Queue.Empty:
				pass
			else:
				self.enlight(msg)

def main():
	# global tx_addr
	# tx = lifiTx(tx_addr)
	tx = lifiTx()
	tx.start()
	cmd = ''
	while cmd != 'stop':
		cmd = raw_input('waiting command:')
		if cmd == 'stop': 
			break
		elif cmd == 'check':
			print tx.check()
		elif cmd == "01":
			tx.arduino.write(bytearray("01"*1000))
		elif cmd == 'stx':
			tx.arduino.write(STX)
		elif cmd == '0':
			tx.arduino.write(bytearray('0'))
		elif cmd == '1':
			tx.arduino.write(bytearray('1'))
		elif cmd == '*':
			tx.arduino.write(bytearray('*'))
		elif cmd == '#':
			for i in range(8):
				tx.arduino.write(bytearray([0]))
				tx.arduino.write(bytearray([0]))
				tx.arduino.write(bytearray([0]))
				tx.arduino.write(bytearray('1'))
				time.sleep(0.5)
				tx.arduino.write(bytearray('0'))
				time.sleep(0.5)
		elif cmd == '-':
			for i in range(8):
				tx.arduino.write(bytearray('1'))
				time.sleep(0.2)
				tx.arduino.write(bytearray('0'))
				time.sleep(0.2)
		else:
			tx.send(cmd)

	tx.stop()

kbdInput = ''
finished = True
def main2():
	lastCmd = ''
	global kbdInput
	global finished
	tx = lifiTx()
	tx.start()

	def kbdListener():
		global kbdInput, finished
		kbdInput = raw_input()
		# print "maybe updating...the kbdInput variable is: {}".format(kbdInput)
		finished = True
	print "> ",
	while True:
		# print "kbdInput: {}".format(kbdInput)
		# print "lastCmd: {}".format(lastCmd)
		if lastCmd != kbdInput:
			print "Received new command", kbdInput
			lastCmd = kbdInput
			if lastCmd == 'stop':
				break
		if finished:
			finished = False
			listener = threading.Thread(target=kbdListener)
			listener.start()
		if lastCmd:
			print lastCmd
			tx.send(lastCmd)
		time.sleep(1)
	tx.stop()

if __name__ == '__main__':
	main2()
		 