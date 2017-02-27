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
	print ' -i:  interval size'

def main(argv):
	opts, args = getopt.getopt(argv, "hf:i:p:", [])

	folder = 'train'
	samplefile = 'sample.txt'
	processedfile = "processed.txt"
	interval = "4400:4800"
	if len(args) > 0:
		folder = args[0]

	if not os.path.exists(folder) or not os.path.isdir(folder):
		os.makedirs(folder)

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

	use_processed(samplefile, processedfile, folder, interval)

def use_processed(samplefile, processedfile, folder, interval):
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()

	stimes = [ float(l.split(" ")[0]) for l in lines]
	svalues = [ l.split(" ")[1] for l in lines]
	slines = dict(zip(stimes, svalues))

	f = open(processedfile, 'r')
	plines = f.readlines()
	f.close()

	start = float(interval.split(":")[0])
	end = float(interval.split(":")[1])

	up = 70
	down = 30
	direction = down

	buff = []
	# keep one before and one after also
	i = 0
	res = ''
	for pl in plines:
		time = float(pl.split(" ")[0])
		value = int(pl.split(" ")[1])

		if value == direction:
			buff.append((time,value))
		else:
			buff.append((time,value))
			xrng = "%f:%f" % (start, time)
			yrange = '10:80'
			label = "-"
			if value == up and len(buff) > 5:
				label = "00"
			elif value == down and len(buff) > 5:
				label = "11"
			elif value == up:
				label = "0"
			elif value == down:
				label = "1"
			res += label
			name = "%s(%s)" % (i, label)
			plot(samplefile, processedfile, folder, name, xrng, yrange)
			# TODO more importantly, store in a file the lines from samplefile that correspond to 
			# the content of buffer, name as title
			fw = open( os.path.join(folder, name + ".txt"), 'w+')
			for b in buff:
				fw.write(str(b[0]) + " " + slines[b[0]])
			fw.close()

			buff = buff[-2:] # last two elements
			start  = buff[0][0]
			direction = value
			i+=1
	compare(res[2:])

def compare(res):
	# for comparing known transmission of "hello world"
	# intendedbin = '0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100'
	# intended = ''.join(['01' if x == '1' else '10' for x in intendedbin])
	intended = '10010110011010101001011010011001100101100101101010010110010110101001011001010101101001101010101010010101100101011001011001010101100101011010011010010110010110101001011010011010'
	# print '========='
	s = min(len(intended), len(res))
	for i in xrange(s):
		if res[i] == intended[i]:
			print res[i],
		else:
			print '-',
	print '_' * abs(len(intended) - len(res))


def plot(samplefile, processedfile, folder, name, xrng, yrange):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term png")
	cmds.append("set out \"" + os.path.join(folder,name) + ".png\" " )
	cmds.append("set xlabel \"time\" " )
	cmds.append("set ylabel \"brightness\"")
	if xrng:
		cmds.append("set xrange [" + xrng + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	cmds.append("plot \"" + samplefile + "\" u 1:2 w linespoints pt 12, \"" + processedfile +"\" u 1:2 w linespoints")
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()


if __name__ == '__main__':
	main(sys.argv[1:])