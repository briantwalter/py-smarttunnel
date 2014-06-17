#!/usr/bin/env python

#
# trappoc.py		TrapPoC
# version		0.0.1
# author		Brian Walter @briantwalter
# description		Speed trap proof of concept for 
#			measuring slot car speed
#

import RPi.GPIO as GPIO
import time
from datetime import datetime

# vars
entr = 23		# GPIO for entrance sensor
exit = 24		# GPIO for exit sensor
loop = .05		# interval to check for values
dist = 11.5		# distance between sensors in inches
prec = 3		# precision in digits to trip on
mphi = 0.0568181818	# 1 inch per second = 0.0568181818 miles per hour
 
DEBUG = 1
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 
def TrapTime (pin):
  reading = 0
  GPIO.setup(pin, GPIO.OUT)
  GPIO.output(pin, GPIO.LOW)
  time.sleep(loop)
  GPIO.setup(pin, GPIO.IN)
  while (GPIO.input(pin) == GPIO.LOW):
    reading += 1
  return reading
 
while True:                                     
  val = TrapTime(entr) 
  if len(str(val)) >= prec:
    #print "DEBUG: got enter time"
    entertime = datetime.now()
    while True:
      val = TrapTime(exit)
      if len(str(val)) >= prec:
        #print "DEBUG: got exit time"
        exittime = datetime.now()
        delta = exittime - entertime
        #print "DEBUG: delta time is " + str(delta)
        ips = dist / delta.total_seconds()
        mph = ips * mphi
        print str("%.4f" % mph) + " MPH"
        break
