#!/usr/bin/python

import serial
import time
import threading
from lifiRx import lifiRx
from lifiTx import lifiTx

tx_addr = '/dev/cu.usbserial-DA0147XE' #RedBoard
rx_addr = '/dev/cu.usbmodem1411' #Yun

def main():
	tx = lifiTx(tx_addr)
	rx = lifiRx(rx_addr, True)
	tx.start()
	rx.start()
	try:
		msg = ''
		while msg != 'close':
			msg = raw_input("type 'close' to stop: ")
			# tx.send(msg)
		print 'closing'
		time.sleep(1)
	except:
		tx.stop()
		rx.stop()
	finally:
		tx.stop()
		rx.stop()

if __name__ == '__main__':
	main()