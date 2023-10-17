import glob
import os
import shutil
from concurrent import futures

import xlrd
from datetime import datetime, timedelta
from os.path import dirname
import openpyxl



class DREAM_KIDS_AMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'dreamkids_amhd'
        self.ADAPTER_TOKEN = 'ff1d7b570e33a053cffe09ea00365d25ac5baa0652c783cf2f35bbd47f87b130'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'dreamkids_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '{}*xls'
        self.DATA = None
        self.PM = {
            'CASH': 'CASH',
            'PAID - IN UNIONPAY POS': 'UNIONPAY',
            'MOMO': 'MOMO'
        }


    def scan_file(self, TYPE):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT.format(TYPE))
        # print(files)
        self.DATA = max(files, key=  os.path.getmtime)
        # if self.DATA.endswith('.xls'):
        #     os.rename(self.DATA, self.DATA + 'x')
        #     self.DATA += 'x'
        print(self.DATA)

    def get_data_ve(self):
        # self.scan_file('G')
        self.scan_file('V')
        # self.scan_file('O')
        dataframe = xlrd.open_workbook(self.DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        # Iterate the loop to read the cell values
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][34].value
                # print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'VE_{code}'
                pur_date = raw[row][0].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][16].value.replace(',',''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][17].value.replace(',',''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][14].value.replace(',',''))
                except:
                    vat = 0
                try:
                    price = float(raw[row][11].value.replace(',', ''))
                except:
                    price = 0
                ods = {
                    'Code': str(raw[row][10].value).strip(),
                    'Name': str(raw[row][10].value).strip(),
                    'Price': price,
                    'Quantity': int(raw[row][12].value)
                }
                pd = str(raw[row][23].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    pms = {
                        'Name': name is not None and name or pd[0].strip().upper(),
                        'Value': float(pd[1].strip().split(' ')[0].replace(',',''))
                    }
                if orders.get(code) is None:
                    orders.update({code:{
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
                print(91,e)
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
        try:
            shutil.move(self.DATA, f"{self.FULL_PATH}bak")
        except:
            pass
    def get_data_game(self):
        self.scan_file('G')
        dataframe = xlrd.open_workbook(self.DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][24].value
                # print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'GAME_{code}'
                pur_date = raw[row][0].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][18].value.replace(',',''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][14].value.replace(',',''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][13].value.replace(',',''))
                except:
                    vat = 0
                ods = {
                    'Code': str(raw[row][9].value).strip(),
                    'Name': str(raw[row][9].value).strip(),
                    'Price': float(raw[row][11].value.replace(',','')),
                    'Quantity': int(raw[row][10].value)
                }
                pd = str(raw[row][20].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    pms = {
                        'Name': name is not None and name or pd[0].strip().upper(),
                        'Value': float(pd[1].strip().split(' ')[0].replace(',',''))
                    }
                if orders.get(code) is None:
                    orders.update({code:{
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
                print(91,e)
                # submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))

        for k, v in orders.items():
            # print(k)
            if len(v.get('OrderDetails')) == 0:
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            # print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        try:
            shutil.move(self.DATA, f"{self.FULL_PATH}bak")
        except:
            pass
    def get_data_other(self):
        self.scan_file('O')
        dataframe = xlrd.open_workbook(self.DATA)
        raw = dataframe['Sheet']
        orders = {}

        nRows = raw.nrows
        # Iterate the loop to read the cell values
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][30].value
                # print(code)
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'OTHER_{code}'
                pur_date = raw[row][0].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                # now = datetime.now() - timedelta(days=1)
                # # if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][15].value.replace(',',''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][16].value.replace(',',''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][13].value.replace(',',''))
                except:
                    vat = 0
                try:
                    price = float(raw[row][10].value.replace(',', ''))
                except:
                    price = 0
                ods = {
                    'Code': str(raw[row][9].value).strip(),
                    'Name': str(raw[row][9].value).strip(),
                    'Price': price,
                    'Quantity': int(raw[row][11].value)
                }
                pd = str(raw[row][22].value).strip().split(':')
                if len(pd) >= 2:
                    name = self.PM.get(pd[0].strip().upper())
                    pms = {
                        'Name': name is not None and name or pd[0].strip().upper(),
                        'Value': float(pd[1].strip().split(' ')[0].replace(',',''))
                    }
                if orders.get(code) is None:
                    orders.update({code:{
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
                print(91,e)
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
        try:
            shutil.move(self.DATA, f"{self.FULL_PATH}bak")
        except:
            pass
    def get_data(self):
        with futures.ThreadPoolExecutor(max_workers=3) as mt:
            thread = [
                mt.submit(self.get_data_game),
                mt.submit(self.get_data_ve),
                mt.submit(self.get_data_other),
            ]
            futures.as_completed(thread)
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    # DREAM_KIDS_AMHD().get_data()