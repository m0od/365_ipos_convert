import codecs
import csv
import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM190(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'koi_amhd'
        self.ADAPTER_TOKEN = '03b5fad3352673a3ad537854a777799c5f920d4f86aa23a3fd7485b0075ad5b5'
        self.FOLDER = 'koi_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.ORDERS = {}
        self.TRANS = []
        self.DATE = datetime.now() - timedelta(days=1)
        self.POS = POS365()
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'
        self.POS.DOMAIN = self.__class__.__name__
        self.POS.DATE = self.DATE
        self.TOTAL = 0

    def scan_file(self, EXT):
        try:
            files = glob.glob(self.FULL_PATH + EXT)
            # print(files)
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

    def get_details(self):
        ext = f"{self.DATE.strftime('%d%m%Y.csv')}"
        DATA = self.scan_file(ext)
        # print(DATA)
        if not DATA: return
        f = codecs.open(DATA, 'r', encoding='utf-8', errors='ignore')
        raw = list(csv.reader(f, delimiter=','))
        # print(raw)
        row = 0
        extract = False
        while row < len(raw):
            if not len(raw[row]) or raw[row][0] != 'Terminal':
                if not extract:
                    row += 1
                    continue
            extract = True
            row += 1
            break
        is_product = False
        ods = []
        code = None
        while row < len(raw):
            if not is_product:
                # print(raw[row])
                code = raw[row][4][1:].strip()
                if not len(raw[row][3].strip()):
                    row += 1
                    continue
                pur_date = datetime.strptime(raw[row][3], '%Y-%m-%d %H:%M')
                total = float(raw[row][-1].strip().replace(',', ''))
                discount = abs(float(raw[row][12].strip().replace(',', '')))
                # print(pur_date, code, total, discount)
                self.ORDERS.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': total,
                        'Discount': discount,
                        'TotalPayment': total,
                        'VAT': 0,
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    }
                })
                row += 2
            if not len(raw[row][0]):
                is_product = True
                p_code = raw[row][4][1:].strip()
                p_name = raw[row][5][1:].strip()
                price = float(raw[row][-1].strip().replace(',', ''))
                qty = float(raw[row][-2].strip().replace(',', ''))
                # print('->', p_code, p_name, price, qty)
                ods.append({
                    'Code': p_code,
                    'Name': p_name,
                    'Price': price,
                    'Quantity': qty
                })
                self.ORDERS[code].update({
                    'OrderDetails': ods
                })
                row += 1
            else:
                ods = []
                is_product = False
                continue
        for k, v in self.ORDERS.items():
            self.TRANS.append({
                'Code': f'{v["Code"]}-CASH',
                'OrderCode': v['Code'],
                'Amount': 0,
                'TransDate': v['PurchaseDate'],
                'AccountId': 'CASH'
            })
        self.backup(DATA)

    def get_summary(self):
        ext = f"S{self.DATE.strftime('%d%m%Y.csv')}"
        DATA = self.scan_file(ext)
        # print(DATA)
        if not DATA: return
        f = codecs.open(DATA, 'r', encoding='utf-8', errors='ignore')
        raw = list(csv.reader(f, delimiter=','))
        row = 0
        while row < len(raw):
            if not len(raw[row]) or raw[row][0] != 'TRANSACTION SUMMARY':
                row += 1
                continue
            row += 2
            break
        vat = float(raw[row][3].strip().replace(',', ''))
        while row < len(raw):
            if not len(raw[row]) or raw[row][0] != 'PAYMENT SUMMARY':
                row += 1
                continue
            row += 2
            break
        pms = []
        while row < len(raw):
            # print(raw[row])
            if '**Total**' in raw[row][0]: break
            name = raw[row][1][1:].strip().upper()
            if name.upper() == 'VND': name = 'CASH'
            value = float(raw[row][3].strip().replace(',', ''))
            # print(name, value)
            pms.append({'Name': name, 'Value': value})
            row += 1
        self.ORDERS.update({
            'FINAL': {
                'Code': f'FINAL_{self.DATE.strftime("%Y%m%d")}',
                'Status': 2,
                'PurchaseDate': self.DATE.strftime('%Y-%m-%d 23:00:00'),
                'Total': 0,
                'TotalPayment': 0,
                'Discount': 0,
                'VAT': vat,
                'PaymentMethods': pms,
                'OrderDetails': [{'ProductId': 0}]
            }
        })
        for _ in pms:
            self.TRANS.append({
                'Code': f'FINAL_{self.DATE.strftime("%Y%m%d")}-{_["Name"]}',
                'OrderCode': f'FINAL_{self.DATE.strftime("%Y%m%d")}',
                'Amount': _['Value'],
                'TransDate': self.DATE.strftime('%Y-%m-%d 23:00:00'),
                'AccountId': _['Name']
            })
        self.backup(DATA)

    def submit_data(self):
        from pos_api.adapter import submit_payment, submit_order
        for _, v in self.ORDERS.items():
            self.TOTAL += v['Total']
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        print(self.TOTAL)
        self.POS.check_total(self.TOTAL)
        for _ in self.TRANS:
            submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)

    def get_data(self):
        self.get_details()
        self.get_summary()
        self.submit_data()
