#!/usr/bin/env python

from util import Mail
# from pprint import pprint
import re
# from collections import defaultdict
import pickle
from pathlib import Path
import datetime
import re
# from util import Config 
from util.Config import Config
from util import Mail



            
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
        msg = Mail.GetMessage(Config.Service(), Config.sender_id(), msg_id)
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
        msg = Mail.GetMessage(Config.Service(), Config.sender_id(), msg_id)
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
        msg = Mail.GetMessage(Config.Service(), Config.sender_id(), msg_id)
        ## TODO: function to get email 
        for info in msg['payload']['headers']:
            for key, val in info.items():
                if val == 'Return-Path':
                    email_add = clean_email(info['value'])
                    data[email_add]['stop'] = True
        read_msg.append(msg_id)

        
        
def GetInbox():
    # print(dir(Config))
    ## load read email 
    read_msg = Config.load_message_ids()
    ## load from watch list
    data = Config.load_data()
    print(data)
    ## start email service
    service = Config.Service()

    # print(Mail.ListMessagesMatchingQuery(service, Config.sender_email(),'') )
    ## Search for watch, unwatch, stop
    watch_list = [x['id'] for x in Mail.ListMessagesMatchingQuery(service, Config.sender_email(), 'subject:watch') if x['id'] not in read_msg]

    unwatch_list = [x['id'] for x in Mail.ListMessagesMatchingQuery(service, Config.sender_email(), 'subject:unwatch') if x['id'] not in read_msg]
    stop_list = [x['id'] for x in Mail.ListMessagesMatchingQuery(service, Config.sender_email(), 'subject:stop') if x['id'] not in read_msg]

    print(watch_list, unwatch_list, stop_list)
  
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
    print(data)
    Config.write_data(data)
    Config.write_message_ids(read_msg)


if __name__ == "__main__":
    GetInbox()
    