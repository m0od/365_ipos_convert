import sys
from datetime import datetime, timedelta
from os.path import dirname

import requests


class AM090(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'jumparena_amhd'
        self.ADAPTER_TOKEN = 'c54fac090b0899fdeb99f4a47f9afb7b2e3942069af0bab9427962f8439da0b1'
        self.ACCOUNT = 'AEON_HaDong'
        self.PASSWORD = 'Hadong@2024'
        self.API_URL = 'https://pos-api.jumparena.vn:8443/api'
        self.BROWSER = requests.session()
        self.orders = {}
        self.DATE = datetime.now() - timedelta(days=1)
        # self.methods = {
        #     'Cash_HaDong': 'CASH'
        # }

    def login(self):
        r = self.BROWSER.post(f'{self.API_URL}/auth/login', json={
            'username': self.ACCOUNT,
            'password': self.PASSWORD
        })
        # print(r.json()['token'])
        self.BROWSER.headers.update({
            'authorization': f'Bearer {r.json()["token"]}'
        })

        # for k, v in orders.items():
        #     print(v)
    def get_orders(self):
        params = {
            'companyCode': 'CP001',
            'storeId': 'JAOF116',
            'userLogin': self.ACCOUNT,
            'fromDate': self.DATE.strftime('%Y-%m-%d'),
            'toDate': self.DATE.strftime('%Y-%m-%d')
        }
        r = self.BROWSER.get(f'{self.API_URL}/report/Get_RPT_SalesTransactionDetail', params=params)
        # self.orders = {}
        # print(r.json())
        for data in r.json()['data']:
            # print(data['transId'])
            # print(data['itemCode'])
            # print(data['quantity'])
            # print(data['price'])
            # print(data['description'])
            # print(data['taxAmt'])
            # print(data['lineTotal'] - data['finalLineTotal'])
            pur_date = data['createdOn']
            try:
                pur_date = datetime.strptime(pur_date, '%m/%d/%Y %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
            code = data['transId']
            ods = [{
                'Code': data['itemCode'],
                'Name': data['description'],
                'Price': data['price'],
                'Quantity': data['quantity']
            }]
            discount = data['lineTotal'] - data['finalLineTotal']
            if self.orders.get(code) is None:
                self.orders.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': data['finalLineTotal'],
                        'TotalPayment': data['finalLineTotal'],
                        'VAT': data['taxAmt'],
                        'Discount': discount,
                        'OrderDetails': ods,
                        # 'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    }
                })
            else:
                self.orders[code]['Total'] += data['finalLineTotal']
                self.orders[code]['TotalPayment'] += data['finalLineTotal']
                self.orders[code]['Discount'] += discount
                self.orders[code]['VAT'] += data['taxAmt']
                self.orders[code]['OrderDetails'].extend(ods)
        # return self.orders
        # print(self.orders)

    def get_payments(self):
        # from pos_api.adapter import submit_error, submit_order
        params = {
            'companyCode': 'CP001',
            'storeId': 'JAOF116',
            'userLogin': self.ACCOUNT,
            'fromDate': self.DATE.strftime('%Y-%m-%d'),
            'toDate': self.DATE.strftime('%Y-%m-%d')
        }
        r = self.BROWSER.get(f'{self.API_URL}/report/Get_RPT_SalesTransactionPayment', params=params)
        for data in r.json()['data']:
            name = data['paymentCode'].split()[0]
            name = name.replace('_HaDong', '').upper()
            pms = [{
                'Name': name,
                'Value': data['totalAmt']
            }]
            code = data['transId']
            if self.orders.get(code) is not None:
                if self.orders[code].get('PaymentMethods') is None:
                    self.orders[code].update({'PaymentMethods': pms})
                else:
                    self.orders[code]['PaymentMethods'].extend(pms)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        self.login()
        self.get_orders()
        self.get_payments()
        for k, v in self.orders.items():
            # print(v)
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, v)
            for _ in v['PaymentMethods']:
                if _['Value'] < 0:
                    pm = {
                        'Code': f'{v["Code"]}-{_["Name"]}',
                        'OrderCode': v["Code"],
                        'Amount': _['Value'],
                        'TransDate': v["PurchaseDate"],
                        'AccountId': _["Name"]
                    }
                    submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)