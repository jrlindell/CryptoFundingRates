import numpy as np
from matplotlib import pyplot as plt

import sys
sys.path.append('../scripts')

from main import bincompare, merge_rates_price
from modules import get_data

BTCpricedata, _ = get_data.Price_data()
BTCdata, _ = get_data.binance_data()

data = merge_rates_price(BTCpricedata, BTCdata)

plt.rcParams["figure.figsize"] = [7.5, 3.5]
plt.rcParams["figure.autolayout"] = True
x = data['Date']
y = data['high']
c = data['Funding Rate']
plt.scatter(x,y,c=c)
plt.show()
z = 2
