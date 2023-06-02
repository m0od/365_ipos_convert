from os.path import dirname
import requests
import hashlib
import string
import random
from datetime import datetime

class MatViet(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'matviet_aeonhd'
        self.ADAPTER_TOKEN = '3bc06ad30c1754ba1c7fbf14338c159535989dbeefd2c82fe2a4651a67806d9e'
        # self.ADAPTER_RETAILER = 'retry'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.URL = 'http://matviet.e-biz.com.vn/api/MatVietPalexy/AeonHaDong/GetTrasaction'
        self.Token = 'C29B4029-7E06-4CDB-9BA6-DCFB4205AD3C'
        self.browser = requests.session()
        self.method = {
            'TIỀN MẶT': 'CASH'
        }
    def get_data(self):
        js = {
            'Tocken': self.Token,
            'TransactionDate': '2023-06-01'
        }
        res = self.browser.post(self.URL, json=js)
        if res.status_code != 200: return False
        js = res.json()
        if len(js['Error']):
            # submit_error(retailer=self.ADAPTER_RETAILER, reason=res.json()['Error'])
            return False
        if len(js['Data']) == 0:
            return False
        for _ in js['Data']:
            # print(_)
            ods = []
            for p in _['OrderDetails']:
                ods.append({
                    'Code': p['ProductCode'],
                    'Name': p['Name'].split('-Mã hàng:')[0],
                    'Quantity': p['Qty'],
                    'Price': p['Price']
                })
            pms = []
            if _['Code'].startswith('SO'):
                total = 0
            else:
                total = _['Total']
            for pm in _['PaymentMethods']:
                name = self.method.get(pm['Name']) is None and pm['Name'] or self.method.get(pm['Name'])
                pms.append({
                    'Name': name,
                    'Value': pm['Value']
                })
                if _['Code'].startswith('SO'):
                    total += pm['Value']
            send = {
                'Code': _['Code'],
                'Total': total,
                'TotalPayment': _['TotalPayment'],
                'PaymentMethods': pms,
                'Discount': _['Discount'],
                'Status': 2,
                'VAT': _['Vat'],
                'PurchaseDate': _['PaymentDate'],
                'OrderDetails': ods
            }
            if _['Status']==1:
                print(send['Code'], send['PurchaseDate'], send['Total'])
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
            else:
                print(_)
            # print(res.json())


if str(__name__):
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    MatViet().get_data()

