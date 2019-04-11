# -*- coding: utf-8 -*-

from time import sleep
import sys
import random
import cloud4rpi
import psutil
import rpi
import os
#import RPi.GPIO as GPIO  # pylint: disable=F0401

# Put your device token here. To get the token,
# sign up at https://cloud4rpi.io and create a device.
DEVICE_TOKEN = os.environ['TOKEN']

# Constants
DATA_SENDING_INTERVAL = 30  # secs
DIAG_SENDING_INTERVAL = 60  # secs
POLL_INTERVAL = 0.5  # 500 ms

# Configure GPIO library
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(LED_PIN, GPIO.OUT)



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
        return psutil.sensors_temperatures()['cpu-thermal'][0].current

def main():

    variables = {
 #        'LED On': {
#            'type': 'bool',
#            'value': False,
#            'bind': led_control
#        },
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
		}

		
    }

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

        while True:
            if data_timer <= 0:
                device.publish_data()
                data_timer = DATA_SENDING_INTERVAL

            if diag_timer <= 0:
                device.publish_diag()
                diag_timer = DIAG_SENDING_INTERVAL

            sleep(POLL_INTERVAL)
            diag_timer -= POLL_INTERVAL
            data_timer -= POLL_INTERVAL

    except KeyboardInterrupt:
        cloud4rpi.log.info('Keyboard interrupt received. Stopping...')

    except Exception as e:
        error = cloud4rpi.get_error_message(e)
        cloud4rpi.log.exception("ERROR! %s %s", error, sys.exc_info()[0])

    finally:
        sys.exit(0)


if __name__ == '__main__':
    main()
