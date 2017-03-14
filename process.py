#!/usr/bin/python
import sys
import subprocess
import getopt
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

def help():
	print 'process the signal (manual reading)'
	print 'options:'
	print ' -i: or --interval=  interval of interesting part (time value)'
	print ' -f: or --file= 		file to read (sample.txt)'
	print ' -w: or --write= 	output file (processed.txt)'
	print ' --epsilon= 			variation considered noise'

def main(argv):
	# read arguments and set variables
	samplefile = "sample.txt"
	processedfile = None
	start = 0
	end = ''
	epsilon = 6

	opts, args = getopt.getopt(argv, 'hi:f:w:', ['interval=', 'file=', 'write=', 'epsilon='])

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
		elif opt == '--epsilon':
			epsilon = int(arg)

	digital(samplefile, processedfile, start, end, epsilon)
	# process(samplefile, processedfile, start, end, epsilon)

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

def digital(samplefile, processedfile, start, end, epsilon):
	# naive version, look only at trend, don't count the things before
	
	if processedfile is None:
		# processedfile = "digital" + str(epsilon) + ".txt"
		processedfile = "processed.txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	fw.write("# digital " + str(epsilon) + " s: " + str(start) + " e: " + str(end) + "\n")
	# up = '110'
	# down = '80'
	# up = '70'
	# down = '30'
	up = '50'
	down = '25' 
	direction = down
	prev = int(lines[0].split(" ")[1])

	if not end:
		end = float(lines[-1].split(" ")[0])

	for l in lines:
		value = int(l.split(" ")[1])
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

# def process(samplefile, processedfile, start, end, epsilon):
# 	# slightly better for a specific case, keep a buffer and count, this way
# 	# it accounts for random peaks
# 	# used for 2 ms transmission rate
# 	if processedfile is None:
# 		processedfile = 'processed.txt'
# 	f = open(samplefile, 'r')
# 	lines = f.readlines()
# 	f.close()
# 	fw = open(processedfile, 'w+')
# 	up = '60'
# 	down = '30'
# 	direction = down
# 	buff = []
# 	res = ''
# 	amount = 0

# 	prev = int(lines[0].split(" ")[1])

# 	if not end:
# 		end = float(lines[-1].split(" ")[0])

# 	for l in lines:
	
# 		value = int(l.split(" ")[1])
# 		time = l.split(" ")[0]

# 		if time < float(start):
# 			continue
# 		elif time > float(end):
# 			break

# 		if abs(value - prev) <= epsilon: #stay
# 			buff.append(direction)

# 		elif value <= prev: #down

# 			if direction != down:
# 				if len(buff) <= 2: # noise, probably
# 					continue

# 				if len(buff) > 12:
# 					res += '11'
# 					amount = 25
# 				else:
# 					res+='1'
# 					amount = 20

# 				buff = []
# 			direction = down
# 			buff.append(direction)

# 		else: #up

# 			if direction != up:
# 				if len(buff) <= 2: # noise, probably
# 					continue

# 				if len(buff) > 12:
# 					res += '00'
# 					amount = 25
# 				else:
# 					res += '0'
# 					amount = 20

# 				buff = []
# 			direction = up
# 			buff.append(direction)
			
# 		fw.write(time + " " + direction + " " + str(amount) + "\n")
# 		amount = 0
# 		prev = value

# 	fw.close()
# 	compare(res)

if __name__ == '__main__':
	# for i in range(1,7):
	# 	main([i])
	main(sys.argv[1:])
















