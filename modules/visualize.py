import matplotlib
import numpy as np
from matplotlib import pyplot as plt, cm
from datetime import datetime
import seaborn as sns
import pandas as pd
import sys
sys.path.append('../scripts')

from main import bincompare, merge_rates_price
from modules import get_data

BTCpricedata, _ = get_data.Price_data()
#BTCdata, _ = get_data.binance_data()
BTCdata = pd.read_csv('/Users/footb/Desktop/Misc/Finance/Crypto/CarterProject/data/BitmexBTC2.csv')

data = merge_rates_price(BTCpricedata, BTCdata)

def price_colored_line(data): # make one with negative or positive
    plt.rcParams["figure.figsize"] = [7.5, 3.5]
    plt.rcParams["figure.autolayout"] = True

    data['Pos'] = ""
    data.loc[data['Funding Rate'] >= 0, 'Pos'] = 1
    data.loc[data['Funding Rate'] < 0, 'Pos'] = 0
    data['color'] = ""
    data.loc[data['Pos'] == '', 'color'] = 'black'
    data.loc[data['bin'] == 0, 'color'] = 'green'
    data.loc[data['bin'] ==1, 'color'] = 'yellow'
    data.loc[data['bin'] == 2, 'color'] = 'orange'
    data.loc[data['bin'] == 3, 'color'] = 'red'


    x = data['Date']
    y = data['high']
    c = data['Funding Rate'] #this color will do a full gradient
    colors = ['blue' if x <= data['Funding Rate'].mean() else 'red' for x in data['Funding Rate']] # this color does red or blue based on above or below average
    plt.scatter(x,y,c=c) # c, data['color']
    plt.show()
    z = 2
price_colored_line(data)

def line_bar(BTCpricedata, BTCdata):
    data = merge_rates_price(BTCpricedata, BTCdata)
    fig, ax = plt.subplots()
    ax2=ax.twinx()
    ax.bar(data['Date'], data['Funding Rate'], color='blue', label='Funding Rate')
    ax2.plot(data['Date'], data['high'], color='black', label='BTC price')
    ax.set_xticklabels(data['Date'])
    ax.legend(loc='best')

