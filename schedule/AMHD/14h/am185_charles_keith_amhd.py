import sys
from os.path import dirname


class AM185(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'charles_keith_amhd'
        self.ADAPTER_TOKEN = '5d2047ebf5f7bdc9437771a1359742cf5ab7d36504c4973cabea8f835993d86c'
        self.POS = POS365()
        self.POS.DOMAIN = 'am185'
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'

    def get_data(self):
        from pos_api.adapter import submit_payment
        self.POS.login()
        self.POS.get_accounts()
        self.POS.get_minus_payment()
        for pm in self.POS.PMS:
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
