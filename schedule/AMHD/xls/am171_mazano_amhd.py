import glob
import os
import shutil
import sys
import xlrd
from datetime import datetime, timedelta
from os.path import dirname


class AM171(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'mazano_amhd'
        self.ADAPTER_TOKEN = '862f17eb1a572858bcdd44c501ed75e0f157800d6d5ab1d61502d01a3c508e92'
        self.FOLDER = 'mazano_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.now = datetime.now() - timedelta(days=1)
        self.EXT = f'*{self.now.strftime("%d-%m-%Y")}*.xls'
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
        dataframe = xlrd.open_workbook(DATA)
        sheet = dataframe[0]
        orders = {}
        nRows = sheet.nrows
        for row in range(1, nRows - 1):
            try:
                code = f"{self.now.strftime('%d%m%y')}-{len(list(self.ORDERS.keys())) + 1}"
                p_code = sheet[row][1].value
                name = sheet[row][2].value
                qty = float(sheet[row][4].value)
                price = float(sheet[row][5].value)
                discount = float(sheet[row][7].value) + float(sheet[row][8].value)
                vat = float(sheet[row][9].value)
                total = float(sheet[row][10].value)
                self.ORDERS.update({code: {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': f"{self.now.strftime('%Y-%m-%d')} 14:00:00",
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'PaymentMethods': [{'Name': 'CASH', 'Value': total}],
                    'OrderDetails': [{
                        'Code': p_code,
                        'Name': name,
                        'Price': price,
                        'Quantity': qty
                    }]
                }})

            except Exception as e:
                print(e)
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        for k, v in self.ORDERS.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        self.backup(DATA)

# MAZANO_AMHD().get_data()
