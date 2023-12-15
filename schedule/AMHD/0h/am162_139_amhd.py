import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname




class AM162(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'kichi_kichi_amhd'
        self.ADAPTER_TOKEN = 'b1a681cca85912c532ee19d74e06dce05428e94fd897f364df476fef417131dc'
        self.FOLDER = '139_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%Y%m%d')

    def get_data(self):
        from drive import Google
        from pos_api.adapter import submit_order
        g = Google()
        g.google_auth()
        files = glob.glob(f'{self.FULL_PATH}/*.xls')
        for _ in files:
            SHEET_ID = g.create_sheet(_)
            ws = g.SHEETS.spreadsheets().values().get(
                spreadsheetId=SHEET_ID, range='1:1000'
            ).execute()
            for row, rec in enumerate(ws['values'][3:]):
                code = rec[2]
                pur_date = f'{rec[5]} {rec[7]}'
                pur_date = datetime.strptime(pur_date, '%m/%d/%Y %H')
                # if pur_date.strftime('%Y%m%d') != self.DATE:
                #     continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(rec[15])
                discount = float(rec[12]) * -1
                vat = float(rec[14])
                cash = float(rec[16])
                card = float(rec[17])
                voucher = float(rec[18])
                voucher += float(rec[22])
                voucher += float(rec[23])
                wallet = float(rec[19])
                tiep_khach = float(rec[20])
                khach_no = float(rec[21])
                grab_food = float(rec[24])
                now = float(rec[25])
                other = float(rec[26])
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CARD', 'Value': card},
                    {'Name': 'VOUCHER', 'Value': voucher},
                    {'Name': 'ONLINE WALLET', 'Value': wallet},
                    {'Name': 'TIẾP KHÁCH', 'Value': tiep_khach},
                    {'Name': 'KHÁCH NỢ', 'Value': khach_no},
                    {'Name': 'GRABFOOD', 'Value': grab_food},
                    {'Name': 'NOW', 'Value': now},
                    {'Name': 'OTHER', 'Value': other},
                ]
                for pm in pms.copy():
                    if not pm['Value']:
                        pms.remove(pm)
                orders = {
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
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
            self.backup(_)
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
