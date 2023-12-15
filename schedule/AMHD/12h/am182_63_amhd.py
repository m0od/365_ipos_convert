import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM182(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'kpub_yutang_amhd'
        self.ADAPTER_TOKEN = '0258845726f8ce2b1c57cfd4896ff364bd34fa3609c9d11f385a7153e005a121'
        self.FOLDER = '63_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%Y%m%d')

    def get_data(self):
        from drive import Google
        from pos_api.adapter import submit_order, submit_error
        g = Google()
        g.google_auth()
        files = glob.glob(f'{self.FULL_PATH}/*.xls')
        for _ in files:
            try:
                SHEET_ID = g.create_sheet(_)
            except Exception as e:
                submit_error(self.ADAPTER_RETAILER, reason=str(e))
                continue
            ws = g.SHEETS.spreadsheets().values().get(
                spreadsheetId=SHEET_ID, range='1:1000'
            ).execute()
            raw = ws['values']
            raw_type = raw[3][0]
            if 'YT' in raw_type:
                raw_type = 'Y_'
            else:
                raw_type = 'K_'
            for row, rec in enumerate(raw[3:]):
                try:
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
                        'Code': f'{raw_type}{code}',
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
                except:
                    pass
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

