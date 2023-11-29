import sys
from os.path import dirname
from datetime import datetime


def random_str():
    return ''.join(random.choice(string.ascii_letters) for i in range(8)).encode('utf-8')


class AM070(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from kiotviet import KIOTVIET
        self.ADAPTER_RETAILER = 'wundertute_amhd'
        self.ADAPTER_TOKEN = 'e9c14839317d5c857614316697f01d0d9bc3e040dbf6e94137958ea453fd4c5b'
        self.KIOT = KIOTVIET()
        self.KIOT.CLASS = self.__class__.__name__
        self.KIOT.ACCOUNT = 'amhdapi'
        self.KIOT.PASSWORD = 'Aeonmall123'
        self.KIOT.DOMAIN = 'b4y'
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
        for order in self.KIOT.ORDERS:
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
