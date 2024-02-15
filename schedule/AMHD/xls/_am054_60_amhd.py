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


class AM054(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'pepper_lunch_amhd'
        self.ADAPTER_TOKEN = '621f2cfd4f710402c089dbae222390c0d7dfda088857d74f3db8c0676218fd60'
        self.FOLDER = '60_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')

    def scan_file(self,EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
            # idx = _.rindex('/')
            # name = _[idx + 1:]
            # idx = name.rindex('.')
            # name = name[:idx]
            # t = os.path.getmtime(_)
            # t = datetime.fromtimestamp(t).strftime('%Y%m%d %H:%M:%S')
            # os.rename(_, f'{self.FULL_PATH}/{name}_{t}.xls')
            # return f'{self.FULL_PATH}/{name}_{t}.xls'
        except:
            return None

    def get_time_data(self):
        from pos_api.adapter import submit_order, submit_error, submit_payment
        DATA = self.scan_file('t*.xls')
        print(DATA)
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'TIME_NOT_FOUND')
            return
        sheet = xlrd.open_workbook(DATA)
        raw = list(sheet.sheets())[0]
        nRows = raw.nrows
        sales = 0
        get = False
        date = None
        hour = None
        for i in range(1, nRows):
            data = raw.row(i)[0].value
            # print(data)
            if 'Business Date' in data:
                date = data.strip().split('From')[1].split('to')[0].strip()
                date = datetime.strptime(date, '%A, %B %d, %Y')
            elif '-' in data:
                get = True
                hour = data.strip().split('-')[1]
                hour = datetime.strptime(hour, '%H:%M')
            elif 'Net Sales' in data and get:
                sales = float(data.strip().split()[-1].replace(',', ''))
            elif 'Avg Chk' in data and get:
                count = int(data.strip().split()[2].replace(',', ''))
                # print(x)
                get = False
                d = date.strftime("%Y%m%d")
                code = f'TIME_{d}{hour.strftime("%H")}'
                d = date.strftime("%Y-%m-%d")
                h = hour.strftime("%H:00:00")
                order = {
                    'Code': f'{code}_{count}',
                    'Status': 2,
                    'PurchaseDate': f'{d} {h}',
                    'Discount': 0,
                    'Total': sales,
                    'TotalPayment': 0,
                    'VAT': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                }
                pm = {
                    'Code': f'{code}_{count}-CASH',
                    "OrderCode": f'{code}_{count}',
                    "Amount": 0,
                    "TransDate": f'{d} {h}',
                    "AccountId": 'CASH'
                }
                # print(order)
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
                for i in range(1, count):
                    order = {
                        'Code': f'{code}_{i}',
                        'Status': 2,
                        'PurchaseDate': f'{d} {h}',
                        'Discount': 0,
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'OrderDetails': [],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    }
                    submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        self.backup(DATA)
    def get_sys_data(self):
        from pos_api.adapter import submit_order, submit_error, submit_payment
        DATA = self.scan_file('*.xls')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'TIME_NOT_FOUND')
            return
        sheet = xlrd.open_workbook(DATA)
        raw = list(sheet.sheets())[0]
        nRows = raw.nrows
        vat = 0
        total = 0
        discount = 0
        keyword = [
            'BUSINESS DATE', 'VAT', 'TOTAL DISCOUNTS'
        ]
        pm = {}
        i = 0
        date = None
        while i < nRows:
            # for row in range(0, nRows):
            data = str(raw.row(i)[0].value).upper().strip()
            # print(data)
            for k in keyword:
                if data.startswith(k):
                    data = data.replace(k, '')
                    if k == 'BUSINESS DATE':
                        data = str(raw.row(i)[0].value)
                        date = data.strip().split('From')[1].split('to')[0].strip()
                        date = datetime.strptime(date, '%A, %B %d, %Y')
                        print(date)
                    elif k == 'TOTAL DISCOUNTS':
                        # print('***',data)
                        discount += abs(float(data.strip().split()[1].replace(',', '')))
                        print(discount, 'discount')
                        i = nRows
                    elif k == 'VAT':
                        vat += float(data.strip().split()[1].replace(',', ''))
                        print(vat)
            i += 1
        i = 0
        keyword = [
            'CASH', 'MASTER', 'VISA', 'ATM', 'JCB', 'UNION PAY',
            'MALL VOUCHER', 'GRAB', 'VNPAY', 'SODEXO', 'NOW', 'GOVIET',
            'BAEMIN', 'MOMO', 'SHOPEE', 'UTOP', 'URBOX', 'ZALO',
            'TTL COLLECTED'
        ]
        pm = {}
        while i < nRows:
            data = str(raw.row(i)[0].value).upper().strip()
            if len(data):
                for k in keyword:
                    if k in data:
                        # print(data)
                        # print(k, data.split(k)[1].split()[-1])
                        value = 0
                        if k == 'TTL COLLECTED':
                            i = nRows
                            continue
                        if k == 'CASH' and not data.startswith(k):
                            value = float(data.split(k)[1].split()[-1].replace(',', ''))
                        else:
                            value = float(data.split(k)[1].split()[-1].replace(',', ''))
                        if value:
                            if not pm.get(k):
                                pm.update({k: value})
                            else:
                                pm.update({k: pm.get(k) + value})
            i+=1
        pms = []
        for k,v in pm.items():
            pms.append({'Name':k, 'Value': v})
        order = {
            'Code': f'FINAL_{date.strftime("%Y%m%d")}',
            'Status': 2,
            'PurchaseDate': f'{date.strftime("%Y-%m-%d 07:00:00")}',
            'Discount': discount,
            'Total': vat,
            'TotalPayment': 0,
            'VAT': vat,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': pms
        }
        # print(order)
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        self.backup(DATA)
    def get_data(self):
        self.get_time_data()
        self.get_sys_data()

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
