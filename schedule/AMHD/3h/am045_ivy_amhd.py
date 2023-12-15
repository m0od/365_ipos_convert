import glob
import os
import shutil
import sys
from datetime import datetime
from unidecode import unidecode
from os.path import dirname


class AM045(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'ivy_amhd'
        self.ADAPTER_TOKEN = '59b03c79d03e2a7189344a6c77476189d31c34666ca3fd1ea2813e6961ef1baa'
        self.FOLDER = 'ivy_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.EXT = '.CSV'
        self.gg = Google()

    def extract_data(self, DATA):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        SHEET_ID = self.gg.create_sheet(DATA)

        ws = self.gg.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        orders = {}
        header = []
        for _ in ws['values'][0]:
            header.append(unidecode(_.strip().upper()))
        if 'NGAY HD' in header:
            sheet_type = -1
            print("TRA_HANG")
        else:
            sheet_type = 1
            print("MUA_HANG")
        for row, _ in enumerate(ws['values'][1:]):
            rec = dict(zip(header, _))
            # print(rec)
            code = rec.get('SO HOA DON')
            # print(code)
            if not code: continue
            if not len(code.strip()): continue
            # print(code)
            # pur_date = rec.get('Ngày').split('.')[0]
            pur_date = float(rec.get('NGAY'))
            pur_date = (pur_date - 25569) * 86400.0
            pur_date = datetime.utcfromtimestamp(pur_date)
            if sheet_type == -1:
                pur_date = pur_date.strftime('%Y-%m-%d 07:00:00')
            else:
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            try:
                total = float(rec.get('TIEN TONG').strip())
            except:
                total = 0
            discount = float(rec.get('TIEN CK').strip())
            try:
                discount += float(rec.get('TIEN VOUCHER').strip())
            except:
                pass
            if sheet_type == -1:
                ods = {
                    'Code': rec.get('MA VT').strip(),
                    'Name': rec.get('MA VT').strip(),
                    'Price': float(rec.get('DON GIA').strip()),
                    'Quantity': float(rec.get('SO LUONG').strip()) * sheet_type
                }
                code = f'R_{code}'
                total *= sheet_type
                discount *= sheet_type
            else:
                ods = {
                    'Code': rec.get('MA VT').strip(),
                    'Name': rec.get('MA VT').strip(),
                    'Price': float(rec.get('DON GIA').strip()),
                    'Quantity': float(rec.get('SL').strip()) * sheet_type
                }
            if not orders.get(code):
                orders.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': discount,
                        'OrderDetails': [ods],
                        'PaymentMethods': [{
                            'Name': 'CASH', 'Value': total
                        }]
                    }
                })
            else:
                total += orders[code]['Total']
                discount += orders[code]['Total']
                orders[code]['OrderDetails'].append(ods)
                orders[code]['PaymentMethods'] = [{
                    'Name': 'CASH', 'Value': total
                }]
        for k, v in orders.items():
            # print(v)
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, v)
            if v['PaymentMethods'][0]['Value'] <= 0:
                pm = {
                    'Code': f'{v["Code"]}-CASH',
                    'OrderCode': v["Code"],
                    'Amount': v['PaymentMethods'][0]['Value'],
                    'TransDate': v['PurchaseDate'],
                    'AccountId': 'CASH'
                }
                submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
        self.backup(DATA)
        self.gg.delete(SHEET_ID)

    def get_data(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        self.gg.google_auth()
        try:
            files = [f for f in os.listdir(self.FULL_PATH) if os.path.isfile(f'{self.FULL_PATH}/{f}')]
            for _ in files:
                DATA = f'{self.FULL_PATH}/{_}'
                if DATA.upper().endswith(self.EXT):
                    print(DATA)
                    self.extract_data(DATA)
                    print('*'*10)
        except Exception as e:
            print(148, e)
            submit_error(self.ADAPTER_RETAILER, reason=str(e))

        # self.backup(DATA)

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

# AM045().get_data()
