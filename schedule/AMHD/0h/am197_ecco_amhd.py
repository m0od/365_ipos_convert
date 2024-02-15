import glob
import os
import random
import shutil
import sys
import xlrd
from datetime import datetime, timedelta
from os.path import dirname


class AM197(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'ecco_amhd'
        self.ADAPTER_TOKEN = '021e1a5a0a00ae143f4794337d9a2cf0473f72e39af6b6616e70ff0ae7d14090'
        self.FOLDER = 'ecco_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*.XLSX'

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

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

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            ws = xlrd.open_workbook(DATA)
            raw = list(ws.sheets())[0]
            orders = []
            headers = []
            for _ in raw.row(0):
                headers.append(str(_.value).strip().upper())
            # print(headers)
            for i in range(1, raw.nrows):
                # print(raw.row(i))
                rec = dict(zip(headers, raw.row(i)))
                try:
                    pur_date = xlrd.xldate_as_datetime(rec["DATE"].value, ws.datemode)
                    t = xlrd.xldate_as_datetime(rec["TIME"].value, ws.datemode)
                    pur_date = pur_date.replace(hour=t.hour, minute=t.minute, second=t.second)
                except:
                    continue
                # print(str(rec["DATE"].value))
                # print(str(rec["TIME"].value))
                # pur_date = f'{str(rec["DATE"].value)[:-8].strip()} {rec["TIME"].value}'
                # try:
                #     print(pur_date)
                #     pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # except:
                #     continue
                # print(pur_date)
                code = str(int(rec["BILL_NO"].value)).strip()
                total = get_value(rec["TOTAL"].value)
                pm = str(rec["TENDER"].value).strip()
                # print(sheet[row][2].value)
                # total = sheet[row][2].value
                # print(sheet[row][3].value)
                # code = f'HD-{pur_date.strftime("%d%m%y")}-{len(orders) + 1:05d}'
                orders.append({
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{'Name': pm, 'Value': total}]
                })
                # print(orders[-1])
            for order in orders:
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            self.backup(DATA)
