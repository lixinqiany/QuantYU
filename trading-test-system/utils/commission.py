import backtrader as bt


class GenericCommInfo(bt.CommInfoBase):
    params = (
        ('commission', 0.0),
        ('mult', 1),
        ('margin', None),
        ('commtype', bt.CommInfoBase.COMM_PERC),
        ('stocklike', False)
    )

    def _getmargin(self, price):
        # 自动判断保证金模式
        if isinstance(self.p.margin, float) and 0 < self.p.margin < 1:
            # 比例模式: 保证金 = 价格 × 合约乘数 × 比例
            return price * self.p.mult * self.p.margin
        else:
            # 固定模式: 直接返回保证金数值
            return self.p.margin
        
    def _getcommission(self, size, price, pseudoexec):
        if self._commtype == self.COMM_PERC:
            return abs(size) * self.p.commission * price * self.p.mult

        return abs(size) * self.p.commission