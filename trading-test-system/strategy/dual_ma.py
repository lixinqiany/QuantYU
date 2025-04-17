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
        ('fast_period', 7),
        ('slow_period', 16),
        ('rsi_period', 7),
        ('rsi_upper', 80),
        ('order_pct', 0.9),
        ('stop_loss_pct', 5),    # 止损比例
        ('risk_per_trade', 0.02),   # 单笔交易风险比例
        ('position_type', 'percentage'), # 仓位类型 fixed/percentage
        ('fixed_size', 100000),
        ('mult',None),
        ('margin', None),
        ('unit', None)
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
        
        self.rsi = bt.indicators.RelativeStrengthIndex(
            period=self.p.rsi_period)
        self.portfolio_value = []
        self.stop_order = None  # 止损订单引用
        self.entry_price = 0    # 入场价格
        self.exit_reason = None # 平仓原因跟踪
        self.pending_order = None  # 跟踪挂起的主订单

    def next(self):
        """策略逻辑执行"""
        self.portfolio_value.append(self.broker.getvalue())
        #print(self.position.size)
        if self.position:
            # 死叉或RSI超卖时平仓
            prev_size = self.position.size
            if self.crossover < 0 or self.rsi > self.p.rsi_upper:
                self.close(tag="manual_close")   
            if prev_size != 0 and self.position.size == 0:
                print(f"平仓原因: {self.exit_reason or '未知'}")
                self.exit_reason = None
        
        # 无持仓时的处理        
        else:
            # 金叉时买入
            if self.crossover > 0 and self.rsi < self.p.rsi_upper:
                size = self._calculate_position_size()
                self.pending_order = self.buy(size=size)

    def notify_order(self, order):
        if order == self.stop_order:
            print("当前止损单")
        """订单状态处理"""
        if order.status in [order.Submitted, order.Accepted]:
            return
            
        if order.status == order.Completed:
            if order.issell():
                if hasattr(order, 'tag'):
                    self.exit_reason = order.tag
            
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
            
            # 平仓后取消未触发的止损单
            if order.issell() and self.position.size == 0:
                if self.stop_order and self.stop_order.status in [order.Submitted, order.Accepted]:
                    self.cancel(self.stop_order)
                    print("已取消未触发止损单")
                    
            if order.isbuy():
                # 记录实际成交价格
                self.entry_price = order.executed.price
                print(f"实际成交价：{self.entry_price}")
                
                # 计算基于实际成交价的止损
                stop_price = self.entry_price - self.p.mult*self.p.unit*self.p.stop_loss_pct
                print(f"计算止损价：{stop_price}（基于成交价{self.entry_price}）")
                
                # 提交止损单
                self.stop_order = self.sell(
                    exectype=bt.Order.Stop,
                    price=stop_price,
                    size=order.executed.size,
                    tag='stop_loss'
                )
                self.pending_order = None
                
            elif order.issell():
                # 处理平仓后的状态重置
                if order == self.stop_order:
                    print(f"止损触发，成交价：{order.executed.price}")
            
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            status_name = order.getstatusname()
            self.log('warning', f"订单异常: {status_name}")
            
    def _calculate_position_size(self):
        """动态仓位计算"""
        if self.p.position_type == 'fixed':
            return int(self.p.fixed_size / self.data.close[0])
        else:
            cash = self.broker.get_cash()
            value = self.broker.get_value()
            risk_amount = value * self.p.risk_per_trade
            price_range = self.p.unit * self.p.stop_loss_pct *self.p.mult
            theoretical_size = risk_amount / (price_range)
            margin_per_lot = self.data.close[0] * self.p.mult * self.p.margin
            max_by_margin = cash * 0.9 / margin_per_lot  # 保留10%缓冲
            return min(int(theoretical_size), int(max_by_margin))
            
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