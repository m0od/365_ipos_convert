import sys
from os.path import dirname


class AM186(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'pedro_amhd'
        self.ADAPTER_TOKEN = 'b8dbc43298ddf8bc28ac5260e7add086b25911bc639d99acdb26d86138f60570'
        self.POS = POS365()
        self.POS.DOMAIN = 'am186'
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'

    def get_data(self):
        from pos_api.adapter import submit_payment
        self.POS.login()
        self.POS.get_accounts()
        self.POS.get_minus_payment()
        for pm in self.POS.PMS:
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
