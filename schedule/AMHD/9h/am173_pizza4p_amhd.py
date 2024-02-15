import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname, getmtime


class AM173(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'pizza4p_amhd'
        self.ADAPTER_TOKEN = 'eabf7ce8b39de13172c11c5c9733a6e7f98ab99e97b702d78e52039bcc82abe6'
        self.FOLDER = 'pizza4p_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*txt'
        self.DATA = None
        self.method = {
            'TIỀN MẶT': 'CASH'
        }
        self.ORDERS = []

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        from pos_api.adapter import submit_order, submit_error
        DATA = self.scan_file()
        if not DATA:
            submit_error(retailer=self.ADAPTER_RETAILER, reason='FILE_NOT_FOUND')
            return
        try:
            f = open(DATA, 'r')
            raw = f.read().strip()
            # print(raw)
            f.close()
            for line in raw.split('\n'):
                _ = line.split('|')
                code = f'{_[2].strip()}_{_[3].strip()}'
                # if code != 'CA_230829_10000002623349': continue
                pur_date = _[2].strip()
                pur_date = datetime.strptime(pur_date, '%d%m%Y')
                # pur_date = data[row][2].value.strip()
                # pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%M')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                total_bill = int(_[4].strip())
                if not total_bill: continue
                # print(line)

                total = float(_[5].strip()) + float(_[6].strip())
                vat = float(_[6].strip())
                discount = float(_[7].strip())
                cash = float(_[10].strip())
                bank = float(_[11].strip())
                card = float(_[12].strip())
                card += float(_[13].strip())
                card += float(_[14].strip())
                voucher = float(_[15].strip())
                other = float(_[16].strip())
                pms = []
                if cash != 0:
                    pms.append({'Name': 'CASH', 'Value': cash})
                if card != 0:
                    pms.append({'Name': 'CARD', 'Value': card})
                if voucher != 0:
                    pms.append({'Name': 'VOUCHER', 'Value': voucher})
                if other != 0:
                    pms.append({'Name': 'OTHER', 'Value': other})
                # print(code, pur_date, total, pms)
                self.ORDERS.append({
                    'Code': f'{code}_{total_bill}',
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': [],
                    'PaymentMethods': pms
                })
                for _ in range(1, total_bill):
                    self.ORDERS.append({
                        'Code': f'{code}_{_}',
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': [],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    })

            for _ in self.ORDERS:
                if len(_['PaymentMethods']) == 0:
                    _['PaymentMethods'] = [{'Name': 'CASH', 'Value': 0}]
                # print(_)
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)

        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            pass
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