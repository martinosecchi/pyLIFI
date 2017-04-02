#!/usr/bin/python

import curses
import time
from lifiTx import lifiTx  

def main():
	stds = curses.initscr()
	curses.cbreak()
	curses.noecho()
	stdscr = curses.newwin(40,60)
	stdscr.keypad(1)
	stdscr.idlok(1)
	stdscr.scrollok(1)
	# stdscr.nodelay(1)
	curses.halfdelay(2) # tenths of second 1 -> 100 ms

	tx = lifiTx()
	tx.start()

	stdscr.addstr(0,0,"Hit 'q' to quit")
	stdscr.refresh()
	i = 1
	key = ''
	while key != ord('q'):
		try:
			key = stdscr.getch()
			stdscr.refresh()
			if key == curses.KEY_UP: 
				stdscr.addstr(i,0,'up    ')
				stdscr.refresh()
				tx.send('up')
			elif key == curses.KEY_DOWN: 
				stdscr.addstr(i,0,'down  ')
				stdscr.refresh()
				tx.send('do')
			elif key == curses.KEY_LEFT:
				stdscr.addstr(i,0,'left  ')
				stdscr.refresh()
				tx.send('le')
			elif key == curses.KEY_RIGHT:
				stdscr.addstr(i,0,'right ')
				stdscr.refresh()
				tx.send('ri')
			else:
				stdscr.addstr(i,0,key)
		except:
			stdscr.addstr(i,0,'stop  ')
			# tx.arduino.write(bytearray(['1']))
			tx.arduino.write(bytearray('0'))
	curses.nocbreak(); stdscr.keypad(0); curses.echo()
	curses.endwin()
	tx.stop()
if __name__ == '__main__':
	main()