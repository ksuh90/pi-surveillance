#!/usr/bin/env python

import os
import sys
import time
import json
import requests
from datetime import datetime
import ConfigParser
from pubnub import Pubnub 
import RPi.GPIO as GPIO
from cloudant.account import Cloudant


config = ConfigParser.ConfigParser()
config.read('config.ini')

# connect to cloudant
db_name      = config.get('Cloudant', 'db_name')
db_username  = config.get('Cloudant', 'username')
db_api_key   = config.get('Cloudant', 'api_key')
db_api_pass  = config.get('Cloudant', 'api_pass')
cloudant     = Cloudant(db_api_key, db_api_pass, url='https://'+db_username+'.cloudant.com')
cloudant.connect()

# Pubnub setup
publish_key    = config.get('Pubnub', 'publish_key')
subscribe_key  = config.get('Pubnub', 'subscribe_key')
pubnub_channel = config.get('Pubnub', 'channel')
pubnub         = Pubnub(publish_key=publish_key, subscribe_key=subscribe_key)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIR_PIN = 18                  # for sensors
GPIO.setup(PIR_PIN, GPIO.IN)  # 

GREEN_LED = 13                  # for the LEDs
RED_LED = 26                    # green : indicates if the system is running
GPIO.setup(GREEN_LED, GPIO.OUT) # red : indicates the alert
GPIO.setup(RED_LED, GPIO.OUT)   #

def callback(resp, channel):
    try:
        if (resp['type'] == 'control'):
            print('Pubnub: callback')
            control(resp['option'])
    except:
        pass
    finally:
        pass    

def error(message):
    print("Pubnub: ERROR : " + str(message))
   
def connect(message):
    print("Pubnub: connected")
  
def reconnect(message):
    print("Pubnub: reconnected") 
  
def disconnect(message):
    print("Pubnub: disconnected")
  
pubnub.subscribe(channels=pubnub_channel, callback=callback, error=callback,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)

def prettify_time(timestamp):
    format = '%Y-%m-%dT%H-%M-%S'
    return datetime.fromtimestamp(timestamp).strftime(format)

def create_docid(timestamp):
    format = "log:%Y%m%dT%H%M%S"
    return datetime.fromtimestamp(timestamp).strftime(format)

def upload(docid, t_pretty, filename, manual=False):
    print('Uploading to db...')

    data = {
        '_id'      : docid,
        'timestamp': t_pretty,
        'filename' : filename,
        'manual'   : manual
    }

    new_document = cloudant[db_name].create_document(data)
    fp = open('img/'+filename, 'rb')
    data = fp.read()
    fp.close()
    new_document.put_attachment(filename, 'image/jpeg', data)

    if new_document.exists():
        print('Upload success!')
        # send live feed to webpage
        payload = {'type': 'doc', 'doc': new_document}
        pubnub.publish(pubnub_channel, payload)
        return True

    print('Failed to upload image.')
    return False

def send_email(t_pretty, filename, docid):
    print('Sending email...')

    url_img = 'https://%s:%s@%s.cloudant.com/%s/%s/%s' % \
              (db_api_key, db_api_pass, db_username, db_name, docid, filename)

    payload = {
        'option'     : 'email',
        'timestamp'  : t_pretty,
        'secret_key' : config.get('Secret', 'key'),
        'email'      : config.get('Email', 'email'),
        'filename'   : filename,
        'url_img'    : url_img,
        'img_type'   : 'image/jpeg',
        'url_webpage': config.get('API', 'control_webpage'),
    }
    url = config.get('API', 'email')
    r = requests.post(url, payload)
    print(r.text)

def say_cheese(t_pretty):
    filename = t_pretty + '.jpg'
    camera_resolution = config.get('Camera', 'resolution')
    command = "fswebcam -r %s %s" % (camera_resolution, 'img/'+filename)
    os.system(command)
    return filename

def alert(PIR_PIN):
    # red led ON
    GPIO.output(RED_LED, True)

    print('\r\n!!!!! Intruder Alert !!!!!\r\n')

    t        = time.time()
    docid    = create_docid(t)
    t_pretty = prettify_time(t)
    filename = say_cheese(t_pretty)

    upload(docid, t_pretty, filename)
    send_email(t_pretty, filename, docid)

    # red led OFF
    GPIO.output(RED_LED, False)

def control(option):
    print('Pubnub CONTROL: ' + option)
    t = time.time()
    t_pretty = prettify_time(t)

    if option == 'take_pic':
        filename = say_cheese(t_pretty)
        docid    = create_docid(t)
        upload(docid, t_pretty, filename, True)
    elif option == 'pause':
        aa = 111
    elif option == 'resume':
        aa = 111
    elif option == 'off':
        aa = 111
        #pubnub.unsubscribe(pubnub_channel)
    else:
        print('Unknown option.')


if __name__ == '__main__':

    # indicate that the system is running
    GPIO.output(GREEN_LED, True)
    GPIO.output(RED_LED, False)

    try:
        print('Booting sensor...')
        GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=alert)
        while True:
            time.sleep(100)

    except KeyboardInterrupt:
        print "Shutting down."

    finally:
        print('System shutdown.')
        pubnub.unsubscribe(channel=pubnub_channel)
        GPIO.cleanup()