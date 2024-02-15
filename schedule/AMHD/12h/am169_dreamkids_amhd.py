import glob
import hashlib
import os
import shutil
import sys
from concurrent import futures
import xlrd
from datetime import datetime, timedelta
from os.path import dirname
from unidecode import unidecode


def get_value(value):
    try:
        # print(value, type(value))
        if type(value) in [float, int]:
            return float(value)
        elif type(value) == str:
            return float(value.replace(',', ''))
    except:
        return 0

class AM169(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'dreamkids_amhd'
        self.ADAPTER_TOKEN = 'ff1d7b570e33a053cffe09ea00365d25ac5baa0652c783cf2f35bbd47f87b130'
        # self.ADAPTER_RETAILER = 'test_dk'
        # self.ADAPTER_TOKEN = '2370aa71a74dfb618107f51b7e5879c2462e1089bafef982ce1fa224035c2ba9'
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
            return glob.glob(f'{self.FULL_PATH}/{EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data_ve(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*V*.xls*')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='VE_NOT_FOUND')
            return
        for DATA in files:
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(1):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            orders = {}
            for i in range(2, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    try:
                        pur_date = rec['DATE'].value
                        pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        continue
                    code = f'VE-{pur_date.strftime("%y%m%d-%H%M%S")}'
                    # print(code)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    discount = get_value(rec['FREE AMOUNT'].value)
                    # print(rec['RECEIVED'].value, type(rec['RECEIVED'].value))
                    total = get_value(rec['RECEIVED'].value)
                    try:
                        total -= get_value(rec['CONSUMPTION DEPOSIT'].value)
                    except:
                        pass
                    vat = get_value(rec['TAX'].value)
                    price = get_value(rec['PRICE'].value)
                    ods = {
                        'Code': str(rec['PACKAGE NAME'].value).strip(),
                        'Name': str(rec['PACKAGE NAME'].value).strip(),
                        'Price': price,
                        'Quantity': get_value(rec['QTY'].value)
                    }
                    pm = rec['PAYMENT DETAILS'].value
                    # if 'E-Cash' in pm:
                    #     print(pm)
                    # print(raw.row(r)[cols['PAYMENT DETAILS']].value)
                    pd = str(rec['PAYMENT DETAILS'].value).strip().split(':')
                    # print(pd)
                    if len(pd) >= 2:
                        name = self.PM.get(pd[0].strip().upper())
                        # val = pd[1].strip().split('(')[0].strip()
                        # if name:
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': get_value(pd[1].strip().split('(')[0].strip())
                        }
                        # else:
                        #     pms = {'Name': 'CASH', 'Value': 0}
                    # if 'E-Cash' in pm:
                    #     print(pms)
                    # md5 = hashlib.md5(pur_date.encode('utf-8')).hexdigest()
                    # print(md5)
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
                        # print(pd)
                        if len(pd) >= 2:
                            orders[code]['PaymentMethods'].append(pms)
                        # print(code, orders[md5].get('PaymentMethods'))
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
                    # print('OrderDetails')
                    v.update({'OrderDetails': [{'ProductId': 0}]})
                if len(v.get('PaymentMethods')) == 0:
                    # print('PaymentMethods', v['Code'], v['PurchaseDate'])
                    v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
                # print(v)
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            self.backup(DATA)
        # except Exception as e:
        # print(e)


    def get_data_deposit(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*D*.xls*')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='DEPOSIT_NOT_FOUND')
            return
        for DATA in files:
            print(DATA)
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(1):
                headers.append(unidecode(str(_.value).upper()))
            print(headers)
            orders = {}
            for i in range(2, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    try:
                        pur_date = rec['DATE'].value
                        pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        continue
                    code = f'DEPOSIT-{pur_date.strftime("%y%m%d-%H%M%S")}'
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    discount = get_value(rec['FREE AMOUNT'].value)
                    total = get_value(rec['RECEIVED'].value)
                    vat = get_value(rec['TAX'].value)
                    ods = {
                        'Code': str(rec['PACKAGE NAME'].value).strip(),
                        'Name': str(rec['PACKAGE NAME'].value).strip(),
                        'Price': get_value(rec['PRICE'].value),
                        'Quantity': get_value(rec['QTY'].value)
                    }
                    # print(ods)
                    pd = str(rec['PAYMENT DETAILS'].value).strip().split(':')
                    if len(pd) >= 2:
                        name = self.PM.get(pd[0].strip().upper())
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': get_value(pd[1].strip().split('(')[0].strip())
                        }
                        # print(pms)
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
                # print(v)
                # break
                if len(v.get('OrderDetails')) == 0:
                    v.update({'OrderDetails': [{'ProductId': 0}]})
                if len(v.get('PaymentMethods')) == 0:
                    v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            self.backup(DATA)


    def get_data_miceslanous(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*M*.xls*')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='MISC_NOT_FOUND')
            return
        for DATA in files:
            print(DATA)
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(1):
                headers.append(unidecode(str(_.value).upper()))
            print(headers)
            orders = {}
            for i in range(2, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    try:
                        pur_date = rec['DATE'].value
                        pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        continue
                    code = f'MICESLANOUS-{pur_date.strftime("%y%m%d-%H%M%S")}'
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    try:
                        discount = get_value(rec['FREE AMOUNT'].value)
                    except:
                        discount = 0
                    total = get_value(rec['RECEIVED'].value)
                    try:
                        total -= get_value(rec['CONSUMPTION DEPOSIT'].value)
                    except:
                        pass
                    vat = get_value(rec['TAX'].value)
                    price = get_value(rec['PRICE'].value)
                    ods = {
                        'Code': str(rec['PACKAGE NAME'].value).strip(),
                        'Name': str(rec['PACKAGE NAME'].value).strip(),
                        'Price': price,
                        'Quantity': get_value(rec['QTY'].value)
                    }
                    pd = str(rec['PAYMENT DETAILS'].value).strip().split(':')
                    if len(pd) >= 2:
                        name = self.PM.get(pd[0].strip().upper())
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': get_value(pd[1].strip().split('(')[0].strip())
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
                # print(v)
                if len(v.get('OrderDetails')) == 0:
                    v.update({'OrderDetails': []})
                if len(v.get('PaymentMethods')) == 0:
                    v.update({'PaymentMethods': [{'NAME': 'CASH', 'Value': 0}]})
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            self.backup(DATA)

    def get_data_coin(self):
        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file(f'*C*.xls*')
        if not len(files):
            submit_error(retailer=self.ADAPTER_RETAILER, reason='COIN_NOT_FOUND')
            return
        for DATA in files:
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            headers = []
            for _ in raw.row(1):
                headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            orders = {}
            for i in range(2, nRows):
                rec = dict(zip(headers, raw.row(i)))
                try:
                    try:
                        pur_date = rec['DATE'].value
                        pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                    except:
                        continue
                    code = f'COIN-{pur_date.strftime("%y%m%d-%H%M%S")}'
                    # print(code)
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    discount = get_value(rec['FREE AMOUNT'].value)
                    total = get_value(rec['RECEIVED'].value)
                    vat = get_value(rec['TAX'].value)
                    price = get_value(rec['PRICE'].value)
                    ods = {
                        'Code': str(rec['PACKAGE NAME'].value).strip(),
                        'Name': str(rec['PACKAGE NAME'].value).strip(),
                        'Price': price,
                        'Quantity': get_value(rec['QTY'].value)
                    }
                    # print(ods)
                    pd = str(rec['PAYMENT DETAILS'].value).strip().split(':')
                    if len(pd) >= 2:
                        name = self.PM.get(pd[0].strip().upper())
                        pms = {
                            'Name': name is not None and name or pd[0].strip().upper(),
                            'Value': float(pd[1].strip().split('(')[0].strip())
                        }
                        # print(pms)
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
        # self.get_data_deposit()
        # self.get_data_miceslanous()
        with futures.ThreadPoolExecutor(max_workers=4) as mt:
            thread = [
                mt.submit(self.get_data_deposit),
                mt.submit(self.get_data_ve),
                mt.submit(self.get_data_miceslanous),
                mt.submit(self.get_data_coin)
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
