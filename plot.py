#!/usr/bin/python
import subprocess
import sys
import os
import getopt


def help():
	print 'normal use:'
	print './plot.py -f file.txt -i 5:10 folder'
	print 'args:'
	print '/folder/where/to/store'
	print 'options:'
	print ' -f: or --file=		default sample.txt, file to read for the plot'
	print ' -i: or --interval=  interval of print on x-axis, in form s:f e.g. -i 5:10 no spaces'
	print ' -m: or --mode= 		select mode: (normal), processed, split, zoom'
	print ' -p: or --processed= select processed file, will be compared with -f argument'
	print ' -s: or --split= 	for split and zoom mode, intervals size, and all fits between -i argument  e.g. -s 10'
	print ' -y: or --yrange= 	yrange, form s:e no space'
	print ''
	print 'for split mode you need a processedfile and a samplefile, or use the defaults ones'
	print 'zoom only uses the samplefile, but still the split interval'
	print ''

def main(argv):
	opts, args = getopt.getopt(argv, 'f:i:m:p:s:y:h', ['file=', 'interval=', 'mode=', 'processed=', 'split=', 'yrange=', 'help'])
	
	if len(args)!=1:
		help()
		return

	folder = args[0]
	if not os.path.exists(folder) or not os.path.isdir(folder):
		os.makedirs(folder)

	mode = 'normal'
	samplefile = 'sample.txt'
	processedfile = 'processed.txt'
	interval = ''
	yrange = ''
	splitint = 10000

	for opt, arg in opts:
		if opt == '-h' or opt == '--help':
			help()
			return
		elif opt == '-f' or opt == '--file':
			samplefile = arg
		elif opt == '-i' or opt == '--interval':
			interval = arg
		elif opt == '-m' or opt == '--mode':
			mode = arg
		elif opt == '-p' or opt == '--processed':
			processedfile = arg
		elif opt == '-s' or opt == '--split':
			splitint = arg
		elif opt == '-y' or opt == '--yrange':
			yrange = arg
	
	# todo check if all the right things are there
	if mode == 'normal' or mode == 'n':
		plotn(folder,samplefile,interval,yrange)
	elif mode == 'processed' or mode == 'p':
		plotp(folder, processedfile, '', interval, yrange)
	elif mode == 'split' or mode == 's':
		if not interval or not splitint:
			help()
			return
		plots(folder, samplefile, processedfile, interval, yrange, splitint)
	elif mode == 'zoom' or mode == 'z':
		if not interval or not splitint:
			help()
			return
		plotz(folder, samplefile, interval, yrange, splitint)

def plots(folder, samplefile, processedfile, interval, yrange, splitint):
	start = interval.split(":")[0]
	end = interval.split(":")[1]
	start = float(start)
	end = float(end)
	splitint = float(splitint)
	i = 0
	temp = start + splitint

	while temp <= end:

		p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
		cmds = []
		cmds.append("set term png")
		cmds.append("set out \"" + os.path.join(folder,samplefile) + str(i) + ".png\" " )
		cmds.append("set xlabel \"time\" " )
		cmds.append("set ylabel \"brightness\"")
		if interval:
			cmds.append("set xrange [%f:%f] " % (start, temp))
		if yrange:
			cmds.append("set yrange ["+ yrange +"]")
		cmds.append("plot \"" + processedfile + "\" u 1:2 w linespoints title \"processed\" pt 12, \"sample.txt\" u 1:2 w linespoints title \"original\" pt 12")
		cmds.append("quit")
		f = p.stdin
		print >> f, '\n'.join(cmds)
		f.close()
		p.wait()

		start = temp
		temp = temp + splitint
		i+=1

def plotz(folder, samplefile, interval, yrange, splitint):
	start = interval.split(":")[0]
	end = interval.split(":")[1]
	start = float(start)
	end = float(end)
	splitint = float(splitint)
	i = 0
	temp = start + splitint

	while temp <= end:

		p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
		cmds = []
		cmds.append("set term png")
		cmds.append("set out \"" + os.path.join(folder,samplefile) + str(i) + ".png\" " )
		cmds.append("set xlabel \"time\" " )
		cmds.append("set ylabel \"brightness\"")
		if interval:
			cmds.append("set xrange [%f:%f] " % (start, temp))
		if yrange:
			cmds.append("set yrange ["+ yrange +"]")
		cmds.append("plot \"" + samplefile + "\" u 1:2 w linespoints pt 12")
		cmds.append("quit")
		f = p.stdin
		print >> f, '\n'.join(cmds)
		f.close()
		p.wait()

		start = temp
		temp = temp + splitint
		i+=1

def plotn(folder, samplefile, interval, yrange):
	# plot normal
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term png")
	cmds.append("set out \"" + os.path.join(folder,samplefile) + ".png\" " )
	cmds.append("set xlabel \"time\" " )
	cmds.append("set ylabel \"brightness\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	cmds.append("plot \"" + samplefile + "\" u 1:2 w linespoints pt 12")
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()

def plotp(folder, processedfile, label, interval, yrange):
	# plot for processed, comparison
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term png")
	cmds.append("set out \"" + os.path.join(folder,processedfile) + str(label) + ".png\" " )
	cmds.append("set xlabel \"time\" " )
	cmds.append("set ylabel \"brightness\"")
	if interval:
		cmds.append("set xrange [" + interval + "] ")
	if yrange:
		cmds.append("set yrange ["+ yrange +"]")
	cmds.append("plot \"" + processedfile + "\" u 1:2 w linespoints title \"processed\" pt 12, \"sample.txt\" u 1:2 w linespoints title \"original\" pt 12")
	cmds.append("quit")
	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()


if __name__ == '__main__':
	main(sys.argv[1:])