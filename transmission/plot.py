#! /usr/bin/python
import subprocess
import os
import sys
import re
import getopt

def plotn(files, filesp, interval, yrange="10:110"):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term pngcairo")
	cmds.append("set out \"sample.png\" " )
	cmds.append("set title \"Transmission sample, with prediction\"")
	cmds.append("set xlabel \"time [ms]\" " )
	cmds.append("set ylabel \"brightness [%]\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	plotstr = "plot "
	colors = ['#8A2BE2', '#008000', '#00BFFF', '#DAA520', 'blue']
	for i in xrange(len(files)):
		if i == 0: 
			continue
		plotstr += ("\"%s\" w linespoints title \"%s\" lt 1 pt 12 lc rgb \"%s\"," % (files[i], 'original '+ str(i), colors[i]))
		plotstr += ("\"%s\" w linespoints title \"%s\" lt 0 pt 12 lc rgb \"%s\"," % (filesp[i], 'predicted '+ str(i), colors[i]))
	plotstr = plotstr[:-1]
	cmds.append(plotstr)
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()

def main(argv):
	predicate1 = re.compile(r'normalised(.*)p.txt')
	predicate2 = re.compile(r'normalised(.*).txt')
	files = []
	filesp = []
	interval = ''

	opts, args = getopt.getopt(argv, 'i:', [])

	for opt, arg in opts:
		if opt == '-i':
			interval = arg

	for fn in os.listdir("."):
		if predicate1.match(fn):
			filesp.append(fn)
			# print 'added %s to processed ' % fn
		elif predicate2.match(fn): 
			files.append(fn)
			# print 'added %s to originalz ' % fn
	plotn(files, filesp, interval)

if __name__ == '__main__':
	main(sys.argv[1:])