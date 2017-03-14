#!/usr/bin/python
import getopt
import os
import sys
import math

def get_avg(lines):
	# the average sample rate, as avg distance between 
	# two consecutive sample timestamps 
	avg = 0.0 
	prev = float(lines[0].split(" ")[0])
	for l in lines[1:]:
		time = float(l.split(" ")[0])
		avg += (time - prev)
		prev = time
	avg = avg / (len(lines)-1.0)
	return avg

def get_std_dev(variance):
	return math.sqrt(variance)

def get_variance(lines, avg):
	s = 0.0 
	prev = float(lines[0].split(" ")[0])
	for l in lines[1:]:
		time = float(l.split(" ")[0])
		s += math.pow((time - prev) - avg, 2)
		prev = time
	return s / (len(lines)-1.0)

def compute_stats(argv):
	opts, args = getopt.getopt(argv, "hf:", [])
	samplefile = "sample.txt"
	for opt, arg in opts:
		if opt == "-h":
			help()
			return
		elif opt == "-f":
			samplefile = arg

	f = open(samplefile, 'r')
	lines = f.readlines()
	lines = lines[1:] # discard the first, most times it's truncated
	f.close()

	avg = get_avg(lines)
	variance = get_variance(lines, avg)
	print 'average rate:', avg
	print 'variance:', variance
	print 'std dev:', get_std_dev(variance)

def help():
	print 'this script produces statistics on the average rate of reception'
	print 'comparing timestamps of samples'
	print 'options : -h for help, -f: for specify a file where to read sample rate'

if __name__ == '__main__':
	compute_stats(sys.argv[1:])