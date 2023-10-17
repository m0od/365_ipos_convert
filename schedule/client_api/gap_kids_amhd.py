import glob
import os
import shutil
from datetime import datetime, timedelta
from os.path import dirname

import csv


class GAP_KIDS_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'gap_kids_amhd'
        self.ADAPTER_TOKEN = '6427a5a755043f0ae7cb19deedf748d2504fb2109ef6fd309997f790c5adde19'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'acfc_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = 'AMHD-274*CSV'
        self.DATA = None
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT)
        # print(files)
        self.DATA = max(files, key=os.path.getmtime)

        print(self.DATA)

    def get_data(self):
        self.scan_file()
        csv_reader = csv.DictReader(open(self.DATA), delimiter=',')
        line_count = 0
        for row in csv_reader:
            try:
                pm = []
                code = row['NO_OF_PURCHASE'].strip()
                pur_date = row['DATE_'].strip()
                pur_date = datetime.strptime(pur_date, '%m/%d/%Y %I:%M:%S %p')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(row['TOTAL_SALES_AMOUNT'])
                vat = float(row['VAT_AMOUNT'])
                cash = row['CASH'].strip()
                if len(cash) != 0 and float(cash) != 0:
                    pm.append({
                        'Name': 'CASH', 'Value': float(cash)
                    })
                credit = row['CREDIT'].strip()
                if len(credit) != 0 and float(credit) != 0:
                    pm.append({
                        'Name': 'CREDIT', 'Value': float(credit)
                    })
                voucher = row['VOUCHER'].strip()
                if len(voucher) != 0 and float(voucher) != 0:
                    pm.append({
                        'Name': 'VOUCHER', 'Value': float(voucher)
                    })
                others = row['SALES_ON_OTHER_PM'].strip()
                if len(others) != 0 and float(others) != 0:
                    pm.append({
                        'Name': 'OTHERS', 'Value': float(others)
                    })
                if self.ORDERS.get(code) is None:
                    self.ORDERS.update({
                        code: {
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pur_date,
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': vat,
                            'Discount': 0,
                            'OrderDetails': [],
                            'PaymentMethods': pm
                        }
                    })
                else:
                    self.ORDERS[code].update({
                        'Total': self.ORDERS[code]['Total'] + total,
                        'TotalPayment': self.ORDERS[code]['TotalPayment'] + total,
                        'VAT': self.ORDERS[code]['VAT'] + vat,
                        'Discount': 0,
                    })
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        for k, v in self.ORDERS.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        try:
            shutil.move(self.DATA, f'{self.FULL_PATH}bak')
        except:
            pass


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    # GAP_KIDS_AMHD().get_data()
