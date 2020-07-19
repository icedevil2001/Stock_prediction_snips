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
import email
import email.mime.application



# SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


# def send_email():
#     """Shows basic usage of the Gmail API.
#     Lists the user's Gmail labels.
#     """
#     creds = None
#     # The file token.pickle stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.pickle'):
#         with open('token.pickle', 'rb') as token:
#             creds = pickle.load(token)
#     # If there are no (valid) credentials available, let the user log in.
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.pickle', 'wb') as token:
#             pickle.dump(creds, token)

#     service = build('gmail', 'v1', credentials=creds)

#     return service


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

def create_message_with_attachment(sender, to, subject, message_text, file):
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

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type, encoding = mimetypes.guess_type(file)
    print(content_type, encoding)
    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
        print("*****")
        main_type, sub_type = content_type.split('/', 1)
    else:
        main_type, sub_type = content_type.split('/', 1)
        print(main_type, sub_type)
    if main_type in ['text', 'application/pdf','pdf']:
        print("HERE")
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
        print('**',main_type, sub_type)
        msg = MIMEBase(main_type, sub_type)
        # msg.add_header("Content-Disposition", filename=file)
        msg.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(msg)


    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)
    # print(message)
    text = message.as_string()
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
    except Exception as e:  #errors.HttpError, error:
        print ('An error occurred: %s' % e)
# service = send_email()


