import hashlib
import random
import string
from datetime import datetime, timedelta

import requests


class KIOTVIET(object):
    def __init__(self):
        self.CLASS = None
        self.DOMAIN = None
        self.ACCOUNT = None
        self.PASSWORD = None
        self.FINGER = f'{hashlib.md5(self.random_str()).hexdigest()}_Firefox_Desktop_Windows'
        self.API_MANS = [
            'api-man.kiotviet.vn',
            'api-man1.kiotviet.vn',
            'api-man2.kiotviet.vn'
        ]
        self.SALE_SRC = ['null']
        self.API_MAN = None
        self.TOKEN = None
        self.BRANCH_ID = None
        self.ORDERS = []
        self.METHOD = None
        self.RETURN = []
        self.browser = requests.session()

    def random_str(self):
        return ''.join(random.choice(string.ascii_letters) for i in range(8)).encode('utf-8')

    def login(self):
        try:
            js = {
                'IsManageSide': True,
                'FingerPrintKey': self.FINGER,
                'model': {
                    'RememberMe': True,
                    'ShowCaptcha': False,
                    'UserName': self.ACCOUNT,
                    'Password': self.PASSWORD
                }
            }
            self.browser.get(f'https://{self.DOMAIN}.kiotviet.vn/man')
            self.browser.headers.update({
                'content-type': 'application/json',
                'retailer': self.DOMAIN
            })
            params = {
                'quan-ly': 'true'
            }
            for _ in self.API_MANS:
                res = self.browser.post(f'https://{_}/api/account/login', json=js, params=params)
                if res.status_code != 200: continue
                res = res.json()
                if res.get('isSuccess'):
                    self.TOKEN = res['token']
                    self.BRANCH_ID = str(res['currentBranch'])
                    return True, None
                else:
                    return False, '[LOGIN] INVALID_LOGIN'
        except Exception as e:
            return False, f'[LOGIN] {str(e)}'

    def get_orders(self):
        skip = 0
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        since = since.strftime('%Y-%m-%dT00:00:00')
        until = until.strftime('%Y-%m-%dT00:00:00')
        while True:
            filter = ['((']
            _src = []
            for src in self.SALE_SRC:
                _src.append(' '.join(['SaleChannelId', 'eq', src]))
            filter += [' or '.join(_src)]
            filter += [')']
            filter += ['and', 'PurchaseDate', 'ge', f"datetime'{since}'"]
            filter += ['and', 'PurchaseDate', 'lt', f"datetime'{until}'"]
            filter += ['and', '(', 'Status', 'eq', '3']
            filter += ['or', 'Status', 'eq', '1', ')', ')']
            params = {
                'format': 'json',
                '$top': '100',
                '$orderby': 'PurchaseDate',
                '$filter': ' '.join(filter),
                '$skip': str(skip)
            }
            # print(params)
            self.browser.headers.update({
                'authorization': f'Bearer {self.TOKEN}',
                'branchId': self.BRANCH_ID
            })
            res = None
            if self.API_MAN is None:
                for _ in self.API_MANS:
                    try:
                        res = self.browser.post(f'https://{_}/api/invoices/list', params=params)
                        res = res.json()
                        self.API_MAN = _
                        break
                    except:
                        pass
            else:
                res = self.browser.post(f'https://{self.API_MAN}/api/invoices/list', params=params)
                res = res.json()
            if len(res['Data']) == 0:
                break
            index = 0
            while index < len(res['Data']):
                id = res['Data'][index]['Id']
                invoice = self.browser.get(f'https://{self.API_MAN}/api/invoices/{id}').json()
                # print(invoice['Code'])
                pur_date = datetime.strptime(invoice['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                ods = invoice['InvoiceDetails']
                od = []
                for i in ods:
                    od.append({
                        'Code': i['ProductCode'].strip(),
                        'Name': i['ProductName'].strip(),
                        'Price': int(i['Price']),
                        'Quantity': int(i['Quantity'])
                    })
                pm = []
                r_pay = 0
                if invoice.get('ReturnId') is not None:
                    ret = self.browser.get(f"https://{self.API_MAN}/api/returns/{invoice['ReturnId']}").json()
                    self.RETURN.append(ret['Code'].strip())
                    ret_date = datetime.strptime(ret['ReturnDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    rds = ret['ReturnDetails']
                    rd = []
                    for item in rds:
                        rd.append({
                            'Code': item['ProductCode'].strip(),
                            'Name': item['ProductName'].strip(),
                            'Price': int(item['Price']),
                            'Quantity': int(item['Quantity'])
                        })
                    r_pm = []
                    for method in ret['Payments']:
                        r_pm.append({
                            'Name': self.METHOD.get(method['Method'].upper()),
                            'Value': abs(int(method['Amount']))
                        })
                    if len(r_pm) == 0:
                        r_pm.append({'Name': 'CASH', 'Value': int(invoice['TotalPayment'])})
                    r_pay = int(ret['TotalPayment'])
                    # print('--->', r_pay)
                    ret_send = {
                        'Code': ret['Code'].strip(),
                        'ReturnDate': ret_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Discount': ret.get('ReturnDiscount') is not None and int(ret['ReturnDiscount']) or 0,
                        'Total': r_pay,
                        'TotalPayment': r_pay,
                        'Status': 0,
                        'ReturnDetails': rd,
                        'PaymentMethods': r_pm
                    }
                    self.ORDERS.append(ret_send)
                    # submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=ret_send)
                    if r_pay > 0:
                        vat = int(round(-r_pay / 11, 0))
                for method in invoice['Payments']:
                    pm.append({
                        'Name': self.METHOD.get(method['Method'].upper()),
                        'Value': int(method['Amount'])
                    })
                if len(pm) == 0:
                    pm.append({'Name': 'CASH', 'Value': int(invoice['TotalPayment'])})
                send = {
                    'Code': invoice['Code'],
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': int(invoice['TotalPayment']),
                    'TotalPayment': int(invoice['TotalPayment']),
                    'VAT': 0,
                    'Discount': invoice.get('Discount') is not None and int(invoice['Discount']) or 0,
                    'OrderDetails': od,
                    'PaymentMethods': pm
                }
                if r_pay > 0:
                    send.update({'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': -r_pay}]})
                self.ORDERS.append(send)
                # submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                index += 1
            skip += 100

    def get_returns(self):
        since = datetime.now() - timedelta(days=1)
        until = datetime.now()
        since = since.strftime('%Y-%m-%dT00:00:00')
        until = until.strftime('%Y-%m-%dT00:00:00')
        skip = 0
        while True:
            filter = ['(', 'SaleChannelId', 'eq', 'null']
            filter += ['and', 'ReturnDate', 'ge', f"datetime'{since}'"]
            filter += ['and', 'ReturnDate', 'lt', f"datetime'{until}'"]
            filter += ['and', 'Status', 'eq', '1', ')']
            params = {
                'format': 'json',
                '$top': '100',
                '$orderby': 'ReturnDate',
                '$filter': ' '.join(filter),
                'skip': str(skip)
            }
            self.browser.headers.update({
                'authorization': f'Bearer {self.TOKEN}',
                'branchId': self.BRANCH_ID
            })
            res = self.browser.get(f'https://{self.API_MAN}/api/returns', params=params).json()
            # print(res)
            if len(res['Data']) == 0: break
            index = 0
            while index < len(res['Data']):
                id = res['Data'][index]['Id']
                invoice = self.browser.get(f'https://{self.API_MAN}/api/returns/{id}').json()
                if invoice['Code'].strip() in self.RETURN:
                    index += 1
                    continue
                pur_date = datetime.strptime(invoice['ReturnDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                rds = invoice['ReturnDetails']
                rd = []
                for item in rds:
                    rd.append({
                        'Code': item['ProductCode'].strip(),
                        'Name': item['ProductName'].strip(),
                        'Price': int(item['Price']),
                        'Quantity': int(item['Quantity'])
                    })
                r_pm = []
                for method in invoice['Payments']:
                    r_pm.append({
                        'Name': self.METHOD.get(method['Method'].upper()),
                        'Value': abs(int(method['Amount']))
                    })
                if len(r_pm) == 0:
                    r_pm.append({'Name': 'CASH', 'Value': int(invoice['TotalPayment'])})
                send = {
                    'Code': invoice['Code'].strip(),
                    'ReturnDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Discount': invoice.get('ReturnDiscount') is not None and int(invoice['ReturnDiscount']) or 0,
                    'Total': int(invoice['ReturnTotal']),
                    'TotalPayment': int(invoice['ReturnTotal']),
                    'Status': 0,
                    'ReturnDetails': rd,
                    'PaymentMethods': r_pm
                }
                self.ORDERS.append(send)
                send = {
                    'Code': f'VAT_{invoice["Code"].strip()}',
                    'Total': 0,
                    'TotalPayment': 0,
                    'PaymentMethods': r_pm,
                    'Discount': 0,
                    'Status': 2,
                    'VAT': 0,
                    'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': -int(invoice['ReturnTotal'])}],
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'OrderDetails': []
                }
                self.ORDERS.append(send)
                index += 1
            skip += 100
