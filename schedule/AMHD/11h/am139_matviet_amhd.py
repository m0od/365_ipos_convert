import sys
from os.path import dirname
import requests
from datetime import datetime, timedelta


class AM139(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'matviet_amhd'
        self.ADAPTER_TOKEN = '3bc06ad30c1754ba1c7fbf14338c159535989dbeefd2c82fe2a4651a67806d9e'
        self.URL = 'http://matviet.e-biz.com.vn/api/MatVietPalexy/AeonHaDong/GetTrasaction'
        self.Token = 'C29B4029-7E06-4CDB-9BA6-DCFB4205AD3C'
        self.browser = requests.session()
        self.method = {
            'TIỀN MẶT': 'CASH'
        }
        self.DATE = datetime.now() - timedelta(days=1)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        js = {
            'Tocken': self.Token,
            'TransactionDate': self.DATE.strftime('%Y-%m-%d')
        }
        try:
            res = self.browser.post(self.URL, json=js)
            if res.status_code != 200: return False
            js = res.json()
            print(js)
            if len(js['Error']):
                # submit_error(retailer=self.ADAPTER_RETAILER, reason=res.json()['Error'])
                return False
            if len(js['Data']) == 0:
                return False
            for _ in js['Data']:
                ods = []
                for p in _['OrderDetails']:
                    ods.append({
                        'Code': p['ProductCode'],
                        'Name': p['Name'].split('-Mã hàng:')[0],
                        'Quantity': p['Qty'],
                        'Price': p['Price']
                    })
                pms = []
                total = 0
                for pm in _['PaymentMethods']:
                    name = self.method.get(pm['Name']) is None and pm['Name'] or self.method.get(pm['Name'])
                    pms.append({
                        'Name': name,
                        'Value': pm['Value']
                    })
                    total += pm['Value']

                if _['Status'] == 1:
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
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                elif _['Status'] == 3:
                    for __ in pms:
                        __.update({'Value': abs(__['Value'])})
                    send = {
                        'Code': _['Code'],
                        'Total': abs(total),
                        'TotalPayment': abs(_['TotalPayment']),
                        'PaymentMethods': pms,
                        'Discount': abs(_['Discount']),
                        'Status': 0,
                        'VAT': 0,
                        'ReturnDate': _['PaymentDate'],
                        'ReturnDetails': ods
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                    send = {
                        'Code': f'VAT_{_["Code"]}',
                        'Total': 0,
                        'TotalPayment': 0,
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}],
                        'Discount': 0,
                        'Status': 2,
                        'VAT': 0,
                        'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': _['Total']}],
                        'PurchaseDate': _['PaymentDate'],
                        'OrderDetails': []
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                else:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(_))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
