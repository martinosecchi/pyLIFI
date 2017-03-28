#!/usr/bin/python

import curses
import time
  

def main():
	stds = curses.initscr()
	curses.cbreak()
	curses.noecho()
	stdscr = curses.newwin(40,60)
	stdscr.keypad(1)
	stdscr.idlok(1)
	stdscr.scrollok(1)
	# stdscr.nodelay(1)
	curses.halfdelay(2)

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
			elif key == curses.KEY_DOWN: 
				stdscr.addstr(i,0,'down  ')
				stdscr.refresh()
			elif key == curses.KEY_LEFT:
				stdscr.addstr(i,0,'left  ')
				stdscr.refresh()
			elif key == curses.KEY_RIGHT:
				stdscr.addstr(i,0,'right ')
				stdscr.refresh()
			else:
				stdscr.addstr(i,0,key)
		except:
			stdscr.addstr(i,0,'stop  ')
	curses.nocbreak(); stdscr.keypad(0); curses.echo()
	curses.endwin()
if __name__ == '__main__':
	main()