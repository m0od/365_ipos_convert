import json
from datetime import datetime, timedelta
from os.path import dirname

import requests
from concurrent import futures


class FixVAT(object):
    global URLS
    URLS = {
        # 'amhp007': {
        #     'username': 'fixvat',
        #     'password': '123456',
        #     'retailer': 'amhp007',
        #     'token': 'e08a3aeb57ac74e651ae4a2ea11fae2ed8ce650d4f5df5a1bc47c56721454755'
        # },
        # 'amhp039': {
        #     'username': 'fixvat',
        #     'password': '123456',
        #     'retailer': 'amhp039',
        #     'token': 'e08a3aeb57ac74e651ae4a2ea11fae2ed8ce650d4f5df5a1bc47c56721454755'
        # },
        'am002': {
            'username': 'admin',
            'password': '123456',
            'retailer': 'hla_aeonhd',
            'token': 'a54e396bfd3ffc8bf01ed9dca0074bb480012c3c255ad446ee7f7a96a94eebb4'
        },
        'am006': {
            'username': 'admin',
            'password': '123456',
            'retailer': 'lugvn_aeonhd',
            'token': '203cb103f845592d8c0640dedcd862bc1c43cca04c2d48e687ba4ea286496ab1'
        },
        'am020': {
            'username': 'fixvat',
            'password': '123456',
            'retailer': 'noithathoanmy_aeonhd',
            'token': '605eb397b92c6afdb3ac7559fbf33bd41792a2a754bae974e6b558db6cf2a03b'
        },
        'am039': {
            'username': 'admin',
            'password': '123456',
            'retailer': 'lovekids_aeonhd',
            'token': '51f3ea6b907b88fac941d28a48adba871f6eb7492f43a35d357dd59534cbcb6e'
        },
        'am051': {
            'username': 'admin',
            'password': '123456',
            'retailer': 'homechef_aeonhd',
            'token': '9bf56eacdaef0a2bb89ec1a3e94c1ae5f9c88a9780785cdc4a25a7715f406be1'
        },
        'am118': {
            'username': 'fixvat',
            'password': '123456',
            'retailer': 'lizanamat_aeonhd',
            'token': 'd85a236914ef0f607ebefbfb95821b9e8cd4dfcaedbbe9a9ec10c7005576439b'
        },
        'am117': {
            'username': 'admin',
            'password': 'aeonhd',
            'retailer': 'digibox_aeonhd',
            'token': '99d464d3287b91a1b70a857c4faee950a048f65ef7728f5370905b72c75dbbfa'
        }
    }

    def __init__(self):
        return

    def auth(self, target, token):
        browser = requests.session()
        browser.headers.update({
            'content-type': 'application/json'
        })
        js = {
            'username': token['username'],
            'password': token['password'],
        }
        while True:
            r = browser.post(f"https://{target}.pos365.vn/api/auth", json=js)
            if r.status_code != 200: continue
            break
        return browser

    def payment_list(self, target, browser):
        while True:
            r = browser.get(f"https://{target}.pos365.vn/api/accounts", params={'Top': '50'})
            if r.status_code != 200:
                continue
            method = {}
            for _ in r.json():
                method.update({
                    _['Id']: _['Name']
                })
            return method

    def payment_methods(self, target, browser, method, oid):
        while True:
            # print(oid)
            r = browser.get(f"https://{target}.pos365.vn/api/accountingtransaction",
                            params={'Top': '50', 'Filter': f'OrderId eq {oid}'})
            # print(r.status_code)
            if r.status_code != 200: continue
            # print(r.text)
            _ = r.json()['results']
            pms = []
            for __ in _:
                if __.get('AccountId') is None:
                    pms.append({
                        'Name': 'CASH',
                        'Value': __['Amount']
                    })
                else:
                    pms.append({
                        'Name': method.get(__['AccountId']),
                        'Value': __['Amount']
                    })

            return pms

    def order_detail(self, target, browser, oid):
        while True:
            r = browser.get(f"https://{target}.pos365.vn/api/orders/detail", params={'OrderId': str(oid),
                                                                                     'Includes': 'Product'})
            if r.status_code != 200: continue
            ods = []
            for _ in r.json()['results']:
                ods.append({
                    'Code': _['Product']['Code'],
                    'Name': _['Product']['Name'].strip(),
                    'Price': _['Price'],
                    'Quantity': _['Quantity']
                })
            return ods

    def order_list(self, target, token, browser, method):
        skip = 0
        while True:
            r = browser.get(f"https://{target}.pos365.vn/api/orders", params={
                'Top': '50',
                'Skip': str(skip),
                # 'Filter': "PurchaseDate eq 'yesterday'"
                'Filter': "PurchaseDate ge 'datetime''2023-06-30T17:00:00Z''' and PurchaseDate lt 'datetime''2023-07-02T16:59:00Z'''"
            })

            if r.status_code != 200: continue
            js = r.json()
            if len(js['results']) == 0:
                break
            js = js['results']
            for _ in js:
                # print(111111, _)
                code = _['Code']
                pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)
                status = _['Status']
                if status != 2: continue
                discount = _['Discount']
                total = _['Total']
                total_payment = _['TotalPayment']
                pms = self.payment_methods(target, browser, method, _['Id'])
                if len(pms) == 0:
                    pms.append({
                        'Name': 'CASH',
                        'Value': total
                    })
                ods = self.order_detail(target, browser, _['Id'])
                data = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': total,
                    'TotalPayment': total_payment,
                    'VAT': 0,
                    'Discount': discount,
                    'OrderDetails': ods,
                    'PaymentMethods': pms
                }
                # print(data)
                submit_order(retailer=token['retailer'], token=token['token'], data=data)
                for __ in pms:
                    if __['Value'] < 0:
                        submit_payment(retailer=token['retailer'], token=token['token'], data={
                            "OrderCode": data['Code'],
                            "Amount": __['Value'],
                            "TransDate": pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "AccountId": __['Name']
                        })
            skip += 50
        # print(target, token)

    def fix(self):
        for target, token in URLS.items():
            browser = self.auth(target, token)
            method = self.payment_list(target, browser)
            self.order_list(target, token, browser, method)
            # break
            print('=' * 10)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order, submit_payment

    FixVAT().fix()
