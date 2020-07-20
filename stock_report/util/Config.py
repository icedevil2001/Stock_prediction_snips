import datetime
from pathlib import Path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



class Config:
    
    default_time = datetime.datetime.strptime('6:00', '%H:%M').time()
    wkd = Path(__file__).parents[1]
    

    data_path  = wkd / 'data' / 'data.plk'

    SCOPES = [
        # 'https://www.googleapis.com/auth/gmail.compose', 
        # 'https://www.googleapis.com/auth/gmail.labels', 
        'https://www.googleapis.com/auth/gmail.modify'
        ]
    def report_dir():
        report_dir = Path("reports") 
        if not report_dir.exists():
            report_dir.mkdir(parents=True)
        return report_dir

    def startdate():
        current_date =  datetime.datetime.now()
        st = current_date - datetime.timedelta(days=365)
        STARTDATE = st.strftime('%Y-%m-%d')
        return STARTDATE    

    def datelimit(days=90):
        current_date =  datetime.datetime.now()
        st = current_date - datetime.timedelta(days=days)
        return st.strftime('%Y-%m-%d')
    
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
            
                
    def setup_metadata():
        return {'watch': set(), 'unwatch': set(), 'time': None, 'stop': None}

    def subject():
        return "Daily stock report: {}".format(Config.current_date)
    def body():
        return """Daily stock report.\nBest Pri"""

    def Service():
        """Shows basic usage of the Gmail API.
        Lists the user's Gmail labels.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        token_path  = (Config.wkd / 'token.pickle')
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file( (Config.wkd /
                    'credentials.json'), Config.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        return service

    def sender_id():
        return  'me'

    def sender_email():
        return 'pri.info66@gmail.com'


class Signal:
    def MACD_long():
#         return dict( [("short",12), ("long",26),("macd_length",9)] )
        return ( 12,26,9 )
    def MACD_short():
#         return dict( [("short",5), ("long",35),("macd_length",5)] )
        return (5,35,5)
    def MACD_setting( short, long,macd_length ):
#         return dict( [("short",short), ("long", long),("macd_length",macd_length)] )
        return (short, long,macd_length )
# config.MACD_setting(1,2,3)