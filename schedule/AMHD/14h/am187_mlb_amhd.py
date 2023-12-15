import sys
from os.path import dirname


class AM187(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'mlb_amhd'
        self.ADAPTER_TOKEN = '4d17e69de06aef75d11483c37f466e3f6ab4cc8629af79505b137135794e69f2'
        self.POS = POS365()
        self.POS.DOMAIN = 'am187'
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'

    def get_data(self):
        from pos_api.adapter import submit_payment
        self.POS.login()
        self.POS.get_accounts()
        self.POS.get_minus_payment()
        for pm in self.POS.PMS:
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
