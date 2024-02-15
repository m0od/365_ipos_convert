import glob
import os
import shutil
import sys
from datetime import datetime
from os.path import dirname


class AM145(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        # self.FOLDER = 'yanghao_amhd'
        # self.FULL_PATH = f'/home/{self.FOLDER}'
        self.ADAPTER_RETAILER = 'orifood_amhd'
        self.ADAPTER_TOKEN = '122a909b82a6dbb3a87c11545a778cb8c0bcfe9d32bff2d1212bc2fb7f4d47ab'
        self.FOLDER = '260_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.EXT = '*.xlsx'
        self.GG = Google()
        self.GG.FOLDER_ID = '1MncWjpNNpQ7WBbw1Itmm1zMqWZ3ixHvu'
        self.GG.FULL_PATH = self.FULL_PATH

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return files
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

    def extract_data(self, SHEET_ID):
        from pos_api.adapter import submit_order
        ws = self.GG.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        for row, rec in enumerate(ws['values'][3:-3]):
            code = rec[7].replace('.00', '').replace(',', '')
            pur_date = f'{rec[4]} {rec[12]}'
            pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M')
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            total = float(rec[18].replace('.00', '').replace(',', ''))
            discount = abs(float(rec[15].replace('.00', '').replace(',', '')))
            discount += float(rec[26].replace('.00', '').replace(',', ''))
            vat = float(rec[17].replace('.00', '').replace(',', ''))
            cash = float(rec[19].replace('.00', '').replace(',', ''))
            card = float(rec[20].replace('.00', '').replace(',', ''))
            momo = float(rec[21].replace('.00', '').replace(',', ''))
            vnpay = float(rec[22].replace('.00', '').replace(',', ''))
            zalopay = float(rec[23].replace('.00', '').replace(',', ''))
            clingme = float(rec[24].replace('.00', '').replace(',', ''))
            point = float(rec[25].replace('.00', '').replace(',', ''))
            voucher = float(rec[27].replace('.00', '').replace(',', ''))
            pms = [
                {'Name': 'CASH', 'Value': cash},
                {'Name': 'CARD', 'Value': card},
                {'Name': 'MOMO', 'Value': momo},
                {'Name': 'VNPAY', 'Value': vnpay},
                {'Name': 'ZALOPAY', 'Value': zalopay},
                {'Name': 'CLINGME', 'Value': clingme},
                {'Name': 'POINT', 'Value': point},
                {'Name': 'VOUCHER', 'Value': voucher},
            ]
            for pm in pms.copy():
                if not pm['Value']: pms.remove(pm)
            order = {
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
            # print(order)
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        self.GG.delete(SHEET_ID)

    def get_data(self):
        from pos_api.adapter import submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            self.GG.google_auth()
            SHEET_ID = self.GG.create_sheet(DATA)
            self.extract_data(SHEET_ID)
            self.backup(DATA)
