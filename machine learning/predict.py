#!/usr/bin/python
import sklearn
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import os
import numpy # import array
import re

categories = ["idle", "11", "00", "1", "0"]

def main():
	 # X = [[0., 0., 1], [1., 1.], [2., 2.,1 ], [3., 3.,1]]
	 # Y = ['a', 'b', 'c', 'd']
	 # # reg = GaussianNB()
	 # # reg = tree.DecisionTreeClassifier()
	 # reg = RandomForestClassifier()
	 # le = LabelEncoder()
	 # # le.fit(Y)
	 # # req.fit(X, le.transform(Y))
	 # reg.fit(X, Y)
	 # print reg.predict ([[1, 1, 2]])


	data, targets = load_train_data()
	testdata, intended = load_test_data()
	reg = GaussianNB(); print 'GaussianNB'
	# reg = RandomForestClassifier(); print 'RandomForest'
	# le = LabelEncoder()
	# le.fit(targets)
	print 'training model', len(data) == len(targets)
	reg.fit( data, targets)
	print 'predicting..'
	for i in xrange(len(testdata)):
		print 'predicted', reg.predict(numpy.array(testdata[i]).reshape(1,-1))[0] == intended[i]

	reg = RandomForestClassifier(); print 'RandomForest'
	print 'training model', len(data) == len(targets)
	reg.fit( data, targets)
	print 'predicting..'
	for i in xrange(len(testdata)):
		print 'predicted', reg.predict(numpy.array(testdata[i]).reshape(1,-1))[0] == intended[i]

def load_test_data():
	global categories
	folder = 'test'
	data = []
	targets = []
	predicate = re.compile(r'(.*)\((.*)\)\.txt')
	for fn in os.listdir(folder):
		for cat in categories:
			match = predicate.match(fn)
			if match and cat in match.group(2):
				f = open(os.path.join(folder, fn), 'r')
				data.append(get_data(f.readlines()))
				targets.append(cat)
				f.close()
				break
	# return (data, targets)
	return (numpy.array(data), numpy.array(targets))

def load_train_data():
	global categories
	folder = 'train'
	data = []
	targets = []
	predicate = re.compile(r'(.*)\((.*)\)\.txt')
	for fn in os.listdir(folder):
		for cat in categories:
			match = predicate.match(fn)
			if match and cat in match.group(2):
				f = open(os.path.join(folder, fn), 'r')
				# data.append(get_data(f.readlines()))
				d = get_data(f.readlines())
				# print fn, cat
				if len(d) > 30:
					# print d
					# print fn, cat, 'a bit too many here', len(d)
					pass
				else:
					data.append(d)
					targets.append(cat)
				f.close()
				break
	# return (data, targets)
	return (numpy.array(data), numpy.array(targets))

def get_data(lines):
	maxsize = 12
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