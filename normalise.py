#! /usr/bin/python

import sys
import os
import getopt

def help():
	print 'normalise the signal, help page'
	print 'values in parenthesis () are the default'
	print 'options:'
	print ' -i: or --interval=  interval of interesting part (time value)'
	print ' -f: or --file= 		file to read (sample.txt)'
	print ' -w: or --write= 	output file (normalised.txt)'
	print 'to use it on different files, call it with find'
	print 'e.g. find ledstats/distance -name \'sample*.txt\' -exec ./normalise.py -f {} \\;'

def main(argv):
	# read arguments and set variables
	infile = "sample.txt"
	outfile = "normalised.txt"
	start = 0
	end = 900000000

	opts, args = getopt.getopt(argv, 'hi:f:w:', [])

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-i':
			start = int(arg.split(":")[0])
			end = int(arg.split(":")[1])
		elif opt == '-f':
			infile = arg
		elif opt == '-w':
			outfile = arg

		f = open(infile, 'r')
		olines = f.readlines()
		f.close()
		lines = [l.split(" ") for l in olines]
		times, values = zip(*lines)
		times = map(float, times)
		values = map(float, values)
		mx = max(values)
		mn = min(values)

		# skip everything before start
		for i in xrange(len(lines)):
			if times[i] >= start:
				times = times[i:]
				values = values[i:]
				break

		start = times[0]
		fw = open(outfile, 'w+')
		for i in xrange(len(times)):
			if times[i] > end:
				break
			perc = (values[i]-mn)*100/(mx-mn)
			t = times[i]-start	
			if 'process' in infile:
				if perc == 0:
					perc = 20.0		
			fw.write("%s %s\n" % (str(t), str(perc)))
		fw.close()


if __name__ == '__main__':
	main(sys.argv[1:])