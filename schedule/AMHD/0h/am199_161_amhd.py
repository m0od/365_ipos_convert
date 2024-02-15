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


class AM199(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'jysk_amhd'
        self.ADAPTER_TOKEN = 'f66398c7a60647fe3b8e1152081a2d1f5708e42d80d20798e6efc46cfbebca60'
        self.FOLDER = '161_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xls'
        self.METHOD = {
            'TIEN MAT': 'CASH',
            'VN PAY': 'VNPAY-QR',
            'NGAN HANG': 'CARD',
            'GOT IT HN': 'GOT IT'
        }

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
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
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            # print(DATA)
            ws = xlrd.open_workbook(DATA)
            raw = list(ws.sheets())[0]
            # print(raw)
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            orders = []
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                state = unidecode(rec.get('STATE').value.upper()).strip()
                if state == 'CANCELED':
                    continue
                try:
                    pur_date = rec.get('PAYMENT DATE').value
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y')
                    # pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
                # print(pur_date)
                pm = rec.get('PAYMENT METHOD').value.replace('(VND)', '').strip()
                pm = unidecode(pm.split('-')[0].strip().upper())
                # print(pm)
                if 'NGAN HANG' in pm:
                    pm = 'NGAN HANG'
                # print(self.METHOD.get(pm))pr
                # print(rec)
                total = get_value(str(rec.get('AMOUNT').value).replace(',',''))
                code = f'HD-{pur_date.strftime("%d%m%y")}-{len(orders) + 1:05d}'
                orders.append({
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{'Name': self.METHOD.get(pm), 'Value': total}]
                })
            time = []
            for idx, order in enumerate(orders):
                h = 10 + int(11 * idx/len(orders))
                pur_date = order['PurchaseDate'].strftime('%Y-%m-%d')
                m = random.randint(0, 59)
                s = random.randint(0, 59)
                pur_date = f'{pur_date} {h:02d}:{m:02d}:{s:02d}'
                time.append(pur_date)
            time.sort()
            for idx, t in enumerate(time):
                orders[idx].update({'PurchaseDate': t})
                # print(orders[idx])
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders[idx])
                if orders[idx]['Total'] < 0:
                    pm = {
                        'Code': f'{orders[idx]["Code"]}-{orders[idx]["PaymentMethods"][0]["Name"]}',
                        'OrderCode': orders[idx]["Code"],
                        'Amount': orders[idx]['Total'],
                        'TransDate': t,
                        'AccountId': orders[idx]["PaymentMethods"][0]["Name"]
                    }
                    submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)

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