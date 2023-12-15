import glob
import os
import shutil
import sys
from datetime import datetime, timedelta, time
from os.path import dirname


class AM183(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'okaidi_obabi_amhd'
        self.ADAPTER_TOKEN = '105255415bbd849c85c9b390a3c87c9bfa745efc8c209cf859d491f9d22ee391'
        self.FOLDER = 'tamson_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        # self.DATE = self.DATE.strftime('%d.%m.%Y')
        self.EXT = f'*{self.DATE.strftime("%d")}*.xls'

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

        # print(self.DATA)

    def get_data(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        from drive import Google
        # self.rename_file()
        DATA = self.scan_file()
        if not DATA:
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        g = Google()
        g.google_auth()
        SHEET_ID = g.create_sheet(DATA)
        ws = g.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        for row, rec in enumerate(ws['values'][3:]):
            try:
                code = rec[4]
                if not code: continue
                if not len(code.strip()): continue
                try:
                    pur_date = rec[1].strip()
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y')
                except:
                    continue
                total = float(rec[6].replace(',', ''))
                vat = float(rec[8].replace(',', ''))
                discount = float(rec[9].replace(',', ''))
                cash = float(rec[22].replace(',', ''))
                order = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{
                        'Name': 'CASH', 'Value': cash
                    }]
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                if cash == 0:
                    pm = {
                        'Code': f'{code}-CASH',
                        'OrderCode': code,
                        'Amount': cash,
                        'TransDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                        'AccountId': 'CASH'
                    }
                    submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)

            except:
                pass
        self.backup(DATA)
        g.delete(SHEET_ID)

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
