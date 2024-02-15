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

    def check_total(self, TOTAL):
        since = self.DATE - timedelta(days=1)
        since = since.strftime('%Y-%m-%dT17:00:00Z')
        before = self.DATE.strftime('%Y-%m-%dT16:59:00Z')

        while True:
            if TOTAL == 0: break
            self.login()
            try:
                filter = []
                filter += ['Status', 'eq', '2']
                filter += ['and']
                filter += ['PurchaseDate', 'ge']
                filter += [f"'datetime''{since}'''"]
                filter += ['and']
                filter += ['PurchaseDate', 'lt']
                filter += [f"'datetime''{before}'''"]
                params = {
                    'Top': '1',
                    'IncludeSummary': 'true',
                    'Filter': ' '.join(filter)
                }
                r = self.browser.get(f'{self.URL}/api/orders',
                                     params=params,
                                     timeout=5).json()
                print(TOTAL, r['results'][0]['Total'])
                if TOTAL == r['results'][0]['Total']:
                    return
                time.sleep(30)
            except:
                time.sleep(5)

    def get_order(self, code):
        while True:
            try:
                filter = []
                filter += ['Status', 'eq', '2']
                filter += ['and']
                filter += ['Code', 'eq', f"'{code}'"]
                params = {
                    'Top': '1',
                    'Filter': ' '.join(filter),
                    # 'Includes': 'OrderDetails'
                }
                r = self.browser.get(f'{self.URL}/api/orders',
                                     params=params,
                                     timeout=5).json()
                if len(r['results']):
                    ret = r['results'][0]
                    ret.update({'OrderDetails': self.get_details(ret['Id'])})
                    return ret
                return None
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