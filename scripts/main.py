import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, date

from modules import get_data, tops_bottoms
from modules.tops_bottoms import BTCTopsandBottoms

# this finds the market cycle tops and dates for larger time frames (500+ days),
# medium time frames (200 days) and small time frames (50 days)
BTCpricedata, _ = get_data.Price_data()
BTCpricedata = BTCpricedata[1326:]
#marketmax, midmax, smallmax, marketmin, midmin, smallmin = tops_bottoms.BTCTopsandBottoms(BTCpricedata)


# bin funding rates, and then % drop/gain after
#BTCdata, ETHdata = get_data.binance_data()
BTCdata = get_data.FR_data()
BTCdata = BTCdata[1327:]



def fundingbins(BTCdata): # old
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
    BTCdata['bin'] = pd.qcut(BTCdata['Funding Rate'], 5, precision=5, duplicates='drop', labels=False)
    BTCdata['bin'].value_counts() # not even, but hard with such low numbers
    bindates =  [[] for x in range(5)]

    for i in range(0, len(BTCdata)):
        # get date
        bindates[BTCdata.iloc[i]['bin']].append(BTCdata.iloc[i]['Date'])
    return bindates


def BTCpricebins(BTCpricedata, BTCdata): # old
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



    data_join = BTCpricedata.merge(BTCdata, how='left', on='Date')
    data_join = data_join[['Date', 'low', 'high', 'open', 'close', 'volume', 'Funding Rate']]
    #data_join = data_join[data_join['Date'] >= data_join.iloc[1326]['Date']]
    data_join['Funding Rate'] = data_join['Funding Rate'].astype(float)
    data_join['FRbin'] = pd.qcut(data_join['Funding Rate'], 5, precision=5, duplicates='drop', labels=False)
    data_join['Pricebin'] = pd.qcut(data_join['high'], 5, precision=5, duplicates='drop', labels=False)
    data_join['FRbin'].value_counts()  # not even, but hard with such low numbers
    return data_join

merge_rates_price(BTCpricedata, BTCdata)

def binsummary(): # done
    data = merge_rates_price(BTCpricedata, BTCdata)
    # get max, min, quartiles, count for each bin
    df = pd.DataFrame()
    for i in np.unique(data['FRbin']):
        a = data[data['FRbin'] == i]
        min, max, vol = a['low'].min(), a['high'].max(), a['volume'].mean()
        a['avg'] = a[['high', 'low', 'open', 'close']].mean(axis=1)
        df[str(i)] = a['avg'].describe()
        df = df.round(2)
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

    changes = pd.DataFrame(changes)
    changes = changes[['Date', 'high', 'low', 'vol', 'rate', 'rate bin', 'future_price']]
    changes = changes[:2101]
    b = changes[['Date', 'future_price']]
    c = b['future_price'].astype("string").str.split(',', expand=True)
    c.columns = ['7day', '14day', '28day', '90day', '180day', '365day']
    c['Date'] = b['Date']
    c['7day'] = c['7day'].map(lambda x: x.lstrip('['))
    c['365day'] = c['365day'].map(lambda x: x.rstrip(']'))
    changes = changes.merge(c, on='Date')

    return changes

def rate_atpeaks(BTCpricedata, BTCdata): # done
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
        rate = data[data['Date'] == i]['Funding Rate'].values[0]
        rate_range = [rate - 0.0005, rate + 0.0005]
        #others = data[data['Funding Rate'] == rate]
        other_marketmax.append([i, data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])

    for i in midmax:
        # get rate
        # are there any other dates with this rate
        # % of tops market tops at this rate
        rate = data[data['Date'] == i]['Funding Rate'].values[0]
        rate_range = [rate - 0.0001, rate + 0.0001]
        # others = data[data['Funding Rate'] == rate]
        other_midmax.append([i, data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])
    for i in smallmax:
        # get rate
        # are there any other dates with this rate
        # % of tops market tops at this rate
        rate = data[data['Date'] == i]['Funding Rate'].values[0]
        rate_range = [rate - 0.0001, rate + 0.0001]
        # others = data[data['Funding Rate'] == rate]
        other_smallmax.append([i, data[data['Funding Rate'].between(rate_range[0], rate_range[1], inclusive=False)]['Date'].values.tolist()])
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
        count = len(i)
        max_lh.append([marketmax[i][0], 1/count])
    mid_lh = []
    for i in midmax:
        count = len(i)
        mid_lh.append([midmax[i][0], 1 / count])
    small_lh = []
    for i in smallmax:
        count = len(i)
        mid_lh.append([smallmax[i][0], 1 / count])
    z = 2

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


def fr_change(BTCpricedata, BTCdata): # done
    # by looking at some of the chanrts it tooks like even if the funding rate doesnt have a threshold, it may have a rate of change that could be concerning
    data = merge_rates_price(BTCpricedata, BTCdata)
    data['FR1day'] = (data['Funding Rate'].diff()) # diff between yesterday and today
    data['FR1day%'] = data['FR1day'] / data['Funding Rate']  # % difference
    data['FR3day'] = data['Funding Rate'].diff(periods=3) # diff b/w 5 days ago and today
    data['FR3day%'] = data['FR3day'] / data['Funding Rate'] # % difference
    ## lets do the same for price to see if they are correlated
    data['Price1day'] = (data['high'].diff())  # diff between yesterday and today
    data['Price1day%'] = data['Price1day'] / data['high']  # % difference
    data['Price3day'] = data['high'].diff(periods=3)  # diff b/w 5 days ago and today
    data['Price3day%'] = data['Price3day'] / data['high']  # % difference
    z = 2



    # check against tops and bottoms
    marketmax, midmax, smallmax, marketmin, midmin, smallmin = BTCTopsandBottoms(BTCpricedata)

    # new col: tops and bottoms
        # marketmax = 3, midmax = 2, smallmax = 1, then oppo for mins
    data['TB'] = ''
    data.loc[data[data['Date'].isin(smallmax)].index.values, 'TB'] = 1
    data.loc[data[data['Date'].isin(midmax)].index.values, 'TB'] = 2
    data.loc[data[data['Date'].isin(marketmax)].index.values, 'TB'] = 3
    # data.loc[data[data['Date'].isin(smallmin)].index.values, 'TB'] = -1
    # data.loc[data[data['Date'].isin(midmin)].index.values, 'TB'] = -2
    # data.loc[data[data['Date'].isin(marketmin)].index.values, 'TB'] = -3

    min_max = data.loc[data['TB'].isin([1, 2, 3])]

    # bin price 5day%, fr5day%
    data['FR3_chg_bin'] = pd.qcut(data['FR3day%'], 10, precision=2, duplicates='drop', labels=False)
    data['Price3_chg_bin'] = pd.qcut(data['Price3day%'], 10, precision=2, duplicates='drop', labels=False)
    data['FR1_chg_bin'] = pd.qcut(data['FR1day%'], 10, precision=2, duplicates='drop', labels=False)
    data['Price1_chg_bin'] = pd.qcut(data['Price1day%'], 10, precision=2, duplicates='drop', labels=False)

    new_data = []
    a = data.dropna().groupby(['TB', 'FR3_chg_bin']).size() # group by TB and FR chg bin and see the overlaps
    b = data.dropna().groupby(['TB', 'Price3_chg_bin']).size() # group by price
    c = data.dropna().groupby(['TB', 'Price3_chg_bin', 'FR3_chg_bin']).size() # all

    for i in range(0, len(b)):
        idx = b.index.tolist()[i]
        new_data.append([idx[0], idx[1], b.iloc[i]])
    z = 2

fr_change(BTCpricedata, BTCdata)


def peak_in_bin(BTCpricedata, BTCdata): # done
    data = merge_rates_price(BTCpricedata, BTCdata)
    marketmax, midmax, smallmax = tops_bottoms.BTCTopsandBottoms(data)

    marketmax_bin, midmax_bin, smallmax_bin = [], [], []
    for i in marketmax:
        val = data[data['Date'] == i]['FRbin']
        marketmax_bin.append([i, val.values[0]])
    for i in midmax:
        val = data[data['Date'] == i]['FRbin']
        midmax_bin.append([i, val.values[0]])
    for i in smallmax:
        val = data[data['Date'] == i]['FRbin']
        smallmax_bin.append([i, val.values[0]])

def fr_price_change(BTCpricedata, BTCdata): # done
    # by looking at some of the chanrts it tooks like even if the funding rate doesnt have a threshold, it may have a rate of change that could be concerning
    data = merge_rates_price(BTCpricedata, BTCdata)
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
    # data.loc[data[data['Date'].isin(smallmin)].index.values, 'TB'] = -1
    # data.loc[data[data['Date'].isin(midmin)].index.values, 'TB'] = -2
    # data.loc[data[data['Date'].isin(marketmin)].index.values, 'TB'] = -3

    min_max = data.loc[data['TB'].isin([1, 2, 3])]

    # bin price 5day%, fr5day%
    data['Price_chg_bin'] = pd.qcut(data['Price5day%'], 5, precision=5, duplicates='drop', labels=False)

    new_data = []
    a = data.dropna().groupby(['TB', 'FRbin']).size() # group by TB and FR chg bin and see the overlaps
    b = data.dropna().groupby(['TB', 'Price_chg_bin']).size() # group by price
    c = data.dropna().groupby(['TB', 'Price_chg_bin', 'FRbin']).size()
    z = 2

fr_price_change(BTCpricedata, BTCdata)