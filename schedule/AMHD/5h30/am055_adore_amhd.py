import sys
from os.path import dirname
from datetime import datetime, timedelta


class AM055(object):
    def __init__(self):
        from kiotviet import KIOTVIET
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'adore_amhd'
        self.ADAPTER_TOKEN = '881f0d44a847ea776619db0d147a8d48fef95e5e4f9112a4b31db3409e4ceed2'
        self.KIOT = KIOTVIET()
        self.KIOT.CLASS = self.__class__.__name__
        self.KIOT.ACCOUNT = 'aeon.hd'
        self.KIOT.PASSWORD = '123'
        self.KIOT.DOMAIN = 'adoredress'
        self.KIOT.METHOD = {
            'CARD': 'THẺ',
            'TRANSFER': 'PAYOO',
            'CASH': 'CASH',
            'VOUCHER': 'VOUCHER'
        }

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        stt, reason = self.KIOT.login()
        if not stt:
            submit_error(self.ADAPTER_RETAILER, reason)
            return
        self.KIOT.get_orders()
        self.KIOT.get_returns()
        for order in self.KIOT.ORDERS:
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)


# now = datetime.now()
# Adore().get_data(now - timedelta(days=10), now)
