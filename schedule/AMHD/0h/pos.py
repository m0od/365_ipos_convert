import time
from datetime import timedelta

import requests


class POS365(object):
    def __init__(self):
        self.ACCOUNT = None
        self.PASSWORD = None
        self.DOMAIN = None
        self.browser = None
        self.DATE = None
        self.URL = None

    def login(self):
        js = {
            'username': self.ACCOUNT,
            'password': self.PASSWORD
        }
        self.URL = f'https://{self.DOMAIN}.pos365.vn'
        while True:
            try:
                self.browser = requests.session()
                r = self.browser.post(f'{self.URL}/api/auth', json=js, timeout=5).json()
                if r.get('SessionId'):
                    self.browser.headers.update({'content-type': 'application/json'})
                    break
            except:
                pass
    def get_order(self):
        while True:
            try:
                filter = []
                filter += ['Status', 'eq', '2']
                filter += ['and']
                filter += ['PurchaseDate', 'eq', "'yesterday'"]
                filter += ['and', 'Total', 'gt', '0']
                params = {
                    'Top': '1',
                    'Filter': ' '.join(filter),
                    # 'Includes': 'OrderDetails'
                }
                r = self.browser.get(f'{self.URL}/api/orders',
                                     params=params,
                                     timeout=5).json()
                # print(r)
                if not len(r['results']):
                    return None
                ret = r['results'][0]
                ret.update({'OrderDetails': self.get_details(ret['Id'])})
                return ret
                # return None
            except:
                pass
            # exit(0)

    def get_details(self, oid):
        while True:
            try:
                params = {
                    'Top': '50',
                    'OrderId': str(oid),
                    'Includes': 'Product'
                }
                r = self.browser.get(f'{self.URL}/api/orders/detail',
                                     params=params,
                                     timeout=5).json()
                ods = []
                for _ in r['results']:
                    if _['Price'] > 0:
                        ods.append({
                            'Code': _['Product']['Code'],
                            'Name': _['Product']['Name'],
                            'Quantity': _['Quantity'] * -1,
                            'Price': _['Price'],
                        })
                return ods
            except:
                pass
            # exit(0)