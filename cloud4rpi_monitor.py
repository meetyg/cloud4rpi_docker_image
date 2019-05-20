# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import psutil
import rpi
import os
import re
import time 
import datetime
from statistics import mean
import pyowm

# regex pattern for reading cpu temp of various SBCs:
pattern = re.compile("^cpu[0-9]?|soc\-thermal$")

#import RPi.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = os.environ['TOKEN']
OWM_API_KEY = os.getenv('OWM_API_KEY')
OWM_CITY_COUNTRY = os.getenv('OWM_CITY_COUNTRY')
OWM_INTERVAL_SEC = os.getenv('OWM_INTERVAL',300) # 5 Mins default

# Constants
DATA_SENDING_INTERVAL = 15  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 5  # seconds

# Configure GPIO library
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(LED_PIN, GPIO.OUT)

owm = None
owm_hum = 0.0
owm_temp = 0.0

	
# Handler for the button or switch variable
def led_control(value=None):
#    GPIO.output(LED_PIN, value)
#    return GPIO.input(LED_PIN)
	 pass

def cpu_percent(value=None):
		return psutil.cpu_percent(interval=1)

def cpu_freq(value=None):
		freq_tuple = psutil.cpu_freq()
		return freq_tuple.current

def mem_percent(value=None):
		mem = psutil.virtual_memory()
		return mem.percent

def swap_percent(value=None):
		swap = psutil.swap_memory()
		return swap.percent

def disk_percent(value=None):
		disk = psutil.disk_usage('/')
		return disk.percent

def cpu_temp(value=None):
		temps = psutil.sensors_temperatures()
		temp_values_arr = []
		for temp_key, temp_val in temps.items():
				if (pattern.match(temp_key)):
						temp_values_arr.append(temp_val[0].current)
		return mean(temp_values_arr)

def up_time(value=None):
	boot_time = psutil.boot_time()
	
	seconds = int(time.time()) - int(boot_time)
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	d, h = divmod(h, 24)

	uptime_str =  f'{d} days, {h:0>2}:{m:0>2}:{s:0>2}'
	
	#return as tuple:
	return uptime_str

def boot_time(value=None):
	boot_time = psutil.boot_time()
	last_boot_str = datetime.datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
	return last_boot_str

def is_empty(s):
	return not s or not s.strip()	

def get_current_owm_data():
	global owm
	global owm_temp
	global owm_hum
	
	if not owm:
		owm = pyowm.OWM(OWM_API_KEY)  
	
	observation = owm.weather_at_place(OWM_CITY_COUNTRY)
	w = observation.get_weather()	
	# Weather details
	#w.get_wind()                  # {'speed': 4.6, 'deg': 330}
	owm_hum = w.get_humidity()              # 87
	owm_temp = w.get_temperature('celsius')['temp']  # {'temp_max': 10.5, 'temp': 9.7, 'temp_min': 9.0}

def get_owm_hum(value=None):
	return owm_hum

def get_owm_temp(value=None):
	return owm_temp

def get_owm_location(value=None):
	return OWM_CITY_COUNTRY

	
def main():


	variables = {
		'CPU Temp': {
		'type': 'numeric',
		'bind': cpu_temp
		},
		'CPU %': {
		'type' : 'numeric',
		'bind' : cpu_percent
		},
		'CPU freq' : {
		'type' : 'numeric',
		'bind' : cpu_freq
		},
		'Memory Usage %': {
		'type' : 'numeric',
		'bind' : mem_percent
		},
		'Swap Usage %': {
		'type' : 'numeric',
		'bind' : swap_percent
		},
		'Disk Usage %': {
		'type' : 'numeric',
		'bind' : disk_percent
		},
		'Up Time' : {
		'type' : 'string',
		'bind' : up_time
		},
		'Last Boot Time' : {
		'type' : 'string',
		'bind' : boot_time}
		}

	
	# Check if OpenWeatherMap api key and location where specified
	owm_enabled = (not is_empty(OWM_API_KEY)) and (not is_empty(OWM_CITY_COUNTRY))
	
	
	if owm_enabled:
		print()
		print(f'OpenWeatherMap data enabled: Key: {OWM_API_KEY}, Location: {OWM_CITY_COUNTRY}')
		print()
		variables['Weather Location'] = { 'type': 'string', 'bind': get_owm_location }
		variables['Weather Temperature Celsius'] = { 'type': 'numeric', 'bind': get_owm_temp }
		variables['Weather Humidity %'] = { 'type': 'numeric', 'bind': get_owm_hum }

	print(variables)
	
	diagnostics = {
		'IP Address': rpi.ip_address,
		'Host': rpi.host_name,
		'Operating System': rpi.os_name
	}
	device = cloud4rpi.connect(DEVICE_TOKEN)

	# Use the following 'device' declaration
	# to enable the MQTT traffic encryption (TLS).
	#
	# tls = {
	#     'ca_certs': '/etc/ssl/certs/ca-certificates.crt'
	# }
	# device = cloud4rpi.connect(DEVICE_TOKEN, tls_config=tls)

	try:
		device.declare(variables)
		device.declare_diag(diagnostics)

		device.publish_config()

		# Adds a 1 second delay to ensure device variables are created
		sleep(1)

		data_timer = 0
		diag_timer = 0
		owm_timer = 0

		while True:
			if owm_enabled:
				# Check if owm data needs to be updated:
				if owm_timer <=0:
					get_current_owm_data()
					owm_timer = OWM_INTERVAL_SEC
					
			if data_timer <= 0:
				device.publish_data()
				data_timer = DATA_SENDING_INTERVAL

			if diag_timer <= 0:
				device.publish_diag()
				diag_timer = DIAG_SENDING_INTERVAL

			sleep(POLL_INTERVAL)
			diag_timer -= POLL_INTERVAL
			data_timer -= POLL_INTERVAL
			owm_timer -= POLL_INTERVAL

	except KeyboardInterrupt:
		cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

	except Exception as e:
		error = cloud4rpi.get_error_message(e)
		cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

	finally:
		sys.exit(0)


if __name__ == '__main__':
	main()
