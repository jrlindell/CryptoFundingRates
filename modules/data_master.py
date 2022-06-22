from modules.get_data import bitmex_data, binance_data, FR_data, Price_data


class BTCDataset():
    def __init__(self, binance_data_path=None):
        self.bitmex_data = bitmex_data()
        self.binance_data = binance_data(binance_data_path)
        self.fund_data = FR_data(self.bitmex_data, self.binance_data)
        self.price_data = Price_data()




