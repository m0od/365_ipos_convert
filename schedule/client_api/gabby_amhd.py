from os.path import dirname
import requests
import hashlib
import string
import random
from datetime import datetime, timedelta


def random_str():
    return ''.join(random.choice(string.ascii_letters) for i in range(8)).encode('utf-8')


class Gabby(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'gabby_amhd'
        self.ADAPTER_TOKEN = '949bc15d0545793090028a4ea255f30075ed52798df455e6c3e09200dd10fff5'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.API_MANS = [ 'api-man.kiotviet.vn', 'api-man1.kiotviet.vn', 'api-man.kiotviet.vn']
        self.API_MAN = None
        self.DOMAIN = 'gabby'
        self.BRANCH_ID = None
        self.USER = 'admaeonhd'
        self.PASSWORD = 'Aeon12345'
        self.FINGER = f'{hashlib.md5(random_str()).hexdigest()}_Firefox_Desktop_Windows'
        self.browser = requests.session()
        self.RETURN = []
        self.METHOD = {
            'CARD': 'THẺ',
            'TRANSFER': 'PAYOO',
            'CASH': 'CASH',
            'VOUCHER': 'VOUCHER'
        }
        self.TOKEN = None

    def login(self):
        try:
            js = {
                'IsManageSide': True,
                'FingerPrintKey': self.FINGER,
                'model': {
                    'RememberMe': True,
                    'ShowCaptcha': False,
                    'UserName': self.USER,
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
                # self.API_MAN = _
                res = res.json()
                # print(res)
                if res['isSuccess']:
                    self.TOKEN = res['token']
                    self.BRANCH_ID = str(res['currentBranch'])
                    return True
                else:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[LOGIN] Invalid Login')
                    return False
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[LOGIN] {str(e)}')
            return False

    def get_data(self, d_from, d_to):
        if not self.login(): return
        skip = 0
        while True:
            params = {
                'format': 'json',
                '$top': '100',
                '$orderby': 'PurchaseDate',
                '$filter': f"(SaleChannelId eq null and (PurchaseDate ge datetime'{d_from.strftime('%Y-%m-%dT00:00:00')}'"
                           f" and PurchaseDate lt datetime'{d_to.strftime('%Y-%m-%dT00:00:00')}') and (Status eq 3 or Status eq 1))",
                '$skip': str(skip)
            }
            self.browser.headers.update({
                'authorization': f'Bearer {self.TOKEN}',
                'branchId': self.BRANCH_ID,
                'retailer': self.DOMAIN
            })
            if self.API_MAN is None:
            # print(self.TOKEN, self.BRANCH_ID, self.DOMAIN)
                for _ in self.API_MANS:
                    try:
                        res = self.browser.post(f'https://{_}/api/invoices/list', params=params)
                        print(res.text)
                        res = res.json()
                        self.API_MAN = _
                        break
                    except:
                        pass
            else:
                res = self.browser.post(f'https://{self.API_MAN}/api/invoices/list', params=params)
                print(res.text)
                res = res.json()
            if len(res['Data']) == 0: break
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
                    # print('--->', ret_send)
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=ret_send)
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
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                index += 1
            skip += 100
        self.get_return_data(d_from, d_to)

    def get_return_data(self, d_from, d_to):
        # if not self.login(): return
        skip = 0
        while True:
            params = {
                'format': 'json',
                '$top': '100',
                '$orderby': 'ReturnDate',
                '$filter': f"(SaleChannelId eq null and ReturnDate ge datetime'{d_from.strftime('%Y-%m-%dT00:00:00')}'"
                           f" and ReturnDate lt datetime'{d_to.strftime('%Y-%m-%dT00:00:00')}' and Status eq 1)",
                'skip': str(skip)
            }
            self.browser.headers.update({
                'authorization': f'Bearer {self.TOKEN}',
                'branchId': self.BRANCH_ID
            })
            res = self.browser.get(f'https://{self.API_MAN}/api/returns', params=params).json()
            print(res)
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
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
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
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                index += 1
            skip += 100


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    # now = datetime.now()
    # Gabby().get_data(now - timedelta(days=1), now)
