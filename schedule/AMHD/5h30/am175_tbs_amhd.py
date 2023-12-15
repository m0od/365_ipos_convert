import glob
import os
import shutil
import sys
from datetime import datetime
from os.path import dirname


class AM175(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'the_body_shop_amhd'
        self.ADAPTER_TOKEN = 'c9c3124721596ffb07ffdb8658df6a4530ce5b491aace807222a40a459655e65'
        self.FOLDER = 'tbs_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.EXT = '*txt'
        self.ORDERS = []

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.FOLDER}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        try:
            f = open(DATA, 'rb')
            lines = f.read().decode('utf-8').strip().split('\n')
            f.close()
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, str(e))
            return
        for line in lines[1:]:
            try:
                raw = line.strip().split('|')
                pur_date = datetime.strptime(f'{raw[2]}{raw[3]}', '%d%m%Y%H')
                rc = int(raw[4])
                total = float(raw[5]) + float(raw[6])
                vat = float(raw[6])
                discount = float(raw[7])
                cash = float(raw[10])
                card = float(raw[11])
                card += float(raw[12])
                card += float(raw[13])
                card += float(raw[14])
                voucher = float(raw[15])
                cash = float(raw[16])
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CARD', 'Value': card},
                    {'Name': 'VOUCHER', 'Value': voucher}
                ]
                for pm in pms.copy():
                    if not pm['Value']: pms.remove(pm)
                if total != 0 or cash != 0 or card != 0 or voucher != 0:
                    self.ORDERS.append({
                        'Code': f'{pur_date.strftime("%Y%m%d_%H")}_{rc}',
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': int(total),
                        'TotalPayment': int(total),
                        'VAT': 0,
                        'Discount': int(discount),
                        'OrderDetails': [{'ProductId': 0}],
                        'PaymentMethods': pms
                    })
                    for _ in range(1, rc):
                        self.ORDERS.append({
                            'Code': f'{pur_date.strftime("%Y%m%d_%H")}_{_}',
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'Total': 0,
                            'TotalPayment': 0,
                            'VAT': 0,
                            'Discount': 0,
                            'OrderDetails': [{'ProductId': 0}],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                        })
            except:
                pass
        for order in self.ORDERS:
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
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
