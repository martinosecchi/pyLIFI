#!/usr/bin/python

import os
import re
import traceback
import subprocess
import math

def main():
	predicate1 = re.compile(r'dark(.*).txt')
	predicate2 = re.compile(r'dark(.*).txt.png')
	locmax = [] # an array of peaks for 1
	locmin = [] # an array of 0 peaks
	n_samples = 0
	files = []
	for fn in os.listdir("."):
			try:
				if predicate1.match(fn) and not predicate2.match(fn): 
					files.append(fn)
					n_samples += 1
					f = open(fn, 'r')
					olines = f.readlines()
					f.close()
					lines = [l.split(" ") for l in olines]
					times, values = zip(*lines)
					times = map(float, times)
					values = map(float, values)
					mx = max(values)
					# mn = min(values)
					mn = 4
					start = times[0]
					ffw = open('x' + fn, 'w+')
					for i in range(len(olines)):
						perc = (values[i]-mn)*100/(mx-mn)
						t = times[i]-start
						if i >= 8 + 2 and i < len(olines) - 25: # skip last 25 and first 8
							a = (values[i-2]-mn)*100/(mx-mn)
							b = (values[i-1]-mn)*100/(mx-mn)
							c = (values[i]-mn)*100/(mx-mn)
							if b > a and b > c:
								locmax.append(b)
							elif b < a and b < c:
								locmin.append(b)
						
						ffw.write("%s %s\n" % (str(t), str(perc)))
					ffw.close()
			except Exception as e:
				print e
				print 'failed for ' + fn
				traceback.print_exc()

	plotn(files[:5])
	print '%d 1s and %d 0s found in %d files' % (len(locmax), len(locmin), n_samples)
	print 'should be %d for ones and %d for 0s' % ((n_samples*24), (n_samples*24)-8)
	print 'error for 1s : %f perc.' %  (100 -(len(locmax)/(n_samples*24.0)*100))
	print 'error for 0s : %f perc.' %  (100 -(len(locmin)/(n_samples*24.0-8)*100))
	avg = get_avg(locmax)
	print 'avg 1: %f std dev: %f' % (avg, get_std_dev(get_variance(locmax, avg)))
	avg = get_avg(locmin)
	print 'avg 0: %f std dev: %f' % (avg, get_std_dev(get_variance(locmin, avg)))


def plotn(files, interval=None, yrange=None):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term pngcairo")
	cmds.append("set out \"overlap.png\" " )
	cmds.append("set xlabel \"time\" " )
	cmds.append("set ylabel \"brightness\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	plotstr = "plot "
	for samplefile in files:
		plotstr += ("\"x" + samplefile + "\" u 1:2 w linespoints pt 12,")
	cmds.append(plotstr[:-1])
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()

def get_avg(lines):
	return sum(lines)/len(lines)

def get_std_dev(variance):
	return math.sqrt(variance)

def get_variance(lines, avg):
	s = 0.0 
	for l in lines:
		s += math.pow(l - avg, 2)
	return s / len(lines)

if __name__ == '__main__':
	main()


# 110 1s and 111 0s found in 7 files
# should be 168 for ones and 160 for 0s
# error for 1s : 34.523810 perc.
# error for 0s : 30.625000 perc.
# avg 1: 66.749699 std dev: 6.102739
# avg 0: 55.781214 std dev: 6.725451