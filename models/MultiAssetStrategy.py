
import backtrader as bt

class MultiAssetStrategy(bt.Strategy):

    params = dict(
        symbols=[],
        mas_init=None,
        mas_next=None,
        mas_next_open=None
    )

    def __init__(self, symbols, mas_init, mas_next, mas_next_open):
        self.p.symbols = symbols
        self.p.mas_init = mas_init
        self.p.mas_next = mas_next
        self.p.mas_next_open = mas_next_open

        for i, d in enumerate(self.datas):
            self.p.mas_init(d)

    def next(self):
        if self.p.mas_next is None:
            return
            
        for i, d in enumerate(self.datas):
            self.p.mas_next(d)

    def next_open(self):
        if self.p.next_open is None:
            return
        for i, d in enumerate(self.datas):
            self.o.mas_next_open(d)

    def get_share_allocation(self, padding):
        stocks_sharing_remaining_cash = len(list(filter(lambda symbol: self.getpositionbyname(symbol).size == 0, self.p.symbols)))
        amount_to_allocated_to_share = (self.p.cash * padding) / stocks_sharing_remaining_cash

        # if(self.p.cash == 100000):
        #     amount_to_allocated_to_share = 98000
        return amount_to_allocated_to_share