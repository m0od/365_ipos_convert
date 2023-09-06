import glob
import os
from datetime import datetime, timedelta
from os.path import dirname

import openpyxl



class NKID_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'nkid_amhd'
        self.ADAPTER_TOKEN = '206839f30026f5c2865a6bac5e3546d228cc9cd8e1f92a318afdfc4109422cf1'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'nkid_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '*txt'
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
        self.DATA = max(files, key=  os.path.getmtime)

        print(self.DATA)


    def get_data(self):
        self.scan_file()
        f = open(self.DATA, 'r')
        lines = f.read().strip().split('\n')
        f.close()
        for line in lines:
            _ = line.split('\t')
            print(_)
            code = _[0].strip()
            # if code != 'CA_230829_10000002623349': continue
            pur_date = _[1].strip()
            pur_date = datetime.strptime(pur_date, '%H%M%d%m%Y')
            # now = datetime.now() - timedelta(days=1)
            # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(pur_date)
            total = float(_[2].strip())
            vat = round(float(_[3].strip()),0)
            cash = float(_[5].strip())
            payoo = float(_[6].strip())
            vnpay = float(_[7].strip())
            momo = float(_[8].strip())
            bank = float(_[9].strip())
            other = float(_[10].strip())
            pms = []
            if cash != 0:
                pms.append({'Name': 'CASH', 'Value': cash})
            if payoo != 0:
                pms.append({'Name': 'PAYOO', 'Value': payoo})
            if vnpay != 0:
                pms.append({'Name': 'VNPAY', 'Value': vnpay})
            if momo != 0:
                pms.append({'Name': 'MOMO', 'Value': momo})
            if bank != 0:
                pms.append({'Name': 'BANK', 'Value': bank})
            if other != 0:
                pms.append({'Name': 'OTHER', 'Value': other})
            print(pur_date, vat)
            self.ORDERS.update({_[0].strip(): {
                'Code': _[0].strip(),
                'Status': 2,
                'PurchaseDate': pur_date,
                'Total': total,
                'TotalPayment': total,
                'VAT': vat,
                'Discount': 0,
                'PaymentMethods': pms,
                'OrderDetails': []
            }})
        for k, v in self.ORDERS.items():
            print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        for k, v in self.ORDERS.items():
            for _ in v['PaymentMethods']:
                if _['Value'] < 0:
                    submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data={
                        "OrderCode": v['Code'],
                        "Amount": _['Value'],
                        "TransDate": v['PurchaseDate'],
                        "AccountId": _['Name'].upper()
                    })
            # submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
if __name__:
    import sys

    # PATH = dirname(dirname(__file__))
    PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order, submit_payment

    NKID_AMHD().get_data()