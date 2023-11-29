import sys
from os.path import dirname


class DecathlonAMHD(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'decathlon_amhd'
        self.ADAPTER_TOKEN = 'ad8a4699296da3788fcc5e14d5296f0c4fcd78a6803e5eecd085416570e94b19'
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