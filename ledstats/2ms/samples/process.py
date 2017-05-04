
def main():
	files = ['slight.txt', 'sdark.txt']
	for fn in files:
		f = open(fn, 'r')
		lines = f.readlines()
		f.close()
		fw = open(fn, 'w')
		start = float(lines[0].split(' ')[0])
		for l in lines:
			t, v = l.split(' ')
			t = float(t) - start
			fw.write('%s %s' % (str(t), v))
		fw.close()


if __name__ == '__main__':
	main()