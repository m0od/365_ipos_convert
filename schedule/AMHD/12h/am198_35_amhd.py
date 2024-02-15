import glob
import os
import random
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname
import xlrd
from unidecode import unidecode


class AM198(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'wayne_amhd'
        self.ADAPTER_TOKEN = '2f55583b0ed7c1caf04a1c321ef4a62069791b8da5d257d28c846336e90871f8'
        self.FOLDER = '35_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        # self.EXT = f'*.xls'
        # self.METHOD = {
        #     'CASH': 'CASH',
        #     'MASTERCARD': 'THẺ',
        #     'VISA': 'THẺ',
        #     'LOCAL BANK': 'BANK'
        # }

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            _ = max(files, key=os.path.getmtime)
            idx = _.rindex('/')
            name = _[idx + 1:]
            idx = name.rindex('.')
            name = name[:idx]
            t = os.path.getmtime(_)
            t = datetime.fromtimestamp(t).strftime('%Y%m%d %H:%M:%S')
            os.rename(_, f'{self.FULL_PATH}/{name}_{t}.xls')
            return f'{self.FULL_PATH}/{name}_{t}.xls'
        except:
            return None

    def get_summary(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        DATA = self.scan_file('*Sum*.xls*')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'SUMMARY NOT FOUND')
            return
        sheet = xlrd.open_workbook(DATA)
        raw = list(sheet.sheets())[0]
        i = 0
        pur_date = None
        while i < raw.nrows:
            if 'FROM' in str(raw.row(i)[13].value).strip().upper():
                pur_date = raw.row(i)[13].value.strip().split('\n')[0].split(':')[1].strip()
                pur_date = datetime.strptime(pur_date, '%A, %B %d, %Y')
                # print(pur_date)
            if 'TOTAL DISCOUNTS' in str(raw.row(i)[2].value).upper():
                break
            i += 1
        # discount = raw.row(i)[6].value
        i += 2
        vat = raw.row(i)[6].value
        i += 2
        total = raw.row(i)[6].value
        while i < raw.nrows:
            i += 1
            if 'TOTAL PAYMENTS' in str(raw.row(i)[2].value).upper():
                break
        pms = []
        while i < raw.nrows:
            i += 1
            name = raw.row(i)[2].value
            if not name: continue
            if 'TENDER BALANCE' in str(raw.row(i)[2].value).upper():
                break
            pms.append({'Name': name.upper(), 'Value':raw.row(i)[3].value})
            # print(name.upper(), raw.row(i)[3].value)
        code = f'FINAL-{pur_date.strftime("%d%m%y")}'
        orders = {
            'Code': code,
            'Status': 2,
            'PurchaseDate': pur_date.strftime('%Y-%m-%d 23:00:00'),
            'Total': 0,
            'TotalPayment': total,
            'VAT': vat,
            'Discount': 0,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': pms
        }
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
        for _ in pms:
            pm = {
                'Code': f'{code}-{_["Name"]}',
                'OrderCode': code,
                'Amount': _['Value'],
                'TransDate': pur_date.strftime('%Y-%m-%d 23:00:00'),
                'AccountId': _['Name']
            }
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
        self.backup(DATA)
    def get_hour(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        DATA = self.scan_file('*Hour*.xls*')
        # print(DATA)
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'HOURS NOT FOUND')
            return
        sheet = xlrd.open_workbook(DATA)
        raw = list(sheet.sheets())[0]
        i = 0
        pur_date = None
        while i < raw.nrows:
            if 'CLOSING' in str(raw.row(i)[1].value).upper().strip():
                pur_date = raw.row(i)[15].value.strip().split('\n')[0].split(':')[1].strip()
                pur_date = datetime.strptime(pur_date, '%A, %B %d, %Y')
            if 'HOUR' == str(raw.row(i)[1].value).upper().strip():
                break
            i += 1
        while i < raw.nrows:
            i += 1
            if not raw.row(i)[1].value: break
            pur_hour = xlrd.xldate.xldate_as_datetime(raw.row(i)[1].value, sheet.datemode)
            total = raw.row(i)[3].value
            void = raw.row(i)[-1].value
            count = int(raw.row(i)[12].value)
            discount = raw.row(i)[-4].value
            code = f'HD-{pur_date.strftime("%d%m%y")}-{pur_hour.strftime("%H")}-{count}'
            trans_date = f'{pur_date.strftime("%Y-%m-%d")} {pur_hour.strftime("%H:%M:%S")}'
            orders = {
                'Code': code,
                'Status': 2,
                'PurchaseDate': trans_date,
                'Total': total - void,
                'TotalPayment': 0,
                'VAT': 0,
                'Discount': discount,
                'OrderDetails': [{'ProductId': 0}],
                'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
            }
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
            pm = {
                'Code': f'{code}-CASH',
                'OrderCode': code,
                'Amount': 0,
                'TransDate': trans_date,
                'AccountId': 'CASH'
            }
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
            for _ in range(1, count):
                code = f'HD-{pur_date.strftime("%d%m%y")}-{pur_hour.strftime("%H")}-{_}'
                # trans_date = f'{pur_date.strftime("%Y-%m-%d")} {pur_hour.strftime("%H:%M:%S")}'
                orders = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': trans_date,
                    'Total': 0,
                    'TotalPayment': 0,
                    'VAT': 0,
                    'Discount': discount,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
        self.backup(DATA)
    def get_data(self):
        self.get_hour()
        self.get_summary()

    def backup(self, DATA):
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        if os.path.exists(f'{self.FULL_PATH}/bak/{name}'):
            os.remove(f'{self.FULL_PATH}/bak/{name}')
        try:
            os.mkdir(f'{self.FULL_PATH}/bak')
        except:
            pass
        try:
            shutil.move(DATA, f'{self.FULL_PATH}/bak')
        except:
            pass
