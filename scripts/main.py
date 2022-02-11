# https://stackoverflow.com/questions/13363553/git-error-host-key-verification-failed-when-connecting-to-remote-repository


import pandas as pd
import numpy as np
import seaborn as sns


from modules import get_data, tops_bottoms

# this finds the market cycle tops and dates for larger time frames (500+ days),
# medium time frames (200 days) and small time frames (50 days)
BTCpricedata, _ = get_data.Price_data()
#marketmax, midmax, smallmax, marketmin, midmin, smallmin = tops_bottoms.BTCTopsandBottoms(BTCpricedata)


# bin funding rates, and then % drop/gain after
BTCdata, ETHdata = get_data.binance_data()




def fundingbins(BTCdata): # get the dates the funding rate is in each bin
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
            pricedates[idx].append([BTCpricedata.iloc[i]['low'], BTCpricedata.iloc[i]['high'], BTCpricedata.iloc[i]['volume']])
            z = 2

BTCpricebins(BTCpricedata, BTCdata)