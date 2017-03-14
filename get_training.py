#!/usr/bin/python

import sys
import os
import getopt
import subprocess
""" let's try groups of 4, and manually label? """

def help():
	print 'this will create a ton of files with chunks of the one that gets read'
	print 'options:'
	print ' -h for this page'
	print ' -f:  for the file to read'
	print ' -p: for the processed file'
	print ' -i:  interval size'
	print ' -m: mode: single s or (double d)'
	print ' -y: set yrange for plot'

def cut_zeroes(res):
	i = 0
	if len(res) == 0:
		return res
	while res[i] == '0':
		i+=1
	return res[i:]

class GetTraining(object):
	"""docstring for GetTraining"""
	def __init__(self, samplefile, processedfile, folder, interval, yrange, plot=False, write=False):
		super(GetTraining, self).__init__()
		if not os.path.exists(folder) or not os.path.isdir(folder):
			os.makedirs(folder)
		self.samplefile = samplefile
		self.processedfile = processedfile
		self.folder = folder
		# up, down same as in processedfile
		self.up, self.down = self.find_updown()
		self.direction = self.down
		self.buff = []
		self.flag = False # I use to see when there is two singles rather than one double (01,10 rather then 00,11)
		self.start = float(interval.split(":")[0])
		self.end = float(interval.split(":")[1])
		# end = float(self.interval.split(":")[1])
		self.res = ''
		self.slines = {}
		self.sizes = []
		self.do_plot = plot
		self.do_write = write
		self.yrange = yrange

	def find_updown(self):
		f = open(self.processedfile, 'r')
		f.readline() #skip first line
		first = float(f.readline().split(" ")[1])
		second = float(f.readline().split(" ")[1])
		while second == first:
			second = float(f.readline().split(" ")[1])
		# now they are different
		f.close()
		if first > second:
			return first, second
		return second,first
	def addres(self, label):
		self.res += label

	def assign_stopped(self, value, time, i):
		xrng = "%f:%f" % (self.start, time)
		label = "-"
		# if self.flag and value == self.up:
		# 	label = "01"
		# elif self.flag and value == self.down:
		# 	label = "10"
		# elif value == self.up:
		# 	label = "11"
		# elif value == self.down:
		# 	label = "00"

		if not self.flag and value == self.up:
			label = "11"
		elif not self.flag and value == self.down:
			label = "00"
		# elif self.flag and value == self.up:
		# 	label = "10"
		# elif self.flag and value == self.down:
		# 	label = "01"
		else: # flag is True, there were changes in direction
			# check if there is a double in though! it might be 
			# single + double
			same5end = True	
			same5start = True	
			j = -3 # to compare -3 with -2
			while j >= -6:
				#check if the 5 preceding samples have the same value -> probable double
				if self.buff[j][1] != self.buff[-2][1]:
					same5end = False
					break
				j += -1
			if not same5end:
				j = 2
				while j <= 5:
					# check if the first 5 are the same then
					if self.buff[j][1] != self.buff[1][1]:
						same5start = False
						break
					j+=1
			else:
				same5start = False

			# shit... there are also 001 and 110
			if same5end and value == self.up:
				label = "011"
			elif same5end and value == self.down:
				label = "100"
			elif same5start and value == self.up:
				label = "001"
			elif same5start and value == self.down:
				label = "110"
			elif value == self.up:
				label = "01"
			elif value == self.down:
				label = "10"

		self.addres(label)
		name = "%s(%s)" % (i, label)

		# print 'stopped at max, class is', label 
		
		if self.do_plot:
			self.plot(self.samplefile, self.processedfile, self.folder, name, xrng)
		# store in a file the lines from samplefile that correspond to 
		# the content of buffer, name as title
		if self.do_write:
			fw = open( os.path.join(self.folder, name + ".txt"), 'w+')
			for b in self.buff:
				fw.write(str(b[0]) + " " + self.slines[b[0]])
			fw.close()
		if len(self.buff) not in self.sizes:
			self.sizes.append(len(self.buff))
		self.buff = self.buff[-2:] # last two elements
		self.start  = self.buff[0][0]
		self.direction = value
		self.flag = False

	def assign(self, value, time, i):
		xrng = "%f:%f" % (self.start, time)
		label = "-"
		if not self.flag and value == self.up:
			label = "00"
		elif not self.flag and value == self.down:
			label = "11"
		# elif self.flag and value == self.up:
		# 	label = "10"
		# elif self.flag and value == self.down:
		# 	label = "01"
		else: # flag is True, there were changes in direction
			# check if there is a double in though! it might be 
			# single + double
			same5end = True	
			same5start = True	
			j = -3 # to compare -3 with -2
			while j >= -6:
				#check if the 5 preceding samples have the same value -> probable double
				if self.buff[j][1] != self.buff[-2][1]:
					same5end = False
					break
				j += -1
			if not same5end:
				j = 2
				while j <= 5:
					# check if the first 5 are the same then
					if self.buff[j][1] != self.buff[1][1]:
						same5start = False
						break
					j+=1
			else:
				same5start = False

			# shit... there are also 001 and 110
			if same5end and value == self.up:
				label = "100"
			elif same5end and value == self.down:
				label = "011"
			elif same5start and value == self.up:
				label = "110"
			elif same5start and value == self.down:
				label = "001"
			elif value == self.up:
				label = "10"
			elif value == self.down:
				label = "01"

		self.addres(label)
		name = "%s(%s)" % (i, label)

		# print len(self.buff), label
		
		if self.do_plot:
			self.plot(self.samplefile, self.processedfile, self.folder, name, xrng)
		if self.do_write:
			# store in a file the lines from samplefile that correspond to 
			# the content of buffer, name as title
			fw = open( os.path.join(self.folder, name + ".txt"), 'w+')
			for b in self.buff:
				fw.write(str(b[0]) + " " + self.slines[b[0]])
			fw.close()
			# if self.do_plot:
			# 	self.plot(os.path.join(self.folder, name + ".txt"), None, self.folder, name, None, yrange)
		if len(self.buff) not in self.sizes:
			self.sizes.append(len(self.buff))
		self.buff = self.buff[-2:] # last two elements
		self.start  = self.buff[0][0]
		self.direction = value
		self.flag = False

	def use_processed_double(self):
		# window sizes:
		# 4-5 single -> two singles 8-10
		# 7-8 double -> single + double 11-13

		f = open(self.samplefile, 'r')
		lines = f.readlines()
		f.close()

		stimes = [ float(l.split(" ")[0]) for l in lines]
		svalues = [ l.split(" ")[1] for l in lines]
		self.slines = dict(zip(stimes, svalues))

		f = open(self.processedfile, 'r')
		plines = f.readlines()
		f.close()

		i = 0
		maxwindow = 10
		for pl in plines:
			if ('#' in pl): continue
			time = float(pl.split(" ")[0])
			value = int(pl.split(" ")[1])

			if time < self.start:
				continue
			elif time >= self.end:
				break

			self.buff.append((time,value))
			if value == self.direction: 
				# following same direction, append
				# but stop at 10!
				if len(self.buff) == maxwindow:
					# print "stopped at", maxwindow
					self.assign_stopped(value, time, i)
					i+=1
			else: # change in direction
				if len(self.buff) > 5: # can be a double, two singles,
				 	# or a single and a double !!
				 	# in theory no more, since a single and a double have buff len 11-13,
				 	# and they stop at 10 when the value doesn't change
				 	# -- edit: nope, it still happens, how to deal with it?
					self.assign(value, time, i)
					i+=1
				elif len(self.buff) <= 5: # it's just a single, keep going
					self.flag = True
					self.direction = value
		print self.sizes
		self.compare()

	# def use_processed_single(self):
	# 	f = open(self.samplefile, 'r')
	# 	lines = f.readlines()
	# 	f.close()

	# 	stimes = [ float(l.split(" ")[0]) for l in lines]
	# 	svalues = [ l.split(" ")[1] for l in lines]
	# 	self.slines = dict(zip(stimes, svalues))

	# 	f = open(processedfile, 'r')
	# 	plines = f.readlines()
	# 	f.close()

	# 	i = 0
	# 	for pl in plines:
	# 		time = float(pl.split(" ")[0])
	# 		value = int(pl.split(" ")[1])

	# 		if value == direction:
	# 			buff.append((time,value))
	# 		else:
	# 			buff.append((time,value))
	# 			self.assign(value, time, i)
	# 			i+=1
	# 	self.compare(res)

	def compare(self, res=None):
		if not res:
			res = self.res
		# for comparing known transmission of "hello world"
		# intendedbin = '0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100'
		# intended = ''.join(['01' if x == '1' else '10' for x in intendedbin])
		intended = '10010110011010101001011010011001100101100101101010010110010110101001011001010101101001101010101010010101100101011001011001010101100101011010011010010110010110101001011010011010'
		print 'intended'
		print intended
		print '==='
		print 'result'
		print res
		print '==='
		res = cut_zeroes(res)
		s = min(len(intended), len(res))
		for i in xrange(s):
			if res[i] == intended[i]:
				print res[i],
			else:
				print '-',
		print '_' * abs(len(intended) - len(res))


	def plot(self, samplefile, processedfile, folder, name, xrng):
		p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
		cmds = []
		cmds.append("set term png")
		cmds.append("set out \"" + os.path.join(folder,name) + ".png\" " )
		cmds.append("set xlabel \"time\" " )
		cmds.append("set ylabel \"brightness\"")
		if xrng:
			cmds.append("set xrange [" + xrng + "] ")
		if self.yrange:
			cmds.append("set yrange ["+ self.yrange +"]")
		cmds.append("plot \"" + samplefile + "\" u 1:2 w linespoints pt 12")
		if processedfile:
			cmds[-1] += ", \"" + processedfile +"\" u 1:2 w linespoints"
		cmds.append("quit")
		f = p.stdin
		print >> f, '\n'.join(cmds)
		f.close()
		p.wait()

def main(argv):
	opts, args = getopt.getopt(argv, "hf:i:p:m:y:", [])

	folder = None
	samplefile = 'sample.txt'
	processedfile = "processed.txt"
	interval = "4400:4800"
	mode = 'd'
	yrange = '0:120'

	if len(args) > 0:
		folder = args[0]

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-f':
			samplefile = arg
		elif opt == '-i':
			interval = arg
		elif opt == '-p':
			processedfile = arg
		elif opt == '-y':
			yrange = arg
		elif opt == '-m':
			if arg == 's' or arg == 'd':
				mode = arg 
			else:
				print 'only modes allowed are s or d, going default', mode
	if mode == 's':
		# if not folder:
		# 	folder = 'train_single'
		# gt = GetTraining(samplefile,processedfile,folder,interval)
		# gt.use_processed_single()
		print 'deprecated, use double mode'
	elif mode == 'd':
		if not folder:
			folder = 'train_double'
		# gt = GetTraining(samplefile,processedfile,folder,interval,yrange,False,True)
		gt = GetTraining(samplefile,processedfile,folder,interval,yrange,True,True)
		# gt = GetTraining(samplefile,processedfile,folder,interval,yrange,False,False)
		gt.use_processed_double()


if __name__ == '__main__':
	main(sys.argv[1:])