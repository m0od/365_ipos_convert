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


class AM078(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'lining_amhd'
        self.ADAPTER_TOKEN = 'a1e414e57c089238e2ffe3ddf1dff056a79734514be222ae86b8953be6ed7dd3'
        self.FOLDER = '100_amhd'
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
                # print(value, type(value))
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
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(str(_.value).upper())
            # print(headers)
            current = None
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    code = rec.get('SỐ CHỨNG TỪ').value.strip()
                    if not len(code):
                        continue
                except:
                    continue
                try:
                    pur_date = rec.get('NGAY').value
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M:%S')
                    code = f'{pur_date.strftime("%Y%m%d")}_{code}'
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
                # print(pur_date, code, type(code))
                total = get_value(rec.get('THÀNH TIỀN CK').value)
                # print(code, total)
                discount = get_value(rec.get('GIẢM GIÁ CHI TIẾT').value)
                discount += get_value(rec.get('GIẢM GIÁ PHÂN BỔ').value)
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
                    orders[code]['PaymentMethods']= [{'Name': 'CASH', 'Value': orders[code]['Total']}]

            # print(self.ORDERS)
            for _, order in orders.items():
                # print(order)
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
