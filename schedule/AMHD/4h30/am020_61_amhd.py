import glob
import os
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname

def get_value(value):
    try:
        return float(value)
    except:
        return 0

class AM020(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'marukame_amhd'
        self.ADAPTER_TOKEN = '2450e3ad06a9126068eef480f16cbfdad42d1aeeb1d06e1f25230be9e89d7717'
        self.FOLDER = '61_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%b%Y')
        self.ORDERS = {}

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_check(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        DATA = self.scan_file(f'*_{self.DATE}_C*.txt')
        # print(DATA)
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, reason='CHECK_FOUND')
            return
        f = open(DATA, 'r')
        lines = f.read().strip().split('\n')
        f.close()
        # ORDERS = {}
        for line in lines:
            _ = line.split('|')
            # print(_)
            cancel = int(_[32].strip())
            if cancel == 1:
                continue
            code = _[4].strip()
            if not len(code):
                continue
            # # if code != 'CA_230829_10000002623349': continue
            pur_date = _[7].strip()
            if not len(pur_date):
                pur_date = _[6].strip()
            try:
                pur_date = datetime.strptime(pur_date, '%d %b %Y %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
            # print(code, pur_date)
            # # now = datetime.now() - timedelta(days=1)
            # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
            # pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # # print(pur_date)
            discount = get_value(_[9].strip())
            total = get_value(_[10].strip())
            # if total == 0: continue
            vat = get_value(_[11].strip())
            card = get_value(_[14].strip())
            voucher = get_value(_[15].strip())
            # print(discount, total, vat)
            # if ORDERS.get(code) is None:
            self.ORDERS.update({
                code: {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'PaymentMethods': [],
                    'OrderDetails': []
                }
            })

        # for k, v in ORDERS.items():
        #     submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        # for k, v in ORDERS.items():
        #     for _ in v['PaymentMethods']:
        #         if _['Value'] < 0:
        #             submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data={
        #                 "Code": f"{v['Code']}-{_['Name'].upper()}",
        #                 "OrderCode": v['Code'],
        #                 "Amount": _['Value'],
        #                 "TransDate": v['PurchaseDate'],
        #                 "AccountId": _['Name'].upper()
        #             })
        self.backup(DATA)

    def get_detail(self):
        from pos_api.adapter import submit_error, submit_order, submit_payment
        DATA = self.scan_file(f'*_{self.DATE}_D*.txt')
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, reason='DETAIL_NOT_FOUND')
            return
        f = open(DATA, 'r')
        lines = f.read().strip().split('\n')
        f.close()
        for line in lines:
            # try:
            _ = line.split('|')
            # print(_)
            code = _[6].strip()
            if not len(code): continue
            if self.ORDERS.get(code) is None: continue
            if _[19].strip().upper() == 'SALES':
                ods = [{
                    'Code': _[16].strip(),
                    'Name': _[17].strip(),
                    'Price': get_value(_[20].strip()) + get_value(_[25].strip()),
                    'Quantity': get_value(_[18].strip())
                }]
                # print(ods)
                self.ORDERS[code]['OrderDetails'].extend(ods)
            elif _[19].strip().upper() == 'TENDER':
                # print(_)
                name = _[17].strip()
                if name == 'VND': name = 'CASH'
                value = get_value(_[23].strip())
                pms = [{'Name': name, 'Value': value}]
                self.ORDERS[code]['PaymentMethods'].extend(pms)
        for _, order in self.ORDERS.items():
            if not len(order['OrderDetails']):
                order['OrderDetails'] = [{'ProductId': 0}]
            if order['Total'] == 0:
                for pm in order['PaymentMethods']:
                    order['Total'] += pm['Value']
                    order['TotalPayment'] += pm['Value']
            # print(order['Code'],order['PaymentMethods'])
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        # for k, v in ORDERS.items():
        #     for _ in v['PaymentMethods']:
        #         if _['Value'] < 0:
        #             pm = {
        #                 'Code': f"{v['Code']}-{_['Name'].upper()}",
        #                 'OrderCode': v['Code'],
        #                 'Amount': _['Value'],
        #                 'TransDate': v['PurchaseDate'],
        #                 'AccountId': _['Name'].upper()
        #             }
        #             submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, data=pm)
        self.backup(DATA)

    def get_data(self):
        self.get_check()
        self.get_detail()


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