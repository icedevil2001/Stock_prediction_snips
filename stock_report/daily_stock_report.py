from util import send_email, stock_reporter, Config 
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import matplotlib 
import yaml
from pathlib import Path


# matplotlib.use('agg')
# sns.set_style('whitegrid')
cwd  = Path(__file__).parent

with open( (cwd / 'config.yaml') ) as fh:
    config = yaml.load(fh, Loader=yaml.Loader)
print('**',config)
tm  = datetime.datetime.now()

st = tm - datetime.timedelta(days=365)
STARTDATE = st.strftime('%Y-%m-%d')
# print(STARTDATE)

skipped = []
plots = []

def create_report(tinker_list, email):
    with PdfPages('{}.stock_daily_report.pdf'.format(email)) as pdf:
        for tinker in tinker_list:
            stock = (stock_reporter.convert_tinker(tinker))
            print(stock)
            try:
                df = stock_reporter.process_df(stock, Config.STARTDATE, stock_reporter.config.MACD_long() )
                # print(df)
                plots.append(stock_reporter.MACD_plot(df, stock))
            except Exception as e:
                print(e)
                skipped.append(tinker)
            pdf.savefig()  # saves the current figure into a pdf page
            plt.close()
        print(f'Plots: {len(plots)}, skipped: {len(skipped)}')
        d = pdf.infodict()
        d['Title'] = 'Stock report'
        d['Author'] = 'Pri '
        # d['Subject'] = 'How to create a multipage pdf file and set its metadata'
        # d['Keywords'] = 'PdfPages multipage keywords author title subject'
        d['CreationDate'] = datetime.datetime.today()
        d['ModDate'] = datetime.datetime.today()

service = send_email.send_email()

for email_add in config['email_address']:
    msg  = send_email.create_message_with_attachment(
        'pri.info66@gmail.com',
        email_add, config['subject'],
        config['message'] + "\n" + "Error with: \n{}".format('\n'.join(skipped)),
        "stock_daily_report.pdf")

    send_email.send_message(service, 'pri.info66@gmail.com', msg)


