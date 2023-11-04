import glob
import os
import shutil
from concurrent import futures

import gspread
import xlrd
from datetime import datetime, timedelta
from os.path import dirname
import openpyxl
from oauth2client.service_account import ServiceAccountCredentials


def a2n(alphabet):
    num = 0
    for idx, _ in enumerate(alphabet):
        num += idx * 26 + ord(_) - 65
    return num


JSON_CRED = {
    "type": "service_account",
    "project_id": "kt365-387014",
    "private_key_id": "9eb19ad641f9d39c1088f931f3c43954e68b2367",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUMuYltO1xyWoW\nNfXavlO02Ch3PSbAseVuUhcnzRPhVTkXqU8UiQYStUuhgcwY0KIypbftw3qRUYrd\nvgub++VqKiEHp2S2/1MYt9SYXVbmTEYmoVO5S7yWQFfXAvrDOPkAwyG3UQtUG2Ve\nF7P+jcUGU6WWLOZih7/WtNklEFi4BmVKaO564NubGtC5qRLlaFVP7DVHCcoghCqK\n4cnX5NHN3F854la3gyZDsm7j8fe/p9RAW4Xv1Hia4AjASJ9BiStkYgmyC7OBCxQM\nOcgI+SVtCiKyH/qnPB+y7v4QcxxvroRNHumCG30bdySHVqUvjpFH46TFQFkZCm2+\nv4hJylYrAgMBAAECggEAKR1t6Gwnq/fbLMpPqR5Ajt2hbGNUywUPx+mSbwJgT5Wb\nP0tDm0jgnHQbxXUDMKdBOJftTVN8P7DFu/srsVzTKv8BJuRz9qkjXqoxmwvaPg5P\nMAx18+RlL7IuLIKxG1RFEMcSJY+gevcWymH9F9QxIy41tFJEoHVU7bZCwBum4XbI\nnJkEr40SF7CoN+8VJvvccZc+BF3ak00SJkxmXMsmvE3PMbOsfdlMNo9mP9f2FpJP\nV2OIOJKBFSJ+9Va++yNZHdl/l+B5Rcfw40AUuY7OJMxRwHVMoNf/PSnZtuGanGzK\nzpC/avLHPA7HbxetFtfbUp64mukPQI5Qas98lNj0sQKBgQDK3FvIhCUZ5j/7A3A8\nKruUKJH7xh/+8OuFIzwnE7URaF9BwdJqnGJ8AvSVJ0Xv3XTTkbyLjeWX9rcJ876o\nbFVkdzRdfZtDM8Ro9tNJAs3unM5jEYuaAKipIGpLjq8aIR8B2zOsz8ZNM57NLKTr\n7ftygxPFmo2TYSlfj6biANrE7QKBgQC7BPbphmhheVfAqw1t6vRYNc2EGqrJghv2\nbeQHR51iS1lNkprGb1s1Tr4QfXqG55J3IEocM25jutWrXTMWQr0qLDDycahRzSHa\nqCCFBvbBuxtp14EhEGQ1wq8tjffqHgWJqbWmPlcSPd9x04MPeVFO/+srX0b5gmjw\nxPayjs58dwKBgQCKHkCLpJVSLfeP40ZuYLX4aSsD3mB4hvYEXvocrQlSQdrhfaLT\nHYjcYHLAfs3aQ9DAH/Dcn48byUnUh9Ve/OujDJplsRieR8fJo4w1oKgvdyn6P77p\n6trq0/wrV4mW48glzmY/mfOtKqFLlsLvM8hIrkAvAUy1dKjjvH3mUKii/QKBgDvk\nbx6CSNNOhOfS384fvHizYkm4MJGv9TyKHMioCqL79nF9TcvWxaLgwMWPKboiVymH\nUbSOU//kSaFDi6TJYsMqu9Ioy/rGct0PkrqHbGbGgRT4SwZHtY/x9R/lo0t6qdNY\nYjAHLuNMpU5Sqlo+Q+fE1Y9iR9yIAwt4SHkOetopAoGAJ+zARDsoxKdBNH3nMmU6\nsF/I9ItT82Liun8beId5+AMqbFlEOmwWChtATPsa42c5rKnvtBpNDwavgD+0FCNW\nq8aZ2KhbN1Z0Fjp0aLMhxbOLTtwk0DDpNDqqRwp3D3BZHX/BbpAScJWVmmtEHG+r\n2NKVg7C/T4EkMflIf8AEUlA=\n-----END PRIVATE KEY-----\n",
    "client_email": "kt365service@kt365-387014.iam.gserviceaccount.com",
    "client_id": "109188131360468428010",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kt365service%40kt365-387014.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class DREAM_KIDS_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'dreamkids_amhd'
        self.ADAPTER_TOKEN = 'ff1d7b570e33a053cffe09ea00365d25ac5baa0652c783cf2f35bbd47f87b130'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'dreamkids_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '*{}*xls'
        self.DATA = None
        self.PM = {
            'CASH': 'CASH',
            'PAID - IN UNIONPAY POS': 'UNIONPAY',
            'MOMO': 'MOMO'
        }
        self.SHEET = '194j9p4EOevSlkasJlqxfN6DXj5e9Ixk2Au0q1h8l8fI'

    def scan_file(self, TYPE):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT.format(TYPE))
        # print(files)
        return max(files, key=os.path.getmtime)
        # if self.DATA.endswith('.xls'):
        #     os.rename(self.DATA, self.DATA + 'x')
        #     self.DATA += 'x'
        # print(self.DATA)

    def get_data_ve(self):
        # self.scan_file('G')
        DATA = self.scan_file('V')
        # self.scan_file('O')
        dataframe = xlrd.open_workbook(DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        # Iterate the loop to read the cell values
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][a2n('AI')].value
                # print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'VE_{code}'
                pur_date = raw[row][a2n('A')].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][a2n('Q')].value.replace(',', ''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][a2n('R')].value.replace(',', ''))
                    deposit = raw[row][a2n('S')].value.replace(',', '').strip()
                    if not deposit: deposit = 0
                    total -= deposit
                except:
                    total = 0
                # print(total)
                try:
                    vat = float(raw[row][a2n('O')].value.replace(',', ''))
                except:
                    vat = 0
                try:
                    price = float(raw[row][a2n('L')].value.replace(',', ''))
                except:
                    price = 0
                ods = {
                    'Code': str(raw[row][a2n('K')].value).strip(),
                    'Name': str(raw[row][a2n('K')].value).strip(),
                    'Price': price,
                    'Quantity': int(raw[row][a2n('M')].value)
                }
                pd = str(raw[row][a2n('X')].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    if name:
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': float(pd[1].strip().split(' ')[0].replace(',', ''))
                        }
                    else:
                        pms = {'Name': 'CASH', 'Value': 0}
                if orders.get(code) is None:
                    orders.update({code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': [ods],
                        'PaymentMethods': []
                    }})
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                else:
                    orders[code]['OrderDetails'].append(ods)
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                    # print(ods)
                    # print(type(orders[code]['OrderDetails']))
                    # print(orders[code]['OrderDetails'].append(ods))
                    orders[code].update({
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': orders[code]['Discount'] + discount,
                        # 'OrderDetails': orders[code]['OrderDetails'].append(ods),
                        # 'PaymentMethods': orders[code]['PaymentMethods'].append(pms)
                    })
                # print(orders[code])
            except Exception as e:
                print(91, e)
        for k, v in orders.items():
            # print(k)
            # if v.get('OrderDetails') is None:
            if len(v.get('OrderDetails')) == 0:
                print(v)
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                print(v)
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            # print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        print('ve', f'{self.FULL_PATH}bak/{name}')
        if os.path.exists(f'{self.FULL_PATH}bak/{name}'):
            os.remove(f'{self.FULL_PATH}bak/{name}')
        try:
            shutil.move(DATA, f"{self.FULL_PATH}bak")
        except Exception as e:
            print(e)
            pass

    def get_data_deposit(self):
        DATA = self.scan_file('D')
        dataframe = xlrd.open_workbook(DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][a2n('Y')].value
                print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'DEPOSIT_{code}'
                pur_date = raw[row][a2n('A')].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][a2n('S')].value.replace(',', ''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][a2n('O')].value.replace(',', ''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][a2n('N')].value.replace(',', ''))
                except:
                    vat = 0
                ods = {
                    'Code': str(raw[row][a2n('J')].value).strip(),
                    'Name': str(raw[row][a2n('J')].value).strip(),
                    'Price': float(raw[row][a2n('L')].value.replace(',', '')),
                    'Quantity': int(raw[row][a2n('K')].value)
                }
                pd = str(raw[row][a2n('U')].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    pms = {
                        'Name': name is not None and name or pd[0].strip().upper(),
                        'Value': float(pd[1].strip().split(' ')[0].replace(',', ''))
                    }
                if orders.get(code) is None:
                    orders.update({code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': [ods],
                        'PaymentMethods': []
                    }})
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                else:
                    orders[code]['OrderDetails'].append(ods)
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                    # print(ods)
                    # print(type(orders[code]['OrderDetails']))
                    # print(orders[code]['OrderDetails'].append(ods))
                    orders[code].update({
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': orders[code]['Discount'] + discount,
                        # 'OrderDetails': orders[code]['OrderDetails'].append(ods),
                        # 'PaymentMethods': orders[code]['PaymentMethods'].append(pms)
                    })
                print(orders[code])
            except Exception as e:
                print(91, e)
                # submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))

        for k, v in orders.items():
            # print(k)
            if len(v.get('OrderDetails')) == 0:
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            # print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        # print(f'{self.FULL_PATH}bak/{name}')
        if os.path.exists(f'{self.FULL_PATH}bak/{name}'):
            os.remove(f'{self.FULL_PATH}bak/{name}')
        try:
            shutil.move(DATA, f"{self.FULL_PATH}bak")
        except:
            pass

    def get_data_miceslanous(self):
        DATA = self.scan_file('M')
        dataframe = xlrd.open_workbook(DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        # Iterate the loop to read the cell values
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][a2n('AF')].value
                # print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'MICESLANOUS_{code}'
                pur_date = raw[row][a2n('A')].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][a2n('Q')].value.replace(',', ''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][a2n('R')].value.replace(',', ''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][a2n('O')].value.replace(',', ''))
                except:
                    vat = 0
                try:
                    price = float(raw[row][a2n('L')].value.replace(',', ''))
                except:
                    price = 0
                ods = {
                    'Code': str(raw[row][a2n('K')].value).strip(),
                    'Name': str(raw[row][a2n('K')].value).strip(),
                    'Price': price,
                    'Quantity': int(raw[row][a2n('M')].value)
                }
                pd = str(raw[row][a2n('X')].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    pms = {
                        'Name': name is not None and name or pd[0].strip().upper(),
                        'Value': float(pd[1].strip().split(' ')[0].replace(',', ''))
                    }
                if orders.get(code) is None:
                    orders.update({code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': [ods],
                        'PaymentMethods': []
                    }})
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                else:
                    orders[code]['OrderDetails'].append(ods)
                    if len(pd) >= 2:
                        orders[code]['PaymentMethods'].append(pms)
                    # print(ods)
                    # print(type(orders[code]['OrderDetails']))
                    # print(orders[code]['OrderDetails'].append(ods))
                    orders[code].update({
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': orders[code]['Discount'] + discount,
                        # 'OrderDetails': orders[code]['OrderDetails'].append(ods),
                        # 'PaymentMethods': orders[code]['PaymentMethods'].append(pms)
                    })
                # print(orders[code])
            except Exception as e:
                print(91, e)
        for k, v in orders.items():
            # print(k)
            # if v.get('OrderDetails') is None:
            if len(v.get('OrderDetails')) == 0:
                # print(v)
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                # print(v)
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            # print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        if os.path.exists(f'{self.FULL_PATH}bak/{name}'):
            os.remove(f'{self.FULL_PATH}bak/{name}')
        try:
            shutil.move(DATA, f"{self.FULL_PATH}bak")
        except:
            pass

    def get_data_drive(self):
        ord = []
        try:
            cred = ServiceAccountCredentials.from_json_keyfile_dict(JSON_CRED, SCOPE)
            self.GS = gspread.authorize(cred)
            ws = self.GS.open_by_key(self.SHEET).worksheet('Sheet1')
            for row, rec in enumerate(ws.get_all_records()):
                pms = []
                date = rec['Ngày'].strip()
                if not date: continue
                if rec['Done'].strip(): continue

                pur_date = datetime.strptime(date, '%d-%m-%Y')
                code = pur_date.strftime("%Y%m%d")
                total = int(rec['Tổng doanh thu'].split()[0].replace(',', ''))
                vat = int(rec['VAT'].split()[0].replace(',', ''))
                cash = int(rec['Tiền mặt'].split()[0].replace(',', ''))
                payoo = int(rec['Payoo'].split()[0].replace(',', ''))
                okara = int(rec['Okara Online'].split()[0].replace(',', ''))
                if cash != 0:
                    pms.append({'Name': 'CASH', 'Value': cash})
                if payoo != 0:
                    pms.append({'Name': 'PAYOO', 'Value': payoo})
                if okara != 0:
                    pms.append({'Name': 'OKARA', 'Value': okara})
                count = rec["Số đơn hàng"]
                for i in range(1, count):
                    ord.append({
                        'Code': f'OKARA_{code}_{i}',
                        'Status': 2,
                        'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'Discount': 0,
                        'PaymentMethods': [{'Name': 'CASH', 'Value': total}],
                        'OrderDetails': []
                    })
                ord.append({
                    'Code': f'OKARA_{code}_{count}',
                    'Status': 2,
                    'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': 0,
                    'PaymentMethods': pms,
                    'OrderDetails': []
                })
                ws.update_cell(row=row + 2, col=9, value=datetime.now().strftime('%y-%m-%d %H:%M:%S'))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        for _ in ord:
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)

    def get_data(self):
        with futures.ThreadPoolExecutor(max_workers=3) as mt:
            thread = [
                mt.submit(self.get_data_deposit),
                mt.submit(self.get_data_ve),
                mt.submit(self.get_data_miceslanous),
                mt.submit(self.get_data_drive),
            ]
            futures.as_completed(thread)


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    # DREAM_KIDS_AMHD().get_data()
