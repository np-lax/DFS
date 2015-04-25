#!/usr/bin/env python

from time import sleep
import os
import RPi.GPIO as GPIO
import subprocess
import string as s

#define outputs
ant_l=25
scan_l=24
gps_l=23

#define inputs
sw=17
reset_sw=22
#setup GPIO pins 
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#setup outputs
GPIO.setup(ant_l, GPIO.OUT)
GPIO.setup(scan_l, GPIO.OUT)
GPIO.setup(gps_l, GPIO.OUT)

#clear outputs
GPIO.output(scan_l, GPIO.LOW)
GPIO.output(ant_l, GPIO.LOW)
GPIO.output(gps_l, GPIO.LOW)

#setup input
GPIO.setup(sw, GPIO.IN)
GPIO.setup(reset_sw, GPIO.IN)

#notify startup
for x in range(0, 3):
	GPIO.output(scan_l, GPIO.HIGH)
        GPIO.output(ant_l, GPIO.HIGH)
        GPIO.output(gps_l, GPIO.HIGH)
        sleep(0.4)
        GPIO.output(scan_l, GPIO.LOW)
        GPIO.output(ant_l, GPIO.LOW)
        GPIO.output(gps_l, GPIO.LOW)
        sleep(0.4)

#var to hold switch status
started=False

#var to hold execution status
exit=False

def blink(num, light, status):
	for x in range(0, num):
		GPIO.output(light, GPIO.HIGH)
		sleep(0.2)
	        GPIO.output(light, GPIO.LOW)
		sleep(0.2)
	
	sleep(1.5)
	
	if ( status ):
   		GPIO.output(light, GPIO.HIGH)
	else:
		GPIO.output(light, GPIO.LOW)

def err_blink(light):
	for x in range(0, 15):
		GPIO.output(light, GPIO.HIGH)
		sleep(0.15)
		GPIO.output(light, GPIO.LOW)
		sleep(0.15)
	
	for x in range(0, 5):
		GPIO.output(scan_l, GPIO.HIGH)
		GPIO.output(ant_l, GPIO.HIGH)
		GPIO.output(gps_l, GPIO.HIGH)
		sleep(0.25)
		GPIO.output(scan_l, GPIO.LOW)
		GPIO.output(ant_l, GPIO.LOW)
		GPIO.output(gps_l, GPIO.LOW)		
		sleep(0.25)
			
	sleep(2)
	GPIO.output(scan_l, GPIO.LOW)
	GPIO.output(ant_l, GPIO.LOW)
	GPIO.output(gps_l, GPIO.LOW)

def check_gps():
	#call gpsprof to check gps connectivity using 1pkt fix + capture output via stdout
	g = subprocess.Popen(['gpsprof','-n','1','localhost:2947:/dev/ttyUSB0'], stdout=subprocess.PIPE)
	gps_status = g.communicate()
       
	#subprocess.call(['gpsprof','-n','1','localhost:2947:/dev/ttyUSB0'], stdout=subprocess.PIPE)

	#check for no device error, if error, return false 
        if not gps_status[0]:
		err_blink(gps_l)
		return False									
	
	#if no error, return true							
	return True

def check_ant():
	#use iwlist freq to check that wifi card is attached and working
	a = subprocess.Popen(['iwlist','wlan0','freq'], stdout=subprocess.PIPE)
	ant_status = a.communicate()	
	
	#check for no device error, if error, return false
	if not ant_status[0]:
		err_blink(ant_l)
		return False

	#if no error, return true
	return True

def start_kismet():
	#start the kismet server in daemon(headless) mode
	s = subprocess.Popen(['/usr/local/bin/kismet_server','--daemonize'], stdout=subprocess.PIPE)	
	
	#x = os.system("ps aux | grep <something> | awk '{print $2}'")
	
	#print x
	

def start_prgm():
#	#exit condition (local var)
	exit_C = False

	#check GPS connectivity
	if not check_gps():
		print "DEBUG: no gps signal"
		exit_C = True
	else:
		blink(5, gps_l, True)

	#check antenna/wifi card connectivty
	if not check_ant():
		print "DEBUG: no connected antenna"
		exit_C = True
	else:
		blink(5, ant_l, True)

	#if no errors start scanning
	if not exit_C:
		#start kismet
		start_kismet()
		blink(3, scan_l, True)
	
	return exit_C
	#else:
	#	#kill kismet
	#	os.system("ps aux | grep <something> | awk '{print $2}' | xargs kill")
		
def reboot():
#reboot system
	for x in range(0, 3):
        	GPIO.output(scan_l, GPIO.HIGH)
	        GPIO.output(ant_l, GPIO.HIGH)
	        GPIO.output(gps_l, GPIO.HIGH)
	        sleep(0.4)
	        GPIO.output(scan_l, GPIO.LOW)
	        GPIO.output(ant_l, GPIO.LOW)
	        GPIO.output(gps_l, GPIO.LOW)
	        sleep(0.4)
	
	subprocess.call(['reboot'])
		


while True:
	if ( GPIO.input(sw) == False and started == False ):
		#set loop var
		started = True
		#start python script on switch throw
		exit = start_prgm()

	if ( GPIO.input(reset_sw) == True and started == True ):
		print "DEBUG: restarting"
		reboot()

	if exit:
		print "DEBUG: exiting prgm"
		break