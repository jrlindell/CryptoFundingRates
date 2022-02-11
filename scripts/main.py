import pandas as pd
import numpy as np
import seaborn as sns


from modules import get_data, tops_bottoms

# this finds the market cycle tops and dates for larger time frames (500+ days),
# medium time frames (200 days) and small time frames (50 days)
#BTCpricedata, _ = get_data.Price_data()
#marketmax, midmax, smallmax, marketmin, midmin, smallmin = tops_bottoms.BTCTopsandBottoms(BTCpricedata)


# bin funding rates, and then % drop/gain after
BTCdata, ETHdata = get_data.binance_data()




def fundingbins(BTCdata):
    bindata = pd.cut(BTCdata['Funding Rate'], 5)
    bins = bindata.cat.categories.values
    BTCdata['bin'] = pd.cut(BTCdata['Funding Rate'], 5, labels=False)
    bindates =  [[] for x in range(5)]

    for i in range(0, len(BTCdata)):
        # get date
        bindates[BTCdata.iloc[i]['bin']].append(str(BTCdata.iloc[i]['Date'].strftime('%m/%d/%Y')))


    z = 2
fundingbins(BTCdata)
z = 2