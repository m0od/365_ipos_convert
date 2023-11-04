import json
from datetime import datetime, timedelta
from os.path import dirname

import requests


class PedroAMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'pedro_amhd'
        self.ADAPTER_TOKEN = 'f09da5187794d23befb9a316b583556b01e424897b073446efc05491b5e34fdb'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.POS = 'https://am186.pos365.vn'
        self.ACCOUNT = 'admin'
        self.PW = 'aeonhd'
        self.browser = None
        self.METHOD = {}

    def login(self):
        while True:
            try:
                self.browser = requests.session()
                self.browser.headers.update({
                    'content-type': 'application/json'
                })
                js = {
                    'Username': self.ACCOUNT,
                    'Password': self.PW
                }
                r = self.browser.post(f'{self.POS}/api/auth', json=js).json()
                if r.get('SessionId'): break
            except:
                pass

    def get_accounts(self):
        while True:
            try:
                r = self.browser.get(f'{self.POS}/api/accounts').json()
                for _ in r:
                    self.METHOD.update({
                        _['Id']: _['Name']
                    })
                if len(list(self.METHOD.keys())) > 0: break
            except:
                pass

    def get_data(self):
        self.login()
        self.get_accounts()
        skip = 0
        now = datetime.now() - timedelta(days=1)
        f = (now - timedelta(days=1)).strftime('%Y-%m-%dT17:00:00Z')
        t = now.strftime('%Y-%m-%dT16:59:00Z')
        while True:
            try:
                params = {
                    'Top': 50, 'Skip': str(skip),
                    'Filter': f"(Status eq 2 and PurchaseDate ge 'datetime''{f}''' and PurchaseDate lt 'datetime''{t}''')"
                }
                # print(params)
                r = self.browser.get(f'{self.POS}/api/orders', params=params).json()
                if len(r['results']) == 0: break
                for _ in r['results']:
                    # print(_.get('MoreAttributes'))
                    if not _.get('MoreAttributes'): continue
                    attr = json.loads(_['MoreAttributes'])
                    if not attr.get('PaymentMethods'): continue
                    for trans in attr['PaymentMethods']:
                        if trans.get('Value') < 0:
                            date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                            date = (date + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                            data = {
                                'OrderCode': _['Code'],
                                'Amount': trans['Value'],
                                'TransDate': date,
                                'AccountId': self.METHOD.get(trans['AccountId'])
                            }
                            submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                            # print(data)
                skip += 50
            except Exception as e:
                print(e)
                pass


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order, submit_payment

    # PedroAMHD().get_data()
