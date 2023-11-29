import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import openpyxl


class AM067(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'yves_rocher_amhd'
        self.ADAPTER_TOKEN = '62f862418ca872e0c98bfaa0133eef4f0d9c550ad454fe4a2a2e4d934414cf00'
        self.FOLDER = 'yvesrocher_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*{self.DATE.strftime("%d.%m.%Y")}*xlsx'
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

        # print(self.DATA)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        dataframe = openpyxl.load_workbook(DATA, data_only=True)

        sheet = dataframe['Dailysale']
        orders = {}
        raw = [tuple(r) for r in sheet.iter_rows(values_only=True)]
        # print(raw[0], type(raw[0]))
        for _ in raw[1:]:
            row = dict(map(lambda i, j: (i, j), raw[0], _))
            # print(row)
            code = row.get('Receipt_number')
            # print(code)
            if code is None: continue
            code = str(code).strip()
            if len(code) == 0: continue

            pur_date = str(row.get('Receipt_date')).split()[0] + str(row.get('Transaction_time'))
            # print(pur_date)
            pur_date = datetime.strptime(pur_date, '%Y-%m-%d%H:%M:%S')
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(pur_date)
            ods = [{
                'Code': row.get('Item_number'),
                'Name': row.get('Item_Name'),
                'Price': row.get('Price_after_dics___Inl_VAT_'),
                'Quantity': row.get('Quantity_')
            }]
            vat = round(row.get('VAT_amount_'), 0)
            discount = row.get('Discount_amount_')
            total = row.get('Total_sale__before_disc__inl_VAT_')

            if not orders.get(code):
                try:
                    discount += row.get('Gift_Voucher')
                    discount += row.get('Free_Voucher')
                except:
                    pass
                try:
                    cash = row.get('Cash')
                except:
                    cash = 0
                try:
                    card = row.get('Card')
                except:
                    card = 0
                try:
                    customer = row.get('Customer_Account')
                except:
                    customer = 0
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

# if __name__:
#     # # import sys
#     #
#     # PATH = dirname(dirname(__file__))
#     # # PATH = dirname(dirname(dirname(__file__)))
#     # # print(PATH)
#     # sys.path.append(PATH)
#     from schedule.pos_api.adapter import submit_error, submit_order
# for _ in range(22, 0, -1):
# YVES_ROCHER_AMHD().get_data()
