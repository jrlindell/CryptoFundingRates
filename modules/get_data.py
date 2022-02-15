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
import time

import numpy as np
from bs4 import BeautifulSoup
import requests
import pandas as pd
import Historic_Crypto
from selenium import webdriver
import matplotlib.pyplot as plt
import re

from webdriver_manager.chrome import ChromeDriverManager

# need to grab the tables from bitmex to start
def bitmex_data(): #wanted to try and get the data w/o using APIs
    url_base = 'https://www.bitmex.com/app/fundingHistory?start='
    # the number changes by 100 for each page
    page = 0
    total_data = []
    while True:
        url = url_base + str(page)
        driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
        driver.get(url)
        text_area = driver.find_element_by_xpath('//*[@id="filter"]')
        text_area.send_keys('{"symbol":"XBTUSD"}')
        button = driver.find_element_by_xpath('/html/body/div[2]/div/span/div[2]/div/div/section/div/div/div/form/fieldset/div/div/div[2]/button[2]')
        button.click()
        time.sleep(5)
        jb = driver.find_element_by_xpath("/html/body/div[2]/div/span/div[2]/div/div/section/div/div/div/div[2]/div[2]/div[2]/table/tbody")
        time.sleep(3)
        a = jb.text
        if a == 'No data.':
            break
        list = a.splitlines()

        array = []
        for i in list:
            newlist = re.split(' AM | PM | every 8 hours |\%', i)[0:4]
            array.append(newlist)
        page += 100
        total_data.extend(array)
        driver.close()
    pd.DataFrame(total_data).to_csv('data/BitmexBTC2.csv')

def Bitmex2():
    BTCdata = pd.read_csv('/Users/footb/Desktop/Misc/Finance/Crypto/CarterProject/data/BitmexBTC2.csv')
    BTCdata['Date'] = pd.to_datetime(BTCdata['Time']).dt.date
    BTCdata = BTCdata[['Date', 'Funding Rate']]
    return BTCdata

def binance_data():
    BTCdata = pd.read_csv('/Users/footb/Desktop/Misc/Finance/Crypto/CarterProject/data/Funding Rate History_BTCUSDT Perpetual_2022-02-11.csv')
    BTCdata['Date'] = pd.to_datetime(BTCdata['Time']).dt.date
    BTCdata['Time'] = pd.to_datetime(BTCdata['Time']).dt.time
    BTCdata['Funding Rate'] = (BTCdata['Funding Rate'].str.rstrip('%').astype('float') / 100.0)
    #BTCdata['Funding Rate'] = float(BTCdata['Funding Rate'].apply(lambda x: '%.8f' % x))
    BTCdata = BTCdata[['Date', 'Time', 'Funding Interval', 'Funding Rate']]
    return BTCdata

def FR_data():
    bitmex = Bitmex2()
    binance = binance_data()
    binance = binance[['Date', 'Funding Rate']]
    bitmex = bitmex.groupby('Date').mean()
    bitmex.reset_index(inplace=True)
    binance = binance.groupby('Date').mean()
    binance.reset_index(inplace=True)
    data = []
    for i in range(0, len(bitmex)):
        date = bitmex.iloc[i]['Date']
        binfr = binance[binance['Date'] == date]['Funding Rate'].values.tolist()
        if binfr == []:
            fr = bitmex.iloc[i]['Funding Rate']
        else:
            fr = (bitmex.iloc[i]['Funding Rate'] + binfr) / 2
        data.append([date, fr])
    data = pd.DataFrame(data)
    data.columns = ['Date', 'Funding Rate']

    return data

def Price_data():
    fr = FR_data()
    BTC_pricedata = Historic_Crypto.HistoricalData('BTC-USD', 86400, '2016-05-14-00-00').retrieve_data()
    BTC_pricedata.index.name = 'Date'
    BTC_pricedata.reset_index(inplace=True)
    BTC_pricedata['Date'] = pd.to_datetime(BTC_pricedata['Date']).dt.date
    BTC_pricedata = BTC_pricedata[['Date', 'low', 'high', 'open', 'close', 'volume']]
    ETH_pricedata = Historic_Crypto.HistoricalData('ETH-USD', 86400, '2016-05-14-00-00').retrieve_data()
    ETH_pricedata.index.name = 'Date'
    ETH_pricedata.reset_index(inplace=True)
    ETH_pricedata['Date'] = pd.to_datetime(ETH_pricedata['Date']).dt.date
    ETH_pricedata = ETH_pricedata[['Date', 'low', 'high', 'open', 'close', 'volume']]
    return BTC_pricedata, ETH_pricedata




