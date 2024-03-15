from os.path import dirname
import sys
import warnings
import requests
import json
from datetime import datetime, timedelta


class AM125(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'suonmuoi_amhd'
        self.ADAPTER_TOKEN = '9c4c333c74678964b66ff96eb9c8d72b32f18958a681c64d90fd7bcbd43edb01'
        self.API = 'https://suonmuoi.cukcuk.vn'
        self.DATE = datetime.now() - timedelta(days=1)
        self.BRANCH_ID = "a506c769-adf6-4d5b-a135-237852dadf6e"
        self.orders = {}
        self.browser = requests.session()

    def login(self):
        from pos_api.adapter import submit_error
        try:
            r = self.browser.get(f'{self.API}/Login')
            from bs4 import BeautifulSoup
            html = BeautifulSoup(r.text, 'html.parser')
            event = html.find('input', {'id': '__EVENTVALIDATION'}).get('value')
            state_gen = html.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
            state = html.find('input', {'id': '__VIEWSTATE'}).get('value')
            data = {
                '__EVENTVALIDATION': event,
                '__VIEWSTATEGENERATOR': state_gen,
                '__VIEWSTATE': state,
                'ctl00$cphMain$LoginUser$UserName': 'trungn@aeonmall-vn.com',
                'ctl00$cphMain$LoginUser$Password': 'Aeon1234',
                # 'ctl00$cphMain$LoginUser$txtCodeCapCha': '',
                'ctl00$cphMain$LoginUser$LoginButton': 'Đăng nhập',
                # 'ctl00$cphMain$drvLanguage': 'vi-VN'
            }

            r = self.browser.post(f'{self.API}/Login', data=data)
            if f'{self.API}/' == r.url:
                return True
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, reason=str(e))
        return False
    def get_orders(self):
        from pos_api.adapter import submit_order, submit_error
        start = 0
        while True:
            try:
                js = {
                    'obj': json.dumps({
                        "BranchID": self.BRANCH_ID,
                        "ByDay": self.DATE.strftime("%Y-%m-%dT00:00:00.0000+07:00")
                    }),
                    "reportID": "RV_BYTIME_DETAIL",
                    "isDetail": True,
                    "hasSummary": False,
                    "hasMaster": False,
                    "start": start,
                    "limit": 100
                }
                r = self.browser.post(f'{self.API}/Service/ReportService.svc/GetReportData', json=js)
                if len(r.json()['data']) == 0:
                    break
                for _ in r.json()['data']:
                    if _['PaymentStatus'] == 4:continue
                    code = _['RefNo']
                    pur_date = datetime.strptime(_['RefDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    pur_date = pur_date + timedelta(hours=7)
                    vat = _['VATAmount']
                    discount = _['DiscountAmount']
                    total = _['TotalAmount']
                    pms = [
                        {'Name': 'CASH', 'Value': _['CashAmount']},
                        {'Name': 'PAYOO', 'Value': _['CardAmount']},
                        {'Name': 'VOUCHER', 'Value': _['VoucherAmount']},
                    ]
                    for pm in pms.copy():
                        if pm['Value'] == 0:
                            pms.remove(pm)
                    # print(pms)
                    # print(_['CashAmount'],_['CardAmount'],_['VoucherAmount'],_['UsedPointAmount'])
                    # print(_['RevenueAmount'], _['BankAccountNumber'], _['ListCardName'])
                    # print(_)
                    ods = self.get_detail(_['RefID'])
                    order = {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': ods,
                        'PaymentMethods': pms
                    }
                    # print(code)
                    submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                    # break
                start += 100
            except Exception as e:
                submit_error(self.ADAPTER_RETAILER, reason=str(e))

    def get_detail(self, refId):
        js = {
            'obj': json.dumps({
                'RefID': refId
            }),
            "reportID": 'RV_LISTSAINVOICE_DETAIL',
            "isDetail": True,
            "hasSummary": False,
            "hasMaster": True,
            "start": 0,
            "limit": 100
        }
        r = self.browser.post(f'{self.API}/Service/ReportService.svc/GetReportData', json=js)
        ods = []
        for _ in r.json()['data']:
            # print(_)
            ods.append({
                'Code': _['ItemID'],
                'Name': _['ItemName'].strip(),
                'Price': int(_['Quantity']),
                'Quantity': float(_['UnitPrice'])
            })
        return ods

    def get_data(self):
        if not self.login():
            return
        self.get_orders()
