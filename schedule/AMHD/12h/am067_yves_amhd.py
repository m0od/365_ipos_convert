import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import xlrd


class AM067(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'yves_rocher_amhd'
        self.ADAPTER_TOKEN = '62f862418ca872e0c98bfaa0133eef4f0d9c550ad454fe4a2a2e4d934414cf00'
        self.FOLDER = 'yvesrocher_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*xlsx'
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        sheet = xlrd.open_workbook(DATA)
        raw = list(sheet.sheets())[0]
        nRows = raw.nrows
        headers = []
        for _ in raw.row(0):
            headers.append(str(_.value))
        orders = {}
        for i in range(1, nRows):
            row = dict(zip(headers, raw.row(i)))
            code = row.get('Receipt_number').value
            if code is None: continue
            code = str(code).strip()
            if len(code) == 0: continue
            pur_date = xlrd.xldate_as_datetime(row.get('Receipt_date').value, sheet.datemode)
            t = xlrd.xldate_as_datetime(row.get('Transaction_time').value, sheet.datemode)
            pur_date = pur_date.replace(hour=t.hour, minute=t.minute, second=t.second)
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(pur_date)
            ods = [{
                'Code': row.get('Item_number').value,
                'Name': row.get('Item_Name').value,
                'Price': get_value(row.get('Price_after_dics___Inl_VAT_').value),
                'Quantity': get_value(row.get('Quantity_').value)
            }]
            vat = get_value(row.get('VAT_amount_').value)
            discount = get_value(row.get('Discount_amount_').value)
            total = get_value(row.get('Total_sale__before_disc__inl_VAT_').value)

            if not orders.get(code):
                discount += get_value(row.get('Gift_Voucher').value)
                discount += get_value(row.get('Free_Voucher').value)
                cash = get_value(row.get('Cash').value)
                card = get_value(row.get('Card').value)
                customer = get_value(row.get('Customer_Account').value)
                pms = []
                if card:
                    pms.append({'Name': 'CARD', 'Value': card})
                if cash:
                    pms.append({'Name': 'CASH', 'Value': cash})
                if customer:
                    pms.append({'Name': 'CUSTOMER ACCOUNT', 'Value': customer})
                orders.update({code: {
                    'Code': code,
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total - discount,
                    'TotalPayment': total - discount,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': ods,
                    'PaymentMethods': pms
                }})
            else:
                orders[code]['OrderDetails'].extend(ods)
                # ods.extend(orders[code]['OrderDetails'])
                orders[code].update({
                    # 'OrderDetails': ods,
                    'Total': total - discount + orders[code]['Total'],
                    'TotalPayment': total - discount + orders[code]['TotalPayment'],
                    'VAT': vat + orders[code]['VAT'],
                    'Discount': discount + orders[code]['Discount'],
                })
        for k, v in orders.items():
            if v.get('OrderDetails') is None:
                v.update({'OrderDetails': []})
            if v.get('PaymentMethods') is None:
                v.update({'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]})
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
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
