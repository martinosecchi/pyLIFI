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
		for b in msg:
			self.arduino.write(bytearray(b)) #send 1 byte at a time, as chars
		self.arduino.write(ETX)
	def check(self):
		return self.arduino.readline()

	def run(self):
		while(not self.do_exit.isSet()):
			try:
				msg = self.queue.get(timeout=1)
			except Queue.Empty:
				pass
			else:
				# msg = self.encoded(msg)
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
			tx.send("01"*1000)
		elif cmd == 'stx':
			tx.arduino.write(STX)
		else:
			tx.send(cmd)

	tx.stop()

if __name__ == '__main__':
	main()
		 