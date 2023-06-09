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
            # if res.status_code == 400:
            #     submit_error(retailer=self.ADAPTER_RETAILER, reason='BAD REQUEST')
            #     return False
            # elif res.status_code == 401:
            #     submit_error(retailer=self.ADAPTER_RETAILER, reason='AUTH FAIL')
            #     return False
            # elif res.status_code != 200:
            #     submit_error(retailer=self.ADAPTER_RETAILER, reason=f'STATUS {str(res.status_code)}')
            #     return False
            # js = res.json()
            # for _ in js:
            #     # print(_)
            #     code = _['orderCode']
            #     pur_date = datetime.strptime(_['purchaseDate'], '%Y-%m-%dT%H:%M:%S')
            #     pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            #     ods = []
            #     pms = []
            #     for __ in _['paymentMethods']:
            #         # print(__['name'])
            #         if __['name'] not in x:
            #             x.append(__['name'])
            #         name = self.METHOD.get(__['name']) is not None and self.METHOD.get(__['name']) or __['name']
            #         pms.append({
            #             'Name': name.upper(),
            #             'Value': abs(__['value'])
            #         })
            #
            #     if _['status'] == 3:
            #         for __ in _['orderDetails']:
            #             ods.append({
            #                 'Code': __['productCode'],
            #                 'Name': __['name'],
            #                 'Price': __['price'],
            #                 'Quantity': abs(__['qty'])
            #             })
            #         print(_)
            #         total = 0
            #         for __ in _['paymentMethods']:
            #             total += abs(__['value'])
            #         data = {
            #             'Status': 0,
            #             'ReturnDetails': ods,
            #             'ReturnDate': pur_date,
            #             'Code': code,
            #             'Total': abs(_['total'] - abs(_['discount'])),
            #             'TotalPayment': total,
            #             'PaymentMethods': pms,
            #             'VAT': 0,
            #             'Discount': abs(_['discount']),
            #         }
            #         # print(data)
            #         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
            #         data = {
            #             'Code': f'VAT_{code}',
            #             'Total': 0,
            #             'TotalPayment': 0,
            #             'PaymentMethods': [],
            #             'Discount': 0,
            #             'Status': 2,
            #             'VAT': 0,
            #             'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': total}],
            #             'PurchaseDate': pur_date,
            #             'OrderDetails': ods
            #         }
            #         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
            #
            #     else:
            #         for __ in _['orderDetails']:
            #             ods.append({
            #                 'Code': __['productCode'],
            #                 'Name': __['name'],
            #                 'Price': __['price'],
            #                 'Quantity': __['qty']
            #             })
            #         data = {
            #             'Code': code,
            #             'Total': _['total'] - _['discount'],
            #             'TotalPayment': _['total'] - _['discount'],
            #             'PaymentMethods': pms,
            #             'Discount': _['discount'],
            #             'Status': 2,
            #             'VAT': _['vat'],
            #             'PurchaseDate': pur_date,
            #             'OrderDetails': ods
            #         }
            #         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
            #         print(data)
            #         # print(_['orderCode'])
            #         # print(_['discount'])
            #         # print(_['vat'])
            #         # print(_['total'])
            #         # print(_['status'])
            #         # print(_['orderDetails'])
            #         # print(_['paymentMethods'])
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        # print(x)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    Lyn().get_data(datetime.now() - timedelta(days=1))
