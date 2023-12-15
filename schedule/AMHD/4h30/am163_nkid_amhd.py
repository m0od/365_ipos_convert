import glob
import os
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname


class AM163(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'nkid_amhd'
        self.ADAPTER_TOKEN = '206839f30026f5c2865a6bac5e3546d228cc9cd8e1f92a318afdfc4109422cf1'
        self.FOLDER = 'nkid_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%y%m%d')

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_tw(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        DATA = self.scan_file(f'*tw_{self.DATE}.txt')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, reason='TW_NOT_FOUND')
            return
        f = open(DATA, 'r')
        lines = f.read().strip().split('\n')
        f.close()
        ORDERS = {}
        for line in lines:
            _ = line.split('|')
            code = _[0].strip()
            # if code != 'CA_230829_10000002623349': continue
            pur_date = _[1].strip()
            pur_date = datetime.strptime(pur_date, '%H%M%d%m%Y')
            # now = datetime.now() - timedelta(days=1)
            # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(pur_date)
            total = float(_[2].strip())
            vat = round(float(_[3].strip()), 0)
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
            ORDERS.update({_[0].strip(): {
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
        for k, v in ORDERS.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        for k, v in ORDERS.items():
            for _ in v['PaymentMethods']:
                if _['Value'] < 0:
                    submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data={
                        "Code": f"{v['Code']}-{_['Name'].upper()}",
                        "OrderCode": v['Code'],
                        "Amount": _['Value'],
                        "TransDate": v['PurchaseDate'],
                        "AccountId": _['Name'].upper()
                    })
        self.backup(DATA)

    def get_ts(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        DATA = self.scan_file(f'*ts_{self.DATE}.txt')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, reason='TS_NOT_FOUND')
            return
        f = open(DATA, 'r')
        lines = f.read().strip().split('\n')
        f.close()
        ORDERS = {}
        for line in lines:
            # try:
            _ = line.split('|')
            code = _[0].strip()
            # if code != 'CA_230829_10000002623349': continue
            pur_date = _[1].strip()
            pur_date = datetime.strptime(pur_date, '%H%M%d%m%Y')
            # now = datetime.now() - timedelta(days=1)
            # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(pur_date)
            total = float(_[2].strip())
            vat = round(float(_[3].strip()), 0)
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
            ORDERS.update({_[0].strip(): {
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
        for k, order in ORDERS.items():
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        for k, v in ORDERS.items():
            for _ in v['PaymentMethods']:
                if _['Value'] < 0:
                    pm = {
                        'Code': f"{v['Code']}-{_['Name'].upper()}",
                        'OrderCode': v['Code'],
                        'Amount': _['Value'],
                        'TransDate': v['PurchaseDate'],
                        'AccountId': _['Name'].upper()
                    }
                    submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, data=pm)
        self.backup(DATA)

    def get_data(self):
        with futures.ThreadPoolExecutor(max_workers=2) as mt:
            thread = [
                mt.submit(self.get_tw),
                mt.submit(self.get_ts)
            ]
            futures.as_completed(thread)

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