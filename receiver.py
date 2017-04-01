#!/usr/bin/python
from lifiRx import lifiRx
from classify import LiFiClassifierLight
import sys
from collections import deque

def main():
	STX = "1010101010100110" # manchester for \x02
	ETX = "1010101010100101" # manchester for \x03
	rx = lifiRx()
	rx.start()

	args = {'epsilon':2}
	classifier = LiFiClassifierLight(args)
	buff16 = deque([0]*16, 16)
	maxlen = 16
	len3bytes = 3 * 8 * 2
	started = False
	ended = False
	pdu = ''
	i = 0
	print 'starting..'
	try:
		while not rx.do_exit.isSet():
			line = rx.getline()
			if line:
				try: 
					time, value = line.split(" ")
					bit = classifier.feed(float(time), float(value))
				except:
					continue
				if bit: # a prediction of 1 or more bits
					# offset = len(buff16) - maxlen + 1
					# if offset > 0:
					# 	buff16 = buff16[offset:] # becomes of length maxlen-1, ready for the new
					
					buff16.append(bit)
					cmd = reduce(lambda x,y: x+y, buff16)
					sys.stdout.write("%20s\r"% cmd)
					sys.stdout.flush()
					if started and not ended and (i == len3bytes or ETX in cmd):
						ended = True
						started = False
						i = 0
						print 'pdu found:', pdu
						pdu = ''
					elif started and not ended:
						i += 1
						pdu += bit
					elif not started and STX in cmd:
						print 'STX motherfuckers !'
						started = True
						ended = False
						i = 0
					

	except KeyboardInterrupt:
		print 'stopping..'
		rx.stop()
	# except Exception as e:
	# 	print e
	
	if not rx.stopped:
		rx.stop()
# go trhough rx.queue and check for stx
# if stx hits, go through the next 3 bytes (3 * 2 * 8 pred values), or until you get etx
# so scan etx as well in the meantime
# then reconstruct
# now, scanning for stx will produce delays, I should try to keep it as fast as I can

if __name__ == '__main__':
	main()