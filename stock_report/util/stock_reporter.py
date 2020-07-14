import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 
from yahoo_fin import stock_info as si
import numpy as np
import yfinance as yf
import datetime
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt

# matplotlib.use('agg')
sns.set_style('whitegrid')

# tm  = datetime.datetime.now()
# dir(tm)
# st = tm - datetime.timedelta(days=365)
# STARTDATE = st.strftime('%Y-%m-%d')


def get_stock(ticker):
    return si.get_data(ticker)

def buy_sell(df):
    Buy = []
    Sell = []
    flag = -1
    
    for i in range(len(df)):
        if df['MACD'][i] > df['signal'][i]:
            Sell.append(np.NaN)
            if flag != 1:
                Buy.append(df['signal'][i])
                flag =1
            else:
                Buy.append(np.NaN)
        elif df['MACD'][i] < df['signal'][i]:
            Buy.append(np.NaN)
            if flag != 0:
                Sell.append(df['signal'][i])
                flag =0
            else:
                Sell.append(np.NaN)
        else:
            Sell.append(np.NaN)
            Buy.append(np.NaN)
    return Buy, Sell

def company_name(tinker):
    try:
        stock = yf.Ticker(tinker)
        return stock.info['longName']
    except:
        return tinker

def process_df(ticker, START_DATE, config  ):
    df = get_stock(ticker)[['close']]
    df = df.loc[START_DATE:]
    short, long, macd_length  = config
    df['shortEWM'] = df.close.ewm(span=short, adjust=False).mean()
    df['longEWM'] = df.close.ewm(span=long, adjust=False).mean()
    df['MACD'] = df.shortEWM - df.longEWM
    df['signal'] = df.MACD.ewm(span=macd_length,adjust=False).mean()
    df['20_EMA'] = df.close.ewm(span=20,min_periods=0,adjust=False,ignore_na=False).mean()
    df['50_EMA'] = df.close.ewm(span=50,min_periods=0,adjust=False,ignore_na=False).mean()
    df['200_EMA'] = df.close.ewm(span=200,min_periods=0,adjust=False,ignore_na=False).mean()
    
#         print(df)
    BS = buy_sell(df)
    df['Buy'] = BS[0]
    df['Sell'] = BS[1]
    return df

def MACD_plot(df, tinker):
    fig, ax = plt.subplots(2,figsize=(15,6))
    ax[0].plot(df.index,df.close, label='stock price')
    
    ax[0].plot(df.index, df['20_EMA'], label='20 EMA', color = 'yellow')
    ax[0].plot(df.index, df['50_EMA'], label='50 EMA', color = 'orange')
    ax[0].plot(df.index, df['200_EMA'], label='200 EMA', color = 'red', linestyle='-.', linewidth=2, alpha=0.25)


    ax[1].plot(df.index, df.MACD, c='r', label='MACD')
    ax[1].plot(df.index, df.signal, c='g', label='Signal')
    ax[1].axhline(0, c='k', linestyle='--', linewidth=2,  alpha=0.5)

    ax[0].scatter(df.index, df.Buy+df.close, c='g', marker="^",label='Buy')
    ax[0].scatter(df.index, df.Sell+df.close, c='r', marker="v" ,label='Sell')
    companyname = company_name(tinker)
    ax[0].set_title(f'Stock: {companyname} Ticker:{tinker}')
    ax[0].legend()
    ax[1].legend()
    return fig, ax 

class config:
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

def convert_tinker(x):
    if x.startswith("LON"):
        tinker = f"{x.split(':')[1]}.L"
        return tinker
    else:
        return x


# df = process_df("BAR.L", STARTDATE, config.MACD_long())
# MACD_plot(df, "BAR.L")
