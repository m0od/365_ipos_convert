import sys
from os.path import dirname
from datetime import datetime, timedelta
import requests


class AM113(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'megane_prince_amhd'
        self.ADAPTER_TOKEN = '1a1238d2deb8d67f44bf97432f2a6b98f3b46c4fab5b4938ba7782b430309023'
        self.URL = 'https://api-v2.masterpro.vn/api'
        self.USER = 'apiaeonhd'
        self.PASSWORD = 'MasterProBvymd7T5^6MPAEON'
        self.TENANT_CODE = 'meganeprince'
        self.browser = requests.session()
        self.browser.verify = False
        self.RETURN = []
        self.TOKEN = None
        self.ORDERS = []
        self.DATE = datetime.now() - timedelta(days=1)

    def login(self):
        from pos_api.adapter import submit_error
        try:
            js = {
                'tenantcode': self.TENANT_CODE,
                'username': self.USER,
                'password': self.PASSWORD
            }
            res = self.browser.post(f'{self.URL}/auth/login', json=js)
            if res.status_code != 200:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[LOGIN] {res.status_code}')
                return False
            js = res.json()
            if js['data'].get('tokenPhp') is None:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[LOGIN] Invalid Login')
                return False
            else:
                self.TOKEN = js['data']['tokenPhp']
                return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[LOGIN] {str(e)}')
            return False

        # print(self.FINGER_PRINT)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        if not self.login():
            return
        try:
            js = {
                'date': self.DATE.strftime('%Y-%m-%d'),
                'token': self.TOKEN
            }
            res = self.browser.post(f'{self.URL}/POSIntegration/ReportDaily_AEON', json=js)
            if res.status_code == 200:
                data = res.json()['data']
                for line in data.strip().split('\n'):
                    raw = line.split('|')
                    pur_date = datetime.strptime(f'{raw[2]}{raw[3]}', '%d%m%Y%H')
                    total = float(raw[5])
                    discount = float(raw[7])
                    cash = float(raw[10])
                    payoo = float(raw[11])
                    payoo += float(raw[12])
                    payoo += float(raw[13])
                    payoo += float(raw[14])
                    voucher = float(raw[15])
                    e_wallet = float(raw[16])
                    if total != 0 or cash != 0 or payoo != 0 and e_wallet != 0:
                        pms = []
                        if cash != 0:
                            pms.append({'Name': 'CASH', 'Value': cash})
                        if payoo != 0:
                            pms.append({'Name': 'PAYOO', 'Value': payoo})
                        if voucher != 0:
                            pms.append({'Name': 'VOUCHER', 'Value': voucher})
                        if e_wallet != 0:
                            pms.append({'Name': 'E-WALLET', 'Value': e_wallet})
                        self.ORDERS.append({
                            'Code': f'{pur_date.strftime("%Y%m%d_%H")}',
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'Total': int(total),
                            'TotalPayment': int(total),
                            'VAT': 0,
                            'Discount': int(discount),
                            'OrderDetails': [],
                            'PaymentMethods': pms
                        })
            else:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[FETCH DATA] api status {res.status_code}')
                return False
            for _ in self.ORDERS:
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
            for _ in self.ORDERS:
                for __ in _['PaymentMethods']:
                    if __['Value'] < 0:
                        submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data={
                            'Code': f"{_['Code']}-{__['Name'].upper()}",
                            'OrderCode': _['Code'],
                            'Amount': __['Value'],
                            'TransDate': _['PurchaseDate'],
                            'AccountId': __['Name'].upper()
                        })
                return True

        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[FETCH DATA] {str(e)}')
            return False
