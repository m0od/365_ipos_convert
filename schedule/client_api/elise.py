from datetime import datetime, timedelta
from os.path import dirname

import requests
import base64


class Elise(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'elise_aeonhd'
        # self.ADAPTER_RETAILER = 'retry'
        self.ADAPTER_TOKEN = '8cfec4500eb706058d8646b6dbec1e55ee4edd74b9629318c5803f27a5219334'
        # self.ADAPTER_TOKEN = 'dad2757652dd799680317b26ccf44f39f88e39c0e917acf2b41194042c4f153b'
        self.MAIN = 'http://elisesrv.ddns.net:6072/pos365/TransactionData/GetOrders'
        self.USERNAME = 'Pos365api'
        self.PASSWORD = 'Elise@456'
        self.OUTLETCODE = 'N050'
        self.browser = requests.session()
        self.METHOD = {
            'Tiền Mặt': 'CASH',
            'Thẻ khác': 'THẺ'
        }

    def get_data(self, from_date):
        try:
            x = []
            self.browser.headers.update({
                'Authorization': f"Basic {base64.b64encode(f'{self.USERNAME}:{self.PASSWORD}'.encode('utf-8')).decode('utf-8')}"
                # 'Authorization': 'Basic UG9zMzY1YXBpOkVsaXNlQDQ1Ng=='
            })
            p = {
                'outletCode': self.OUTLETCODE,
                'frPurchaseDate': f'{from_date.strftime("%Y-%m-%d")} 00:00:00',
                'toPurchaseDate': f'{from_date.strftime("%Y-%m-%d")} 23:59:59'
            }
            print(p, self.MAIN)
            res = self.browser.get(self.MAIN, params=p)
            if res.status_code == 400:
                submit_error(retailer=self.ADAPTER_RETAILER, reason='BAD REQUEST')
                return False
            elif res.status_code == 401:
                submit_error(retailer=self.ADAPTER_RETAILER, reason='AUTH FAIL')
                return False
            elif res.status_code != 200:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'STATUS {str(res.status_code)}')
                return False
            js = res.json()
            for _ in js:
                # print(_)
                code = _['orderCode']
                pur_date = datetime.strptime(_['purchaseDate'], '%Y-%m-%dT%H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                ods = []
                pms = []
                for __ in _['paymentMethods']:
                    # print(__['name'])
                    if __['name'] not in x:
                        x.append(__['name'])
                    name = self.METHOD.get(__['name']) is not None and self.METHOD.get(__['name']) or __['name']
                    pms.append({
                        'Name': name.upper(),
                        'Value': abs(__['value'])
                    })

                if _['status'] == 3:
                    for __ in _['orderDetails']:
                        ods.append({
                            'Code': __['productCode'],
                            'Name': __['name'],
                            'Price': __['price'],
                            'Quantity': abs(__['qty'])
                        })
                    print(_)
                    total = 0
                    for __ in _['paymentMethods']:
                        total += abs(__['value'])
                    data = {
                        'Status': 0,
                        'ReturnDetails': ods,
                        'ReturnDate': pur_date,
                        'Code': code,
                        'Total': abs(_['total'] - abs(_['discount'])),
                        'TotalPayment': total,
                        'PaymentMethods': pms,
                        'VAT': 0,
                        'Discount': abs(_['discount']),
                    }
                    # print(data)
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                    data = {
                        'Code': f'VAT_{code}',
                        'Total': 0,
                        'TotalPayment': 0,
                        'PaymentMethods': [],
                        'Discount': 0,
                        'Status': 2,
                        'VAT': 0,
                        'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': total}],
                        'PurchaseDate': pur_date,
                        'OrderDetails': ods
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)

                else:
                    for __ in _['orderDetails']:
                        ods.append({
                            'Code': __['productCode'],
                            'Name': __['name'],
                            'Price': __['price'],
                            'Quantity': __['qty']
                        })
                    data = {
                        'Code': code,
                        'Total': _['total'] - _['discount'],
                        'TotalPayment': _['total'] - _['discount'],
                        'PaymentMethods': pms,
                        'Discount': _['discount'],
                        'Status': 2,
                        'VAT': _['vat'],
                        'PurchaseDate': pur_date,
                        'OrderDetails': ods
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                    print(data)
                    # print(_['orderCode'])
                    # print(_['discount'])
                    # print(_['vat'])
                    # print(_['total'])
                    # print(_['status'])
                    # print(_['orderDetails'])
                    # print(_['paymentMethods'])
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        # print(x)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    Elise().get_data(datetime.now() - timedelta(days=1))
