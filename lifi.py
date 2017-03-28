#!/usr/bin/python

import serial
import time as threadtime
import threading
import datetime
from lifiRx import lifiRx
from lifiTx import lifiTx
from classify import LiFiClassifier
import sys

tx_addr = '/dev/cu.usbserial-DA0147XE' #RedBoard
rx_addr = '/dev/cu.usbmodem1411' #Yun

def now():
	return datetime.datetime.now()

def main():
	tx = lifiTx(tx_addr)
	rx = lifiRx(rx_addr, False)
	tx.start()
	rx.start()
	rx.do_exit.set() # I'll just read from this thread instead
	try:
		msg = ''
		while msg != 'stop':
			classifier = None
			print 'new classifier'
			classifier = LiFiClassifier()
			classifier.epsilon = 2
			classifier.v = True
			classifier.result = ''
			msg = raw_input("type 'stop' to stop: ")
			if msg == 'stop':
				break
			tx.send(msg)
			start = now()
			print 'collecting'
			prev = None
			timestart = None
			count = 0
			buff = None
			buff = []
			while (now() - start).total_seconds() <= 0.5: # about the time for hello world
				l = rx.read()
				if l:
					try:
						value = int(l.split(" ")[1])
						if (value >= 15):
							buff.append(l)
							count += 1
						else:
							sys.stdout.write('%d \r' % value )
							sys.stdout.flush()
					except:
						pass
				# 	value = float(l.split(" ")[1])
				# 	time = float(l.split(" ")[0])
				# 	if not prev:
				# 		prev = value
				# 		timestart = time
				# 		continue

				# 	# staying
				# 	if abs(value - prev) <= classifier.epsilon:
				# 		pass

				# 	#going down
				# 	elif value <= prev: 
				# 		if classifier.direction == classifier.up:
				# 			delta = int((time-timestart)*100)
				# 			classifier.seq += str(delta) + classifier.direction + classifier.down
				# 			classifier.predict(classifier.seq)
				# 			classifier.direction = classifier.down
				# 			timestart = time

				# 	# going up
				# 	elif value > prev: 
				# 		if classifier.direction == classifier.down:
				# 			delta = int((time-timestart)*100)
				# 			classifier.seq += str(delta) + classifier.direction + classifier.up
				# 			classifier.predict(classifier.seq)
				# 			classifier.direction = classifier.up
				# 			timestart = time

				# 	prev = value
				else:
					print 'missed smthg'
			# delta = int((time-timestart)*100)
			# classifier.seq += str(delta) + classifier.direction + classifier.direction
			# classifier.predict(classifier.seq)
			if len(buff) > 0:
				print 'found %d values' % count,'comparing..'
				classifier.process(buff)
				fn = 'temp.txt'
				print 'storing sample in %s..'%fn
				store(buff, fn)
				if classifier.result:
					# classifier.result = cut_zeroes(classifier.result)
					# print "I read\n", classifier.result
					# print "it should be\n", manchester(msg)
					# print classifier.result in manchester(msg)
					classifier.compare(intended=msg, v=True)
			else:
				print 'empty'
				if rx.arduino:
					print rx.arduino.closed
					print rx.arduino.readline()
		threadtime.sleep(1)
	except Exception as e:
		print e.message
	finally:
		tx.stop()
		rx.stop()

def store(buff, fn):
	f = open(fn, 'w+')
	for l in buff:
		f.write(l)
	f.close()

def manchester(string):
	s = ""
	for c in bytearray(string):
		for i in range(7,-1,-1):
			s +=  "01" if (c & (1 << i)) else "10"
	return s;

def cut_zeroes(res):
	i = 0
	while res[i] == '0' and i+1 < len(res):
		i+=1
	return res[i:]

if __name__ == '__main__':
	main()