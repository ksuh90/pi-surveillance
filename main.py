#!/usr/bin/env python

import os
import time
import datetime
import ConfigParser

# Pubnub
from pubnub import Pubnub 

# GPIO
import RPi.GPIO as GPIO

# modules for sending email
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# GPIO for the sensor
TRIG = 23
ECHO = 12
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

# GPIO for the LEDs
GREEN_LED = 13  # indicates if the system is running
RED_LED = 26    # indicates the alert
GPIO.setup(GREEN_LED, GPIO.OUT)
GPIO.setup(RED_LED, GPIO.OUT)

config = ConfigParser.ConfigParser()
config.read('config.ini')

# initialize variables from config.ini
publish_key       = config.get('Pubnub', 'publish_key')
subscribe_key     = config.get('Pubnub', 'subscribe_key')
email             = config.get('Email', 'email')
camera_resolution = config.get('Camera', 'resolution')
border_distance   = int(config.get('Border', 'distance'))

# Pubnub api setup
pubnub = Pubnub(publish_key=publish_key, subscribe_key=subscribe_key)
channel = 'Rangefinder'


def say_cheese(filename):
    command = "fswebcam -r %s %s" % (camera_resolution, filename)
    os.system(command)
    return filename

def send_email(filename):
    print 'sending email...'
    msg = MIMEMultipart()
    msg['Subject'] = 'ALERT from the Pi'
    msg['From'] = email
    msg['To'] = email
    msg.preamble = 'There has been an intruder!'

    fp = open(filename, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    msg.attach(img)
    server = smtplib.SMTP('localhost', 1025)
    server.sendmail(email, email, msg.as_string())
    server.quit()

def publish_to_pubnub():
    # Publish the measured distance to PubNub
    '''
    message = {
        'distance': distance,
        'time': '....'
    }
    '''
    #print pubnub.publish(channel, message)

    return True

def alert_owner(timestamp):

    print "!!!!! Intruder Alert !!!!!"

    format = '%Y-%m-%dT%H-%M-%S'
    timestamp_formatted = datetime.datetime.fromtimestamp(timestamp).strftime(format)
    filename = say_cheese(timestamp_formatted+'.jpg')
    #send_email(filename)
    #publish to pubnub



if __name__ == '__main__':

    # indicate that the system is running
    GPIO.output(GREEN_LED, True)

    # Boot the trigger
    GPIO.output(TRIG,False)
    print("Waiting for sensor to settle.")
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
            
            print("Distance:", distance, "cm")

            # test if proximity breached the border
            if (distance < border_distance):
                GPIO.output(RED_LED, True)
                alert_owner(pulse_start)
                GPIO.output(RED_LED, False)

            time.sleep(1)

    finally:
        print 'Shutting down system...'
        GPIO.cleanup()