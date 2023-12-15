import glob
import os
import shutil
import sys
from datetime import datetime
from os.path import dirname
import csv


class AM153(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'banana_republic_amhd'
        self.ADAPTER_TOKEN = '7310bcdf756ba1722488329a1ba248cf4acebd154edc9899c514848486a62944'
        self.FOLDER = 'acfc_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.EXT = 'AMHD-025*CSV'
        self.ORDERS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        csv_reader = csv.DictReader(open(DATA), delimiter=',')
        line_count = 0
        for row in csv_reader:
            try:
                code = row['NO_OF_PURCHASE'].strip()
                pur_date = row['DATE_'].strip()
                pur_date = datetime.strptime(pur_date, '%m/%d/%Y %I:%M:%S %p')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(row['TOTAL_SALES_AMOUNT'])
                vat = float(row['VAT_AMOUNT'])
                try:
                    cash = float(row['CASH'].strip())
                except:
                    cash = 0
                try:
                    credit = float(row['CREDIT'].strip())
                except:
                    credit = 0
                try:
                    voucher = float(row['VOUCHER'].strip())
                except:
                    voucher = 0
                try:
                    others = float(row['SALES_ON_OTHER_PM'].strip())
                except:
                    others = 0
                pm = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CREDIT', 'Value': credit},
                    {'Name': 'VOUCHER', 'Value': voucher},
                    {'Name': 'OTHERS', 'Value': others}
                ]
                for _ in pm.copy():
                    if not _['Value']: pm.remove(_)
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
                            'OrderDetails': [{'ProductId': 0}],
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
