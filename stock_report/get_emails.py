#!/usr/bin/env python

from util import send_email
# from pprint import pprint
import re
# from collections import defaultdict
import pickle
from pathlib import Path
import datetime
import re


def load_message_ids(f='data/message-id.plk'):
    f = Path(f)
    if f.exists():
        with open(f,'rb') as fh:
            return pickle.load(fh)
    else:
        return []
def write_message_ids(read_msg, f='data/message-id.plk'):
    with open(f, 'wb') as fh:
        pickle.dump(read_msg, fh)
        
        
def load_data(f='data/data.plk'):
    f = Path(f)
    if f.exists() and f.stat().st_size>0:
        with open(f, 'rb') as fh:
            return pickle.load(fh)
    else:
        if not f.parent.exists():
            f.parent.mkdir(parents=True)
        return {}  ## dict of dict
    
def write_data(data=None, f='data/data.plk'):
    
    if data:
        for k in data.keys():
            data[k]['watch'] = [x.upper() for x in  set(data[k]['watch'])]
            data[k]['unwatch'] = [x.upper() for x in  set(data[k]['unwatch'])]
        with open(f, 'wb') as fh:
            pickle.dump(data,fh)
            
def clean_email(email_add):
    return re.sub('(<|>)','',email_add)


def set_time(data, default="06:00"):
    tm = data['time']
    if tm == '' or tm is None:
        return default
    return tm

def time_format(timestr):
    def __timefmt__(timestr):
        if re.match('.*?(pm|am)', timestr.lower()):
            return '%I:%M%p'
        else:
            return '%H:%M'
    return datetime.datetime.strptime(timestr, __timefmt__(timestr)).time() 

def get_time(body):
    r = re.search(r'.*?time.(\d+:\d+)', body, flags = re.I | re.MULTILINE | re.DOTALL)
    if r:
        return time_format(r.groups(1)[0])
    return None

def get_msg_watch(BODY):
    watch = []
    add = False
    for text in BODY.strip().split():
        text = text.lower()
        if text in ['watch:', 'unwatch:','watch', 'unwatch']:
            add = True
            continue
        if text == 'end':
            add = False
            continue
        if add:
            yield text
            
def remove_from_list(value, alist):
    
    try:
        alist.remove(value)
#         print(alist)
    except Exception as e:
        print(e)
    
def setup_metadata():
    return {'watch': set(), 'unwatch': set(), 'time': None, 'stop': None}

def watch_stock(msg_ids,data,read_msg):
#     data = load_data()
    for msg_id in msg_ids:
        msg = send_email.GetMessage(service,'me', msg_id)
        BODY = msg['snippet'] 
        ## TODO: function to get email 
        for info in msg['payload']['headers']:
            for key, val in info.items():
                if val == 'Return-Path':
                    email_add = clean_email(info['value'])
                    if email_add not in data:
                        data[email_add] = setup_metadata()
                    watch = data[email_add]['watch']
                    set_time = get_time(BODY)
                    if set_time:
                        data[email_add]['time'] = set_time                 
                    for stock in get_msg_watch(BODY):
                        stock = stock.upper()

                        watch.add(stock)
                    data[email_add]['stop'] = False
        read_msg.append(msg_id)


def unwatch_stock(msg_ids,data,read_msg):
#     data = load_data()
    for msg_id in msg_ids:
#         print(msg_id)
        msg = send_email.GetMessage(service, 'me', msg_id)
        BODY = msg['snippet'] 
        ## TODO: function to get email 
        for info in msg['payload']['headers']:
            for key, val in info.items():
                if val == 'Return-Path':
                    email_add = clean_email(info['value'])
                    unwatch = data[email_add]['unwatch']
                    watch = data[email_add]['watch']
                    for stock in get_msg_watch(BODY):
                        stock = stock.upper()
                        unwatch.add(stock)
                        remove_from_list(stock, watch)
                    data[email_add]['stop'] = False
        read_msg.append(msg_id)
         
def stop_notification(msg_ids, data,read_msg):
#     data = load_data()
    for msg_id in msg_ids:
        msg = send_email.GetMessage(service,'me', msg_id)
        ## TODO: function to get email 
        for info in msg['payload']['headers']:
            for key, val in info.items():
                if val == 'Return-Path':
                    email_add = clean_email(info['value'])
                    data[email_add]['stop'] = True
        read_msg.append(msg_id)

        
        
def main():
    
    ## load read email 
    read_msg = load_message_ids()
    ## load from watch list
    data = load_data()
    ## start email service
    service = send_email.send_email()

    ## Search for watch, unwatch, stop
    watch_list = [x['id'] for x in send_email.ListMessagesMatchingQuery(service, 'me', 'subject:watch') if x['id'] not in read_msg]

    unwatch_list = [x['id'] for x in send_email.ListMessagesMatchingQuery(service, 'me', 'subject:unwatch') if x['id'] not in read_msg]
    stop_list = [x['id'] for x in send_email.ListMessagesMatchingQuery(service, 'me', 'subject:stop') if x['id'] not in read_msg]

  
    for action, msg_ids in zip(['watch', 'unwatch', 'stop'], [watch_list, unwatch_list, stop_list]):
        if len(msg_ids) == 0:
            continue
        if action == 'watch':
            print(action,msg_ids)
            watch_stock(msg_ids,data, read_msg)
        elif action == 'unwatch':
            print(action, msg_ids)
            unwatch_stock(msg_ids, data, read_msg)
        elif action == 'stop':
            print(action,msg_ids)
            stop_notification(msg_ids, data, read_msg)
    
    ## write data
    write_data(data)
    write_message_ids(read_msg)