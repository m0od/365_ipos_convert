import glob
import os
import random
import shutil
import sys
import time
# import time
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname
import xlrd
from unidecode import unidecode


class AM075(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'adidas_original_amhd'
        self.ADAPTER_TOKEN = 'c1d775cbbdb75746fce03fd0d8d7d0975777986910f00f095fb93fdde1c8d16b'
        self.FOLDER = '40_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xlsx'
        self.ORDERS = None

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            orders = {}
            idx = DATA.rindex('/')
            name = DATA[idx + 1:]
            idx = name.rindex('.')
            name = name[:idx].split('-')[1]
            d = datetime.strptime(name, '%d.%m.%Y')
            d = d.strftime('%Y-%m-%d')
            # self.ORDERS = {}
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            # current = None
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    t = rec.get('THOI GIAN GIAO DICH').value
                    t = datetime.strptime(t, '%H:%M:%S')
                    t = t.strftime('%H:%M:%S')
                except:
                    continue
                pur_date = f'{d} {t}'
                # print(pur_date)
                try:
                    code = rec.get('MA HOA DON').value.strip()
                    if not len(code):
                        continue
                except:
                    continue
                code = f'{d}_{code}'
                #     # print(pur_date, code, type(code))
                total = get_value(rec.get('SO TIEN GIAO DICH').value)
                orig = get_value(rec.get('GIA GOC').value)
                discount = orig - total
                if orders.get(code) is None:
                    orders.update({
                        code: {
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pur_date,
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': [{'ProductId': 0}],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': total}]
                        }
                    })
                else:
                    orders[code]['Total'] += total
                    orders[code]['TotalPayment'] += total
                    orders[code]['Discount'] += discount
                    orders[code]['PaymentMethods'] = [{
                        'Name': 'CASH',
                        'Value': orders[code]['Total']
                    }]
            for k, order in orders.items():
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                for _ in order['PaymentMethods']:
                    if _['Value'] <= 0:
                        pm = {
                            'Code': f'{order["Code"]}-{_["Name"]}',
                            'OrderCode': order["Code"],
                            'Amount': _["Value"],
                            'TransDate': order["PurchaseDate"],
                            'AccountId': _['Name']
                        }
                        submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)

            self.backup(DATA)

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
