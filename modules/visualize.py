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
BTCdata = get_data.FR_data()

data = merge_rates_price(BTCpricedata, BTCdata)

def price_colored_line(data): # make one with negative or positive

    plt.rcParams["figure.figsize"] = [7.5, 3.5]
    plt.rcParams["figure.autolayout"] = True


    data['color'] = ""
    data.loc[data['Pricebin'] == 0, 'color'] = 'black'
    data.loc[data['Pricebin'] == 1, 'color'] = 'green'
    data.loc[data['Pricebin'] ==2, 'color'] = 'yellow'
    data.loc[data['Pricebin'] == 3, 'color'] = 'orange'
    data.loc[data['Pricebin'] == 4, 'color'] = 'red'


    x = data['Date']
    y = data['high']
    #c = data['Pricebin'] #this color will do a full gradient
    colors = ['blue' if x <= data['Funding Rate'].mean() else 'red' for x in data['Funding Rate']] # this color does red or blue based on above or below average
    plt.scatter(x,y,c=data['color']) # c, data['color']
    plt.show()
    z = 2

price_colored_line(data)

def line_bar(BTCpricedata, BTCdata):
    data = merge_rates_price(BTCpricedata, BTCdata)
    #data = data[data['Date'] >= data.iloc[1326]['Date']]
    fig, ax = plt.subplots()
    ax2=ax.twinx()
    ax.bar(data['Date'], data['Funding Rate'], color='blue', label='Funding Rate')
    #ax.axhline(y=0.3, color='red', linestyle='-')
    ax2.plot(data['Date'], data['high'], color='black', label='BTC price')
    z = 12
    #ax.set_xticklabels(data['Date'])

#line_bar(BTCpricedata, BTCdata)