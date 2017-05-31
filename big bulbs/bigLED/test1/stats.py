#!/usr/bin/python

import os
import re
import traceback
import subprocess
import math

def main():
	predicate1 = re.compile(r'dark(.*)y.txt')
	predicate2 = re.compile(r'(.*).png')
	locmax = [] # an array of peaks for 1
	locmin = [] # an array of 0 peaks
	n_samples = 0
	files = []
	offset = 0
	for fn in os.listdir("."):
			try:
				# print fn
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
					mx = 800
					mn = 80
					start = times[0]
					ffw = open('x' + fn, 'w+')
					for i in range(len(olines)):
						perc = (values[i]-mn)*100/(mx-mn)
						t = times[i]-start						
						ffw.write("%s %s\n" % (str(t+offset), str(perc)))
					ffw.close()
					if '7' in fn or '8' in fn:
						offset += 100
					else:
						offset += 50
			except Exception as e:
				print e
				print 'failed for ' + fn
				traceback.print_exc()

	plotn(files)
	# print '%d 1s and %d 0s found in %d files' % (len(locmax), len(locmin), n_samples)
	# # print 'should be %d for ones and %d for 0s' % ((n_samples*24), (n_samples*24)-8)
	# # print 'error for 1s : %f perc.' %  (100 -(len(locmax)/(n_samples*24.0)*100))
	# # print 'error for 0s : %f perc.' %  (100 -(len(locmin)/(n_samples*24.0-8)*100))
	# avg = get_avg(locmax)
	# print 'avg 1: %f std dev: %f' % (avg, get_std_dev(get_variance(locmax, avg)))
	# avg = get_avg(locmin)
	# print 'avg 0: %f std dev: %f' % (avg, get_std_dev(get_variance(locmin, avg)))

	# fw = open('results.txt', 'w+')
	# fw.write('avg 1: %f std dev: %f \n' % (avg, get_std_dev(get_variance(locmax, avg))))
	# fw.write('avg 0: %f std dev: %f \n' % (avg, get_std_dev(get_variance(locmin, avg))))


def plotn(files, interval="-500:500", yrange="-10:110"):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term pngcairo")
	cmds.append("set out \"ssr.png\" " )
	cmds.append("set title \"SSR speed\"")
	# cmds.append("set xlabel \"time [ms]\" " )
	cmds.append("set ylabel \"brightness [%]\"")
	cmds.append('set xtics ("30 ms" 30, "20 ms" 120, "10 ms" 210, "9 ms" 260, "8 ms" 310)')
	# if interval:
	# 	cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	plotstr = "plot "
	i = 1
	for samplefile in files:
		title = samplefile
		# if 'y' not in samplefile:
		# 	continue
		if '7' in samplefile:
			title = '30 ms'
		elif '8' in samplefile:
			title = '20 ms'
		elif '9' in samplefile:
			title = '10 ms'
		elif '10' in samplefile:
			title = '9 ms'
		elif '11' in samplefile:
			title = '8 ms'
		plotstr += ("\"x" + samplefile + "\" w linespoints title \"" + title + "\" pt 12,")
		i +=1 
		if samplefile == files[-1]:
			plotstr = plotstr[:-1] + " lt rgb \"blue\""
	cmds.append(plotstr)
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

# 2 ms
# 120 1s and 114 0s found in 5 files
# should be 120 for ones and 112 for 0s
# error for 1s : 0.000000 perc.
# error for 0s : -1.785714 perc.
# avg 1: 70.223163 std dev: 7.061368
# avg 0: 50.181241 std dev: 5.791186
# 1 ms
# 110 1s and 111 0s found in 7 files
# should be 168 for ones and 160 for 0s
# error for 1s : 34.523810 perc.
# error for 0s : 30.625000 perc.
# avg 1: 66.749699 std dev: 6.102739
# avg 0: 55.781214 std dev: 6.725451