import glob
import hashlib
import os
import shutil
import sys
from concurrent import futures

import openpyxl
import xlrd
from datetime import datetime, timedelta
from os.path import dirname


class AM169(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        # self.ADAPTER_RETAILER = 'dreamkids_amhd'
        # self.ADAPTER_TOKEN = 'ff1d7b570e33a053cffe09ea00365d25ac5baa0652c783cf2f35bbd47f87b130'
        self.ADAPTER_RETAILER = 'test_dk'
        self.ADAPTER_TOKEN = '2370aa71a74dfb618107f51b7e5879c2462e1089bafef982ce1fa224035c2ba9'
        self.FOLDER = 'dreamkids_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=2)
        self.PM = {
            'CASH': 'CASH',
            'PAID - IN UNIONPAY POS': 'UNIONPAY',
            'MOMO': 'MOMO'
        }

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data_ve(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file(f'*V*{self.DATE.strftime("%d.%m.%Y")}.xls')
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='VE_NOT_FOUND')
            return
        print(DATA)
        # try:
        dataframe = xlrd.open_workbook(DATA)
        # except Exception as e:
        #     print(e)
        try:
            # print(dataframe)
            raw = list(dataframe.sheets())[0]
            orders = {}
            nRows = raw.nrows
            # print(52, nRows)
            cols = {}
            for i in range(raw.ncols):
                # print(55, list(raw[1]))
                if str(raw.row(1)[i].value).strip():
                    cols.update({str(raw.row(1)[i].value).strip().upper(): i})
            # print(57, cols)
            for r in range(2, nRows - 1):
                try:
                    pm = []
                    # code = raw.row(row)[cols['RECEIPT NUM.']].value
                    # if code is None: continue
                    # code = str(code).strip()
                    # code = code.replace("'", '').strip()
                    # if len(code) == 0: continue
                    pur_date = raw.row(r)[cols['DATE']].value
                    try:
                        pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')

                    except:
                        continue
                    code = f'VE_{pur_date.strftime("%Y%m%d")}_{len(orders.keys()) + 1:04d}'
                    # print(code)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        discount = float(raw.row(r)[cols['FREE AMOUNT']].value)
                    except:
                        discount = 0
                    try:
                        total = float(raw.row(r)[cols['RECEIVED']].value)
                        # deposit = raw.row(r)[cols['CONSUMPTION DEPOSIT']].value.replace(',', '').strip()
                        # if not deposit: deposit = 0
                        # total -= deposit
                    except:
                        total = 0
                    try:
                        vat = float(raw.row(r)[cols['TAX']].value)
                    except:
                        vat = 0
                    try:
                        price = float(raw.row(r)[cols['PRICE']].value)
                    except:
                        price = 0
                    ods = {
                        'Code': str(raw.row(r)[cols['PACKAGE NAME']].value).strip(),
                        'Name': str(raw.row(r)[cols['PACKAGE NAME']].value).strip(),
                        'Price': price,
                        'Quantity': int(raw.row(r)[cols['QTY']].value)
                    }
                    pm = raw.row(r)[cols['PAYMENT DETAILS']].value
                    # if 'E-Cash' in pm:
                    #     print(pm)
                    # print(raw.row(r)[cols['PAYMENT DETAILS']].value)
                    pd = str(raw.row(r)[cols['PAYMENT DETAILS']].value).strip().split(':')
                    # print(pd)
                    if len(pd) >= 2:
                        name = self.PM.get(pd[0].strip().upper())
                        # val = pd[1].strip().split('(')[0].strip()
                        # if name:
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': float(pd[1].strip().split('(')[0].replace(',', ''))
                        }
                        # else:
                        #     pms = {'Name': 'CASH', 'Value': 0}
                    # if 'E-Cash' in pm:
                    #     print(pms)
                    md5 = hashlib.md5(pur_date.encode('utf-8')).hexdigest()
                    # print(md5)
                    if orders.get(md5) is None:
                        orders.update({md5: {
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
                        # print(pd)
                        if len(pd) >= 2:
                            orders[md5]['PaymentMethods'].append(pms)
                        # print(code, orders[md5].get('PaymentMethods'))
                    else:
                        orders[md5]['OrderDetails'].append(ods)
                        if len(pd) >= 2:
                            orders[md5]['PaymentMethods'].append(pms)
                        orders[md5].update({
                            'Total': orders[md5]['Total'] + total,
                            'TotalPayment': orders[md5]['Total'] + total,
                            'VAT': orders[md5]['VAT'] + vat,
                            'Discount': orders[md5]['Discount'] + discount,
                        })
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            for k, v in orders.items():
                if len(v.get('OrderDetails')) == 0:
                    # print('OrderDetails')
                    v.update({'OrderDetails': []})
                if len(v.get('PaymentMethods')) == 0:
                    # print('PaymentMethods', v['Code'], v['PurchaseDate'])
                    v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
                # print(v)
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            self.backup(DATA)
        except Exception as e:
            print(e)

    def get_data_deposit(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file(f'*D*{self.DATE.strftime("%d.%m.%Y")}.xls')
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='DEPOSIT_NOT_FOUND')
            return
        dataframe = xlrd.open_workbook(DATA)
        raw = dataframe[0]
        orders = {}
        nRows = raw.nrows
        cols = {}
        for i in range(raw.ncols):
            if str(raw[1][i].value).strip():
                cols.update({str(raw[1][i].value).strip().upper(): i})
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][cols['RECEIPT NUM.']].value
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'DEPOSIT_{code}'
                pur_date = raw[row][cols['DATE']].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][cols['FREE AMOUNT']].value.replace(',', ''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][cols['RECEIVED']].value.replace(',', ''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][cols['TAX']].value.replace(',', ''))
                except:
                    vat = 0
                ods = {
                    'Code': str(raw[row][cols['PACKAGE NAME']].value).strip(),
                    'Name': str(raw[row][cols['PACKAGE NAME']].value).strip(),
                    'Price': float(raw[row][cols['PRICE']].value.replace(',', '')),
                    'Quantity': int(raw[row][cols['QTY']].value)
                }
                pd = str(raw[row][cols['PAYMENT DETAILS']].value).strip().split(':')
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
                    orders[code].update({
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': orders[code]['Discount'] + discount,
                    })
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))

        for k, v in orders.items():
            if len(v.get('OrderDetails')) == 0:
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        self.backup(DATA)

    def get_data_miceslanous(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file(f'*M*{self.DATE.strftime("%d")}*.xls')
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='MISC_NOT_FOUND')
            return
        dataframe = xlrd.open_workbook(DATA)
        raw = dataframe[0]
        orders = {}
        nRows = raw.nrows
        cols = {}
        for i in range(raw.ncols):
            if str(raw[1][i].value).strip():
                cols.update({str(raw[1][i].value).strip().upper(): i})
        for row in range(2, nRows - 1):
            try:
                pm = []
                code = raw[row][cols['RECEIPT NUM.']].value
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                code = f'MICESLANOUS_{code}'
                pur_date = raw[row][cols['DATE']].value
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                try:
                    discount = float(raw[row][cols['FREE AMOUNT']].value.replace(',', ''))
                except:
                    discount = 0
                try:
                    total = float(raw[row][cols['RECEIVED']].value.replace(',', ''))
                except:
                    total = 0
                try:
                    vat = float(raw[row][cols['TAX']].value.replace(',', ''))
                except:
                    vat = 0
                try:
                    price = float(raw[row][cols['PRICE']].value.replace(',', ''))
                except:
                    price = 0
                ods = {
                    'Code': str(raw[row][cols['PACKAGE NAME']].value).strip(),
                    'Name': str(raw[row][cols['PACKAGE NAME']].value).strip(),
                    'Price': price,
                    'Quantity': int(raw[row][cols['QTY']].value)
                }
                pd = str(raw[row][cols['PAYMENT DETAILS']].value).strip().split(':')
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
                    orders[code].update({
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': orders[code]['Discount'] + discount,
                    })
            except Exception as e:
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        for k, v in orders.items():
            if len(v.get('OrderDetails')) == 0:
                v.update({'OrderDetails': []})
            if len(v.get('PaymentMethods')) == 0:
                v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        self.backup(DATA)

    def get_data(self):
        with futures.ThreadPoolExecutor(max_workers=3) as mt:
            thread = [
                mt.submit(self.get_data_deposit),
                mt.submit(self.get_data_ve),
                mt.submit(self.get_data_miceslanous)
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

# if __name__:
# import sys
#
# PATH = dirname(dirname(__file__))
# # PATH = dirname(dirname(dirname(__file__)))
# # print(PATH)
# sys.path.append(PATH)
# from schedule.pos_api.adapter import submit_error, submit_order

# DREAM_KIDS_AMHD().get_data()
