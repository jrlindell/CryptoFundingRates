def find_max(data_full, timeframe):
    tf = timeframe
    data = data_full['high'].tolist()
    list = []
    bottom = 0
    top = 0
    while True:
        if top > len(data):
            break
        bottom = top
        top += tf
        set = data[(bottom):(top)]
        m = max(set)
        list.append(data_full[data_full['high'] == m]['Date'].tolist()[0])

    return list

def find_min(data_full, timeframe):
    tf = timeframe
    data = data_full['high'].tolist()
    list = []
    bottom = 0
    top = tf
    while True:
        if top > len(data):
            break
        set = data[(bottom):(top)]
        m = min(set)
        list.append(data_full[data_full['high'] == m]['Date'].tolist()[0])
        bottom = top
        top += tf
    return list


def BTCTopsandBottoms(BTC_price_data):

    marketTF = 500 # market cycles are relatively every 4 years
    midTF = 200
    smallTF = 50

    marketmax = find_max(BTC_price_data, marketTF)
    midmax = find_max(BTC_price_data, midTF)
    smallmax = find_max(BTC_price_data, smallTF)
    marketmin = find_min(BTC_price_data, marketTF)
    midmin = find_min(BTC_price_data, midTF)
    smallmin = find_min(BTC_price_data, smallTF)

    return marketmax, midmax, smallmax, marketmin, midmin, smallmin