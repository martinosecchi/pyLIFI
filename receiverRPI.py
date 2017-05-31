#!/usr/bin/python
from lifiRx import lifiRx
from classify import LiFiClassifierLight, manchester
import sys
import os
from time import sleep

def setpath():
	exe = sys.argv[0]
	p = os.path.split(exe)[0]
	modulepath = os.path.join(p, 'alignment')
	sys.path.insert(0,modulepath)
	sys.path.insert(0,p)
	sys.path.insert(0,exe)
setpath()

from collections import deque
from alignment.sequence import Sequence
from alignment.vocabulary import Vocabulary
from alignment.sequencealigner import SimpleScoring, GlobalSequenceAligner


import dbus
import dbus.mainloop.glib

acc = 50

def main():
	global acc
	STX = "1010101010100110" # manchester for \x02
	ETX = "1010101010100101" # manchester for \x03
	commands = {}
	commands['up'] = manchester('up')
	commands['down'] = manchester('do')
	commands['left'] = manchester('le')
	commands['right'] = manchester('ri')
	scores = {}
	rx = lifiRx(buff=False, write=False)
	rx.connect() # not starting the thread, just using the object to read

	args = {'epsilon':2}
	classifier = LiFiClassifierLight(args)
	buff16 = deque(['0']*16, 16) # a buffer of length 16 in manchester encoding (min 1 byte), contains predicted bits (1, 0, but also 11111 00000 and so on they could be longer than 1!)
	maxlen = 10 * 8 * 2 # 10 chars max
	len3bytes = 3 * 8 * 2 # =48 for manchester coding
	mismatches_prob = 6 # how many bits could I have skipped out of 3 bytes? arbitrary for now
	started = False
	ended = True
	pdu = ''
	i = 0
	bit = None
	stop = False
	takinglength = False
	lengthbuff = ''
	length = -1
	noise = 3
	print 'starting..'
	try:
		while not stop:
			line = rx.readline()
			if line:
				try: 
					time, value, left, right = line.split(" ")
					value = float(value)
					left = float(left)
					right = float(right)
					sys.stdout.write("%10s %10f " % (time, value))
					bit = classifier.feed(float(time), value)
					# 5 as noise factor, arbitrary
					if left - value > noise and left - right > noise:
						send_cmd('ri')
					elif right - value > noise and right - left > noise: 
						send_cmd('le')
					else: #center
						send_cmd(str(acc))
				except ValueError:
					bit = None

				if bit: # a prediction of 1 or more bits
					buff16.append(bit)
					cmd = reduce(lambda x,y: x+y, buff16)
					if takinglength:
						for b in bit:
							lengthbuff += b
							if len(lengthbuff) == 16:
								try:
									length = 2* 8* int(manch_to_bin(lengthbuff),2)
									if length > maxlen:
										length = maxlen
									print 'LEN', length, '                  '
								except:
									print 'didn\'t get length', manch_to_bin(lengthbuff)
									started = False
								takinglength = False
							elif length != -1:
								i += 1
								pdu += b
					elif started and not ended and i > length - mismatches_prob and ETX in cmd:
						print 'ETX                                             ' 
						ended = True
						started = False
						print 'pdu found:', pdu
						command = reconstruct(pdu)
						print command
						if send_cmd(command):
							sleep(0.5)
							send_cmd('stop')
						pdu = ''
					elif started and not ended:
						i += len(bit)
						pdu += bit
					elif not started and STX in cmd:
						print 'STX                                               '
						started = True
						ended = False
						takinglength = True
						lengthbuff = ''
						length = -1
						i = 0
				sys.stdout.write("\r")
				sys.stdout.flush()

	except KeyboardInterrupt:
			stop = True
		# except Exception as e:
		# 	print e

	print 'stopping..'
	send_cmd('stop')
	if not rx.stopped:
		rx.stop()

def score(a, b):
	a = Sequence(list(a))
	b = Sequence(list(b))
	voc = Vocabulary()
	aEncoded = voc.encodeSequence(a)
	bEncoded = voc.encodeSequence(b)

	scoring = SimpleScoring(1, -4) # match, mismatch
	aligner = GlobalSequenceAligner(scoring, -1) # score, gap score
	return aligner.align(aEncoded, bEncoded, backtrace=False)

def manch_to_bin(manch):
	binary = ''
	for i in range(0, len(manch), 2):
		if i+1 >= len(manch):
			binary += '.'
			break
		if manch[i] + manch[i+1] == '01':
			binary += '1'
		elif manch[i] + manch[i+1] == '10':
			binary += '0'
		else:
			binary += '-'
	return binary

def reconstruct(pdu):
	# pdu is a string of bits in manchester encoding
	# take 16 bits at a time to reconstruct 1 byte into char, until there are no more enough
	i = 0
	bytlen = 16
	res = ''
	while i + bytlen < len(pdu):
		p = manch_to_bin(pdu[i:i+bytlen])
		print pdu[i:i+bytlen], '->', p, '->',
		try: 
			r = chr(int(p, 2))
		except:
			r = '_'
		print r
		res += r
		i += bytlen
	return res

def send_cmd(cmd):
	global acc
	left = 0
	right = 0
	go = acc
	done = True
	if cmd == 'up':
		left = go
		right = go
	elif cmd == 'down' or cmd == 'do':
		left = -go
		right = -go
	elif cmd == 'left' or cmd == 'le':
		left = 50
		right = -50
	elif cmd == 'right' or cmd == 'ri':
		left = -50
		right = 50
	elif cmd == 'stop':
		right = 0
		left = 0
	elif cmd.isdigit() or (len(cmd) > 1 and cmd[1:].isdigit() and (cmd[0] == '-' or cmd[0] == '+')):
		right = int(cmd)
		left = int(cmd)
		acc = int(cmd)
	else:
		done = False
	network.SetVariable("thymio-II", "motor.left.target", [left])
	network.SetVariable("thymio-II", "motor.right.target", [right])
	return done

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
	bus = dbus.SessionBus() #dbus.SystemBus()
	network = dbus.Interface(bus.get_object('ch.epfl.mobots.Aseba', '/'), dbus_interface='ch.epfl.mobots.AsebaNetwork')

	print 'network nodes list:'
	print network.GetNodesList()
	print ''

	main()
