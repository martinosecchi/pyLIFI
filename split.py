#! /usr/bin/python
import sys
import os
import getopt

def help():
	print '-f takes a file to read and split in multiple files with highlighted passages'
	print '-v to specify the threashold after which tx starts'
	print '-m where tx ends'
	print 'the transmission needs to start from 0 and finish at 1'
	print 'to use it on different files, call it with find'
	print 'e.g. find ledstats/distance -name \'sample*.txt\' -exec ./split.py -f {} \\;'

def main(argv):
	
	opts, args = getopt.getopt(argv, 'hf:v:m:', [])
	samplefile = None
	threashold = None
	minthreashold = None

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-f':
			samplefile = arg
		elif opt == '-v':
			threashold = int(arg)
		elif opt == '-m':
			minthreashold = int(arg)
	if not threashold and not samplefile:
		help()
		return
	if not minthreashold:
		minthreashold = threashold

	folder = os.path.dirname(samplefile)
	f = open(samplefile, 'r')
	olines = f.readlines()
	f.close()

	lines = [l.split(" ") for l in olines]
	times, values = zip(*lines)
	times = map(float, times)
	values = map(float, values)

	n = 1

	fw = None
	for i in xrange(len(olines)):
		if values[i] > threashold and fw is None:
			fw = open(os.path.join(folder,'dark%d.txt'%n), 'w+')
			n+=1
			for l in olines[i-8:i]:
				fw.write(l)
		elif values[i] > threashold and fw:
			fw.write(olines[i])
		elif values[i] < minthreashold and fw:
			fw.close()
			fw = None


if __name__ == '__main__':
	main(sys.argv[1:])