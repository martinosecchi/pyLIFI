#!/usr/bin/python
# statsA
import os
import re
import math

def main():
	predicate1 = re.compile(r'A(.*).txt')
	locmax = [] # an array of peaks for 1
	locmin = [] # an array of 0 peaks
	for fn in os.listdir("."):
			try:
				if predicate1.match(fn): 
					f = open(fn, 'r')
					olines = f.readlines()
					f.close()
					lines = [l.split(" ") for l in olines]
					times, values = zip(*lines)
					times = map(float, times)
					values = map(float, values)
					mx = max(values)
					# mn = min(values)
					mn = 30
					start = times[0]
					ffw = open('x' + fn, 'w+')
					wrote90 = False
					wrote95 = False
					wrote80 = False
					for i in range(len(olines)):
						perc = (values[i]-mn)*100/(mx-mn)
						t = times[i]-start
						if i >= 10 + 2 and i < len(olines) - 30: # skip last 30 and first 10
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


# ---------- 1
# avg peak: 65.2306215159
# max peak: 82.9592684954
# min peak: 41.4870353015
# variance: 60.1835877304
# stddev: 7.75780817825
#  64.6090534979 /100 elements between
#  avg + stddev: 72.9884296942   avg - stddev: 57.4728133377
#  96.70781893 /100 elements between
#  avg + 2stddev: 80.7462378724   avg - 2stddev: 49.7150051594
# --------- 0
# avg peak: 33.7990142637
# max peak: 65.2326421129
# min peak: 6.90619175813
# variance: 149.300859718
# stddev: 12.2188730952
#  64.2857142857 /100 elements between
#  avg + stddev: 46.017887359   avg - stddev: 21.5801411685
#  96.4285714286 /100 elements between
#  avg + 2stddev: 58.2367604542   avg - 2stddev: 9.36126807324

if __name__ == '__main__':
	main()