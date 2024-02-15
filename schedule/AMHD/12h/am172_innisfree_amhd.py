import glob
import os
import shutil
import sys
import xlrd
from datetime import datetime, timedelta
from os.path import dirname


class AM172(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'innisfree_amhd'
        self.ADAPTER_TOKEN = '9efbf2b6aa6337f497c9a060b0fc2e658f27d06af0b514de3d50ba552af7f00a'
        self.FOLDER = 'innisfree_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*.xlsx'
        self.ORDERS = {}

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

        from pos_api.adapter import submit_error, submit_order
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE NOT FOUND')
            return
        for DATA in files:
            ws = xlrd.open_workbook(DATA)
            raw = list(ws.sheets())[0]
            for i in range(2, raw.nrows - 1):
                try:
                    code = raw.row(i)[1].value
                    pur_date = f'{raw.row(i)[2].value} {raw.row(i)[3].value}'
                    pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M:%S')
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    E = get_value(raw.row(i)[4].value)
                    F = get_value(raw.row(i)[5].value)
                    P = get_value(raw.row(i)[15].value)
                    total = E - F - P
                    discount = F + P
                    vat = get_value(raw.row(i)[7].value)
                    cash = get_value(raw.row(i)[8].value)
                    card = get_value(raw.row(i)[9].value)
                    card += get_value(raw.row(i)[10].value)
                    card += get_value(raw.row(i)[11].value)
                    card += get_value(raw.row(i)[12].value)
                    card += get_value(raw.row(i)[13].value)
                    card += get_value(raw.row(i)[14].value)
                    voucher = get_value(raw.row(i)[17].value)
                    gift_card = get_value(raw.row(i)[18].value)
                    moca = get_value(raw.row(i)[19].value)
                    now = get_value(raw.row(i)[20].value)
                    air_pay = get_value(raw.row(i)[21].value)
                    got_it = get_value(raw.row(i)[22].value)
                    vn_pay = get_value(raw.row(i)[23].value)
                    ur_box = get_value(raw.row(i)[24].value)
                    gift_pop = get_value(raw.row(i)[25].value)
                    cod = get_value(raw.row(i)[26].value)
                    atome = get_value(raw.row(i)[27].value)
                    momo = get_value(raw.row(i)[28].value)
                    pms = [
                        {'Name': 'CASH', 'Value': cash},
                        {'Name': 'THẺ', 'Value': card},
                        {'Name': 'VOUCHER', 'Value': voucher},
                        {'Name': 'GIFT CARD', 'Value': gift_card},
                        {'Name': 'MOCA', 'Value': moca},
                        {'Name': 'NOW', 'Value': now},
                        {'Name': 'AIRPAY', 'Value': air_pay},
                        {'Name': 'GOT IT', 'Value': got_it},
                        {'Name': 'VNPAY', 'Value': vn_pay},
                        {'Name': 'URBOX', 'Value': ur_box},
                        {'Name': 'GIFT POP', 'Value': gift_pop},
                        {'Name': 'COD', 'Value': cod},
                        {'Name': 'ATOME', 'Value': atome},
                        {'Name': 'MOMO', 'Value': momo}
                    ]
                    for pm in pms.copy():
                        if not pm['Value']: pms.remove(pm)
                    if not len(pms):
                        pms = [{'Name': 'CASH', 'Value': 0}]
                    self.ORDERS.update({code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'PaymentMethods': pms,
                        'OrderDetails': [{'ProductId': 0}]
                    }})

                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            for k, v in self.ORDERS.items():
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            self.backup(DATA)
            # if len(self.ORDERS.items()) == 0:
            #     self.send_zero()

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

    def send_zero(self):
        from pos_api.adapter import submit_order
        order = {
            'Code': f'NOBILL_{self.DATE.strftime("%d%m%Y")}',
            'Status': 2,
            'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
            'Total': 0,
            'TotalPayment': 0,
            'VAT': 0,
            'Discount': 0,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
        }
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
