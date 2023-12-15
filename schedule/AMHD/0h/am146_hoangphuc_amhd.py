import sys
from datetime import datetime, timedelta
from os.path import dirname

import requests


class AM146(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'hoangphuc_amhd'
        self.ADAPTER_TOKEN = '9092b80bacca47f979fc394b42d614c048d54e643dc1a759e53c9ae1a40d7c1a'
        self.URL = 'http://www.ninunick.vn:8855/services/hpi/get/transoffline'
        self.AUTHORIZATION = 'hoangphuc@SZYYufR8CNxvXm5obclbYA=='
        self.browser = requests.session()
        self.RETURN = []
        self.METHOD = {
            'DEBIT': 'THẺ',
            'CASH': 'CASH',
            'CREATE VOUCHER RETURN': 'CASH',
            'VOUCHER RETURN': 'CASH',
            'VN PAY': 'VNPAY',
            'VOUCHER TẶNG': 'VOUCHER'
        }
        self.TOKEN = None
        self.DATE = datetime.now() - timedelta(days=1)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        params = {
            'to_date': self.DATE.strftime('%Y-%m-%d')
        }
        self.browser.headers.update({
            'Authorization': self.AUTHORIZATION
        })
        res = self.browser.get(self.URL, params=params)
        if res.status_code != 200:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(res.status_code))
            return False

        js = res.json()
        for _ in js:
            # print(_)
            code = _['Receipt_No']
            pur_date = datetime.strptime(_['Date_Time'], '%Y-%m-%d %H:%M:%S')
            discount = 0
            ods = []
            for __ in _['Items']:
                discount += __['Discount_amount']
                ods.append({
                    'Code': __['Barcode'].strip(),
                    'Name': __['Description'].strip(),
                    'Price': __['Price'],
                    'Quantity': __['Quantity']
                })
            pms = []
            for __ in _['Payment_method']:
                values = list(__.values())
                pms.append({
                    'Name': self.METHOD.get(values[0].upper()),
                    'Value': values[1]
                })
            if _['Revenue'] < 0:
                for __ in pms:
                    __.update({'Value': abs(__['Value'])})
                ret_send = {
                    'Code': code,
                    'ReturnDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Discount': abs(discount),
                    'Total': abs(_['Revenue']),
                    'TotalPayment': abs(_['Revenue']),
                    'Status': 0,
                    'ReturnDetails': ods,
                    'PaymentMethods': pms
                }
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=ret_send)
                send = {
                    'Code': f'VAT_{code}',
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': 0,
                    'TotalPayment': 0,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': 0}],
                    'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': _['Revenue']}]
                }
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)

            else:
                send = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': _['Revenue'],
                    'TotalPayment': _['Revenue'],
                    'VAT': 0,
                    'Discount': discount,
                    'OrderDetails': ods,
                    'PaymentMethods': pms
                }
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
