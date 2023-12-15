import json
import time
from datetime import timedelta, datetime

import requests


class POS365(object):
    def __init__(self):
        self.ACCOUNT = None
        self.PASSWORD = None
        self.DOMAIN = None
        self.browser = None
        self.DATE = None
        self.URL = None
        self.METHOD = {None: 'CASH'}
        self.PMS = []

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

    def get_accounts(self):
        while True:
            try:
                r = self.browser.get(f'{self.URL}/api/accounts').json()
                for _ in r:
                    self.METHOD.update({
                        _['Id']: _['Name']
                    })
                if len(list(self.METHOD.keys())) > 0: break
            except:
                pass

    def get_minus_payment(self):
        skip = 0
        since = datetime.now() - timedelta(days=19)
        until = datetime.now() - timedelta(days=1)
        since = since.strftime('%Y-%m-%dT17:00:00Z')
        until = until.strftime('%Y-%m-%dT16:59:00Z')
        filter = ['(', 'Status', 'eq', '2']
        filter += ['and', 'PurchaseDate', 'ge', f"'datetime''{since}'''"]
        filter += ['and', 'PurchaseDate', 'lt', f"'datetime''{until}'''"]
        filter += [')']
        while True:
            try:
                params = {
                    'Top': 50,
                    'Skip': str(skip),
                    'Filter': ' '.join(filter)
                }
                r = self.browser.get(f'{self.URL}/api/orders', params=params).json()
                if len(r['results']) == 0: break
                for _ in r['results']:
                    if not _.get('MoreAttributes'): continue
                    attr = json.loads(_['MoreAttributes'])
                    if not attr.get('PaymentMethods'): continue
                    for trans in attr['PaymentMethods']:
                        if trans.get('Value') < 0:
                            date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                            date = (date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                            data = {
                                'Code': f'{_["Code"]}-{self.METHOD.get(trans["AccountId"])}',
                                'OrderCode': _['Code'],
                                'Amount': trans['Value'],
                                'TransDate': date,
                                'AccountId': self.METHOD.get(trans['AccountId'])
                            }
                            self.PMS.append(data)
                skip += 50
            except:
                pass
