#!/usr/bin/python
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.neural_network import MLPClassifier
import re
import numpy
import os

categories = ["101", "100", "011", "110", "001", "11", "00", "10", "01"]
maxsize = 12

def main():
	global maxsize
	data, targets = load_train_data()
	# reg = GaussianNB(); print 'GaussianNB'
	reg = RandomForestClassifier(); print 'RandomForest'
	# reg = AdaBoostClassifier(); print 'AdaBoost'
	# reg = MLPClassifier(); print 'ANN MLP'
	reg.fit(data, targets)
	print 'model trained'

	f = open('sample0.txt', 'r')
	lines = f.readlines()
	f.close()
	lines = lines[2120:2600]
	# lines = lines[2124:2200] # smaller example
	# lines = lines[2136:2200] # smaller in medias res
	buff = []
	res = ''
	start = 0
	# for approach 3
	# tempprev = None
	# tempprev = {}
	# temp = '00'
	# for approach 4
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

		# # 1. bad approach: fixed window of 7 from start
		# # close to the one in process.py and get_training.py but with ML
		# if len(buff) == 7:
		# 	buff += [0,0,0,0]
		# 	res += reg.predict(numpy.array(buff).reshape(1,-1))[0]
		# 	buff = []

		# # 2. predict always when 8 values
		# # but I do it twice over partially overlapped windows
		# if len(buff) >= 8:
		# 	buff += [0,0,0,0]
		# 	temp = reg.predict(numpy.array(buff).reshape(1,-1))[0]
		# 	if tempprev:
		# 		if temp == tempprev:
		# 			res+=temp
		# 		else:
		# 			res+='-'
		# 	tempprev = temp
		# 	buff = buff[4:8]

		# # 3. predict a number of times, remember when you started the sequence
		# # in the end, take the most common one
		# if len(buff) == 8:
		# 	buff += [0,0,0,0]
		# 	start+=1
		# 	pred = reg.predict(numpy.array(buff).reshape(1,-1))[0]
		# 	if not tempprev.has_key(pred):
		# 		tempprev[pred] = 0
		# 	tempprev[pred] += 1
		# 	if start == 8:
		# 		m = max(tempprev.values())
		# 		res += [k for k,v in tempprev.items() if v == m][0]
		# 		tempprev = {}
		# 		start = 0
		# 	buff = buff[1:8]

		# # 4. mixed approach: follow the fluctuation manually and predict 
		# # at the right times, with enough values
		# shifted = False
		# if abs(value - prev) > epsilon:
		# 	shifted = True
		# 	shifts+=1

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
			buff += [0] * (maxsize - len(buff)) # fill in with zeros
			pred = reg.predict(numpy.array(buff).reshape(1,-1))[0]
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
	s = min(len(intended), len(res))
	for i in xrange(s):
		if res[i] == intended[i]:
			print res[i],
		else:
			print '-',
	print '_' * abs(len(intended) - len(res))

def load_train_data():
	global categories
	global maxsize

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
							data.append(d)
							targets.append(cat)
						f.close()
						break
	return (numpy.array(data), numpy.array(targets))

def get_data(lines, maxsize):
	a = []
	for l in lines:
		a.append(int(l.split(" ")[1]))
	more = maxsize - len(a)
	for i in xrange(more):
		a.append(0)
	# print len(a)
	return a

if __name__ == '__main__':
	main()