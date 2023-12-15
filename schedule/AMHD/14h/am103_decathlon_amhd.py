import sys
from os.path import dirname


class AM103(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'decathlon_amhd'
        self.ADAPTER_TOKEN = 'bf52c6a1b7244d114a3372f1ed750808b8f3cae4dcbfaa1ab42d900ecbe68fa7'
        self.POS = POS365()
        self.POS.DOMAIN = 'am103'
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'

    def get_data(self):
        from pos_api.adapter import submit_payment
        self.POS.login()
        self.POS.get_accounts()
        self.POS.get_minus_payment()
        for pm in self.POS.PMS:
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)