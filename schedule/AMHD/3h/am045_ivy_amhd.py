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
        from pos import POS365
        self.ADAPTER_RETAILER = 'ivy_amhd'
        self.ADAPTER_TOKEN = '59b03c79d03e2a7189344a6c77476189d31c34666ca3fd1ea2813e6961ef1baa'
        self.FOLDER = 'ivy_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.EXT = '*.CSV'
        self.gg = Google()
        self.POS = POS365()
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = '123456'
        self.POS.DOMAIN = self.__class__.__name__

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return files
        except:
            return None

    def extract_order(self, DATA):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        SHEET_ID = self.gg.create_sheet(DATA)

        ws = self.gg.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        orders = {}
        header = []
        for _ in ws['values'][0]:
            header.append(unidecode(_.strip().upper()))
        for row, _ in enumerate(ws['values'][1:]):
            rec = dict(zip(header, _))
            code = rec.get('SO HOA DON')
            if not code: continue
            if not len(code.strip()): continue
            try:
                code = float(code)
                code = str(int(code))
            except:
                continue
            pur_date = float(rec.get('NGAY'))
            pur_date = (pur_date - 25569) * 86400.0
            pur_date = datetime.utcfromtimestamp(pur_date)
            print(pur_date)
            code = f'{pur_date.strftime("%Y")}-{code}'
            print(code)
            try:
                total = float(rec.get('TIEN TONG').strip())
            except:
                total = 0
            discount = float(rec.get('TIEN CK').strip())
            try:
                discount += float(rec.get('TIEN VOUCHER').strip())
            except:
                pass
            ods = {
                'Code': rec.get('MA VT').strip(),
                'Name': rec.get('MA VT').strip(),
                'Price': float(rec.get('DON GIA').strip()),
                'Quantity': float(rec.get('SL').strip())
            }
            if not orders.get(code):
                orders.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime("%Y-%m-%d %H:%M:%S"),
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
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, v)
            # if v['PaymentMethods'][0]['Value'] <= 0:
            #     pm = {
            #         'Code': f'{v["Code"]}-CASH',
            #         'OrderCode': v["Code"],
            #         'Amount': v['PaymentMethods'][0]['Value'],
            #         'TransDate': v['PurchaseDate'],
            #         'AccountId': 'CASH'
            #     }
            #     submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
        self.backup(DATA)
        self.gg.delete(SHEET_ID)

    def extract_return(self, DATA):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        SHEET_ID = self.gg.create_sheet(DATA)

        ws = self.gg.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        orders = {}
        header = []
        for _ in ws['values'][0]:
            header.append(unidecode(_.strip().upper()))
        ret = []
        for row, _ in enumerate(ws['values'][1:]):
            rec = dict(zip(header, _))
            pur_date = float(rec.get('NGAY HD'))
            pur_date = (pur_date - 25569) * 86400.0
            pur_date = datetime.utcfromtimestamp(pur_date)
            code = f'{pur_date.strftime("%Y")}-{rec.get("HD")}'
            if code not in ret:
                ret.append(code)
            else:
                continue
            order = self.POS.get_order(code)
            if not order:
                continue
            pur_date = float(rec.get('NGAY'))
            pur_date = (pur_date - 25569) * 86400.0
            pur_date = datetime.utcfromtimestamp(pur_date)
            pur_date = pur_date.strftime('%Y-%m-%d 07:00:00')
            data = {
                'Code': f"R-{code}",
                'Status': 2,
                'PurchaseDate': pur_date,
                'Total': order['Total'] * -1,
                'TotalPayment': order['TotalPayment'] * -1,
                'VAT': 0,
                'Discount': 0,
                'OrderDetails': order['OrderDetails'],
                'PaymentMethods': [{'Name': 'CASH', 'Value': order['Total'] * -1}]
            }
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, data)
            pm = {
                'Code': f'{data["Code"]}-CASH',
                'OrderCode': data['Code'],
                'Amount': data['Total'],
                'TransDate': data['PurchaseDate'],
                'AccountId': 'CASH'
            }
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
        self.backup(DATA)
        self.gg.delete(SHEET_ID)

    def get_data(self):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        self.POS.login()
        self.gg.google_auth()
        files = self.scan_file('TL*.CSV')
        for DATA in files:
            try:
                self.extract_return(DATA)
            except Exception as e:
                submit_error(self.ADAPTER_RETAILER, reason=str(e))
        # files = self.scan_file('*.CSV')
        # for DATA in files:
        #     try:
        #         self.extract_order(DATA)
        #     except Exception as e:
        #         submit_error(self.ADAPTER_RETAILER, reason=str(e))

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
