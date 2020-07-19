import datetime
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



class Config:
    
    default_time = datetime.datetime.strptime('6:00', '%H:%M').time()
    wkd = Path(__file__).parents[1]
    current_date =  datetime.datetime.now()

    data_path  = wkd/'data'/'data.plk'

    def stardate()
        st = current_date - datetime.timedelta(days=365)
        STARTDATE = st.strftime('%Y-%m-%d')
    
    def load_data(f=data_path):
        f = Path(f)
        if f.exists() and f.stat().st_size>0:
            with open(f, 'rb') as fh:
                return pickle.load(fh)
        else:
            if not f.parent.exists():
                f.parent.mkdir(parents=True)
            return {}
    
    def write_data(data=None, f=data_path):
        if data:
            with open(f, 'wb') as fh:
                pickle.dump(data,fh)
            
    def setup_metadata():
        return {'watch': set(), 'unwatch': set(), 'time': None, 'stop': None}

    def subject():
        return "Daily stock report: {}".format(Config.current_date)
    def body():
        return """Daily stock report.\nBest Pri"""


class Mail: 
    SCOPES = [
        # 'https://www.googleapis.com/auth/gmail.compose', 
        # 'https://www.googleapis.com/auth/gmail.labels', 
        'https://www.googleapis.com/auth/gmail.modify'
        ]

    def Service():

        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path  = (Config.wkd / 'token.pickle')
        if token_path:
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file( (Config.wkd /
                    'credentials.json'), Mail.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        return service

        def sender_id:
            return  'me'

        def sender_email:
            return 'pri.info66@gmail.com'