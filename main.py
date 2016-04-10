#!/usr/bin/env python

import os
import sys
import time
import json
import socket
import requests
import ConfigParser
import RPi.GPIO as GPIO
from datetime import datetime
from pubnub import Pubnub 
from cloudant.account import Cloudant
from cloudant.database import CloudantDatabase


config = ConfigParser.ConfigParser()
config.read('config.ini')

# connect to cloudant
db_name      = config.get('Cloudant', 'db_name')
db_username  = config.get('Cloudant', 'username')
db_api_key   = config.get('Cloudant', 'api_key')
db_api_pass  = config.get('Cloudant', 'api_pass')
client = Cloudant(db_api_key, db_api_pass, 
                  url='https://'+db_username+'.cloudant.com')

# Pubnub setup
publish_key    = config.get('Pubnub', 'publish_key')
subscribe_key  = config.get('Pubnub', 'subscribe_key')
pubnub_channel = config.get('Pubnub', 'channel')
pubnub         = Pubnub(publish_key=publish_key,
                        subscribe_key=subscribe_key)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIR_PIN = 18                  # for sensors
GPIO.setup(PIR_PIN, GPIO.IN)  # 

GREEN_LED = 13                  # for the LEDs
RED_LED = 26                    # green : indicates that the system is running
GPIO.setup(GREEN_LED, GPIO.OUT) # red : indicates alert
GPIO.setup(RED_LED, GPIO.OUT)   #

# Global state vars
system_paused = False
email_notification = True

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
  
def prettify_time(timestamp):
    format = '%Y-%m-%dT%H-%M-%S'
    return datetime.fromtimestamp(timestamp).strftime(format)

def upload(t_pretty, filename, manual=False):
    print('Uploading to db...')

    # compute the pk for this new entry
    db = CloudantDatabase(client, db_name)
    resp = db.get_view_raw_result('_design/view', 'log', reduce=True)
    if not resp['rows']:
        pk = 1
    else:
        pk = resp['rows'][0]['value']
        pk += 1

    docid = 'log:' + str(pk)
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
        return docid

    print('Failed to upload image.')
    return False

def send_email(t_pretty, filename, docid):
    print('Sending email...')
    payload = {
        'option'     : 'email',
        'timestamp'  : t_pretty,
        'secret_key' : config.get('Secret', 'key'),
        'email'      : config.get('Email', 'email'),
        'filename'   : filename,
        'url_image'  : docid + '/' + filename,
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
    global system_paused, email_notification
    if system_paused:
        return True

    # red led ON
    GPIO.output(RED_LED, True)

    print('\r\n!!!!! Intruder Alert !!!!!\r\n')

    t        = time.time()
    t_pretty = prettify_time(t)
    filename = say_cheese(t_pretty)
    docid = upload(t_pretty, filename)
    if (email_notification):
        send_email(t_pretty, filename, docid)

    # red led OFF
    GPIO.output(RED_LED, False)
    return True

def control(option):
    global system_paused, email_notification
    print('Pubnub control option: ' + option)

    t = time.time()
    t_pretty = prettify_time(t)
    msg = ''
    if option == 'take_pic':
        if (upload(t_pretty, say_cheese(t_pretty), True)):
            msg = 'Picture taken!'
    elif option == 'pause':
        system_paused = True
        msg = 'System paused.'
    elif option == 'resume':
        system_paused = False
        msg = 'Resuming system.'
    elif option == 'email_on':
        email_notification = True
        msg = 'Email notification turned on.'
    elif option == 'email_off':
        email_notification = False
        msg = 'Email notification off.'
    elif option == 'ping':
        msg = 'Pong!'
        msg = msg + ('  [System: paused]' if system_paused else '')
        msg = msg + '  [Email notification: ' + \
                    ('on' if email_notification else 'off') + ']'
    else:
        msg = 'Unknown remote control option.'
        print(msg)

    # publish the response object
    pubnub.publish(pubnub_channel, {'type': 'control_resp', 'msg': msg})

def has_internet():
    remote_server = 'www.google.com'
    try:
        host = socket.gethostbyname(remote_server)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        pass
    return False


if __name__ == '__main__':

    # ensure we have internet connection
    # mark every 10 minutes
    startup_time = time.time()
    while not has_internet():
        elapsed = time.time() - startup_time
        if elapsed % 600 == 0:
            print '%s mins without internet connection...' % (elapsed/60)

    # connect to cloudant client
    client.connect()

    # subscribe to pubnub channel
    pubnub.subscribe(channels=pubnub_channel, callback=callback, error=callback,
                 connect=connect, reconnect=reconnect, disconnect=disconnect)

    # ensure red led is off
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