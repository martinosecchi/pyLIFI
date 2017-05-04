#!/usr/bin/python
# 2 ms
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

	print '---------- 1'
	avgpeak = (sum(locmax) + 0.0) / len(locmax)
	minpeak = min(locmax)
	maxpeak = max(locmax)

	variance = (sum(map(lambda a: math.pow(a-avgpeak, 2),  locmax)) + 0.0)/len(locmax)
	stddev = math.sqrt(variance)

	print 'avg peak: %s' % str(avgpeak)
	print 'max peak: %s' % str(maxpeak)
	print 'min peak: %s' % str(minpeak)
	print 'variance: %s' % str(variance)
	print 'stddev: %s' % str(stddev)

	count = 0
	for v in locmax:
		if (v <= avgpeak + stddev) and (v >= avgpeak - stddev):
			count += 1
	print ' %s /100 elements between' % str((((count+0.0)/len(locmax))*100))
	print ' avg + stddev: %s   avg - stddev: %s' % (str(avgpeak + stddev), str(avgpeak - stddev))

	count = 0
	for v in locmax:
		if (v <= avgpeak + 2*stddev) and (v >= avgpeak - 2*stddev):
			count += 1
	print ' %s /100 elements between' % str((((count+0.0)/len(locmax))*100))
	print ' avg + 2stddev: %s   avg - 2stddev: %s' % (str(avgpeak + 2*stddev), str(avgpeak - 2*stddev))

	print '--------- 0'

	avgpeak = (sum(locmin) + 0.0) / len(locmin)
	minpeak = min(locmin)
	maxpeak = max(locmin)

	variance = (sum(map(lambda a: math.pow(a-avgpeak, 2),  locmin)) + 0.0)/len(locmin)
	stddev = math.sqrt(variance)

	print 'avg peak: %s' % str(avgpeak)
	print 'max peak: %s' % str(maxpeak)
	print 'min peak: %s' % str(minpeak)
	print 'variance: %s' % str(variance)
	print 'stddev: %s' % str(stddev)

	count = 0
	for v in locmin:
		if (v <= avgpeak + stddev) and (v >= avgpeak - stddev):
			count += 1
	print ' %s /100 elements between' % str((((count+0.0)/len(locmin))*100))
	print ' avg + stddev: %s   avg - stddev: %s' % (str(avgpeak + stddev), str(avgpeak - stddev))

	count = 0
	for v in locmin:
		if (v <= avgpeak + 2*stddev) and (v >= avgpeak - 2*stddev):
			count += 1
	print ' %s /100 elements between' % str((((count+0.0)/len(locmin))*100))
	print ' avg + 2stddev: %s   avg - 2stddev: %s' % (str(avgpeak + 2*stddev), str(avgpeak - 2*stddev))

	# store data for histograms from locmax and locmin
	# brightness: x count normalised: y
	# would it make more sense to have something different? like I don't know

	def find(p):
		for i in range(0,100,5):
			if p >=i and p < i+5:
				return i
		return 100
	# 1s
	hist1 = {}
	hist0 = {}
	for i in range(0,100,5):
		hist1[i] = 0
		hist0[i] = 0
	for p in locmax:
		hist1[find(p)]+=1
	fw = open("hist1.txt", 'w+')
	# write in sorted manner:
	h = [0] * 101
	for k,v in hist1.iteritems():
		h[k] = v*100.0/len(locmax)
	for i in range(len(h)):
		if i % 5 == 0:
			# print i, h[i]
			fw.write("%d %f\n"% (i, h[i]))
	fw.close()

	# 0s
	for p in locmin:
		hist0[find(p)]+=1
	h = [0] * 101
	for k,v in hist0.iteritems():
		h[k] = v*100.0/len(locmin)
	fw = open("hist0.txt", 'w+')
	for i in range(len(h)):
		if i % 5 == 0:
			fw.write("%d %f\n"% (i, h[i]))
	fw.close()

	plothist('1')
	plothist('0')


def plotn(files, interval="-10:165", yrange="-10:110"):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term pngcairo")
	cmds.append("set out \"overlap2.png\" " )
	cmds.append("set title \"Alternating signals, rate with 2ms interval\"")
	cmds.append("set xlabel \"time [ms]\" " )
	cmds.append("set ylabel \"brightness [%]\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	plotstr = "plot "
	i = 1
	for samplefile in files:
		plotstr += ("\"x" + samplefile + "\" w linespoints title \"" + str(i) + "\" pt 12,")
		i +=1 
		if samplefile == files[-1]:
			plotstr = plotstr[:-1] + " lt rgb \"blue\""
	cmds.append(plotstr)
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()

def plothist(z_o = '1', interval='-10:110', yrange='-10:60'):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term pngcairo")
	cmds.append("set out \"hist" + z_o + ".png\" " )
	cmds.append("set title \"Distribution of brightness levels for " + z_o + "s\"")
	cmds.append("set xlabel \"brightness [%]\" " )
	cmds.append("set ylabel \"frequency [%]\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	if z_o == '0':
		cmds.append("plot \"hist0.txt\" w boxes notitle")
	elif z_o == '1':
		cmds.append("plot \"hist1.txt\" w boxes notitle")
	else:
		raise ValueError("z_o can only be '0' or '1'")
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