# from util import send_email, stock_reporter, Config 
# import datetime
# from matplotlib.backends.backend_pdf import PdfPages
# import matplotlib.pyplot as plt
# import matplotlib 
# import yaml
# from pathlib import Path
from util.Config import Config
from util import Mail, stock_reporter
import schedule
from get_emails  import GetInbox



def create_report():
    data = Config.load_data()
    for email_add in data.keys():
        # print('**',email_add)
        print('report: ',email_add, data[email_add])
        stock_reporter.create_report(data[email_add]['watch'], email_add)

def get_report(email_add):
    outdir = Config.report_dir()
    return outdir / '{}.stock_daily_report.pdf'.format(email_add)

def send_report():
    data = Config.load_data()
    for email_add in data:
        if not data[email_add]['stop']:
            msg  = Mail.create_message_with_attachment(
                            Config.sender_id,
                            email_add, Config.subject(),
                            Config.body(),
                            get_report(email_add))

            Mail.send_message(Config.Service(), Config.sender_id(), msg)

schedule.every(30).seconds.do(GetInbox).tag('read_email')

schedule.every(32).seconds.do(create_report).tag('create_daily_report')

schedule.every(34).seconds.do(send_report).tag('send_report')

try:
    while True:
        schedule.run_pending()   
except KeyboardInterrupt:
    print() 
    print('Interrupt')
    schedule.clear()







