import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import openpyxl


class AM136(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'concung_amhd'
        self.ADAPTER_TOKEN = 'f546ab681fa530a14671096bd43715bb0b73de3bdabb63125be2f80a8fd53cdd'
        self.FOLDER = 'concung_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.NOW = datetime.now() - timedelta(days=1)
        self.EXT = f'{self.NOW.strftime("%d.%m.%Y")}*xlsx'
        self.method = {
            'TIỀN MẶT': 'CASH'
        }

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

        # print(self.DATA)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        try:
            DATA = self.scan_file()
            if not DATA:
                submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
                return
            dataframe = openpyxl.load_workbook(DATA, data_only=True)
            data = dataframe.worksheets[0]
            orders = {}
            for row in range(2, data.max_row + 1):
                code = data[row][0].value
                if not code: continue
                code = str(code)
                pur_date = data[row][3].value
                if self.NOW.strftime("%d.%m.%Y") != pur_date.strftime('%d.%m.%Y'):
                    continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = float(data[row][6].value)
                cash = float(data[row][8].value)-float(data[row][7].value)
                voucher = float(data[row][7].value)
                credit = float(data[row][9].value)
                pms = []
                if cash:
                    pms.append({'Name': 'CASH', 'Value': cash})
                if voucher:
                    pms.append({'Name': 'VOUCHER', 'Value': voucher})
                if credit:
                    pms.append({'Name': 'CREDIT', 'Value': credit})
                if not len(pms):
                    pms.append({'Name': 'CASH', 'Value': 0})
                send = {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': pms
                }
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)

        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        self.backup(DATA)

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
