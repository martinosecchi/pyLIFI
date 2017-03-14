#!/usr/bin/python
import sys
import getopt
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner


class LiFiClassifier(object):
	def __init__(self, args={}):
		self.labels = ['1', '0', '11', '00']
		# the difference between two subsequent values is sonsidered noise
		# below the epsilon value (default 4)
		self.epsilon = args['epsilon'] if args.has_key('epsilon') else 4
		self.up = 'u'
		self.down = 'd'
		self.direction = self.down
		self.seq = self.direction
		self.result = ''
		self.start = args['start'] if args.has_key('start') else 0
		self.end = args['end'] if args.has_key('end') else None

	def predict(self, wndw):
		# wndw is a string [dir start][timedelta][dir][dir end]
		# ex: 'd300ud' -> d,u,u,u,d
		# timedelta of 100 is 1 ms

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

		print delta, 

		if delta >= isdoubleafter:
			# pred = '11' if mid == self.up else '00'
			pred = '1'*(delta/issingle) if mid == self.up else '0'*(delta/issingle)
		else:
			pred = '1' if mid == self.up else '0'

		print pred
		
		self.result += pred
		self.size = 1
		self.seq = self.direction

	def process(self, lines):
		if not self.end:
			self.end = float(lines[-1].split(" ")[0])
		prev = int(lines[0].split(" ")[1])
		timestart = float(lines[0].split(" ")[0])

		print 'EPSILON:',self.epsilon

		for l in lines[1:]:
			value = int(l.split(" ")[1])
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

	def find_epsilon(self, lines):
		# the idea is to scan a certain number of initial values (100 ?)
		# these values need to be taken at light off, in order to register 
		# the ambient brightness level
		# from there, I could costumise my epsilon perhaps?
		# with the small LED:
		# dark environment, low around 10 at rest, low 30, high 70, eps: 6
		# variations: 70-30 -> 40, eps = 6
		# light env, low at rest (depends) 80, low 90, high 110, eps: 4
		# variations: 110-90 -> 30, eps = 4

		avg = 0.0
		num = 100
		for l in lines[:num]:
			avg += float(l.split(" ")[1])
		avg = avg / num
		if abs(avg - 30) < abs(avg-70): # closer to 30 than to 70
			self.epsilon = 6
		else:
			self.epsilon = 4


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


def help():
	pass

def main(argv):

	samplefile = "sample.txt"  #"sample0.txt" #original helloworld
	model = LiFiClassifier()

	opts, args = getopt.getopt(argv, 'hi:f:', ['interval=', 'file=', 'epsilon='])

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-i' or opt == '--interval':
			model.start = int(arg.split(":")[0])
			model.end = int(arg.split(":")[1])
		elif opt == '-f' or opt == '--file':
			samplefile = arg
		elif opt == '--epsilon':
			model.epsilon = int(arg)

	print 'FILE:',samplefile
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	# model.find_epsilon(lines[1:102])
	# model.process(lines[2100:2600]) # sample0.txt
	model.process(lines)
	print compare(model.result)
	

if __name__ == '__main__':
	main(sys.argv[1:])