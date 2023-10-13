from datetime import datetime, timedelta
from os.path import dirname

import requests
import base64


class Lyn(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'lyn_aeonhd'
        # self.ADAPTER_RETAILER = 'retry'
        self.ADAPTER_TOKEN = 'd51fe8aa8c51fc795d7e145ebe4bb3ce2f9f28b5d44db831b50718b419972662'
        # self.ADAPTER_TOKEN = 'dad2757652dd799680317b26ccf44f39f88e39c0e917acf2b41194042c4f153b'
        self.MAIN = 'https://am062.pos365.vn'
        self.USERNAME = 'admin'
        self.PASSWORD = '123456'
        self.browser = requests.session()

    def get_data(self, from_date):
        try:
            self.browser.headers.update({
                'Content-Type': 'application/json'
            })
            js = {
                'Username': self.USERNAME,
                'Password': self.PASSWORD
            }
            res = self.browser.post(f'{self.MAIN}/api/auth', json=js)
            if res.status_code != 200:
                submit_error(self.ADAPTER_RETAILER, reason='LOGIN FAILED')
                return
            skip = 0
            while True:
                p = {
                    'Top': '50',
                    'Skip': str(skip),
                    'Filter': "PurchaseDate eq 'yesterday'"
                }
                res = self.browser.get(f'{self.MAIN}/api/orders', params=p)
                if res.status_code != 200:
                    continue
                js = res.json()
                if len(js['results']) == 0: break
                for _ in js['results']:
                    print(_)
                    if _['TotalPayment'] < 0:
                        print(_)
                        id = _.get('AccountId')
                        pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                        pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                        data = {
                            'AccountingTransaction': {
                                'Id': 0,
                                'Amount': _['TotalPayment'],
                                'OrderId': _['Id'],
                                'AccountingTransactionType': 1,
                                'TransDate': pur_date,
                                'AccountId': id,
                                'Code': f'PT_{_["Code"]}'
                            }
                        }
                        while True:
                            r = self.browser.post(f'{self.MAIN}/api/accountingtransaction', json=data)
                            if r.status_code == 200: break
                skip += 50
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        # print(x)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    # Lyn().get_data(datetime.now() - timedelta(days=1))
