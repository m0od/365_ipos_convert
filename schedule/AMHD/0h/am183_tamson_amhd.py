import glob
import os
import shutil
import sys
from datetime import datetime, timedelta, time
from os.path import dirname

import xlrd


class AM183(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'okaidi_obabi_amhd'
        self.ADAPTER_TOKEN = '105255415bbd849c85c9b390a3c87c9bfa745efc8c209cf859d491f9d22ee391'
        self.FOLDER = 'tamson_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        # self.DATE = self.DATE.strftime('%d.%m.%Y')
        self.EXT = f'*.xls'

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

        # print(self.DATA)

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0
        from pos_api.adapter import submit_order, submit_payment, submit_error
        # from drive import Google
        # self.rename_file()
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            ws = xlrd.open_workbook(DATA)
            raw = list(ws.sheets())[0]
            for i in range(8, raw.nrows):
                code = raw.row(i)[4].value
                if not code: continue
                if not len(code.strip()): continue
                try:
                    pur_date = (raw.row(i)[1].value - 25569) * 86400
                    pur_date = datetime.utcfromtimestamp(pur_date)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
                total = get_value(raw.row(i)[6].value)
                # print(total)
                vat = float(raw.row(i)[8].value)
                discount = float(raw.row(i)[9].value)
                cash = float(raw.row(i)[22].value)
                order = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{
                        'Name': 'CASH', 'Value': cash
                    }]
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                if cash == 0:
                    pm = {
                        'Code': f'{code}-CASH',
                        'OrderCode': code,
                        'Amount': cash,
                        'TransDate': pur_date,
                        'AccountId': 'CASH'
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
