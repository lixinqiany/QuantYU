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
        ('fast_period', 10),
        ('slow_period', 30),
        ('rsi_period', 14),
        ('rsi_upper', 70),
        ('order_pct', 0.95),
    )

    def __init__(self):
        # 初始化技术指标
        self.fast_ma = SMA(
            self.data.close, 
            period=self.p.fast_period
        )
        self.slow_ma = SMA(
            self.data.close, 
            period=self.p.slow_period
        )
        self.rsi = RSI(
            self.data.close, 
            period=self.p.rsi_period
        )
        
        # 交叉信号指标
        self.crossover = bt.ind.CrossOver(
            self.fast_ma, 
            self.slow_ma
        )

    def next(self):
        """策略逻辑执行"""
        # 有持仓时的处理
        if self.position:
            # 死叉或RSI超卖时平仓
            if self.crossover < 0 or self.rsi > self.p.rsi_upper:
                self.close()
        
        # 无持仓时的处理        
        else:
            # 金叉时买入
            if self.crossover > 0 and self.rsi < self.p.rsi_upper:
                self.order_target_percent(
                    target=self.p.order_pct
                )

    def notify_order(self, order):
        """订单状态处理"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status == order.Completed:
            direction = '买入' if order.isbuy() else '卖出'
            print(
                f'{direction}执行: 价格={order.executed.price:.2f} '
                f'数量={order.executed.size} '
                f'成本={order.executed.value:.2f} '
                f'佣金={order.executed.comm:.2f}'
            )
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            print('订单未完成:', order.getstatusname())