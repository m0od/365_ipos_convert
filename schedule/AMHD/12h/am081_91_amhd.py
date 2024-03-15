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


class AM081(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'canifa_amhd'
        self.ADAPTER_TOKEN = '4fc881a6fb606d2a7e313dd7e25245f8a2b323cacb6207f7ae9d9a11c5cec99f'
        self.FOLDER = '91_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xlsx'
        self.ORDERS = None

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
            orders = {}
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(6):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            # current = None
            for i in range(7, nRows):
                rec = dict(zip(headers, raw.row(i)))
                # print(rec)
                try:
                    code = rec.get('SO CHUNG TU').value.strip()
                    if not len(code):
                        continue
                    code = code.replace('Order', '').strip()
                    # print(code)
                    if not len(code):
                        continue
                except:
                    continue
                # print(code)
                try:
                    pur_date = rec.get('NGAY').value
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y')
                    pur_hour = rec.get('GIO').value
                    pur_hour = datetime.strptime(pur_hour, '%H:%M:%S')
                    pur_date = pur_date + timedelta(hours=pur_hour.hour,
                                                    minutes=pur_hour.minute,
                                                    seconds=pur_hour.second)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    # print(pur_date)
                except:
                    continue
            #     # print(pur_date, code, type(code))
                total = get_value(rec.get('DOANH SO TINH TIEN THUE').value)
            #     # print(code, total)
                discount = get_value(rec.get('TIEN CK PROMOTION').value)
                discount += get_value(rec.get('TIEN CK LOYALTY').value)
                discount += get_value(rec.get('TONG TIEN THE MENH GIA').value)
                discount += get_value(rec.get('TIEN CK VOUCHER').value)
                discount += get_value(rec.get('TIEN CK VOUCHER GIAM GIA TOAN DON').value)
                discount += get_value(rec.get('CHIET KHAU C-POINT').value)
                cash = get_value(rec.get('TONG TIEN THANH TOAN TIEN MAT').value)
                card = get_value(rec.get('TONG TIEN THE QT HOP TAC DOI TAC').value)
                bank = get_value(rec.get('TONG TIEN THANH TOAN NGAN HANG').value)
                other = get_value(rec.get('THANH TOAN KHAC').value)
                # voucher = get_value(rec.get('TIEN CK VOUCHER').value)
                # voucher += get_value(rec.get('TONG TIEN THE MENH GIA').value)
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
                            'CASH': cash,
                            'CARD': card,
                            'BANK': bank,
                            'OTHER': other,
                            # 'VOUCHER': voucher
                        }
                    })
                else:
                    orders[code]['Total'] += total
                    orders[code]['TotalPayment'] += total
                    orders[code]['Discount'] += discount
                    orders[code]['CASH'] += cash
                    orders[code]['CARD'] += card
                    orders[code]['BANK'] += bank
                    orders[code]['OTHER'] += other
                    # orders[code]['VOUCHER'] += voucher
            #
            # # print(self.ORDERS)
            for _, order in orders.items():
                pms = [
                    {'Name': 'CASH', 'Value': order['CASH']},
                    {'Name': 'CARD', 'Value': order['CARD']},
                    {'Name': 'BANK', 'Value': order['BANK']},
                    {'Name': 'OTHER', 'Value': order['OTHER']},
                    # {'Name': 'VOUCHER', 'Value': order['VOUCHER']},
                ]
                for pm in pms.copy():
                    if pm['Value'] == 0: pms.remove(pm)
                    order.pop(pm['Name'])
                order.update({'PaymentMethods': pms})
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
