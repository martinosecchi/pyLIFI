#!/usr/bin/python
import sys
import subprocess

intendedbin = '0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100'
intended = ''.join(['01' if x == '1' else '10' for x in intendedbin])

def main(args):
	# read arguments and set variables
	samplefile = "sample.txt"
	wndwsize = 4
	if len(args)==0:
		pass
	elif len(args) == 1:
		wndwsize = args[0]
	elif len(args) == 2:
		samplefile = args[0]
		wndwsize = args[1]
	else:
		print "wrong arguments"
		return
	# filterout(samplefile, wndwsize)
	# digital(samplefile, wndwsize)
	process(samplefile)

def confront(res):
	global intended
	print res
	print '========='
	s = min(len(intended), len(res))
	for i in xrange(s):
		if res[i] == intended[i]:
			print res[i],
		else:
			print '-',
	print '_' * abs(len(intended) - len(res))

def process(samplefile):
	# open files
	epsilon = 3
	processedfile = "processed.txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	up = '60'
	down = '30'
	direction = down
	buff = []
	res = ''
	amount = 0

	prev = int(lines[0].split(" ")[1])

	for l in lines[1:]:
	
		value = int(l.split(" ")[1])
		time = l.split(" ")[0]

		if float(time) <= 1.8 :
			continue
		elif float(time) >= 2.19:
			break

		if abs(value - prev) <= epsilon: #stay
			buff.append(direction)

		elif value <= prev: #down

			if direction != down:
				if len(buff) <= 2: # noise, probably
					continue

				if len(buff) > 12:
					res += '11'
					amount = 25
				else:
					res+='1'
					amount = 20

				buff = []
			direction = down
			buff.append(direction)

		else: #up

			if direction != up:
				if len(buff) <= 2: # noise, probably
					continue

				if len(buff) > 12:
					res += '00'
					amount = 25
				else:
					res += '0'
					amount = 20

				buff = []
			direction = up
			buff.append(direction)
			
		fw.write(time + " " + direction + " " + str(amount) + "\n")
		amount = 0
		prev = value

	fw.close()
	plot(processedfile, '')
	confront(res[2:])

def digital(samplefile, epsilon):
	# open files
	processedfile = "processed/digital" + str(epsilon) + ".txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	up = '60'
	down = '30'
	direction = down

	prev = int(lines[0].split(" ")[1])
	for l in lines[1:]:
		value = int(l.split(" ")[1])
		time = l.split(" ")[0]
		if abs(value - prev) <= epsilon: #difference is less than noise, stationary
			pass
		elif value <= prev:
			direction = down
		else:
			direction = up
		fw.write(time + " " + direction + "\n")
		prev = value
	fw.close()
	plot(processedfile, str(epsilon))


def plot(processedfile, label):
	# plot result
	p = subprocess.Popen(['gnuplot', '-'], stdin=subprocess.PIPE)
	cmds = []
	cmds.append("set term png")
	cmds.append("set out \" " + processedfile + str(label) + ".png\" " )
	cmds.append("set xlabel \"seconds\" " )
	cmds.append("set ylabel \"brightness\"")
	cmds.append("set xrange [2.05:2.1] ")
	cmds.append("set yrange [15:70]")
	cmds.append("plot \"" + processedfile + "\" u 1:2 w linespoints title \"processed\" pt 12, \"sample.txt\" u 1:2 w linespoints title \"original\" pt 12")
	cmds.append("quit")

	f = p.stdin
	print >> f, '\n'.join(cmds)
	f.close()
	p.wait()


if __name__ == '__main__':
	# for i in range(1,7):
	# 	main([i])
	main(sys.argv[1:])
















