#!/usr/bin/python
import sys
import getopt
import math
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner


class LiFiClassifier(object):
	def __init__(self, args={}):
		self.labels = ['1', '0', '11', '00']
		# the difference between two subsequent values is sonsidered noise
		# below the epsilon value (default 4)
		self.epsilon = args['epsilon'] if args.has_key('epsilon') else None
		self.up = 'u'
		self.down = 'd'
		self.direction = self.down
		self.seq = self.direction
		self.result = ''
		self.start = args['start'] if args.has_key('start') else 0
		self.end = args['end'] if args.has_key('end') else None
		self.intended = 'hello world'
		self.v = False

	def predict(self, wndw):
		# wndw is a string [dir start][timedelta][dir][dir end]
		# ex: 'd300ud' -> d,u,u,u,d
		# timedelta of 100 is 1 ms

		if self.v:
			print wndw,

		pred = '-'
		start = wndw[0]
		end = wndw[-1]
		wndw = wndw[1:-1]
		delta = int(''.join(filter(str.isdigit,wndw)))
		mid = wndw[-1]
		isdoubleafter = 390
		issingle = 180

		if mid == start or mid == end:
			delta+=100

		if self.v:
			print delta, 

		if delta >= isdoubleafter:
			# pred = '11' if mid == self.up else '00'
			pred = '1'*(delta/issingle) if mid == self.up else '0'*(delta/issingle)
		else:
			pred = '1' if mid == self.up else '0'

		if self.v:
			print pred
		
		self.result += pred
		self.size = 1
		self.seq = self.direction

	def process(self, lines):
		if not self.end:
			self.end = int(lines[-1].split(" ")[0])
		prev = float(lines[0].split(" ")[1])
		timestart = float(lines[0].split(" ")[0])

		if self.epsilon is None:
			self.preprocess(lines, 100)

		print 'EPSILON:',self.epsilon

		for l in lines[1:]:
			value = float(l.split(" ")[1])
			time = float(l.split(" ")[0])

			if time < float(self.start):
				prev = value
				timestart = time
				continue
			elif float(time) >= float(self.end):
				break

			# staying
			if abs(value - prev) <= self.epsilon:
				pass

			#going down
			elif value <= prev: 
				if self.direction == self.up:
					delta = int((time-timestart)*100)
					self.seq += str(delta) + self.direction + self.down
					self.predict(self.seq)
					self.direction = self.down
					timestart = time

			# going up
			elif value > prev: 
				if self.direction == self.down:
					delta = int((time-timestart)*100)
					self.seq += str(delta) + self.direction + self.up
					self.predict(self.seq)
					self.direction = self.up
					timestart = time

			prev = value

		delta = int((time-timestart)*100)
		self.seq += str(delta) + self.direction + self.direction
		self.predict(self.seq)


	def preprocess(self, lines, N):
		lines = lines[1:N+1]
		if self.v:
			print 'first', lines[0], 'last', lines[-1]
		avg = get_avg(lines)
		variance = get_variance(lines, avg)
		stddev = get_std_dev(variance)
		# if self.v:
		print avg, variance, stddev
		self.epsilon = stddev

	def compare(self, res):

		intended = manchester(self.intended)
		if self.v:
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

		scoring = SimpleScoring(1, -1) # match, mismatch 2, -1
		aligner = GlobalSequenceAligner(scoring, -1) # score, gap score -2
		score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

		for encoded in encodeds:
		    alignment = v.decodeSequenceAlignment(encoded)
		    if self.v:
				print alignment
		    print 'Percent identity:', alignment.percentIdentity()
		    print

def get_avg(lines):
	# the average value
	avg = 0.0 
	for l in lines:
		val = float(l.split(" ")[1])
		avg += val
	avg = avg / (len(lines))
	return avg

def get_std_dev(variance):
	return math.sqrt(variance)

def get_variance(lines, avg):
	s = 0.0 
	prev = float(lines[0].split(" ")[1])
	for l in lines[1:]:
		curr = float(l.split(" ")[1])
		s += math.pow((curr - prev) - avg, 2)
		prev = curr
	return s / (len(lines)-1.0)

def cut_zeroes(res):
	i = 0
	while res[i] == '0' and i+1 < len(res):
		i+=1
	return res[i:]

def manchester(string):
	s = ""
	for c in bytearray(string):
		for i in range(7,-1,-1):
			s +=  "01" if (c & (1 << i)) else "10"
	return s;



def help():
	print 'use LiFiClassifier to predict lifi transmission stored in a file as "timestamp value" from the sensor'
	print 'usage:'
	print '-i to specify a time interval for prediction as start:finish'
	print '-f for the file where to read from'
	print '-e to specify the noise factor'
	print 'if epsilon is not specified, it will be found through preprocessing phase in rest mode'
	print '-r to specifiy the result to compare the predicition with (deafaults to hello world)'
	print '-v for verbose output (no argument)'

def main(argv):

	samplefile = "sample.txt"  #"sample0.txt" #original helloworld
	model = LiFiClassifier()

	opts, args = getopt.getopt(argv, 'hi:f:r:e:v', ['interval=', 'file=', 'epsilon=', 'result='])

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-i' or opt == '--interval':
			model.start = int(arg.split(":")[0])
			model.end = int(arg.split(":")[1])
		elif opt == '-f' or opt == '--file':
			samplefile = arg
		elif opt == '-e' or opt == '--epsilon':
			model.epsilon = int(arg)
		elif opt == '-r' or opt == '--result':
			model.intended = arg
		elif opt == '-v':
			model.v = True

	print 'FILE:',samplefile
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	# model.find_epsilon(lines[1:102])
	# model.process(lines[2100:2600]) # sample0.txt
	model.process(lines[2:]) #first line sometimes a comment, second might be truncated
	print model.compare(model.result)
	

if __name__ == '__main__':
	main(sys.argv[1:])