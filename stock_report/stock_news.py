import requests
from datetime import datetime

from pprint import pprint
from dateutil.parser import parse
from datetime import datetime
from time import sleep
import jmespath


from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText


class Info:
    def __init__(self,symbol):
        self.token = 'pk_4667974e324a475cb0c4eabb796d2088'
        self.url = 'https://cloud.iexapis.com/v1/stock/'
        self.symbol = symbol.lower()
        self.data = self.get_data()
#         return 
    
    def get_data(self):
      
        URL='{}{}/batch?types=quote,news&range=1m&last=1&token={}'.format(self.url, self.symbol, self.token)
        response = requests.get(URL)
        if response.status_code == 200:
            return response.json()
        else:
            print('ERROR',self.symbol,response.status_code)
            return None 
            
    def get_news(self) :
        return jmespath.search('news[0].summary', self.data)#.encode('utf-8')#.decode("utf-8", "replace")
#         return self.data['news'][0]['summary']
        
    def get_source(self):
        return jmespath.search('news[0].source', self.data).encode('utf-8')
#         return self.data['news'][0]['source']
    def get_headline(self):
        return jmespath.search('news[0].headline', self.data).encode('utf-8')

        
    def get_datetime(self):
        ## https://stackoverflow.com/questions/10286224/javascript-timestamp-to-python-datetime-conversion
        return (datetime
                .utcfromtimestamp(
                    jmespath.search('news[0].datetime', self.data)/1000
                )
                .strftime('%Y-%m-%d %H:%M'))
    
    def companyName(self):
        return jmespath.search('quote.companyName', self.data)#.encode('utf-8')
    
    def price(self):
#         close = jmespath.search('quote.clsoe', self.data)
        d = []
        for key in ['close','change', 'high', 'low', 'avgTotalVolume']:
            data = self.data.get('quote',False)

            if data:
                d.append( "{}: {}".format(key, self.data['quote'].get(key, 'N/A') ) )
            else:
                d.append( "{}: {}".format(key, 'N/A') )
        return ' '.join(map(str,d))
                               
class Builder:
    ## Jinja2 Template builder 
    def __init__(self):
        return 
    
    def build_template(self, symbol, companyNames,  news, prices):
        try:
            ## Load the html tempate from template/email.html
            file_loader = FileSystemLoader('template')
            env = Environment(loader=file_loader)
            template =  env.get_template('email.html')
            
            ## Build Jinja2 template
            output = template.render(symbols=symbol, companyNames=companyNames,  news=news,prices=prices)
#             print(output)
            body = MIMEText(output, "html")
            return output #body 
        except Exception as e:
            print('ERROR - builder', e)
            print()


def stock_news(STOCKS):
    # STOCKS = ['AAPL','FSLY', 'MSFT']
    companyNames = []
    news = []
    prices = []

    for stock in STOCKS:
        stock_data = Info(stock)
        if not stock_data.get_data():
            print('News- skipped',stock)
            continue 
        print(stock)
        companyNames.append(stock_data.companyName())
        news.append(stock_data.get_news())
        prices.append(stock_data.price())
        sleep(.25)



    builder = Builder()
    report = builder.build_template(STOCKS, companyNames, news, prices)
    return report 
    # print(report)

    # # print(report)
    # with open('stock_report.html', 'w') as fileout:
    #     fileout.write(report)