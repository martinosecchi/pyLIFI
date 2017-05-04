#!/usr/bin/python

import os
import re

def main():
	predicate1 = re.compile(r'up(.*).txt')
	predicate2 = re.compile(r'down(.*).txt')
	# 1: 65 avg 73 mu+sigma (65%) 80 mu + 2sigma (97%)
	up65 = [] # time of reached 90% of growth
	up73 = []
	up80 = []
	locmax = [] # time of full growth
	#0: 35 avg 45 mu + sigma(65%) 58 mu + 2 sigma (96%)
	down35 = []
	down45 = []
	down58 = []
	locmin = []
	for fn in os.listdir("."):
			try:
				if predicate1.match(fn) or predicate2.match(fn): 
					f = open(fn, 'r')
					olines = f.readlines()
					f.close()
					lines = [l.split(" ") for l in olines]
					times, values = zip(*lines)
					times = map(float, times)
					values = map(float, values)
					mx = max(values)
					mn = min(values)
					start = times[0]
					ffw = open('x' + fn, 'w+')
					wrote80 = False
					wrote73 = False
					wrote65 = False
					wrote35 = False
					wrote45 = False
					wrote58 = False
					for i in range(len(olines)):
						perc = (values[i]-mn)*100/(mx-mn)
						t = times[i]-start
						if predicate1.match(fn): # up
							if perc == 100:
								locmax.append(t)
							elif perc >= 80  and not wrote80:
								up80.append(t)
								wrote80 = True
							elif perc >=73 and not wrote73:
								up73.append(t)
								wrote73 = True
							elif perc >= 65  and not wrote65:
								up65.append(t)
								wrote65 = True
						else: # down
							if perc == 0:
								locmin.append(t)
							elif perc <= 35 and not wrote35 :
								down35.append(t)
								wrote35 = True
							elif perc <= 45 and not wrote45:
								down45.append(t)
								wrote45 = True
							elif perc <= 58 and not wrote58 :
								down58.append(t)
								wrote58 = True
							
						ffw.write("%s %s\n" % (str(t), str(perc)))
					ffw.close()
					# print fn
			except Exception as e:
				print e
				print 'failed for ' + fn

	print 'times of 65% growth (avg)',
	print sum(up65)/len(up65)
	print 'times of 73% growth (65% of 1s)',
	print sum(up73)/len(up73)
	print 'times of 80% growth (96% of 1s)',
	print sum(up80)/len(up80)
	print 'times of full growth',
	print sum(locmax)/len(locmax)

	print 'times for decrease to 35% (avg 0s)',
	print sum(down35)/len(down35)
	print 'times for decrease to 45% (65% of 0s)',
	print sum(down45)/len(down45)
	print 'times for decrease to 58% (96% of 0s)',
	print sum(down58)/len(down58)
	print 'times of full decrease ',
	print sum(locmin)/len(locmin)

# old results		
# 80\%  &  ~6.1 ms & ~7.2 ms \\
# 90\% & ~10.9 ms & ~12.3 ms \\
# 95\% & ~10.7 ms & ~22.7 ms \\
# 100\% & ~49.0 ms & ~62.8 ms \\ 
# new results
# times of 65% growth (avg) 3.48200000001
# times of 73% growth (65% of 1s) 4.52000000001
# times of 80% growth (96% of 1s) 6.122
# times of full growth 49.03
# times for decrease to 35% (avg 0s) 4.25999999999
# times for decrease to 45% (65% of 0s) 3.37999999999
# times for decrease to 58% (96% of 0s) 2.50999999999
# times of full decrease  62.84


if __name__ == '__main__':
	main()