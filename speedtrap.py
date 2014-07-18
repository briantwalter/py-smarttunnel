#!/usr/bin/env python

#
# speedtrap.py		SpeedTrap for #SmartTunnel
# version		0.0.1
# author		Brian Walter @briantwalter
# description		Speed trap and dashing updater
#			for measuring slot car speed
#

import requests
import simplejson as json
import RPi.GPIO as GPIO
import os
import time
from daemon import runner
from datetime import datetime
from ConfigParser import SafeConfigParser
from multiprocessing import Process

# GPIO set up
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
 
# grab configurations
config = SafeConfigParser()
config.read('speedtrap_conf.py')
ledtop = config.getint('speedtrap', 'ledtop')
ledentr = config.getint('speedtrap', 'ledentr')
ledexit = config.getint('speedtrap', 'ledexit')
trigger = config.getint('speedtrap', 'trigger')
entr = config.getint('speedtrap', 'entr')
exit = config.getint('speedtrap', 'exit')
prec = config.getint('speedtrap', 'prec')
dist = config.getfloat('speedtrap', 'dist')
loop = config.getfloat('speedtrap', 'loop')
mphi = config.getfloat('speedtrap', 'mphi')
apiend = config.get('speedtrap', 'apiend')
apikey = config.get('speedtrap', 'apikey')
logfile = config.get('speedtrap', 'logfile')
pidfile = config.get('speedtrap', 'pidfile')
audfile = config.get('speedtrap', 'audfile')

# switch on smarttunel
def smarttunnelon():
    GPIO.setup(ledtop, GPIO.OUT)
    GPIO.output(ledtop, GPIO.HIGH)
    GPIO.setup(ledentr, GPIO.OUT)
    GPIO.output(ledentr, GPIO.HIGH)
    GPIO.setup(ledexit, GPIO.OUT)
    GPIO.output(ledexit, GPIO.HIGH)
    #payload = {'auth_token': apikey, 'text': "SmartTunnel is ON" }
    #req = requests.post(apiend + "/banner", data=json.dumps(payload))
 
# switch off smarttunel
def smarttunneloff():
    GPIO.setup(ledtop, GPIO.OUT)
    GPIO.output(ledtop, GPIO.LOW)
    GPIO.setup(ledentr, GPIO.OUT)
    GPIO.output(ledentr, GPIO.LOW)
    GPIO.setup(ledexit, GPIO.OUT)
    GPIO.output(ledexit, GPIO.LOW)
    #payload = {'auth_token': apikey, 'text': "SmartTunnel is OFF" }
    #req = requests.post(apiend + "/banner", data=json.dumps(payload))

# play crowd noise
def crowd():
    os.system("/usr/bin/mpg123 -q " + audfile)

# get timing value from pin
def traptime(pin):
    reading = 0
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    time.sleep(loop)
    GPIO.setup(pin, GPIO.IN)
    while (GPIO.input(pin) == GPIO.LOW):
        reading += 1
    return reading
 
# main
def main():
    # zero out top speed value before the loop
    # set up the GPIO tunnel switch pin to low by default 
    GPIO.setup(trigger, GPIO.OUT, pull_up_down = GPIO.PUD_DOWN)
    topspeed = 0
    while True:                                     
        if (GPIO.input(trigger) == GPIO.HIGH):
            smarttunnelon()
            val = traptime(entr) 
            if len(str(val)) >= prec:
                entertime = datetime.now()
                while True:
                    val = traptime(exit)
                    if len(str(val)) >= prec:
                        exittime = datetime.now()
                        delta = exittime - entertime
                        ips = dist / delta.total_seconds()
                        mph = ips * mphi
                        speed = str("%.2f" % mph)
                        if float(speed) > 10:
                            speed = 0
                        payload = {'auth_token': apikey, 'value': speed }
                        req = requests.post(apiend + "/lastmph", data=json.dumps(payload))
                        if float(speed) > float(topspeed):
                            payload = {'auth_token': apikey, 'value': speed }
                            req = requests.post(apiend + "/bestmph", data=json.dumps(payload))
                            # kick off the noise in an async process 
                            p = Process(target=crowd)
                            p.start()
                            topspeed = speed
                        break
        else:
            smarttunneloff()
            time.sleep(2)  
    GPIO.cleanup()

# main app class
class App():
    def __init__(self):
        self.stdin_path = '/dev/null'
        self.stdout_path = logfile
        self.stderr_path = logfile
        self.pidfile_path = pidfile
        self.pidfile_timeout = 5
    def run(self):
        main()

# execute the app according to run time argument
app = App()
daemon_runner = runner.DaemonRunner(app)
daemon_runner.do_action()
