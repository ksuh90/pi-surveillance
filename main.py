#!/usr/bin/env python

import os
import time
from datetime import datetime
import ConfigParser
from pubnub import Pubnub 
import RPi.GPIO as GPIO
from cloudant.account import Cloudant


config = ConfigParser.ConfigParser()
config.read('config.ini')

# initialize variables from config.ini
publish_key       = config.get('Pubnub', 'publish_key')
subscribe_key     = config.get('Pubnub', 'subscribe_key')
email             = config.get('Email', 'email')
camera_resolution = config.get('Camera', 'resolution')
border_distance   = int(config.get('Border', 'distance'))
db_name           = config.get('Cloudant', 'db_name')
db_username       = config.get('Cloudant', 'username')
db_api_key        = config.get('Cloudant', 'api_key')
db_api_pass       = config.get('Cloudant', 'api_pass')

# connect to cloudant
cloudant = Cloudant(db_api_key, db_api_pass, url='https://'+db_username+'.cloudant.com')
cloudant.connect()

# Pubnub api setup
pubnub = Pubnub(publish_key=publish_key, subscribe_key=subscribe_key)
channel = 'Rangefinder'

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

TRIG = 23                   # for sensors
ECHO = 12                   # 
GPIO.setup(TRIG,GPIO.OUT)   #
GPIO.setup(ECHO,GPIO.IN)    #

GREEN_LED = 13                  # for the LEDs
RED_LED = 26                    # green : indicates if the system is running
GPIO.setup(GREEN_LED, GPIO.OUT) # red : indicates the alert
GPIO.setup(RED_LED, GPIO.OUT)   #



def upload(timestamp, filename, manual=False):

    print 'Uploading to db...'
    
    db = cloudant[db_name]
    data = {
        'timestamp': timestamp,
        'filename' : filename,
        'manual'   : manual
    }
    new_document = db.create_document(data)
    fp = open('img/'+filename, 'rb')
    data = fp.read()
    fp.close()
    new_document.put_attachment(filename, 'image/jpeg', data)
    
    if new_document.exists():
        print 'Upload success!'


def say_cheese(timestamp):
    filename = timestamp+'.jpg'
    command = "fswebcam -r %s %s" % (camera_resolution, 'img/'+filename)
    os.system(command)
    return filename


def alert_owner(timestamp):

    print '!!!!! Intruder Alert !!!!!'

    format = '%Y-%m-%dT%H-%M-%S'
    timestamp_formatted = datetime.fromtimestamp(timestamp).strftime(format)
    filename = say_cheese(timestamp_formatted)
    upload(timestamp_formatted, filename)
    # POST call to https://k-suh.com/api/pi-surveillance



if __name__ == '__main__':

    # indicate that the system is running
    GPIO.output(GREEN_LED, True)
    GPIO.output(RED_LED, False)

    # Boot the trigger
    GPIO.output(TRIG, False)
    print 'Booting  the sensor...'
    time.sleep(3)


    try:
        print 'Press Ctrl-C to quit.'
        while True:
            # Fire the trigger
            GPIO.output(TRIG, True)
            time.sleep(0.00001)
            GPIO.output(TRIG, False)

            # Instatiate a time stamp for when a signal is detected by setting beginning + end values.
            # Then subtract beginning from end to get duration value.

            pulse_start = time.time()
            while GPIO.input(ECHO) == 0:
                pulse_start = time.time()

            while GPIO.input(ECHO) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start

            # Speed of sound at sea-level is 343 m/s.
            # 34300 cm/s = Distance/Time; 34300 cm/s = Speed of sound;
            # "Time" is there and back; divide by 2 to get time-to-object only.
            # So: 34300 = Distance/(Time/2) >>> speed of sound = distance/one-way time

            # Simplify + Flip it: distance = pulse_duration x 17150
            distance = pulse_duration * 17150

            # Round out distance(in centimeters) for simplicity and print.
            distance = round(distance, 0)

            print 'Distance: %s cm' % (distance)

            # test if proximity breached the border
            if (distance < border_distance):
                GPIO.output(RED_LED, True)
                alert_owner(pulse_start)
                GPIO.output(RED_LED, False)

            time.sleep(1)

    finally:
        print 'Shutting down system...'
        GPIO.cleanup()
