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


class AM015(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'fancy_time_amhd'
        self.ADAPTER_TOKEN = 'b75bf5025a61dada8c9cacc3502b68ba6c47ac89cd1e16150999fa5f35bbdfab'
        self.FOLDER = '92_amhd'
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
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            self.ORDERS = {}
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(0):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            current = None
            for i in range(1, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    pur_date = rec.get('NGAY').value
                    pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M:%S')
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    pur_date = None
                try:
                    code = rec.get('ID').value.strip()
                    if not len(code):
                        code = None
                    else:
                        current = code
                except:
                    code = None
                # print(pur_date, code, type(code))
                total = get_value(rec.get('TONG TIEN').value)
                discount = get_value(rec.get('CHIET KHAU').value)
                p_name = rec.get('TEN SAN PHAM').value.strip()
                p_price = get_value(rec.get('GIA BAN').value)
                p_total = get_value(rec.get('DOANH THU SP SAU CHIET KHAU').value)
                p_total += discount
                if p_price == 0:
                    qty = 1
                else:
                    qty = p_total / p_price
                cash = get_value(rec.get('TIEN MAT').value)
                bank = get_value(rec.get('CHUYEN KHOAN').value)
                if rec.get('TAI KHOAN QUET THE').value:
                    card = total - cash - bank
                else:
                    card = 0
                if code is not None:
                    if not self.ORDERS.get(code):
                        self.ORDERS.update({
                            code: {
                                'Code': code,
                                'Status': 2,
                                'PurchaseDate': pur_date,
                                'Total': total,
                                'TotalPayment': total,
                                'VAT': 0,
                                'Discount': discount,
                                'OrderDetails': [{
                                    'Code': unidecode(p_name.upper()),
                                    'Name': p_name,
                                    'Quantity': qty,
                                    'Price': p_price
                                }],
                                'CASH': cash,
                                'BANK': bank,
                                'CARD': card
                            }
                        })
                    else:
                        self.ORDERS[code]['Total'] += total
                        self.ORDERS[code]['TotalPayment'] += total
                        self.ORDERS[code]['Discount'] += discount
                        self.ORDERS[code]['OrderDetails'].extend([{
                            'Code': unidecode(p_name.upper()),
                            'Name': p_name,
                            'Quantity': qty,
                            'Price': p_price
                        }])
                        self.ORDERS[code]['CASH'] += cash
                        self.ORDERS[code]['BANK'] += bank
                        self.ORDERS[code]['CARD'] += card
                else:
                    try:
                        self.ORDERS[current]['Total'] += total
                        self.ORDERS[current]['TotalPayment'] += total
                        self.ORDERS[current]['Discount'] += discount
                        self.ORDERS[current]['OrderDetails'].extend([{
                            'Code': unidecode(p_name.upper()),
                            'Name': p_name,
                            'Quantity': qty,
                            'Price': p_price
                        }])
                        self.ORDERS[current]['CASH'] += cash
                        self.ORDERS[current]['BANK'] += bank
                        self.ORDERS[current]['CARD'] += card
                    except:
                        pass
            # print(self.ORDERS)
            for _, order in self.ORDERS.items():
                pms = [
                    {'Name': 'CASH', 'Value': order['CASH']},
                    {'Name': 'CARD', 'Value': order['CARD']},
                    {'Name': 'BANK', 'Value': order['BANK']},
                ]
                for pm in pms.copy():
                    if pm['Value'] == 0:
                        pms.remove(pm)
                if not len(pms):
                    pms = [{'Name': 'CASH', 'Value': 0}]
                order.update({'PaymentMethods': pms})
                order.pop('CASH')
                order.pop('CARD')
                order.pop('BANK')
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
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
