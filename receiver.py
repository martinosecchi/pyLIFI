#!/usr/bin/python
from lifiRx import lifiRx
from classify import LiFiClassifierLight
import sys
from collections import deque

def main():
	STX = "1010101010100110" # manchester for \x02
	ETX = "1010101010100101" # manchester for \x03
	rx = lifiRx(buff=False, write=False)
	rx.connect() # not starting the thread, just using the object to read

	args = {'epsilon':2}
	classifier = LiFiClassifierLight(args)
	buff16 = deque(['0']*16, 16)
	maxlen = 16
	len3bytes = 3 * 8 * 2
	started = False
	ended = False
	pdu = ''
	i = 0
	bit = None
	stop = False
	print 'starting..'
	while not stop:
		try:
			line = rx.readline() #rx.getbuffered()
			if line:
				try: 
					time, value = line.split(" ")
					sys.stdout.write("%10s %10s " % (time, value.rstrip('\n')))
					# sys.stdout.flush()
					bit = classifier.feed(float(time), float(value))
				except ValueError:
					bit = None

				if bit: # a prediction of 1 or more bits
					buff16.append(bit)
					cmd = reduce(lambda x,y: x+y, buff16)
					# sys.stdout.write(" %80s "% cmd)
					if started and not ended and (i >= len3bytes or ETX in cmd):
						if i >= len3bytes:
							print 'truncated',
						else:
							print 'ETX', 
						ended = True
						started = False
						i = 0
						print 'pdu found:', pdu
						pdu = ''
					elif started and not ended:
						i += len(bit)
						pdu += bit
					elif not started and STX in cmd:
						print 'STX'
						started = True
						ended = False
						i = 0
				sys.stdout.write("\r")
				sys.stdout.flush()

		except KeyboardInterrupt:
			stop = True
			break
		# except Exception as e:
		# 	print e

	print 'stopping..'
	
	if not rx.stopped:
		rx.stop()
# go trhough rx.queue and check for stx
# if stx hits, go through the next 3 bytes (3 * 2 * 8 pred values), or until you get etx
# so scan etx as well in the meantime
# then reconstruct
# now, scanning for stx will produce delays, I should try to keep it as fast as I can

def manch_to_bin(manc):
	

if __name__ == '__main__':
	main()