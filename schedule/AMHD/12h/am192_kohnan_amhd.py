import codecs
import csv
import glob
import io
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from os.path import dirname
import pandas


class AM192(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'kohnan_amhd'
        self.ADAPTER_TOKEN = '603ce6e4fccb106c90b1f50ddf527d1c270a610eddb755269807b8f003480cf3'
        self.FOLDER = 'kohnan_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.ORDERS = {}
        self.TRANS = []
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.browser = None
        self.VAT = 0

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
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
        from pos_api.adapter import submit_order, submit_payment, submit_error
        VAT = self.scan_file(f'T{self.DATE}.csv')
        if not VAT:
            submit_error(self.ADAPTER_RETAILER, 'SUMMARY_NOT_FOUND')
            return
        f = codecs.open(VAT, 'r', encoding='utf-8', errors='ignore')
        raw = list(csv.reader(f, delimiter=','))
        try:
            self.VAT = float(raw[1][8].strip())
            self.backup(VAT)
        except:
            return
        DATA = self.scan_file(f'{self.DATE}.csv')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'DETAIL_NOT_FOUND')
            return
        f = codecs.open(DATA, 'r', encoding='utf-8', errors='ignore')
        x = str(f.read())
        x = io.StringIO(x)
        raw = pandas.read_csv(x, delimiter=',').values
        row = 0
        while row < len(raw):
            try:
                code = str(int(raw[row][4]))
                pur_date = raw[row][0].replace('/', '').replace('-', '').replace(':', '')
                if len(pur_date.split()[0]) == 6:
                    form = '%d%m%y %H%M'
                    pur_date = datetime.strptime(pur_date, form)
                    code = f"{pur_date.strftime('%Y%m%d%H%M')}_{time.perf_counter_ns()}"
                else:
                    form = '%d%m%Y %H%M'
                    pur_date = datetime.strptime(pur_date, form)
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(raw[row][7])
                if self.VAT > total:
                    vat = total
                    self.VAT -= total
                elif self.VAT > 0:
                    vat = self.VAT
                    self.VAT = 0
                else:
                    vat = 0
                discount = float(raw[row][8])
                cash = float(raw[row][13])
                credit = float(raw[row][14])
                receivable = float(raw[row][15])
                pms = []
                if cash > 0:
                    pms.append({
                        'Name': 'CASH', 'Value': cash
                    })
                if credit > 0:
                    pms.append({
                        'Name': 'CREDIT', 'Value': credit
                    })
                if receivable > 0:
                    pms.append({
                        'Name': 'RECEIVABLE', 'Value': receivable
                    })
                orders = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': pms
                }
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=orders)

                if not len(pms):
                    data = {
                        "Code": f"{code}-CASH",
                        "OrderCode": code,
                        "Amount": total,
                        "TransDate": pur_date,
                        "AccountId": 'CASH'
                    }
                    submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)

            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            row += 1
        self.backup(DATA)
