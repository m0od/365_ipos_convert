import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM046(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'namco_amhd'
        self.ADAPTER_TOKEN = '02be07b6450c20f956d10d6d59d7b614f0accfcd662dd1582fdf2a97c226a105'
        self.FOLDER = '116_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*xlsx'
        self.GG = Google()
        self.ORDERS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
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

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        self.GG.google_auth()
        SHEET_ID = self.GG.create_sheet(DATA)
        ws = self.GG.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range='1:1000'
        ).execute()
        raw = ws['values']
        header = raw[0]
        for row, _ in enumerate(ws['values'][1:]):
            rec = dict(zip(header, _))
            code = rec['Mã hóa đơn']
            if not code: continue
            if not len(code.strip()): continue
            try:
                pur_date = datetime.strptime(rec['Thời gian'], '%d/%m/%Y %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
            ods = [{
                'Code': rec['Mã hàng'],
                'Name': rec['Tên hàng'],
                'Price': float(rec['Đơn giá'].replace(',', '')),
                'Quantity': float(rec['Số lượng'])
            }]
            if not self.ORDERS.get(code):
                total = float(rec['Khách cần trả'].replace(',', ''))
                discount = float(rec['Giảm giá'].replace(',', ''))
                cash = float(rec['Tiền mặt'].replace(',', ''))
                card = float(rec['Thẻ'].replace(',', ''))
                bank = float(rec['Chuyển khoản'].replace(',', ''))
                point = float(rec['Điểm'].replace(',', ''))
                voucher = float(rec['Voucher'].replace(',', ''))
                pms = [
                    {'Name': 'CASH', 'Value': cash},
                    {'Name': 'CARD', 'Value': card},
                    {'Name': 'TRANSFER', 'Value': bank},
                    {'Name': 'POINT', 'Value': point},
                    {'Name': 'VOUCHER', 'Value': voucher},
                ]
                for pm in pms.copy():
                    if not pm['Value']: pms.remove(pm)
                self.ORDERS.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': discount,
                        'OrderDetails': ods,
                        'PaymentMethods': pms
                    }
                })
            else:
                self.ORDERS[code]['OrderDetails'].extend(ods)
        for _, order in self.ORDERS.items():
            # print(order)
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
        self.GG.delete(SHEET_ID)
        self.backup(DATA)
        if not len(list(self.ORDERS.keys())):
            self.send_zero()


    def send_zero(self):
        from pos_api.adapter import submit_order
        order = {
            'Code': f'NOBILL_{self.DATE.strftime("%d%m%Y")}',
            'Status': 2,
            'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
            'Total': 0,
            'TotalPayment': 0,
            'VAT': 0,
            'Discount': 0,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
        }
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)