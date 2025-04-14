import backtrader as bt


class GenericCommInfo(bt.CommInfoBase):
    params = (
        ('commission', 0.0),
        ('mult', 1),
        ('margin', 0.1),
        ('commtype', bt.CommInfoBase.COMM_FIXED),
        ('stocklike', False),
        ('fixed_tax', 2)
    )

    def get_margin(self, price):
        #print(price * self.p.mult * self.p.margin)
        return price * self.p.mult * self.p.margin
        
    def _getcommission(self, size, price, pseudoexec):
        fixed = abs(size) * self.p.fixed_tax
        exchange = abs(size) * price * self.p.commission
        # print(f"fix={fixed},交易所{exchange}")
        return fixed + exchange