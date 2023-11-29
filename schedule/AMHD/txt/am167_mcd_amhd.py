import glob
import os
import shutil
import sys
from os.path import dirname
from datetime import datetime, timedelta


class AM167(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'mcdonald_amhd'
        self.ADAPTER_TOKEN = '59be732c9d48d58772011f30f74c447cbfee32a9b82c4cebe1e0d8b1a35aac9a'
        self.FOLDER = 'mcd_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*{self.DATE.strftime("%Y%m%d")}.txt'
        self.ORDERS = []

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        from pos_api.adapter import submit_order, submit_error
        try:
            DATA = self.scan_file()
            if not DATA:
                submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
                return
            f = open(DATA, 'rb')
            lines = f.read().decode('utf-8').strip().split('\n')
            f.close()
            for line in lines[1:]:
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
                point = float(raw[16])
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CARD', 'Value': card},
                    {'Name': 'VOUCHER', 'Value': voucher},
                    {'Name': 'POINT', 'Value': point}
                ]
                for _ in pms.copy():
                    if not _['Value']: pms.remove(_)
                if total != 0 or cash != 0 or card != 0 and point != 0 or voucher != 0:
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
                            'OrderDetails': [],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                        })
            for _ in self.ORDERS:
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
            self.backup(DATA)
        except:
            pass

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
