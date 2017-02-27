#!/usr/bin/python
import sys
import subprocess
import getopt

def help():
	print 'process the signal (manual reading)'
	print 'options:'
	print ' -s: or --start=   	start of interesting part (line in file)'
	print ' -e: or --end= 		end of interesting part   (line in file)'
	print ' -f: or --file= 		file to read (sample.txt)'
	print ' -w: or --write= 	output file (processed.txt)'
	print ' --epsilon= 			variation considered noise'

def main(argv):
	# read arguments and set variables
	samplefile = "sample.txt"
	processedfile = None
	start = 0
	end = ''
	epsilon = 3

	opts, args = getopt.getopt(argv, 'hs:e:f:w:', ['start=', 'end=', 'file=', 'write=', 'epsilon='])

	for opt, arg in opts:
		if opt == '-h':
			help()
			return
		elif opt == '-s' or opt == '--start':
			start = int(arg)
		elif opt == '-e' or opt == '--end':
			end = int(arg)
		elif opt == '-f' or opt == '--file':
			samplefile = arg
		elif opt == '-w' or opt == '--write':
			processedfile = arg
		elif opt == '--epsilon':
			epsilon = int(arg)

	
	digital(samplefile, processedfile, start, end, epsilon)
	# process(samplefile, processedfile, start, end, epsilon)

def compare(res):
	# for comparing known transmission of "hello world"
	intendedbin = '0110100001100101011011000110110001101111001000000111011101101111011100100110110001100100'
	intended = ''.join(['01' if x == '1' else '10' for x in intendedbin])
	# print res
	# print '========='
	s = min(len(intended), len(res))
	for i in xrange(s):
		if res[i] == intended[i]:
			print res[i],
		else:
			print '-',
	print '_' * abs(len(intended) - len(res))

def process(samplefile, processedfile, start, end, epsilon):
	# slightly better for a specific case, keep a buffer and count, this way
	# it accounts for random peaks
	# used for 2 ms transmission rate
	if processedfile is None:
		processedfile = 'processed.txt'
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

	prev = int(lines[start].split(" ")[1])

	if not end:
		end = len(lines)

	for l in lines[start+1:end]:
	
		value = int(l.split(" ")[1])
		time = l.split(" ")[0]

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
	compare(res[2:])

def digital(samplefile, processedfile, start, end, epsilon):
	# naive version, look only at trend, don't count the things before
	
	if processedfile is None:
		processedfile = "digital" + str(epsilon) + ".txt"
	f = open(samplefile, 'r')
	lines = f.readlines()
	f.close()
	fw = open(processedfile, 'w+')
	up = '70'
	down = '30'
	direction = down
	prev = int(lines[start].split(" ")[1])

	if not end:
		end = len(lines)

	for l in lines[start+1:end]:
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

if __name__ == '__main__':
	# for i in range(1,7):
	# 	main([i])
	main(sys.argv[1:])
















