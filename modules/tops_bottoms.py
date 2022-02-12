def find_max(data_full, timeframe):
    tf = timeframe
    data = data_full['high'].tolist()
    maxes, loc = [], []
    list = []
    for i in range(0, len(data)):
        if i - tf < 0:
            bottom = 0
        else:
            bottom = i - tf
        if i + tf > len(data):
            top = len(data)
        else:
            top = i + tf
        set = data[(bottom):(top)]
        m = max(set)
        if data[i] == m:
            list.append((m, data_full.iloc[i]['Date']))
            m = 0
        else:
            pass
    return list

def find_min(data_full, timeframe):
    tf = timeframe
    data = data_full['high'].tolist()
    mins, loc = [], []
    for i in range(0, len(data)):
        if i - tf < 0:
            bottom = 0
        else:
            bottom = i - tf
        if i + tf > len(data):
            top = len(data)
        else:
            top = i + tf
        set = data[(bottom):(top)]
        m = min(set)
        if data[i] == m: # want date
            list.append((m, data_full.iloc[i]['Date']))
            m = 0
        else:
            pass
    return list


def BTCTopsandBottoms(data):
    BTC_price_data = data

    marketTF = 500 # market cycles are relatively every 4 years
    midTF = 200
    smallTF = 50

    marketmax = find_max(BTC_price_data, marketTF)
    midmax = find_max(BTC_price_data, midTF)
    smallmax = find_max(BTC_price_data, smallTF)
    marketmin = find_max(BTC_price_data, marketTF)
    midmin = find_max(BTC_price_data, midTF)
    smallmin = find_max(BTC_price_data, smallTF)

    return marketmax, midmax, smallmax, marketmin, midmin, smallmin