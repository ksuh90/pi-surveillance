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
from cloudant.database import CloudantDatabase


config = ConfigParser.ConfigParser()
config.read('config.ini')

# connect to cloudant
db_name      = config.get('Cloudant', 'db_name')
db_username  = config.get('Cloudant', 'username')
db_api_key   = config.get('Cloudant', 'api_key')
db_api_pass  = config.get('Cloudant', 'api_pass')
client = Cloudant(db_api_key, db_api_pass, url='https://'+db_username+'.cloudant.com')
client.connect()

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
RED_LED = 26                    # green : indicates that the system is running
BLUE_LED = 5                    # blue : indicates remote command
GPIO.setup(GREEN_LED, GPIO.OUT) # red : indicates alert
GPIO.setup(RED_LED, GPIO.OUT)   #
GPIO.setup(BLUE_LED, GPIO.OUT)  #

# Global state vars
system_paused = False

def callback(resp, channel):
    try:
        if (resp['type'] == 'control_request'):
            print('Pubnub: callback')
            control(resp['option'])
    except:
        pass
    finally:
        pass    

def error(message):
    print('Pubnub: ERROR : ' + str(message))
   
def connect(message):
    print('Pubnub: connected')
  
def reconnect(message):
    print('Pubnub: reconnected') 
  
def disconnect(message):
    print('Pubnub: disconnected')
  
pubnub.subscribe(channels=pubnub_channel, callback=callback, error=callback,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)

def prettify_time(timestamp):
    format = '%Y-%m-%dT%H-%M-%S'
    return datetime.fromtimestamp(timestamp).strftime(format)

def create_docid(timestamp):
    format = 'log:%Y%m%dT%H%M%S'
    return datetime.fromtimestamp(timestamp).strftime(format)

def upload(docid, t_pretty, filename, manual=False):
    print('Uploading to db...')

    # compute the pk for this new entry
    db = CloudantDatabase(client, db_name)
    resp = db.get_view_raw_result('_design/view', 'log', reduce=True)
    if not resp['rows']:
        pk = 1
    else:
        pk = resp['rows'][0]['value']
        pk += 1

    data = {
        '_id'      : docid,
        'pk'       : pk,
        'timestamp': t_pretty,
        'filename' : filename,
        'manual'   : manual
    }
    new_document = client[db_name].create_document(data)
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
    command = 'fswebcam -r %s %s' % (camera_resolution, 'img/'+filename)
    os.system(command)
    return filename

def alert(PIR_PIN):
    global system_paused
    if system_paused:
        return True

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
    return True


def control(option):
    global system_paused
    print('Pubnub control option: ' + option)
    #GPIO.output(BLUE_LED, True)
    t = time.time()
    t_pretty = prettify_time(t)
    msg = ''
    if option == 'take_pic':
        if (upload(
            create_docid(t), t_pretty, say_cheese(t_pretty), True)):
            msg = 'Picture taken!'
    elif option == 'ping':
        msg = 'Pong!'
    elif option == 'pause':
        system_paused = True
        msg = 'System paused.'
    elif option == 'resume':
        system_paused = False
        msg = 'Resuming system.'
    else:
        msg = 'Unknown remote control option.'
        print(msg)

    # publish the response object
    pubnub.publish(pubnub_channel, {'type': 'control_resp', 'msg': msg})
    #GPIO.output(BLUE_LED, False)


if __name__ == '__main__':

    # ensure red led is off
    #time.sleep(10)
    GPIO.output(RED_LED, False)

    try:
        print('Booting system...')
        GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=alert)
        
        # indicate the system is ready
        GPIO.output(GREEN_LED, True)

        while True:
            time.sleep(100)

    finally:
        print('Shutting down...')
        pubnub.unsubscribe(channel=pubnub_channel)
        GPIO.cleanup()