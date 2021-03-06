################################################################################
# analogplot.py
#
# Display analog data from Arduino using Python (matplotlib)
# 
# electronut.in
#
################################################################################

import sys, serial
import numpy as np
from time import sleep
from collections import deque
from matplotlib import pyplot as plt

# class that holds analog data for N samples
class AnalogData:
  # constr
  def __init__(self, maxLen):
    self.ax = deque([0.0]*maxLen)
    self.maxLen = maxLen

  # ring buffer
  def addToBuf(self, buf, val):
    if len(buf) < self.maxLen:
      buf.append(val)
    else:
      buf.pop()
      buf.appendleft(val)

  # add data
  def add(self, data):
    assert(len(data) == 1)
    self.addToBuf(self.ax, data[0])
    
# plot class
class AnalogPlot:
  # constr
  def __init__(self, analogData):
    # set plot to animated
    plt.ion() 
    self.axline, = plt.plot(analogData.ax)
    plt.ylim([0, 400])

  # update plot
  def update(self, analogData):
    self.axline.set_ydata(analogData.ax)
    plt.draw()

# main() function
def main():
  # expects 1 arg - serial port string
  if(len(sys.argv) != 2):
    print 'Example usage: python analogplot.py "/dev/tty.usbmodem411"'
    print 'known ports:'
    print 'type yun for /dev/cu.usbmodem1411'
    print 'type red for /dev/cu.usbserial-DA0147XE'
    exit(1)

  red = '/dev/cu.usbserial-DA0147XE'
  yun = '/dev/cu.usbmodem1421'
 #strPort = '/dev/tty.usbserial-A7006Yqh'
  strPort = sys.argv[1];
  if strPort == 'yun':
    strPort = yun
  elif strPort == 'red':
    strPort = red

  # plot parameters
  analogData = AnalogData(1000)
  analogPlot = AnalogPlot(analogData)

  print 'plotting data...'

  # open serial port
  ser = serial.Serial(strPort, 9600)
  while True:
    try:
      sleep(1)
      line = ser.readline()
      try:
        data = [float(val) for val in line.split()]
      	sys.stdout.write(str(line).rstrip('\n\r') + ' ' + str(data) + '\r')
      	sys.stdout.flush()
        if(len(data) == 2):
          analogData.add(data[1])
          analogPlot.update(analogData)
        # elif(len(data) == 1):
        #   analogData.add(data)
        #   analogPlot.update(analogData)
      except:
        # skip line in case serial data is corrupt
        pass
    except KeyboardInterrupt:
      print 'exiting'
      break
  # close serial
  ser.flush()
  ser.close()

# call main
if __name__ == '__main__':
  main()
