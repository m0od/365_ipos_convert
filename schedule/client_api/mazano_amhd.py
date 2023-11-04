import glob
import os
import shutil
import xlrd
from datetime import datetime, timedelta
from os.path import dirname


class MAZANO_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'mazano_amhd'
        self.ADAPTER_TOKEN = '862f17eb1a572858bcdd44c501ed75e0f157800d6d5ab1d61502d01a3c508e92'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'mazano_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '*xls'
        self.DATA = None
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT)
        # print(files)
        self.DATA = max(files, key=os.path.getmtime)
        # if self.DATA.endswith('.xls'):
        #     os.rename(self.DATA, self.DATA + 'x')
        #     self.DATA += 'x'
        print(self.DATA)

    def get_data(self):
        self.scan_file()
        dataframe = xlrd.open_workbook(self.DATA)
        sheet = dataframe[0]
        orders = {}
        nRows = sheet.nrows
        now = datetime.now() - timedelta(days=1)
        # Iterate the loop to read the cell values
        for row in range(1, nRows - 1):
            try:
                code = f"{now.strftime('%d%m%y')}-{len(list(self.ORDERS.keys())) + 1}"
                # print(sheet[row][2].value)
                p_code = sheet[row][1].value
                name = sheet[row][2].value
                qty = float(sheet[row][4].value)
                price = float(sheet[row][5].value)
                discount = float(sheet[row][7].value) + float(sheet[row][8].value)
                vat = float(sheet[row][9].value)
                total = float(sheet[row][10].value)
                print(qty)
                self.ORDERS.update({code: {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': f"{now.strftime('%Y-%m-%d')} 14:00:00",
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
        try:
            shutil.move(self.DATA, f"{self.FULL_PATH}bak")
        except:
            pass


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    # MAZANO_AMHD().get_data()
