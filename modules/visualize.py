def binanceBTC():
    BTCfunddata, _ = binance_data()
    BTCpricedata, _ = Price_data()

    BTCfunddata = BTCfunddata.groupby('Date', as_index=False).agg({"Funding Rate": "max"})
    # x = date, y = price, line = funding fee


    fig, ax = plt.subplots()
    ax1.plot(BTCfunddata['Date'], BTCfunddata['Funding Rate'], color='red')
    ax2 = ax1.twinx()
    ax2.plot(BTCpricedata['Date'], BTCpricedata['high'], color='blue')
    plt.show()