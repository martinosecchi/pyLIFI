#!/usr/bin/python
import sys
import subprocess
import getopt
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

def help():
	print 'process the signal, help page'
	print 'values in parenthesis () are the default'
	print 'options:'
	print ' -i: or --interval=  interval of interesting part (time value)'
	print ' -f: or --file= 		file to read (sample.txt)'
	print ' -w: or --write= 	output file (processed.txt)'
	print ' -m: or --mode=		mode, filter f, differential d or process (p)'
	print ' -e or --epsilon= 	variation considered noise'
	print ' --ud= set up down as up:down'
	print 'in filter mode, epsilon will be the number of values used to average out each one'

def main(argv):
	# read arguments and set variables
	samplefile = "sample.txt"
	processedfile = None
	start = 0
	end = ''
	epsilon = 6
	mode = 'p'
	up = None
	down = None
	opts, args = getopt.getopt(argv, 'hi:f:w:m:e:', ['ud=', 'interval=', 'file=', 'write=', 'epsilon=', 'mode='])

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-i' or opt == '--interval':
			start = int(arg.split(":")[0])
			end = int(arg.split(":")[1])
		elif opt == '-f' or opt == '--file':
			samplefile = arg
		elif opt == '-w' or opt == '--write':
			processedfile = arg
		elif opt == '-e' or opt == '--epsilon':
			epsilon = int(arg)
		elif opt == '-m' or opt == '--mode':
			mode = arg
		elif opt == '--ud':
			up = arg.split(":")[0]
			down = arg.split(":")[1]

	if mode == 'p':
		digital(samplefile, processedfile, start, end, epsilon, up, down)
	elif mode == 'f':
		filterAVG(samplefile, processedfile, start, end, epsilon)
	elif mode == 'd':
		differential(samplefile, processedfile, start, end)

def digital(samplefile, processedfile, start, end, epsilon, up, down):
	# naive version, look only at trend, don't count the things before
	
	if processedfile is None:
		# processedfile = "digital" + str(epsilon) + ".txt"
		processedfile = "processed.txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	fw.write("# digital " + str(epsilon) + " s: " + str(start) + " e: " + str(end) + "\n")
	if up is None and down is None:
		# up = '110'
		# down = '80'
		# up = '70'
		# down = '30'
		up = '50'
		down = '25' 
	direction = down
	prev = float(lines[1].split(" ")[1])

	if not end:
		end = float(lines[-1].split(" ")[0])

	for l in lines[2:]:
		value = float(l.split(" ")[1])
		time = float(l.split(" ")[0])

		if time < float(start):
			sys.stdout.write('skip smaller\r')
			sys.stdout.flush()
			prev = value
			continue
		elif float(time) >= float(end):
			# print 'end reached', str(time), str(end), str(time >= end)
			break

		if abs(value - prev) <= epsilon: #difference is less than noise, stationary
			pass	
		elif value <= prev:
			direction = down
		else:
			direction = up
		fw.write(str(time) + " " + direction + "\n")
		prev = value
	fw.close()

def differential(samplefile, processedfile, start, end):
	if processedfile is None:
		processedfile = "differential.txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	fw.write("# differential  s: " + str(start) + " e: " + str(end) + "\n")

	prev = float(lines[1].split(" ")[1])

	if not end:
		end = float(lines[-1].split(" ")[0])

	for l in lines[2:]:
		value = float(l.split(" ")[1])
		time = float(l.split(" ")[0])

		if time < float(start):
			prev = value
			continue
		elif float(time) >= float(end):
			break

		fw.write(str(time) + " " + str((value - prev)) + "\n")
		prev = value
	fw.close()


def filterAVG(samplefile, processedfile, start, end, epsilon):
	print 'WARNING, this function is now included in lifiRX, thus processing here will be added on that'
	print 'WARNING, hardcoding epsilon to 2'
	epsilon = 2
	
	if processedfile is None:
		processedfile = "filtered" + str(epsilon) + ".txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	fw.write("# filtered " + str(epsilon) + " s: " + str(start) + " e: " + str(end) + "\n")

	
	prev = float(lines[1].split(" ")[1])

	if not end:
		end = float(lines[-1].split(" ")[0])

	for l in lines[2:]:
		value = float(l.split(" ")[1])
		time = float(l.split(" ")[0])

		if time < float(start):
			prev = value
			continue
		elif float(time) >= float(end):
			break

		fw.write(str(time) + " " + str((prev+value)/epsilon) + "\n")
		prev = value
	fw.close()

def cut_zeroes(res):
	i = 0
	while res[i] == '0':
		i+=1
	return res[i:]

def manchester(string):
	s = ""
	for c in bytearray(string):
		for i in range(7,-1,-1):
			s +=  "01" if (c & (1 << i)) else "10"
	return s;

def compare(res, intended='hello world'):

	intended = manchester(intended)
	print 
	print 'intended'
	print intended
	print 
	print 'result'
	print res
	print 
	
	a = Sequence(list(res))
	b = Sequence(list(intended))
	v = Vocabulary()
	aEncoded = v.encodeSequence(a)
	bEncoded = v.encodeSequence(b)

	# Create a scoring and align the sequences using global aligner.
	scoring = SimpleScoring(2, -1)
	aligner = GlobalSequenceAligner(scoring, -2)
	score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

	# Iterate over optimal alignments and print them.
	for encoded in encodeds:
	    alignment = v.decodeSequenceAlignment(encoded)
	    print alignment
	    print 'Alignment score:', alignment.score
	    print 'Percent identity:', alignment.percentIdentity()
	    print

if __name__ == '__main__':
	# for i in range(1,7):
	# 	main([i])
	main(sys.argv[1:])
















