#!/usr/bin/python
import os
import re
import traceback


def main():
	predicate1 = re.compile(r'xsample(.*).txt')
	predicate2 = re.compile(r'(.*).png')

	for fn in os.listdir("."):
			try:
				if predicate1.match(fn) and not predicate2.match(fn): 
					f = open(fn, 'r')
					olines = f.readlines()
					f.close()
					lines = [l.split(" ") for l in olines]
					times, values = zip(*lines)
					times = map(float, times)
					values = map(float, values)
					print 'max %s %f' % (fn, max(values))
					# print 'min %s %f' % (fn, min(values))
					
			except Exception as e:
				print e
				print 'failed for ' + fn
				traceback.print_exc()
if __name__ == '__main__':
	main()