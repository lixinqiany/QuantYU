# -*- coding: utf-8 -*-
import backtrader as bt
from backtrader.indicators import SMA, RSI

class DualMovingAverageStrategy(bt.Strategy):
    """
    双均线交叉策略
    策略逻辑：
    1. 当快速均线上穿慢速均线时买入
    2. 当快速均线下穿慢速均线时卖出
    3. 使用RSI过滤超买信号
    
    参数说明：
    fast_period: 快速均线周期（默认10）
    slow_period: 慢速均线周期（默认30）
    rsi_period: RSI计算周期（默认14）
    rsi_upper: RSI超买阈值（默认70）
    order_pct: 每次交易仓位比例（默认95%）
    """
    params = (
        ('fast_period', 5),
        ('slow_period', 10),
        ('rsi_period', 7),
        ('rsi_upper', 80),
        ('order_pct', 0.9),
    )

    def __init__(self):
        # 初始化技术指标
        self.fast_ma = SMA(
            period=self.p.fast_period
        )
        self.slow_ma = SMA( 
            period=self.p.slow_period
        )
        
        # 交叉信号指标
        self.crossover = bt.ind.CrossOver(
            self.fast_ma, 
            self.slow_ma
        )

    def next(self):
        """策略逻辑执行"""
        # 有持仓时的处理
        #print(f'{self.data.datetime.date()}')
        #print(f"当前价格{self.data.close[0]}")
        #print('当前可用资金', self.broker.getcash())
        #print('当前总资产', self.broker.getvalue())
        #print('当前持仓量', self.broker.getposition(self.data).size)
        #print('当前持仓成本', self.broker.getposition(self.data).price)
        #print(f'保证金占用: {self.broker.getmargin(pos)}')
        if self.position:
            # 死叉或RSI超卖时平仓
            if self.crossover < 0:
                self.close(size=1)
                
        
        # 无持仓时的处理        
        else:
            # 金叉时买入
            if self.crossover > 0 :
                self.buy(size=1)

    def notify_order(self, order):
        """订单状态处理"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status == order.Completed:
            direction = '买入' if order.isbuy() else '卖出'
            pos = self.broker.getposition(self.data).size
            cash = self.broker.getcash()
            value = self.broker.getvalue()
            log_msg = (
                f"{direction} "
                f"价格={order.executed.price:.2f} "
                f"手数={order.executed.size} "
                f"佣金={order.executed.comm:.2f} "
                f"当前持仓量={pos} "
                f"当前可用资金={cash:.2f} "
                f"当前总资产={value:.2f}"
            )
            self.log('info', log_msg)
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            status_name = order.getstatusname()
            self.log('warning', f"订单异常: {status_name}")
            
    def log(self, level, msg):
        dt = self.data.datetime.datetime().strftime('%Y-%m-%d %H:%M:%S')
        
        # 颜色代码（可选，增强可读性）
        colors = {
            'info': '\033[94m',    # 蓝色
            'warning': '\033[91m', # 红色
            'reset': '\033[0m'     # 重置颜色
        }
        
        # 组装带颜色的日志格式（如果不需要颜色可移除）
        log_msg = (
            f"{colors.get(level, '')}"
            f"[{dt}] [{level.upper()}] {msg}"
            f"{colors['reset']}"
        )
        print(log_msg)