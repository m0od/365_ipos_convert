import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import xlrd


class AM119(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'shooz_amhd'
        self.ADAPTER_TOKEN = '0f01518005cdb6b3817e126de95f13d0599f3885a534d43795db3c047b04f70e'
        self.FOLDER = 'shooz_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*xlsx'
        self.DATA = None
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def rename_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            for _ in files:
                t = os.path.getmtime(_)
                t = datetime.fromtimestamp(t).strftime('%Y%m%d %H:%M:%S')
                os.rename(_, f'{self.FULL_PATH}/{t}.xlsx')
        except:
            return None

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0
        from pos_api.adapter import submit_error, submit_order
        self.rename_file()
        DATA = self.scan_file()
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        ws = xlrd.open_workbook(DATA)
        raw = ws.sheet_by_name('Danh sách đơn hàng')
        nrows = raw.nrows
        orders = {}
        for i in range(1, nrows):
            try:
                pm = []
                code = raw.row(i)[0].value
                if code is None: continue
                code = str(code).strip()
                code = code.replace("'", '').strip()
                if len(code) == 0: continue
                pur_date = raw.row(i)[2].value
                pur_date = datetime.strptime(pur_date, '%d%m%Y%H%M')
                # print(pur_date)
                now = datetime.now() - timedelta(days=1)
                if pur_date.replace(hour=0, minute=0) < now.replace(hour=0, minute=0, second=0, microsecond=0): continue
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total = get_value(raw.row(i)[3].value)
                vat = get_value(raw.row(i)[4].value)
                if orders.get(code) is None:
                    orders.update({code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': 0,
                    }})
                else:
                    orders[code].update({
                        'Code': code,
                        'Status': 2,
                        # 'PurchaseDate': pur_date,
                        'Total': orders[code]['Total'] + total,
                        'TotalPayment': orders[code]['Total'] + total,
                        'VAT': orders[code]['VAT'] + vat,
                        'Discount': 0,
                    })
            except:
                pass
        raw = ws.sheet_by_name('Phương thức thanh toán')
        nrows = raw.nrows
        pms = {}
        for i in range(1, nrows):
            code = raw.row(i)[0].value
            if code is None: continue
            code = str(code).strip()
            code = code.replace("'", '').strip()
            if len(code) == 0: continue
            name = str(raw.row(i)[1].value).strip().upper()
            if name == 'NONE' or name == 'TIỀN MẶT': name = 'CASH'
            value = get_value(raw.row(i)[2].value)
            if pms.get(code) is None:
                pms.update({code: [{'Name': name, 'Value': value}]})
            else:
                pms[code].append({'Name': name, 'Value': value})
        for k, v in pms.items():
            if orders.get(k) is not None:
                orders[k].update({'PaymentMethods': v})
        raw = ws.sheet_by_name('Chi tiết đơn hàng')
        nrows = raw.nrows
        ods = {}
        for i in range(1, nrows):
            code = raw.row(i)[0].value
            if code is None: continue
            code = str(code).strip()
            code = code.replace("'", '').strip()
            if len(code) == 0: continue
            p_code = raw.row(i)[1].value
            p_code = p_code.replace("'", '')
            p_name = raw.row(i)[2].value
            qty = get_value(raw.row(i)[3].value)
            price = get_value(raw.row(i)[5].value)
            if ods.get(code) is None:
                ods[code] = [{
                    'Code': p_code,
                    'Name': p_name,
                    'Price': price,
                    'Quantity': qty
                }]
            else:
                ods[code].append({
                    'Code': p_code,
                    'Name': p_name,
                    'Price': price,
                    'Quantity': qty
                })
        for k, v in ods.items():
            if orders.get(k) is not None:
                orders[k].update({'OrderDetails': v})
        for k, v in orders.items():
            if v.get('OrderDetails') is None:
                v.update({'OrderDetails': [{'ProductId': 0}]})
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

    # def send_zero(self):
    #     from pos_api.adapter import submit_order
    #     order = {
    #         'Code': f'NOBILL_{self.DATE.strftime("%d%m%Y")}',
    #         'Status': 2,
    #         'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
    #         'Total': 0,
    #         'TotalPayment': 0,
    #         'VAT': 0,
    #         'Discount': 0,
    #         'OrderDetails': [{'ProductId': 0}],
    #         'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
    #     }
    #     submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)