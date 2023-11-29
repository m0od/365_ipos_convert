import sys
from os.path import dirname
import requests
import hashlib
import string
import random
from datetime import datetime, timedelta


def random_str():
    return ''.join(random.choice(string.ascii_letters) for i in range(8)).encode('utf-8')


class AM041(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from kiotviet import KIOTVIET
        self.ADAPTER_RETAILER = 'kakao_amhd'
        self.ADAPTER_TOKEN = '8add972c8f30406354872d3272f755fff035661f9ddd590e6e71c267b756a546'
        self.KIOT = KIOTVIET()
        self.KIOT.CLASS = self.__class__.__name__
        self.KIOT.ACCOUNT = 'aeonmall'
        self.KIOT.PASSWORD = '12345'
        self.KIOT.DOMAIN = 'diossoft'
        self.KIOT.METHOD = {
            'CARD': 'THẺ',
            'TRANSFER': 'CHUYỂN KHOẢN',
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


# AM041().get_data()
# if __name__:
#     from schedule.pos_api.adapter import submit_error, submit_order

    # now = datetime.now()
    # print(now - timedelta(days=12))
    # Kakao().get_data(now - timedelta(days=5), now - timedelta(days=4))
