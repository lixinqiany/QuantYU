import os, json
import backtrader as bt
from backtrader.feeds import GenericCSVData
from datetime import datetime, timedelta
from utils.commission import GenericCommInfo
import matplotlib.pyplot as plt
from backtrader import TimeFrame
import seaborn as sns
import numpy as np
from matplotlib.ticker import FormatStrFormatter

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
        self.contract_specs = {}
        self._setup()
        
        
    def _setup(self):
        self._load()
        
        self.cerebro.broker.setcash(self.cash)
        self.cerebro.broker.addcommissioninfo(self.comm)
        # 收益率
        self.cerebro.addanalyzer(
            bt.analyzers.Returns, 
            _name='returns',
            
        )
        # 回撤
        self.cerebro.addanalyzer(
            bt.analyzers.DrawDown, 
            _name='drawdown'
        )
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, riskfreerate=0.02, _name="sharpe",timeframe=TimeFrame.Days,compression=1)
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
            self.contract_specs["mult"] = my_comm['mult']
            self.contract_specs['margin'] = my_comm['margin']
            self.contract_specs['unit'] = my_comm['unit']
            result ={k: v for k,v in my_comm.items() if k != "unit"}
            return result

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
        self.cerebro.addstrategy(strategy, **self.contract_specs)
        
    def run(self):
        results = self.cerebro.run()
        self._print_analysis(results[0])
        self.cerebro.plot(style="candlestick")
        
        return results
    
    def run_optimization(self, maxcpus=1):
        """执行参数优化"""
        print(f"\n{'='*30} 开始参数优化 {'='*30}")
        results = self.cerebro.run(maxcpus=maxcpus)
        self._analyze_optimization_results(results)
        return results
    
    def _analyze_optimization_results(self, results):
        """分析优化结果"""
        import pandas as pd
        
        performance = []
        for strat_run in results:  # 遍历每个参数组合
            if not strat_run:
                continue
                
            strategy = strat_run[0]  # 获取策略实例
            params = strategy.params._getkwargs()
            
            # 过滤只显示优化的参数
            filtered_params = {
                k: v for k, v in params.items() 
                if k in self.param_ranges
            }
            
            # 获取分析器数据
            try:
                returns_an = strategy.analyzers.returns.get_analysis()
                sharpe_an = strategy.analyzers.sharpe.get_analysis()
                drawdown_an = strategy.analyzers.drawdown.get_analysis()
                trade_an = strategy.analyzers.trades.get_analysis()
            except Exception as e:
                print(f"分析器数据获取失败: {e}")
                continue

            # 计算关键指标
            print("="*20)
            print(trade_an)
            print("="*20)
            total_trades = trade_an.total.closed if trade_an.total.total !=0 else 0
            win_rate = (trade_an.won.total/total_trades*100) if total_trades > 0 else 0
            
            performance.append({
                **filtered_params,
                '总收益率 (%)': returns_an['rtot'],
                '年化收益率 (%)': returns_an['rnorm100'],
                '夏普比率': sharpe_an['sharperatio'],
                '最大回撤 (%)': drawdown_an.max.drawdown,
                '交易次数': total_trades,
                '胜率 (%)': win_rate
            })

        # 生成分析报告
        if not performance:
            print("没有有效结果")
            return
            
        df = pd.DataFrame(performance)
        df.sort_values(by='夏普比率', ascending=False, inplace=True)
        
        print("\n优化结果排序（按夏普比率降序）：")
        print(df.head(10))
        
        # 保存结果
        df.to_csv('优化结果.csv', index=False)
        print("\n完整结果已保存至 优化结果.csv")
        
        # 显示最佳参数
        best_params = df.iloc[0].to_dict()
        print("\n最佳参数组合：")
        for k, v in best_params.items():
            print(f"{k:>15}: {v}")
    
    def add_optimization_strategy(self, strategy, param_ranges):
        """添加参数优化策略"""
        self.param_ranges = param_ranges  # 保存参数范围
        self.cerebro.optstrategy(
            strategy,
            **param_ranges,
            **self.contract_specs
        )
    
    def _print_analysis(self, result):
        """打印专业化的回测报告"""
        analyzers = result.analyzers
        
        print("\n========== 专业回测分析报告 ==========")
        print(f"初始资金: {self.cash:.2f}")
        print(f"期末资金: {self.cerebro.broker.getvalue():.2f}")
        print(f"总收益率: {analyzers.returns.get_analysis()['rtot']:.2f}%")
        print(f"年化收益率: {analyzers.returns.get_analysis()['rnorm100']:.2f}%")
        print(f"夏普比率: {analyzers.sharpe.get_analysis()['sharperatio']}")
        print(f"最大回撤: {analyzers.drawdown.get_analysis().max.drawdown:.2f}%")
        print(f"最长回撤周期: {analyzers.drawdown.get_analysis().max.len} 根K线")
        
        trade_analysis = analyzers.trades.get_analysis()
        print("\n====== 交易统计 ======")
        #print(f"总交易次数: {trade_analysis.total.closed}")
        #print(f"胜率: {trade_analysis.won.total/trade_analysis.total.closed*100:.1f}%")
        #print(f"盈亏比: {trade_analysis.won.pnl.average/abs(trade_analysis.lost.pnl.average):.2f}")
    
    def plot_optimization_results(self, csv_path='优化结果.csv'):
        """可视化优化结果（需先运行过优化）"""
        # 读取优化结果
        import pandas as pd
        import seaborn as sns
        df = pd.read_csv(csv_path)
        
        # 设置专业金融图表样式
        #plt.style.use('seaborn-whitegrid')
        plt.rcParams.update({
            'font.sans-serif': 'Microsoft YaHei',  # 中文显示
            'axes.unicode_minus': False,
            'figure.dpi': 150,
            'figure.figsize': (12, 8)
        })

        # 生成参数组合列表
        params = [col for col in df.columns if col not in [
            '总收益率 (%)', '年化收益率 (%)', '夏普比率', 
            '最大回撤 (%)', '交易次数', '胜率 (%)'
        ]]

        # 绘制热力图矩阵
        for metric in ['夏普比率', '最大回撤 (%)', '总收益率 (%)']:
            if len(params) >= 2:
                self._plot_heatmap(df, params[0], params[1], metric)
            if len(params) >= 3:
                self._plot_3d_surface(df, params[0], params[1], params[2], metric)

    def _plot_heatmap(self, df, x_col, y_col, metric_col):
        """二维参数热力图"""
        pivot = df.pivot_table(
            values=metric_col,
            index=y_col,
            columns=x_col,
            aggfunc='mean'
        )

        plt.figure(figsize=(10, 8))
        ax = sns.heatmap(
            pivot, 
            annot=True, 
            fmt=".2f",
            cmap='RdYlGn', 
            linewidths=0.5,
            annot_kws={'size': 8},
            cbar_kws={'label': metric_col}
        )
        
        plt.title(f'参数优化热力图: {x_col} vs {y_col} → {metric_col}', pad=20)
        plt.xlabel(x_col, labelpad=15)
        plt.ylabel(y_col, labelpad=15)
        plt.xticks(rotation=45)
        plt.yticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f'热力图_{x_col}vs{y_col}_{metric_col}.png')
        plt.close()

    def _plot_3d_surface(self, df, x_col, y_col, z_col, metric_col):
        """三维参数曲面图"""
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 创建数据透视表
        pivot = df.pivot_table(
            values=metric_col,
            index=[x_col, y_col],
            columns=z_col,
            aggfunc='mean'
        )

        # 生成网格数据
        X, Y = np.meshgrid(pivot.columns, pivot.index.levels[1])
        Z = pivot.unstack().values.reshape(X.shape)

        # 绘制曲面
        surf = ax.plot_surface(
            X, Y, Z, 
            cmap='viridis',
            edgecolor='k',
            alpha=0.8
        )
        
        # 添加颜色条
        fig.colorbar(surf, shrink=0.5, label=metric_col)
        
        # 设置坐标轴
        ax.set_xlabel(z_col, labelpad=15)
        ax.set_ylabel(y_col, labelpad=15)
        ax.set_zlabel(metric_col, labelpad=15)
        ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
        
        plt.title(f'三维参数优化: {x_col} × {y_col} × {z_col} → {metric_col}', pad=20)
        plt.savefig(f'3D曲面_{x_col}×{y_col}×{z_col}_{metric_col}.png')
        plt.close()

if __name__=="__main__":
    from strategy.dual_ma import DualMovingAverageStrategy
    
    today = datetime.today()
    diff = timedelta(days=200)
    start = today - diff
    tester = BackTester("RB", "RB2505", "daily", start, today)
    tester.add_strategy(DualMovingAverageStrategy)
    tester.run()
    # 定义参数网格
    #param_grid = {
    #    'fast_period': range(5, 10, 1),    # [5, 10, 15, 20]
    #    'slow_period': range(15, 20, 1),  # [20, 30, 40, 50]
    #    'rsi_upper': [70, 75, 80]
    #}
    
    # 添加优化策略
    #tester.add_optimization_strategy(
    #    DualMovingAverageStrategy,
    #    param_ranges=param_grid
    #)
    
    # 执行参数优化
    #tester.run_optimization()
    #tester.plot_optimization_results()
        