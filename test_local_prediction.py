#!/usr/bin/python
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import re
import numpy
import os
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner

categories = ["101", "100", "011", "110", "001", "11", "00", "10", "01"]
maxsize = 12
sizes = []

def main():
	global maxsize
	global sizes

	data, targets = load_train_data()
	# scaler = StandardScaler()
	# scaler.fit(data)
	# data = scaler.transform(data)
	# # reg = GaussianNB(); print 'GaussianNB'
	# # reg = RandomForestClassifier(); print 'RandomForest'
	# # reg = AdaBoostClassifier(); print 'AdaBoost'
	# reg = MLPClassifier(); print 'ANN MLP' 
	# reg.fit(data, targets)
	# print 'model trained'

	reg = {}
	scaler = {}
	# classifier = GaussianNB; print 'GaussianNB'
	# classifier = RandomForestClassifier; print 'RandomForest'
	# classifier = AdaBoostClassifier; print 'AdaBoost'
	classifier = MLPClassifier; print 'ANN MLP' 
	for size in sizes:
		sub = [e for e in zip(data,targets) if len(e[0]) == size]
		subdata, subtarget = zip(*sub)
		scaler[size] = StandardScaler()
		scaler[size].fit(subdata)
		subdata = scaler[size].transform(subdata)
		reg[size] = classifier()
		reg[size].fit(subdata, subtarget)

	f = open('sample0.txt', 'r')
	lines = f.readlines()
	f.close()
	lines = lines[2120:2600]
	# lines = lines[2124:2200] # smaller example
	# lines = lines[2136:2200] # smaller in medias res
	buff = []
	res = ''
	start = 0
	up = 'up'
	down = 'down'
	direction = down
	prev = int(lines[start].split(" ")[1])
	epsilon = 6
	shifts = 0
	shifted = False
 
 	for l in lines[1:]:
		time = float(l.split(" ")[0])
		value = int(l.split(" ")[1])
		buff.append(value)

		shifted = False
		if abs(value - prev) <= epsilon: #difference is less than noise, stationary
			pass	
		elif value <= prev:
			if direction != down:
				direction = down
				shifted = True
				shifts += 1
		else:
			if direction != up:
				direction = up
				shifted = True
				shifts += 1

		if len(buff) > 9 or (len(buff)>6 and shifted and shifts>1):
			shifts = 0
			# print len(buff), buff,
			# last, two = buff[-2:]

			# buff += [0] * (maxsize - len(buff)) # fill in with zeros
			# pred = reg.predict(numpy.array(buff).reshape(1,-1))[0]
			# pred = reg.predict(scaler.transform(numpy.array(buff).reshape(1,-1)))[0]
			if len(buff) in sizes:
				buff += [0] * (min(sizes) - len(buff))
				pred = reg[len(buff)].predict(scaler[len(buff)].transform(numpy.array(buff).reshape(1,-1)))[0]
			
			# print pred
				res += pred
			# buff = [last,two]
			# if abs(two-last) > epsilon:
			# 	shifts+=1
			buff = [value]
			# buff = []
			
		prev = value
	compare(res)


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

	# intended = cut_zeroes(intended)
	# res = cut_zeroes(res)
	
	a = Sequence(list(res))
	b = Sequence(list(intended))
	v = Vocabulary()
	aEncoded = v.encodeSequence(a)
	bEncoded = v.encodeSequence(b)

	# Create a scoring and align the sequences using global aligner.
	scoring = SimpleScoring(2, -2)
	aligner = GlobalSequenceAligner(scoring, -1)
	score, encodeds = aligner.align(aEncoded, bEncoded, backtrace=True)

	# Iterate over optimal alignments and print them.
	# for encoded in encodeds:
	encoded = encodeds[0]	
	alignment = v.decodeSequenceAlignment(encoded)
	print alignment
	print 'Alignment score:', alignment.score
	print 'Percent identity:', alignment.percentIdentity()
	print

def load_train_data():
	global categories
	global maxsize
	global sizes

	folder = 'train'
	data = []
	targets = []
	predicate = re.compile(r'(.*)\((.*)\)\.txt')
	for directory in os.listdir(folder):
		if os.path.isdir(os.path.join(folder,directory)) and 'train' in directory:
			print directory
			for fn in os.listdir(os.path.join(folder,directory)):
				for cat in categories:
					match = predicate.match(fn)
					if match and cat in match.group(2):
						f = open(os.path.join(folder, directory, fn), 'r')
						d = get_data(f.readlines(), maxsize)
						if len(d) > maxsize:
							pass
						else:
							if len(d) not in sizes:
								sizes.append(len(d))
							data.append(d)
							targets.append(cat)
						f.close()
						break
	print sizes
	return (numpy.array(data), numpy.array(targets))

def get_data(lines, maxsize):
	a = []
	for l in lines:
		a.append(int(l.split(" ")[1]))
	# more = maxsize - len(a)
	# for i in xrange(more):
	# 	a.append(0)
	return a

if __name__ == '__main__':
	main()