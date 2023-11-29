import glob
import os
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname
import xlrd


class AM191(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'converse_newera_amhd'
        self.ADAPTER_TOKEN = 'f1e3248d153caa028846c0e55a698cae9446795e81fbe5c6cfe0fd5e58e7b89f'
        self.FOLDER = '249_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=0)
        self.DATE = self.DATE.strftime('%d%m%Y')

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_newera(self):
        from pos_api.adapter import submit_order, submit_error
        DATA = self.scan_file(f'N*{self.DATE}.xls')
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='NEWERA_NOT_FOUND')
            return
        wb = xlrd.open_workbook(DATA)
        sheet = wb[0]
        nrows = sheet.nrows

        try:
            pur_date = sheet[1][1].value.strip()
            if len(pur_date) == 0: raise Exception
            pur_date = datetime.strptime(pur_date, '%d-%m-%Y')
            ods = []
            for row in range(2, nrows):
                code = sheet[row][0].value
                if 'Total For' in code and pur_date.strftime('%d-%m-%Y') not in code:
                    code = code.replace('Total For', '').strip()[:-1].strip()
                    total = float(sheet[row][-2].value)
                    data = {
                        'Code': f'NEWERA_{code}',
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': ods,
                        'PaymentMethods': [{
                            'Name': 'CASH',
                            'Value': total
                        }]
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                    ods = []
                else:
                    try:
                        qty = float(sheet[row][1].value)
                        _ = sheet[row][0].value.split('/')
                        p_code = _[0].strip()
                        p_name = _[1].strip()
                        price = float(sheet[row][1].value)
                        ods.append({
                            'Code': p_code,
                            'Name': p_name,
                            'Price': price,
                            'Quantity': qty
                        })
                    except:
                        pass
        except:
            pass
        self.backup(DATA)

    def get_converse(self):
        from pos_api.adapter import submit_order
        DATA = self.scan_file(f'C*{self.DATE}.xls')
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='CONVERSE_NOT_FOUND')
            return
        wb = xlrd.open_workbook(DATA)
        sheet = wb[0]
        nrows = sheet.nrows
        try:
            pur_date = sheet[1][1].value.strip()
            if len(pur_date) == 0: raise Exception
            pur_date = datetime.strptime(pur_date, '%d-%m-%Y')
            ods = []
            for row in range(2, nrows):
                code = sheet[row][0].value
                if 'Total For' in code and pur_date.strftime('%d-%m-%Y') not in code:
                    code = code.replace('Total For', '').strip()[:-1].strip()
                    total = float(sheet[row][-2].value)
                    data = {
                        'Code': f'CONVERSE_{code}',
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': ods,
                        'PaymentMethods': [{
                            'Name': 'CASH',
                            'Value': total
                        }]
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                    ods = []
                else:
                    try:
                        qty = float(sheet[row][1].value)
                        _ = sheet[row][0].value.split('/')
                        p_code = _[0].strip()
                        p_name = _[1].strip()
                        price = float(sheet[row][1].value)
                        ods.append({
                            'Code': p_code,
                            'Name': p_name,
                            'Price': price,
                            'Quantity': qty
                        })
                    except:
                        pass
        except:
            pass
        self.backup(DATA)

    def get_data(self):
        with futures.ThreadPoolExecutor(max_workers=2) as mt:
            thread = [
                mt.submit(self.get_newera),
                mt.submit(self.get_converse)
            ]
            futures.as_completed(thread)

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
