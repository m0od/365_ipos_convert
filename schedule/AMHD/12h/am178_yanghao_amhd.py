import os
import shutil
import sys
from datetime import datetime
from os.path import dirname


class AM178(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.FOLDER = 'yanghao_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.ADAPTER_RETAILER = 'yanghao_amhd'
        self.ADAPTER_TOKEN = '4a63189b3901f20ae2fecaa490d658be6b3d5c6228e116a545b07c45c7752f23'
        self.FOLDER = 'yanghao_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.GG = Google()
        self.GG.FOLDER_ID = '1oqTTtH4CUEA6ZFqonhPKEAzzlhLFGpR0'
        self.GG.FULL_PATH = self.FULL_PATH

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
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        self.GG.delete(SHEET_ID)

    def get_data(self):
        from pos_api.adapter import submit_error
        self.GG.google_auth()
        try:
            for file in self.GG.get_file():
                # print(file)
                try:
                    DATA = self.GG.download(file)
                    SHEET_ID = self.GG.create_sheet(DATA)
                    self.extract_data(SHEET_ID)
                    self.backup(DATA)
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))

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
