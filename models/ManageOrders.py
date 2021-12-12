import backtrader as bt

class ManageOrders(bt.Strategy):

    def __init__(self):
        self.o = dict()

    def notify_order(self, order):
        # print(f"Order notification. status{order.getstatusname()}.")
        # print(f"Order info. status{order.info}.")
        if order.status == order.Submitted:
            return

        dt, dn = self.datetime.date(), order.data._name
        print('{} {} Order {} Status {}'.format(
            dt, dn, order.ref, order.getstatusname())
        )

        whichord = ['main', 'stop', 'limit', 'close']
        if not order.alive():  # not alive - nullify
            # print(order.data)
            # print(self.o)
            dorders = self.o[order.data]
            idx = dorders.index(order)
            dorders[idx] = None
            print('-- No longer alive {} Ref'.format(whichord[idx]))

            if all(x is None for x in dorders):
                dorders[:] = []  # empty list - New orders allowed
                