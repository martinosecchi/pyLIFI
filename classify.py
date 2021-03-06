#!/usr/bin/python
import sys
import getopt
import math
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

class LiFiClassifierLight(object):
	""" 
	this class focuses on live predictions, 
	storing intermediate results and classifying in linear time
	also 
	"""
	def __init__(self, args={}):
		self.epsilon = args.get('epsilon', 2)
		self.prev = None
		self.seqstart = None
		# up: True, down: False
		self.direction = True
		# s, m, e form a peak, either up or down
		self.s = None #'start direction'
		self._doubletime = 330*2 #340*2#390 #~400
		self._singletime = 175*2 #170 #~200
		self.verbose = False
		self._limit = 4 # limit for long sequences of the same bit

	def feed(self, time, value): # give me a value! I might have a prediction for you
		pred = None
		if self.prev is None:
			self.prev = value
			self.seqstart = time
			self.s = self.direction
			return pred

		# staying
		if abs(value - self.prev) <= self.epsilon:
			pass

		#going down
		elif value <= self.prev: 
			if self.direction: # up	
				pred = self._predict(time)

		# going up
		elif value > self.prev: 
			if not self.direction: # down
				pred = self._predict(time)

		self.prev = value
		return pred
	
	def _predict(self, time):
		m = self.direction
		e = not self.direction	
		
		delta = (time-self.seqstart)*100
		if m == self.s:
			delta += 100
		pred = '-'
		if delta >= self._doubletime:
			# pred = '11' if m else '00' # no long strikes
			pred = '1'*int(delta/self._singletime) if m else '0'*int(delta/self._singletime) # long strikes
		else:
			pred = '1' if m else '0'

		if len(pred) > self._limit:
			pred = pred[0] * self._limit

		if self.verbose:
			self._printpred(m,e,delta,pred)

		self.s = self.direction
		self.direction = not self.direction
		self.seqstart = time
		return pred
	
	def _printpred(self, m, e, delta, pred):
		seq = 'u' if self.s else 'd'
		seq += str(int(delta))
		seq += 'u' if m else 'd'
		seq += 'u' if e else 'd'
		print seq, pred


class LiFiClassifier(object):
	"""
	this class can be used for predicting a given sequence of values
	ideal for reading files and predict
	"""
	def __init__(self, args={}):
		# self.labels = ['1', '0', '11', '00']
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
		self.seq = self.direction
		return pred

	def process(self, lines):
		if not self.end:
			self.end = float(lines[-1].split(" ")[0])
		prev = float(lines[0].split(" ")[1])
		seqstart = float(lines[0].split(" ")[0])

		if self.epsilon is None:
			self.preprocess(lines, 100)

		print 'EPSILON:',self.epsilon

		for l in lines[1:]:
			value = float(l.split(" ")[1])
			time = float(l.split(" ")[0])

			if time < float(self.start):
				prev = value
				seqstart = time
				continue
			elif float(time) >= float(self.end):
				break

			# staying
			if abs(value - prev) <= self.epsilon:
				pass

			#going down
			elif value <= prev: 
				if self.direction == self.up:
					delta = int((time-seqstart)*100)
					self.seq += str(delta) + self.direction + self.down
					self.predict(self.seq)
					self.direction = self.down
					seqstart = time

			# going up
			elif value > prev: 
				if self.direction == self.down:
					delta = int((time-seqstart)*100)
					self.seq += str(delta) + self.direction + self.up
					self.predict(self.seq)
					self.direction = self.up
					seqstart = time

			prev = value

		delta = int((time-seqstart)*100)
		self.seq += str(delta) + self.direction + self.direction
		self.predict(self.seq)
		res = self.result
		self.result = ''
		return res


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

	def compare(self, intended=None, res=None, v=None):
		if v is None:
			v = self.v
		if res is None:
			res = self.result
		if intended is None:
			intended = self.intended
		intended = manchester(intended)
		
		# res = cut_zeroes(res)
		# intended = cut_zeroes(intended)

		if v:
			print 
			print 'intended'
			print intended
			print 
			print 'result'
			print res
			print 

		a = Sequence(list(res))
		b = Sequence(list(intended))
		voc = Vocabulary()
		aEncoded = voc.encodeSequence(a)
		bEncoded = voc.encodeSequence(b)

		# scoring = SimpleScoring(1, -1) # match, mismatch 2, -1
		# aligner = GlobalSequenceAligner(scoring, -1) # score, gap score -2
		scoring = SimpleScoring(1, -4) # match, mismatch 2, -1
		aligner = GlobalSequenceAligner(scoring, -1) # score, gap score -2

		try:
			score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)
		except:
			print "too much, couldn't align"
			encodeds = []
			
		for encoded in encodeds[:1]:
		    alignment = voc.decodeSequenceAlignment(encoded)
		    if v:
				print alignment
		    print 'Percent identity:', alignment.percentIdentity()
		    print 'Score:', score

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

def test():
	samplefile = "sample0.txt" 
	model = LiFiClassifier()
	print 'FILE:',samplefile
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	model.start = 4400
	model.end = 4800
	model.epsilon = 6
	res1 = model.process(lines[2:])
	print model.compare(model.intended, res1, v=True)

	lightmodel = LiFiClassifierLight()
	lightmodel.epsilon = model.epsilon
	lightmodel.direction = False
	lightmodel.verbose = True
	res2 = ""
	
	print 'EPSILON:', lightmodel.epsilon
	print 'start line', lines[2100]

	for l in lines[2100:2600]:
		time, value = l.split(" ")
		r = lightmodel.feed(float(time), float(value))
		res2 += r if r else ''
	print model.compare(model.intended, res2, True)

def help():
	print 'use LiFiClassifier to predict lifi transmission stored in a file as "timestamp value" from the sensor'
	print 'usage:'
	print '-i to specify a time interval for prediction as start:finish'
	print '-f for the file where to read from'
	print '-e to specify the noise factor'
	print 'if epsilon is not specified, it will be found through preprocessing phase in rest mode'
	print '-r to specifiy the result to compare the predicition with (deafaults to hello world)'
	print '-v for verbose output (no argument)'
	print '-c if you want to encapsulate the intended result between stx and etx'

def main(argv):

	samplefile = "sample0.txt" 
	model = LiFiClassifier()
	epsilon = 2
	encapsulated = False
	opts, args = getopt.getopt(argv, 'hi:f:r:e:vc', ['interval=', 'file=', 'epsilon=', 'result='])

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
			epsilon = int(arg)
		elif opt == '-r' or opt == '--result':
			model.intended = arg
		elif opt == '-v':
			model.v = True
		elif opt == '-c':
			encapsulated = True

	if encapsulated:
		model.intended = '\x02' + model.intended + '\x03'

	print 'FILE:',samplefile
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	# print '--Slow version--'
	model.epsilon = epsilon
	# res1 = model.process(lines[2:]) #first line sometimes a comment, second might be truncated
	# print model.compare(model.intended, res1, v=True)

	lightmodel = LiFiClassifierLight()
	lightmodel.epsilon = model.epsilon
	lightmodel.direction = False
	lightmodel.verbose = True
	res2 = ""
	
	print '--Light version--'
	print 'EPSILON:', lightmodel.epsilon
	print 'start line', lines[2]
	last = None
	for l in lines[2:]:
		time, value = l.split(" ")
		if float(time) < model.start:
				continue
		elif float(time) >= model.end:
				last = float(time)
				break
		r = lightmodel.feed(float(time), float(value))
		res2 += r if r else ''
	res2 += lightmodel._predict(last) if last else ''
	print model.compare(model.intended, res2, True)
	# print 'heavy vs light', res2 in res1

if __name__ == '__main__':
	main(sys.argv[1:])
