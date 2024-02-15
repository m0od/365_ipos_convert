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


class AM029(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'coffee_house_amhd'
        self.ADAPTER_TOKEN = 'e2c972c2f91ff8fafa640a8c103468d51c8b0230adc12f77f91bfe7f86d505d0'
        self.FOLDER = '62_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xls'

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return files
            # _ = max(files, key=os.path.getmtime)
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

    def get_data(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'SUMMARY NOT FOUND')
            return
        for DATA in files:
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            i = 0
            pur_date = None
            for i in range(6, raw.nrows):
                # print(raw.row(i))
                code = raw.row(i)[2].value
                if not code: continue
                code = code.strip()
                if not len(code): continue
                pur_date = f'{raw.row(i)[1].value} {raw.row(i)[7].value}'
                try:
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M')
                except:
                    continue
                # print(pur_date)
                total = raw.row(i)[8].value
                # print(total, type(total))
                pms = [
                    {'Name': 'CASH', 'Value': raw.row(i)[9].value},
                    {'Name': 'VISA', 'Value': raw.row(i)[11].value},
                    {'Name': 'VOUCHER', 'Value': raw.row(i)[12].value},
                    {'Name': 'ONLINE', 'Value': raw.row(i)[13].value},
                    {'Name': 'AIRPAY', 'Value': raw.row(i)[14].value},
                    {'Name': 'MOMO', 'Value': raw.row(i)[17].value},
                    {'Name': 'PLATFORM', 'Value': raw.row(i)[18].value},
                ]
                # print(pms)
                for _ in pms.copy():
                    if _['Value'] == 0:
                        pms.remove(_)
                if len(pms) == 0:
                    pms = [{'Name': 'CASH', 'Value': 0}]
                orders = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': pms
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
                for _ in pms:
                    if _['Value'] <= 0:
                        pm = {
                            'Code': f'{code}-{_["Name"]}',
                            'OrderCode': code,
                            'Amount': _["Value"],
                            'TransDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'AccountId': _['Name']
                        }
                        submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
            self.backup(DATA)
            # break
        # self.get_hour()
        # self.get_summary()

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
