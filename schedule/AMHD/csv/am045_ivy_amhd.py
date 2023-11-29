import glob
import os
import shutil
import sys
import uuid
from datetime import timedelta, datetime, time
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
        self.EXT = f'*.csv'
        self.gg = Google()

    def extract_data(self, DATA):
        from pos_api.adapter import submit_order, submit_payment, submit_error
        SHEET_ID = self.gg.create_sheet(DATA)

        ws = self.gg.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        # print(ws)
        if 'tra_lai' in ws['range'].lower():
            sheet_type = -1
        elif 'hoa_don' in ws['range'].lower():
            sheet_type = 1
        else:
            sheet_type = 0
        orders = {}
        for row, rec in enumerate(ws['values'][1:]):
            # print(rec)
            code = rec[3]
            if not code: continue
            if not len(code.strip()): continue
            # print(code)
            pur_date = rec[2].split('.')[0]
            pur_date = float(rec[2])
            pur_date = (pur_date - 25569) * 86400.0
            pur_date = datetime.utcfromtimestamp(pur_date)
            if sheet_type == -1:
                code = f'R{code[1:]}'
                ods = {
                    'Code': rec[5].strip(),
                    'Name': rec[5].strip(),
                    'Price': float(rec[13].strip()),
                    'Quantity': float(rec[12].strip()) * sheet_type
                }
                try:
                    total = float(rec[12].strip()) * -1
                except:
                    total = 0
                discount = float(rec[9].strip()) * -1
                # print(total, discount)
                if not orders.get(code):
                    orders.update({
                        code: {
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
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
            if sheet_type == 1:
                # print(code)
                try:
                    total = float(rec[14].strip())
                except:
                    total = 0
                discount = float(rec[8].strip())
                try:
                    discount += float(rec[13].strip())
                except:
                    pass
                ods = {
                    'Code': rec[4].strip(),
                    'Name': rec[4].strip(),
                    'Price': float(rec[6].strip()),
                    'Quantity': float(rec[5].strip())
                }
                if not orders.get(code):
                    orders.update({
                        code: {
                            'Code': code[1:],
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
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
            print(v)
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
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            for DATA in files:
                # # print(_)
                # t = os.path.getmtime(_)
                # t = datetime.fromtimestamp(t).strftime('%d%m%Y')
                # DATA = f'{self.__class__.__name__} {t} {str(uuid.uuid4()).split("-")[0]}.xlsx'
                # DATA = f'{self.FULL_PATH}/{DATA}'
                # os.rename(_, DATA)
                self.extract_data(DATA)
        except Exception as e:
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


AM045().get_data()
