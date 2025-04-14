# -*- coding: utf-8 -*-
import os
import akshare as ak
import pandas as pd
from abc import ABC, abstractmethod


class DataCollector(ABC):
    """数据获取基类（抽象接口）"""

    def __init__(self, symbol):
        self.symbol = symbol
        self.daily_data = None

    @abstractmethod
    def get_daily_data(self):
        """loading daily data at once"""
        pass

    def save_to_csv(self, period='daily'):
        """export data 

        Args:
            period (str, optional): specify the frequency of data. Defaults to 'daily'.
        """
        file_path = os.path.join(
            '../data',
            f"{self.symbol}_{period}.csv"
        )
        
        if period == "daily":
            self.daily_data.to_csv(file_path, index=False)
            
        print(f"{symbol}的{period}数据已保存至: {file_path}")


class AkshareCollector(DataCollector):
    """Collect historical data of specific contract from AKShare

    Used API:
    - futures_zh_daily_sina(symbol="RB2505"): return all daily data of the contract at once
    """  
    
    def get_daily_data(self,)-> pd.DataFrame:
        """Collect daily data from API(futures_zh_daily_sina)

        Args:
            symbol (str): the code of specific contract

        Returns:
            _type_: _description_
        """
        
        print(f"[INFO] 加载{symbol}的所有日线数据...")

        self.daily_data = ak.futures_zh_daily_sina(
            symbol=self.symbol
        )

        used_columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'openinterest']
        bt_format = {'date': "datetime",
                     'hold': 'openinterest'}
        self.daily_data['date'] = pd.to_datetime(self.daily_data['date'])
        self.daily_data['date'] = self.daily_data['date'].dt.strftime("%Y-%m-%d %H:%M:%S")
        self.daily_data.set_index('date', inplace=True, drop=False)
        self.daily_data.rename(columns=bt_format, inplace=True)
        print(f"[INFO] {symbol}数据已取回...")
        
        return self.daily_data[used_columns]


if __name__ == "__main__":
    
    import matplotlib.pyplot as plt

    print("***数据模块test***")

    symbol = "RB2505"
    period = "daily"

    collector = AkshareCollector(symbol)

    data = collector.get_daily_data()
    print(f"获取到 {len(data)} 条数据")
    print("数据样例:")
    print(data.head(3))
    # print(data['datetime'][1])

    collector.save_to_csv(period)