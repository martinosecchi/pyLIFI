#!/usr/bin/python
from lifiRx import lifiRx
from classify import LiFiClassifierLight, manchester
import sys
from collections import deque
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner


def main():
	STX = "1010101010100110" # manchester for \x02
	ETX = "1010101010100101" # manchester for \x03
	commands = {}
	commands['up'] = manchester('up')
	commands['down'] = manchester('do')
	commands['left'] = manchester('le')
	commands['right'] = manchester('ri')
	scores = {}
	rx = lifiRx(buff=False, write=False)
	rx.connect() # not starting the thread, just using the object to read

	args = {'epsilon':2}
	classifier = LiFiClassifierLight(args)
	buff16 = deque(['0']*16, 16)
	maxlen = 16
	len3bytes = 3 * 8 * 2 # =48 for manchester coding
	mismatches_prob = 6 # how many bits could I have skipped out of 3 bytes? arbitrary for now
	started = False
	ended = False
	pdu = ''
	i = 0
	bit = None
	stop = False
	print 'starting..'
	try:
		while not stop:
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
					# sys.stdout.write(" %100s "% cmd)
					if started and not ended and (i >= len3bytes or (ETX in cmd and i >= len3bytes - mismatches_prob)):
						# if i >= len3bytes:
						# 	print 'truncated',
						# else:
						# 	print 'ETX', 
						ended = True
						started = False
						i = 0
						print 'pdu found:', pdu, manch_to_bin(pdu)
						for c in commands:
							scores[score(pdu,commands[c] + ETX)] = c
						print scores
						print scores[max(scores)], '                                       '
						scores = {}
						pdu = ''
					elif started and not ended:
						i += len(bit)
						pdu += bit
					elif not started and STX in cmd:
						# print ''
						# print 'STX'
						started = True
						ended = False
						i = 0
				sys.stdout.write("\r")
				sys.stdout.flush()

	except KeyboardInterrupt:
			stop = True
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

def score(a, b):
	a = Sequence(list(a))
	b = Sequence(list(b))
	voc = Vocabulary()
	aEncoded = voc.encodeSequence(a)
	bEncoded = voc.encodeSequence(b)

	scoring = SimpleScoring(1, -4) # match, mismatch
	aligner = GlobalSequenceAligner(scoring, -1) # score, gap score
	return aligner.align(aEncoded, bEncoded, backtrace=False)

def manch_to_bin(manch):
	binary = ''
	for i in range(0, len(manch), 2):
		if i+1 >= len(manch):
			binary += '.'
			break
		if manch[i] + manch[i+1] == '01':
			binary += '1'
		elif manch[i] + manch[i+1] == '10':
			binary += '0'
		else:
			binary += '-'
	return binary


if __name__ == '__main__':
	main()