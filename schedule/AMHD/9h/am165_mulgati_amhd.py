import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM165(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from nhanh import NHANH
        self.ADAPTER_RETAILER = 'mulgati_amhd'
        self.ADAPTER_TOKEN = 'dbb831aa0f237e97d5b15c6116f8bcb6ff47f869aa4ba0544d89fa81b9e5833a'
        self.NHANH = NHANH()
        self.NHANH.ACCOUNT = 'nhanvienmulgati'
        self.NHANH.PASSWORD = 'Mulgati@123'
        self.NHANH.DATE = datetime.now() - timedelta(days=1)
        self.NHANH.METHOD = {
            'Quẹt thẻ': 'THẺ',
            'Tiền khách đưa': 'CASH',
            'Chuyển khoản': 'CHUYỂN KHOẢN',
            'Tiền chuyển khoản trả khách': 'CHUYỂN KHOẢN',
            'Tiền mặt trả khách': 'CASH'
        }

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        stt, reason = self.NHANH.auth()
        if not stt:
            submit_error(self.ADAPTER_RETAILER, reason)
            return
        self.NHANH.get_orders()
        self.NHANH.get_returns()
        for _, order in self.NHANH.ORDERS.items():
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        for _, ret in self.NHANH.RETURNS.items():
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, ret)
