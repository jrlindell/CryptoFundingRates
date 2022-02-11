import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime

from modules import get_data, tops_bottoms

# this finds the market cycle tops and dates for larger time frames (500+ days),
# medium time frames (200 days) and small time frames (50 days)
BTCpricedata, _ = get_data.Price_data()
#marketmax, midmax, smallmax, marketmin, midmin, smallmin = tops_bottoms.BTCTopsandBottoms(BTCpricedata)


# bin funding rates, and then % drop/gain after
BTCdata, ETHdata = get_data.binance_data()




def fundingbins(BTCdata): # get the dates the funding rate is in each bin
    '''

    :param BTCdata: input from the binance_data in the get_data module. This is the funding rate for BTC on binance
    :what is happening:
        the bins are calculating for the Funding rates (split into 5 bins), and they are uneven, but that is b/c the funding rates are
        very small numbers and the pandas.qcut can't figure that out. i am sure there is a way to do this better manually.
        the funding rates are put into bins, within the bindates param
    :param bindates: split into the amount of bins, each having a list of dates associated with that bin.
        example: if the funding rate -0.0002 is in bin 1, then the date that is associated with will be placed into the bindates[1]
    :return:
    '''
    BTCdata = BTCdata.groupby('Date').mean('Funding Rate')
    BTCdata.reset_index(inplace=True)
    BTCdata['bin'] = pd.qcut(BTCdata['Funding Rate'], 5, precision=5, duplicates='drop', labels=False)
    BTCdata['bin'].value_counts() # not even, but hard with such low numbers
    bindates =  [[] for x in range(5)]

    for i in range(0, len(BTCdata)):
        # get date
        bindates[BTCdata.iloc[i]['bin']].append(BTCdata.iloc[i]['Date'])
    return bindates


def BTCpricebins(BTCpricedata, BTCdata):
    '''

    :param BTCpricedata: this is the price date for BTC coming from the Historic Crypto package
    :param BTCdata: BTCdata: input from the binance_data in the get_data module. This is the funding rate for BTC on binance
    : what is happening:
        taking the bindates parameter from fundingbins, we are trying to put the prices of the same date into the same bins
            example: if funding rate of -0.0003 occured on 11/20/2020, then this will get the prices and volume for that date and
            put it into pricedates
    :return:
    '''
    bindates = fundingbins(BTCdata)
    # want toget the price at each date in each bin
        # get 14 day lookahead price

    pricedates = [[] for x in range(5)]
    for i in range(0, len(BTCpricedata)):
        a = [BTCpricedata.iloc[i]['Date'] in list for list in bindates] # see what bins this date is in
        idx = [i for i, x in enumerate(a) if x]
        if idx == []:# get the index of the bin the date is in
            pass
        else:
            idx = idx[0]
            pricedates[idx].append([BTCpricedata.iloc[i]['Date'],BTCpricedata.iloc[i]['low'], BTCpricedata.iloc[i]['high'], BTCpricedata.iloc[i]['volume']])
    return pricedates, bindates

# want to take the prices and funding rates of each date and see where price was 7, 14, 28, 90, 180, 365 days into the future

def bincompare(BTCpricedata, BTCdata):
    pricedates, bindates = BTCpricebins(BTCpricedata, BTCdata)

    bin1, bin2, bin3, bin4, bin5 = [], [], [], [], [] # for simplicity I am creating multiple lists for the data, but would have normall
    for i in pricedates:
        i[0], i[1], i[2], i[3] = date, low, high, vol
        change = []
        fut = pd.to_datetime(i[0]) + pd.DateOffset(days=7) # get the day in the future we want
        fut_info = BTCpricedata.loc[BTCpricedata['Date'] == fut] # get info for that day
        fut_high = fut_info.iloc[0][2]
        price_chg = ((i[2] - fut_high) / i[2]) * 100

    z = 2

bincompare(BTCpricedata, BTCdata)