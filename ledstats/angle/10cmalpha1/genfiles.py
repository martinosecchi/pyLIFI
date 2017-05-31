#! /usr/bin/python

def main():
	f = open('total.txt')
	lines = f.readlines()
	f.close()
	fw = None

	for l in lines:
		if './' in l :
			if fw:
				fw.close()
			if '<==' in l:
				fw = open(l[6:15], 'w+')
		elif l != '\n':
			fw.write(l)


if __name__ == '__main__':
	main()