import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, date

from modules import get_data, tops_bottoms
from modules.tops_bottoms import BTCTopsandBottoms

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

    pricedates = []
    for i in range(0, len(BTCpricedata)):
        a = [BTCpricedata.iloc[i]['Date'] in list for list in bindates] # see what bins this date is in
        idx = [i for i, x in enumerate(a) if x]
        if idx == []:# get the index of the bin the date is in
            pass
        else:
            idx = idx[0]
            pricedates[idx].append([BTCpricedata.iloc[i]['Date'],BTCpricedata.iloc[i]['low'], BTCpricedata.iloc[i]['high'], BTCpricedata.iloc[i]['volume']])
    return pricedates, bindates


def merge_rates_price(BTCpricedata, BTCdata):
    # forgot about being able to merge datasets (duh), so the BTCpricebins and fundingbins functions are deprecated

    BTCdata = BTCdata.groupby('Date').mean('Funding Rate')
    BTCdata.reset_index(inplace=True)
    BTCdata['bin'] = pd.qcut(BTCdata['Funding Rate'], 5, precision=5, duplicates='drop', labels=False)
    BTCdata['bin'].value_counts()  # not even, but hard with such low numbers
    data_join = BTCpricedata.merge(BTCdata, how='left', on='Date')
    data_join = data_join[['Date', 'low', 'high', 'open', 'close', 'volume', 'Funding Rate', 'bin']]
    return data_join

def binsummary():
    data = merge_rates_price(BTCpricedata, BTCdata)
    # get max, min, quartiles, count for each bin
    df = pd.DataFrame()
    for i in np.unique(data['bin']):
        a = data[data['bin'] == i]
        min, max, vol = a['low'].min(), a['high'].max(), a['volume'].mean()
        a['avg'] = a[['high', 'low', 'open', 'close']].mean(axis=1)
        df[str(i)] = a['avg'].describe()
    return df[['0.0', '1.0', '2.0', '3.0']]

# want to take the prices and funding rates of each date and see where price was 7, 14, 28, 90, 180, 365 days into the future
def bincompare(BTCpricedata, BTCdata):
    data = merge_rates_price(BTCpricedata, BTCdata)

    changes = []
    for i in range(0, len(data)):
        dict, future_chg, future_dates = {}, [], []
            # date, high, low, vol, funding rate, bin, future date, %chg ...
        future_dates = [pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=7), pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=14),
                            pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=28), pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=90),
                            pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=180), pd.to_datetime(data.iloc[i][0]) + pd.DateOffset(days=365)]
        for f in future_dates:
            if f > date.today():
                f = date.today()
            fut_high = BTCpricedata.loc[BTCpricedata['Date'] == f].iloc[0][2]
            future_chg.append(((data.iloc[i][2] - fut_high) / data.iloc[i][2]) * 100)
        dict.update({
            'Date': data.iloc[i][0],
            'high': data.iloc[i][2],
            'low': data.iloc[i][1],
            'vol': data.iloc[i][5],
            'rate': data.iloc[i][6],
            'rate bin': data.iloc[i][7],
            'future_date': future_dates,
            'future_price': future_chg
        })
        changes.append(dict)

    return changes

def rate_atpeaks(BTCpricedata, BTCdata):
    """
    try and figure out what the funding rate is at the peaks, at the bottoms, is it the only time it gets there?
    :param BTCpricedata:
    :param BTCdata:
    :return:
    :takeaways: this showed that the funding rate itself does not have any correlation to peaks, but might to valleys
        (if funding rate <= 0 then...
    """

    data = merge_rates_price(BTCpricedata, BTCdata)
    marketmax, midmax, smallmax, marketmin, midmin, smallmin = BTCTopsandBottoms(BTCpricedata)

    other_marketmax, other_midmax, other_smallmax = [], [], []
    for i in marketmax:
        # get rate
        # are there any other dates with this rate
        # % of tops market tops at this rate
        rate = data[data['Date'] == i[1]]['Funding Rate'].values[0]
        rate_range = [rate - 0.00005, rate + 0.00005]
        #others = data[data['Funding Rate'] == rate]
        other_marketmax.append([i[1], data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])
    for i in midmax:
        # get rate
        # are there any other dates with this rate
        # % of tops market tops at this rate
        rate = data[data['Date'] == i[1]]['Funding Rate'].values[0]
        rate_range = [rate - 0.00005, rate + 0.00005]
        # others = data[data['Funding Rate'] == rate]
        other_midmax.append([i[1], data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])
    for i in smallmax:
        # get rate
        # are there any other dates with this rate
        # % of tops market tops at this rate
        rate = data[data['Date'] == i[1]]['Funding Rate'].values[0]
        rate_range = [rate - 0.00005, rate + 0.00005]
        # others = data[data['Funding Rate'] == rate]
        other_smallmax.append([i[1], data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])
    return other_marketmax, other_midmax, other_smallmax



def likelihood_of_peak(BTCpricedata, BTCdata):
    '''
    find the likelihood of there being a peak given a funding rate
        what about in 7 day groups?
        does one on macro signal micro?
    :param BTCpricedata:
    :param BTCdata:
    :return:
    '''
    marketmax, midmax, smallmax = rate_atpeaks(BTCpricedata, BTCdata)
    max_lh = []
    for i in marketmax:
        count = len(marketmax[i][1])
        max_lh.append([marketmax[i][0], 1/count])
    mid_lh = []
    for i in midmax:
        count = len(midmax[i][1])
        mid_lh.append([midmax[i][0], 1 / count])
    small_lh = []
    for i in smallmax:
        count = len(smallmax[i][1])
        mid_lh.append([smallmax[i][0], 1 / count])

def changes(BTCpricedata, BTCdata):
    # see relation between price, funding rate, and future prices
        # split into bins and see if the bin predicts a downturn? up turn? likelihood of going up x?
    changes = bincompare(BTCpricedata, BTCdata)
    data = pd.DataFrame(changes)
    data[['7days', '14days', '28days', '90days', '180days', '365days']] = pd.DataFrame(data.future_date.to_list(), index = data.index)
    data[['7days%', '14days%', '28days%', '90days%', '180days%', '365days%']] = pd.DataFrame(data.future_price.to_list(), index = data.index)
    data = data.drop(['future_date', 'future_price'], axis=1)

    bin7 = data.groupby('rate bin', dropna=True)['7days%'].mean()
    bin14 = data.groupby('rate bin', dropna=True)['14days%'].mean()
    bin28 = data.groupby('rate bin', dropna=True)['28days%'].mean()
    bin90 = data.groupby('rate bin', dropna=True)['90days%'].mean()
    bin180 = data.groupby('rate bin', dropna=True)['180days%'].mean()
    bin365 = data.groupby('rate bin', dropna=True)['365days%'].mean()


def fr_change(BTCpricedata, BTCdata):
    # by looking at some of the chanrts it tooks like even if the funding rate doesnt have a threshold, it may have a rate of change that could be concerning
    data = merge_rates_price(BTCpricedata, BTCdata)
    data['FR1day'] = (data['Funding Rate'].diff()) # diff between yesterday and today
    data['FR5day'] = data['Funding Rate'].diff(periods=5) # diff b/w 5 days ago and today
    data['FR5day%'] = data['FR5day'] / data['Funding Rate'] # % difference
    ## lets do the same for price to see if they are correlated
    data['Price1day'] = (data['high'].diff())  # diff between yesterday and today
    data['Price5day'] = data['high'].diff(periods=5)  # diff b/w 5 days ago and today
    data['Price5day%'] = data['Price5day'] / data['high']  # % difference



    # check against tops and bottoms
    marketmax, midmax, smallmax, marketmin, midmin, smallmin = BTCTopsandBottoms(BTCpricedata)

    # new col: tops and bottoms
        # marketmax = 3, midmax = 2, smallmax = 1, then oppo for mins
    data['TB'] = ''
    data.loc[data[data['Date'].isin(smallmax)].index.values, 'TB'] = 1
    data.loc[data[data['Date'].isin(midmax)].index.values, 'TB'] = 2
    data.loc[data[data['Date'].isin(marketmax)].index.values, 'TB'] = 3
    data.loc[data[data['Date'].isin(smallmin)].index.values, 'TB'] = -1
    data.loc[data[data['Date'].isin(midmin)].index.values, 'TB'] = -2
    data.loc[data[data['Date'].isin(marketmin)].index.values, 'TB'] = -3

    for j in range(-3,3, 1):
        for i in range(0, len(data[data['TB'] == j].index.values)):
            data.iloc[data[data['TB'] == 3].index.values[0] - 3: data[data['TB'] == 3].index.values[0]]


    z = 2
        # now i have the column, i can check the price% or fr % before max to see if there is any correlation
            # bin fr% change, price % change?

fr_change(BTCpricedata, BTCdata)
