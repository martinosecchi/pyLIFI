#!/usr/bin/python
import sys
import getopt


class LiFiClassifier(object):
	def __init__(self, args={}):
		self.labels = ['1', '0', '11', '00']
		# the difference between two subsequent values is sonsidered noise
		# below the epsilon value (default 4)
		self.epsilon = args['epsilon'] if args.has_key('epsilon') else 4
		self.up = 'u'
		self.down = 'd'
		self.direction = self.down
		self.count = 1
		self.seq = self.direction
		self.size = 0
		self.result = ''
		self.start = args['start'] if args.has_key('start') else 0
		self.end = args['end'] if args.has_key('end') else None

	def predict(self, wndw):
		# wndw is a string [dir start][num=1][dir][dir end]
		# ex: 'd3ud' -> d,u,u,u,d

		print wndw,

		pred = '-'
		start = wndw[0]
		end = wndw[-1]
		wndw = wndw[1:-1]
		count = int(''.join(filter(str.isdigit,wndw)))
		mid = wndw[-1]

		if mid == start or mid == end:
			count+=1

		if count >= 5:
			pred = '11' if mid == self.up else '00'
			# pred = '11'*(count/5) if mid == self.up else '00'*(count/5) # in case no max size
		else:
			pred = '1' if mid == self.up else '0'
		print pred
		self.result += pred
		self.size = 1
		self.count = 1
		self.seq = self.direction

	def process(self, lines):
		if not self.end:
			self.end = float(lines[-1].split(" ")[0])
		prev = float(lines[0].split(" ")[0])

		print self.epsilon

		for l in lines[1:]:
			value = int(l.split(" ")[1])
			time = float(l.split(" ")[0])

			if time < float(self.start):
				prev = value
				continue
			elif float(time) >= float(self.end):
				break

			print '(%f, %d)'%(time,value) , 
			self.size += 1

			# staying
			if abs(value - prev) <= self.epsilon:
				self.count += 1 
				# maybe, interrupt on size > somevalue?	

			#going down
			elif value <= prev: 
				if self.direction == self.up:
					self.seq += str(self.count) + self.direction + self.down
					self.predict(self.seq)
					self.direction = self.down

				elif self.direction == self.down:
					self.count += 1

			# going up
			elif value > prev: 
				if self.direction == self.down:
					self.seq += str(self.count) + self.direction + self.up
					self.predict(self.seq)
					self.direction = self.up

				elif self.direction == self.up:
					self.count += 1

			prev = value
		self.seq += str(self.count) + self.direction + self.direction
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

def compare(res):
	# for comparing known transmission of "hello world"
	# intendedbin = '0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100'
	# intended = ''.join(['01' if x == '1' else '10' for x in intendedbin])
	intended = '10010110011010101001011010011001100101100101101010010110010110101001011001010101101001101010101010010101100101011001011001010101100101011010011010010110010110101001011010011010'
	print 'intended'
	print intended
	print '==='
	print 'result'
	print res
	print '==='
	res = cut_zeroes(res)

	intended = intended[3:]
	res = res[2:]

	s = min(len(intended), len(res))
	for i in xrange(s):
		if res[i] == intended[i]:
			print res[i],
		else:
			print '-',
	print '_' * abs(len(intended) - len(res))

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

	print samplefile
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	# model.find_epsilon(lines[1:102])
	# model.process(lines[2100:2600]) # sample0.txt
	model.process(lines)
	print compare(model.result)
	

if __name__ == '__main__':
	main(sys.argv[1:])