#!/bin/usr/env python

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.multipart import MIMEMultipart
import mimetypes
import base64
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from os.path import basename
from util.Config import Config

import email.mime.application

from apiclient import errors

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib 
# import yaml
# from pathlib import Path



def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def create_message_with_attachment(sender, to, subject, message_text,file, body_type='text'):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.
    file: The path to the file to be attached.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text, body_type)
    message.attach(msg)
    print(file)
    content_type, encoding = mimetypes.guess_type(file)
    # print(content_type, encoding)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
        print("*****")
        main_type, sub_type = content_type.split('/', 1)
    else:
        main_type, sub_type = content_type.split('/', 1)
        print(main_type, sub_type)
    if main_type in ['text', 'application/pdf','pdf']:
  
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        #msg.add_header("Content-Disposition", filename=file)
        msg.set_payload(fp.read())
        encoders.encode_base64(msg)
        fp.close()
      

    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    # print(msg)
    message.attach(msg)
    text = message.as_string() #.encode('UTF-8').decode('ascii')
    ## .encode('UTF-8')).decode('ascii')
    # message.attach(MIMEText(open(file, 'rb').read()), _subtype='pdf')
    return {"raw":base64.urlsafe_b64encode(text.encode('UTF-8')).decode('ascii')} #{'raw': base64.urlsafe_b64encode(message.as_string())}


## https://blog.mailtrap.io/sending-emails-in-python-tutorial-with-code-examples/

# body = "This is an example of how you can send a boarding pass in attachment with Python"
# message.attach(MIMEText(body, "plain"))

# filename = "yourBP.pdf"
# # Open PDF file in binary mode

# # We assume that the file is in the directory where you run your Python script from
# with open(filename, "rb") as attachment:
#     # The content type "application/octet-stream" means that a MIME attachment is a binary file
#     part = MIMEBase("application", "octet-stream")
#     part.set_payload(attachment.read())

# # Encode to base64
# encoders.encode_base64(part)

# # Add header 
# part.add_header(
#     "Content-Disposition",
    # f"attachment; filename= {filename}",
# )

# Add attachment to your message and convert it to string
# message.attach(part)
# text = message.as_string()


def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print ('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as e:  #errors.HttpError, error:
        print ('An error occurred: %s' % e)
# service = send_email()



def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message."""
    try:
        response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                             pageToken=page_token).execute()
            messages.extend(response['messages'])
        return messages
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)


def ListMessagesWithLabels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

    Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message."""
    try:
        response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                     labelIds=label_ids,
                                                     pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages
    except Exception as error:
        print ('An error occurred: %s' % error)


def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        print ('Message snippet: %s' % message['snippet'])
        return message
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)

def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

    Returns:
    A MIME Message, consisting of data from Message.
  """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

        print ('Message snippet: %s' % message['snippet'])

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

        mime_msg = email.message_from_string(msg_str)

        return mime_msg
    except errors.HttpError as error:
        print ('An error occurred: %s' % error)


