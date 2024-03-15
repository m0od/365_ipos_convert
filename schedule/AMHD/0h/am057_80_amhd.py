import glob
import os
import shutil
import sys

import xlrd
from datetime import datetime, timedelta
from os.path import dirname

from unidecode import unidecode


class AM057(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'highlands_amhd'
        self.ADAPTER_TOKEN = '2676295040c0b2cb1e39c72f4127f90d1ad2725506d1c447e95c76cc38dd6002'
        self.FOLDER = '80_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.GG = Google()
        self.TOTAL = None

    def scan_file(self, EXT):
        try:
            return glob.glob(f'{self.FULL_PATH}/{EXT}')
            # return max(files, key=os.path.getmtime)
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

    def get_cpn(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*M*xlsx')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='CPN NOT_FOUND')
            return
        for DATA in files:
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            code = None
            orders = {}
            for i in range(1, nRows):
                stt = raw.row(i)[0].value
                if stt:
                    code = raw.row(i)[1].value
                    pur_date = raw.row(i)[3].value
                    pur_date = datetime.strptime(pur_date, '%Y-%m-%d')
                    pur_date = pur_date + timedelta(hours=10)
                    # pur_date = pur_date.strftime('%Y-%m-%d 07:00:00')
                    total = float(raw.row(i)[6].value)
                    discount = float(raw.row(i)[5].value)
                    p_name = raw.row(i)[7].value.upper()
                    orders.update({
                        code: {
                            'Code': f'CPN_{code.strip()}',
                            'Status': 2,
                            'PurchaseDate': pur_date,
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': [],
                            'PaymentMethods': [{'Name': p_name, 'Value': total}]
                        }
                    })
                else:
                    name = raw.row(i)[1].value
                    if not (len(name.strip())): break
                    if name.strip().upper() == 'TÊN SẢN PHẨM': continue
                    p_code = raw.row(i)[4].value
                    if not p_code:
                        p_code = unidecode(name.strip())
                    try:
                        price = float(raw.row(i)[6].value)
                    except:
                        price = 0
                    try:
                        qty = float(raw.row(i)[5].value)
                    except:
                        qty = 0
                    orders[code]['OrderDetails'].append({
                        'Code': p_code,
                        'Name': name.strip(),
                        'Price': price,
                        'Quantity': qty
                    })
            # self.TOTAL = len(list(orders.keys()))
            total_bill = len(orders.keys())
            for i, (k, order) in orders.items():
                pur_date = order['PurchaseDate']
                pur_date = pur_date + timedelta(seconds=i*int(43200/total_bill))
                order['PurchaseDate'] = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            self.backup(DATA)

    def get_report(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*xlsx')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='REPORT NOT_FOUND')
            return
        for DATA in files:
            SHEET_ID = self.GG.create_sheet(DATA)
            ws = self.GG.SHEETS.spreadsheets().values().get(
                spreadsheetId=SHEET_ID,
                range='1:1000'
            ).execute()
            raw = ws['values']
            header = ['Type']
            header.extend(raw[3])
            for idx, _ in enumerate(header.copy()):
                if not _: header.pop(idx)
            orders = {}
            pm = None
            for row, _ in enumerate(raw[4:]):
                rec = dict(zip(header, _))
                if rec == {}: continue
                if 'Pay Type:' in rec.get('Type'):
                    tmp = rec['Type'].strip().split(':')[1].strip()
                    if len(tmp):
                        pm = tmp.upper()
                        continue
                    else:
                        break
                else:
                    try:
                        pur_date = datetime.strptime(rec['Date'], '%d/%m/%Y')
                        pur_date = pur_date + timedelta(hours=10)
                        # pur_date = pur_date.strftime('%Y-%m-%d 07:00:00')
                    except:
                        continue
                    code = rec.get('Ref Num').strip()
                    value = float(rec.get('Net Pay Amt').strip().replace(',', ''))
                    if not orders.get(code):
                        orders.update({
                            code: {
                                'Code': f'N-{code}',
                                'Status': 2,
                                'PurchaseDate': pur_date,
                                'Total': float(rec.get('Bill Amt').strip().replace(',', '')),
                                'TotalPayment': float(rec.get('Bill Amt').strip().replace(',', '')),
                                'VAT': 0,
                                'Discount': 0,
                                'OrderDetails': [{'ProductId': 0}],
                                'PaymentMethods': [{
                                    'Name': pm, 'Value': value
                                }]
                            }
                        })
                    else:
                        orders[code]['PaymentMethods'].append({
                            'Name': pm, 'Value': value
                        })
            # if self.TOTAL is None:
            #     self.TOTAL = len(list(orders.keys()))
            # else:
            #     self.TOTAL += len(list(orders.keys()))
            total_bill = len(orders.keys())
            for i, (k, order) in orders.items():
                pur_date = order['PurchaseDate']
                pur_date = pur_date + timedelta(seconds=i * int(43200 / total_bill))
                order['PurchaseDate'] = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            self.GG.delete(SHEET_ID)
            self.backup(DATA)
            # if self.TOTAL == 0:
            #     self.send_zero()

    def get_data(self):
        self.GG.google_auth()
        self.get_cpn()
        self.get_report()

    # def send_zero(self):
    #     from pos_api.adapter import submit_order
    #     order = {
    #         'Code': f'NOBILL_{self.DATE.strftime("%d%m%Y")}',
    #         'Status': 2,
    #         'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
    #         'Total': 0,
    #         'TotalPayment': 0,
    #         'VAT': 0,
    #         'Discount': 0,
    #         'OrderDetails': [{'ProductId': 0}],
    #         'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
    #     }
    #     submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
