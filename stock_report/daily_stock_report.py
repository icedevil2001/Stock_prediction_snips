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
import time
from stock_news import stock_news 

def create_report():
    data = Config.load_data()
    for email_add in data.keys():
        # print('**',email_add)
        print('report: ',email_add, data[email_add])
        stock_reporter.create_report(data[email_add]['watch'], email_add)

def get_report(email_add):
    outdir = Config.report_dir()
    return str(outdir / '{}.stock_daily_report.pdf'.format(email_add))

def send_report():
    print('Send report')
    data = Config.load_data()
    for email_add in data:
        print(email_add,Config.sender_id)
        if not data[email_add]['stop']:
            msg  = Mail.create_message_with_attachment(
                            Config.sender_id(),
                            email_add, Config.subject(),
                            # Config.body(),
                            stock_news(data[email_add]['watch']),
                            get_report(email_add),
                            body_type='html'
                            )

            Mail.send_message(Config.Service(), Config.sender_id(), msg)
            # schedule.every(44).seconds.do(send_report).tag('send_report')
        # schedule.every().day.at(data[email_add]['time']).do(job_that_executes_once)
    # return schedule.CancelJob

print('-'*50)
print(f'Check inbox every hours: {Config.read_inbox_hr}')
print(f'Create report daily at: {Config.report_time}')
print(f'Send email at: {Config.default_time}')
print('-'*50)



# schedule.every(10).seconds.do(GetInbox)#.tag('read_email')

# schedule.every(12).seconds.do(create_report)#.tag('create_daily_report')
# schedule.every(15).seconds.do(send_report)#.tag('send_report')

schedule.every(Config.read_inbox_hr).hours.do(GetInbox).tag('read_email')
schedule.every().day.at(Config.report_time).do(create_report).tag('create_daily_report')
schedule.every().day.at(str(Config.default_time)).do(send_report).tag('send_report')
try:
    while True:
        schedule.run_pending() 
        time.sleep(3) 
        # schedule.clear()
except KeyboardInterrupt:
    print() 
    print('Interrupt')
    schedule.clear()







