import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM120(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'timezone_amhd'
        self.ADAPTER_TOKEN = 'fb7226b8d3033064611519b2683d15fa9ce2ce80b4a44c6a40dcf28d55a42af3'
        self.FOLDER = 'timezone_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}/TEEG_Test'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*{self.DATE.strftime("%d%m%Y")}.txt'

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
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        try:
            f = open(DATA, 'rb')
            s = f.read().decode('utf-8')
            f.close()
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            return
        lines = s.strip().split('\n')
        for line in lines:
            try:
                _ = line.strip().split('|')
                code = _[0].strip()
                pur_date = datetime.strptime(_[1], '%H%M%d%m%Y')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(_[2].strip())
                discount = float(_[3].strip())
                vat = round(float(_[4].strip()), 0)
                cash = float(_[6].strip())
                payoo = float(_[7].strip())
                cheque = float(_[8].strip())
                momo = float(_[9].strip())
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'PAYOO', 'Value': payoo},
                    {'Name': 'CHEQUE', 'Value': cheque},
                    {'Name': 'MOMO', 'Value': momo}
                ]
                for pm in pms.copy():
                    if not pm['Value']: pms.remove(pm)
                send = {
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
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, send)
            except Exception as e:
                submit_error(self.ADAPTER_RETAILER, str(e))
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
