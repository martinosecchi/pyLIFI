#!/usr/bin/python

import os
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import time
import traceback

def scale():
	predicate1 = re.compile(r'up(.*).txt')
	predicate2 = re.compile(r'down(.*).txt')
	# 1: 65 avg 73 mu+sigma (65%) 80 mu + 2sigma (97%)
	muu = 65
	musu = 73
	mu2su = 80

	mud = 35
	musd = 45
	mu2sd = 58

	upmu = [] # time of reached 90% of growth
	upmus = []
	upmu2s = []
	locmax = [] # time of full growth
	#0: 35 avg 45 mu + sigma(65%) 58 mu + 2 sigma (96%)
	downmu = []
	downmus = []
	downmu2s = []
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
					wrotemu2su = False
					wrotemusu = False
					wrotemuu = False
					wrotemud = False
					wrotemusd = False
					wrotemus2d = False
					for i in range(len(olines)):
						perc = (values[i]-mn)*100/(mx-mn)
						t = times[i]-start
						if predicate1.match(fn): # up
							if perc == 100:
								locmax.append(t)
							elif perc >= mu2su  and not wrotemu2su:
								upmu2s.append(t)
								wrotemu2su = True
							elif perc >=musu and not wrotemusu:
								upmus.append(t)
								wrotemusu = True
							elif perc >= muu  and not wrotemuu:
								upmu.append(t)
								wrotemuu = True
						else: # down
							if perc == 0:
								locmin.append(t)
							elif perc <= mud and not wrotemud :
								downmu.append(t)
								wrotemud = True
							elif perc <= musd and not wrotemusd:
								downmus.append(t)
								wrotemusd = True
							elif perc <= mu2sd and not wrotemus2d :
								downmu2s.append(t)
								wrotemus2d = True
							
						ffw.write("%s %s\n" % (str(t), str(perc)))
					ffw.close()
					# print fn
			except Exception as e:
				print e
				print 'failed for ' + fn

	print 'stats for mu as %s, mu+-sigma as %s, mu+-2sigma as %s ' % (str(muu), str(musu), str(mu2su))
	print 'mu avg times of growth',
	print sum(upmu)/len(upmu)
	print 'mu +- sigma of samples times of growth',
	print sum(upmus)/len(upmus)
	print 'mu +- 2sigma times of growth',
	print sum(upmu2s)/len(upmu2s)
	print 'times of full growth',
	print sum(locmax)/len(locmax)

	print 'stats for mu as %s, mu+-sigma as %s, mu+-2sigma as %s ' % (str(mud), str(musd), str(mu2sd))
	print 'times for decrease to avg',
	print sum(downmu)/len(downmu)
	print 'times for decrease to mu+-sigma',
	print sum(downmus)/len(downmus)
	print 'times for decrease to mu+-2sigma',
	print sum(downmu2s)/len(downmu2s)
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


def analyse():
	# predicate1 = re.compile(r'xup(.*).txt')
	# predicate2 = re.compile(r'xdown(.*).txt')
	predicate1 = re.compile(r'xup1.txt')
	predicate2 = re.compile(r'xdown1.txt')

	N = 11
	M = 11

	matrix = [[0 for n in range(N)] for m in range(M)]
	count1 = 0
	count0 = 0
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
					
					x = np.array(times)
					y = np.array(values)
					p = np.poly1d(np.polyfit(x, y, 9))

					# show graph
					xp = np.linspace(-10, 80, 100)
					_ = plt.plot(x, y, '.', xp, p(xp), '-')#, xp, p3(xp), '--')
					plt.ylim(-10,110)
					plt.show()

					if predicate1.match(fn): # warmup
						print 'up', count1
						for i in range(N):
							for j in range(i+1, M):
								matrix[i][j] += solve(p, j*10, times, True) - solve(p, i*10, times, True)
								# print i,j
								if i == 0 and j == 10:
									print '0 to 100: ', solve(p, j*10, times, True) - solve(p,i*10,times, True)
						count1 += 1
					elif predicate2.match(fn): # warmdown
						print 'down', count0
						for i in range(N):
							for j in range(i):
								matrix[i][j] += solve(p, j*10, times) - solve(p,i*10,times)
								# print i,j
								if i == 10 and j == 0:
									print '100 to 0: ', solve(p, j*10, times) - solve(p,i*10,times)
						count0 += 1
					
					xp = np.linspace(-10, 80, 100)
					_ = plt.plot(x, y, '.', xp, p(xp), '-')#, xp, p3(xp), '--')
					plt.ylim(-10,110)
					plt.show()
			except Exception as e:
				print e
				print 'failed for ' + fn
				traceback.print_exc()

	print 'matrix of distances ( 1 = 10 )'
	if count0 == count1 and count0 > 0:
		for i in range(N):
			print ''
			for j in range(M):
				matrix[i][j] /= count0 + 0.0
				print matrix[i][j],
		print ''
		print '0 to 100: ', matrix[0][10]
		print '100 to 0: ', matrix[10][0]

def solve(p, i, times, flag = False):
	# I know the range i care about in x : times is between 0 and 60 roughly
	maxX = int(max(times))
	minX = 0
	minN = 0
	step = 10.0
	for n in range(int(minX*step), int(maxX*step), 1): # precision of 0.1 ms, range doesn't take floats
		if abs(i - p(n/step)) < abs(i - p(minN)):
			minN = n/step
		# if flag and p(n) > i + 5:
		# 	print '(up) breaking at: ', n
		# 	break
		# elif not flag and p(n) < i - 5:
		# 	print '(down) breaking at: ', n
		# 	break
	return minN

if __name__ == '__main__':
	scale()
	analyse()