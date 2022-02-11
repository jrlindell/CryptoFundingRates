# PROMPT
#Take the funding rates of BTC and ETH going back to Jan 2018 from an equally weighted index of BitMex and Binance.
#Then test and see which levels of funding correspond to market peaks and bottom. Separate them into equal groups.
#The goal is to find the best time to buy and sell based around funding, giving you the highest returns.
#A good example would include: “when funding is in X percentile, the likelihood of a 5 percent correction  is Y.
#The likelihood of a 10 percent correction is Z. Different variables laddered down to 30 to 50%. To see the correlation.”
#There’s a lot you can do with funding, even tracking how correlated the price is to funding.
#If higher funding leads to an increase in volatility, or a lower increase. If so, how correlated is it?
#It’s flexible, the thing is for you to show your knowledge so I’ll let you have range to explore.



# PACKAGES
import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
import Historic_Crypto
import matplotlib.pyplot as plt

# need to grab the tables from bitmex to start
def bitmex_data():
    url_base = 'https://www.bitmex.com/app/fundingHistory?start='
    # the number changes by 100 for each page
    page = 0
    table_headers = []
    while True:
        url = url_base + str(page)
        bitmex = requests.get(url)
        html = bitmex.text
        soup = BeautifulSoup(html)
        data = soup.find_all('table')[0].find('tr')
        tbl = soup.find('tbody')

def binance_data():
    BTCdata = pd.read_csv('/Users/footb/Downloads/Funding Rate History_BTCUSD Perpetual_2022-02-10.csv')
    BTCdata['Date'] = pd.to_datetime(BTCdata['Time']).dt.date
    BTCdata['Time'] = pd.to_datetime(BTCdata['Time']).dt.time
    BTCdata['Funding Rate'] = (BTCdata['Funding Rate'].str.rstrip('%').astype('float') / 100.0)
    #BTCdata['Funding Rate'] = float(BTCdata['Funding Rate'].apply(lambda x: '%.8f' % x))
    BTCdata = BTCdata[['Date', 'Time', 'Funding Interval', 'Funding Rate']]
    ETHdata = pd.read_csv('/Users/footb/Downloads/Funding Rate History_ETHUSD Perpetual_2022-02-10.csv')
    return BTCdata, ETHdata


def Price_data():
    BTC_pricedata = Historic_Crypto.HistoricalData('BTC-USD', 86400, '2018-01-01-00-00').retrieve_data()
    BTC_pricedata.index.name = 'Date'
    BTC_pricedata.reset_index(inplace=True)
    BTC_pricedata['Date'] = pd.to_datetime(BTC_pricedata['Date']).dt.date
    BTC_pricedata = BTC_pricedata[['Date', 'low', 'high', 'open', 'close', 'volume']]
    ETH_pricedata = Historic_Crypto.HistoricalData('ETH-USD', 86400, '2018-01-01-00-00').retrieve_data()
    ETH_pricedata.index.name = 'Date'
    ETH_pricedata.reset_index(inplace=True)
    ETH_pricedata['Date'] = pd.to_datetime(ETH_pricedata['Date']).dt.date
    ETH_pricedata = ETH_pricedata[['Date', 'low', 'high', 'open', 'close', 'volume']]
    return BTC_pricedata, ETH_pricedata




