import glob
import os
import random
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname
import xlrd
from unidecode import unidecode


class AM082(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'dookki_amhd'
        self.ADAPTER_TOKEN = '781c49ce25a9a56d3c1be92eb8a6da9534e64ed7677c4c1eeeebdda04662cc3a'
        self.FOLDER = '138_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xlsx'
        self.ORDERS = None
        self.PAYMENT= {
            'TIEN MAT': 'CASH',
            'THE TIN DUNG': 'CARD'
        }

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        def get_value(value):
            try:
                # print(value, type(value))
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            # print(DATA)
            idx = DATA.rindex('/')
            name = DATA[idx + 1:].split('.')[0]
            name = datetime.strptime(name, '%d%m%Y')
            orders = {}
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            # current = None
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                # print(rec)
                try:
                    code = rec.get('INVOICE NO').value.strip()
                    if not len(code):
                        continue
                except:
                    continue
                # print(code)
                try:
                    pur_date = rec.get('T.T').value
                    pur_date = xlrd.xldate_as_datetime(pur_date, sheet.datemode)
                    pur_date = pur_date.replace(year=name.year,
                                                month=name.month,
                                                day=name.day)
                    if pur_date.hour < 10:
                        pur_date = pur_date + timedelta(hours=12)
                    # print(pur_date)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    continue
                # break
            # #     # print(pur_date, code, type(code))
                total = get_value(rec.get('THANH TOAN').value)
            # #     # print(code, total)
                discount = get_value(rec.get('TONG GIAM GIA').value)
                pms = rec.get('LOAI T.T').value.upper()
                if self.PAYMENT.get(pms):
                    pms = [{'Name': self.PAYMENT[pms], 'Value': total}]
                else:
                    pms = [{'Name': pms, 'Value': total}]
            #     discount += get_value(rec.get('TONG TIEN THE MENH GIA').value)
            #     discount += get_value(rec.get('TIEN CK VOUCHER').value)
            #     discount += get_value(rec.get('TIEN CK VOUCHER GIAM GIA TOAN DON').value)
            #     discount += get_value(rec.get('CHIET KHAU C-POINT').value)
            #     cash = get_value(rec.get('TONG TIEN THANH TOAN TIEN MAT').value)
            #     card = get_value(rec.get('TONG TIEN THE QT HOP TAC DOI TAC').value)
            #     bank = get_value(rec.get('TONG TIEN THANH TOAN NGAN HANG').value)
            #     other = get_value(rec.get('THANH TOAN KHAC').value)
            #     # voucher = get_value(rec.get('TIEN CK VOUCHER').value)
            #     # voucher += get_value(rec.get('TONG TIEN THE MENH GIA').value)
                if orders.get(code) is None:
                    orders.update({
                        code: {
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pur_date,
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': [{'ProductId': 0}],
                            'PaymentMethods': pms
                        }
                    })
                else:
                    orders[code]['Total'] += total
                    orders[code]['TotalPayment'] += total
                    orders[code]['Discount'] += discount
                    orders[code]['PaymentMethods'].extend(pms)
                    # orders[code]['VOUCHER'] += voucher
            #
            # # print(self.ORDERS)
            for _, order in orders.items():
                # print(order)
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                for _ in order['PaymentMethods']:
                    if _['Value'] <= 0:
                        pm = {
                            'Code': f'{order["Code"]}-{_["Name"]}',
                            'OrderCode': order["Code"],
                            'Amount': _["Value"],
                            'TransDate': order["PurchaseDate"],
                            'AccountId': _['Name']
                        }
                        submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
            self.backup(DATA)
            # break

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
