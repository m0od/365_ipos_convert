import sys
from os.path import dirname


class AM025(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from kiotviet import KIOTVIET
        self.ADAPTER_RETAILER = 'rabity_amhd'
        self.ADAPTER_TOKEN = '5cac0cb929e198022bd37bcc5d0e09863bab722c8517ce58cd36a2f194490404'
        self.KIOT = KIOTVIET()
        self.KIOT.CLASS = self.__class__.__name__
        self.KIOT.ACCOUNT = 'ketoan.aeonhadong'
        self.KIOT.PASSWORD = 'Ketoan123'
        self.KIOT.DOMAIN = 'tanphu'
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
