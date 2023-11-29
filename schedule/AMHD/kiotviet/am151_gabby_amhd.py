import sys
from os.path import dirname



class AM151(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from kiotviet import KIOTVIET
        self.ADAPTER_RETAILER = 'gabby_amhd'
        self.ADAPTER_TOKEN = '949bc15d0545793090028a4ea255f30075ed52798df455e6c3e09200dd10fff5'
        self.KIOT = KIOTVIET()
        self.KIOT.CLASS = self.__class__.__name__
        self.KIOT.ACCOUNT = 'admaeonhd'
        self.KIOT.PASSWORD = 'Aeon12345'
        self.KIOT.DOMAIN = 'gabby'
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
