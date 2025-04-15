import os, json
import backtrader as bt
from backtrader.feeds import GenericCSVData
from datetime import datetime, timedelta
from utils.commission import GenericCommInfo
import matplotlib.pyplot as plt

class BackTester():
    def __init__(self, name: str, 
                 symbol: str, 
                 period: str, 
                 beginning: datetime, end: datetime, 
                 cash=10000):
        self.name = name
        self.symbol = symbol
        self.period = period
        self.beginning = beginning
        self.end = end
        
        self.cerebro = bt.Cerebro()
        self.cash = cash
        self.comm ={}
        self._setup()
        
        
    def _setup(self):
        self._load()
        
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.addcommissioninfo(self.comm)
        # 收益率
        self.cerebro.addanalyzer(
            bt.analyzers.Returns, 
            _name='returns',
            tann=252
        )
        # 回撤
        self.cerebro.addanalyzer(
            bt.analyzers.DrawDown, 
            _name='drawdown'
        )
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.02, _name="sharpe")
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        
    def _get_commmission(self):
        fp = os.path.join(
            "data/commission/commission.json",
        )
        
        with open(fp, 'r') as f:
            comm = json.load(f)
            my_comm = comm[self.name]
            commtype_map = {
                "COMM_FIXED": bt.CommInfoBase.COMM_FIXED,
                "COMM_PERC": bt.CommInfoBase.COMM_PERC
            }
            my_comm['commtype'] = commtype_map[my_comm['commtype']]
            
            return my_comm

    def _load(self):
        fp = os.path.join(
            "data",
            f"{self.symbol}_{self.period}.csv"
        )
        
        data = GenericCSVData(
            dataname="./data/RB2505_daily.csv",
            fromdate=self.beginning,
            todate=self.end,
            nullvalue=0,
            dtformat="%Y-%m-%d %H:%M:%S",
            datetime=0,
            open=1,high=2,low=3,close=4,volume=5,openinterest=6
        )
        
        self.cerebro.adddata(data)
        comm = self._get_commmission()
        self.comm = GenericCommInfo(
            **comm
        )
        
    def add_strategy(self, strategy):
        self.cerebro.addstrategy(strategy)
        
    def run(self):
        results = self.cerebro.run()
        self._print_analysis(results[0])
        self.cerebro.plot(style="candlestick")
        
        return results
    
    def _print_analysis(self, result):
        """打印专业化的回测报告"""
        analyzers = result.analyzers
        
        print("\n========== 专业回测分析报告 ==========")
        print(f"初始资金: {self.cash:.2f}")
        print(f"期末资金: {self.cerebro.broker.getvalue():.2f}")
        print(f"总收益率: {analyzers.returns.get_analysis()}%")
        print(f"年化收益率: {analyzers.returns.get_analysis()['rnorm100']:.2f}%")
        print(f"夏普比率: {analyzers.sharpe.get_analysis()['sharperatio']}")
        print(f"最大回撤: {analyzers.drawdown.get_analysis().max.drawdown:.2f}%")
        print(f"最长回撤周期: {analyzers.drawdown.get_analysis().max.len} 根K线")
        
        trade_analysis = analyzers.trades.get_analysis()
        print("\n====== 交易统计 ======")
        print(f"总交易次数: {trade_analysis.total.closed}")
        print(f"胜率: {trade_analysis.won.total/trade_analysis.total.closed*100:.1f}%")
        print(f"盈亏比: {trade_analysis.won.pnl.average/abs(trade_analysis.lost.pnl.average):.2f}")
    

if __name__=="__main__":
    from strategy.dual_ma import DualMovingAverageStrategy
    
    today = datetime.today()
    diff = timedelta(days=200)
    start = today - diff
    tester = BackTester("RB", "RB2505", "daily", start, today)
    tester.add_strategy(DualMovingAverageStrategy)
    tester.run()
        
        