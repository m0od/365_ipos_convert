from os.path import dirname
import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


class SneakerBuzz(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'sneaker_buzz_aeonhd'
        self.ADAPTER_TOKEN = '5850c0e17891292129239c07c5cc97b14fa88573c9523d933bda682395d5e6fa'
        # self.ADAPTER_RETAILER = 'retry'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.API = 'https://sneakerbuzzpremium.mshopkeeper.vn'
        self.DOMAIN = 'sneakerbuzzpremium'
        self.USER = '0979830232'
        self.PASSWORD = '123456a@A'

        # self.DOMAIN = 'testipos'
        # self.API = 'https://testipos.mshopkeeper.vn'
        # self.USER = 'sieunhan@tuumalo.com'
        # self.PASSWORD = 'Kevin!@#$123'

        self.TOKEN = None
        self.BRANCH_ID = None
        self.browser = requests.session()
        self.TOKEN = None
        self.PAYMENT = None

    def login(self):
        try:
            data = {
                'LanguageLogin': 'vi-VN',
                'UserName': self.USER,
                'Password': self.PASSWORD
            }
            self.browser.headers.update({'content-type': 'application/x-www-form-urlencoded'})
            self.browser.post(f'{self.API}/Login', data=data)
            res = self.browser.get(f"{self.API}/main?isLogged=true&language=vi-VN")
            if f'{self.DOMAIN}_Token' not in self.browser.cookies.keys():
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f"[LOGIN] Login Fail")
                return False
            js = json.loads(res.text.split('saveInfoUser(')[1].split('},')[0] + '}')
            self.TOKEN = f"Bearer {js['access_token']}"
            self.BRANCH_ID = json.loads(js['branch'])[0]['BranchID']
            self.browser.headers.update({
                'authorization': self.TOKEN,
                'companycode': self.DOMAIN,
                'x-misa-branchid': self.BRANCH_ID
            })
            return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f"[LOGIN] {str(e)}")
            return False

    def get_data(self, d_from):
        if not self.login(): return False
        self.get_payment_config()
        start = 0
        page = 1
        while True:
            try:
                data = {
                    'reportID': 'RP_ListInvoice',
                    'objParams': json.dumps({
                        "FromDate": d_from.strftime('%Y-%m-%d 00:00:00'),
                        "ToDate": d_from.strftime('%Y-%m-%d 23:59:59'),
                        "BranchID": self.BRANCH_ID
                    }),
                    'page': str(page),
                    'start': str(start),
                    'limit': '100',
                    'filter': json.dumps([{
                        "xtype": "filter",
                        "property": "PaymentStatus",
                        "operator": 0, "value": 8,

                        "type": 7}])
                }
                res = self.browser.post(f"{self.API}/backendg2/api/ReportList/GetReport", data=data).json()
                if len(res['Data']) == 0: break
                for index in range(len(res['Data'])):
                    od = res['Data'][index]
                    vat = int(od['TaxAmount'])
                    if vat > 0:
                        discount = int(round(od['DiscountAmount'] / 10 * 11, 0))
                    else:
                        discount = int(od['DiscountAmount'])
                    pur_date = datetime.strptime(od['FormatRefDate'], '%d/%m/%Y %H:%M')
                    detail = self.get_detail(od['RefID'])
                    pm = []
                    for name in self.PAYMENT:
                        value = int(od[f'{name}_CardName'])
                        if value != 0:
                            map = name.upper()
                            if map == 'VN PAY': map = 'VNPAY'
                            pm.append({'Name': map, 'Value': value})
                    cash = int(od['CashAmount'])
                    if cash != 0:
                        pm.append({'Name': 'CASH', 'Value': cash})
                    voucher = int(od['VoucherAmount'])
                    if voucher != 0:
                        pm.append({'Name': 'VOUCHER', 'Value': voucher})
                    total = int(od['ActualAmountCustom']) + voucher
                    send = {
                        'Code': od['RefNo'],
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': detail,
                        'PaymentMethods': pm
                    }
                    print(send)
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                start += 100
                page += 1
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Order] {str(e)}')

    def get_detail(self, ref_id):
        try:
            detail = []
            params = {
                'refId': ref_id
            }
            res = self.browser.get(f"{self.API}/backendg2/api/SAInvoices/ReportSAInvocieDetails", params=params).json()

            for i in res['Data'][0]['SAInvocieDetails']:
                # print(i['InventoryItemName'])
                soup = BeautifulSoup(i['EncodeInventoryItemName'], 'html.parser')
                detail.append({
                    'Code': i['SKUCode'].strip(),
                    'Name': soup.text.strip(),
                    'Price': int(i['UnitPrice']),
                    'Quantity': int(i['Quantity'])
                })

            return detail
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Detail] {str(e)}')

    def get_payment_config(self):
        self.PAYMENT = []
        c = 0
        while True:
            try:
                URL = f"{self.API}/backendg{c % 2 + 1}/api/Card"
                res = self.browser.get(URL)
                for i in res.json()['Data']:
                    if not i['Inactive']:
                        self.PAYMENT.append(i['CardName'])
                break
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Payment] {str(e)}')
                c += 1
                pass


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    # SneakerBuzz().get_data(datetime.now() - timedelta(days=1))
