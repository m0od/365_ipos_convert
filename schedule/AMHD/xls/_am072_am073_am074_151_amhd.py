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


class AM072(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.DQ_RETAILER = 'dairy_queen_amhd'
        self.DQ_TOKEN = '5b5a30047e4c3a205b2c3b6627113e5a15ab9a76ca8a375dac24aa3b47bc04b5'
        self.SW_RETAILER = 'swensen_amhd'
        self.SW_TOKEN = '6b70abd47cffc64322010330f99e592e9118530a696fa1b8c1cd6dd73dfbe0ae'
        self.TPC_RETAILER = 'the_pizza_company_amhd'
        self.TPC_TOKEN = '7be7b5e5bc7206fe27b907ec8bf1723e07fc9d19c0fac10c80064e5c773e111e'

        self.FOLDER = '151_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xls*'
        self.METHOD = {
            'TIEN MAT': 'CASH',
            'VN PAY': 'VNPAY-QR',
            'NGAN HANG': 'CARD',
            'GOT IT HN': 'GOT IT'
        }

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return files
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
            submit_error(self.FOLDER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(unidecode(str(_.value).upper()))
            orders = []
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    code = rec.get('TRANSACTION CODE').value
                    code = int(code)
                    code = str(code)
                except:
                    continue
                try:
                    pur_date = rec.get('TRANSACTION TIME').value
                    pur_date = datetime.strptime(pur_date, '%m/%d/%Y %I:%M:%S %p')
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
                total = get_value(rec.get('TRANSACTION AMOUNT').value)
                discount = abs(get_value(rec.get('DISCOUNT').value))
                vat = get_value(rec.get('TRANSACTION TAX').value)
                try:
                    pm = rec.get('PAYMENT METHOD').value
                    pm = pm.upper().replace('VND', '').strip()
                    if len(pm):
                        pms = [{'Name': pm, 'Value': total}]
                    else:
                        pms = [{'Name': 'CASH', 'Value': 0}]
                except:
                    pms = [{'Name': 'CASH', 'Value': 0}]
                order = {
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
                branch = rec.get('RESTAURANT').value
                if branch == 'DQ_050_AHD_HAN':
                    submit_order(self.DQ_RETAILER, self.DQ_TOKEN, order)
                elif branch == 'SW_021_AHD_HAN':
                    submit_order(self.SW_RETAILER, self.SW_TOKEN, order)
                elif branch == 'TPC_074_AHD_HAN':
                    submit_order(self.TPC_RETAILER, self.TPC_TOKEN, order)
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