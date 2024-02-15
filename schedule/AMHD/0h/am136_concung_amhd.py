import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname
import xlrd


class AM136(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'concung_amhd'
        self.ADAPTER_TOKEN = 'f546ab681fa530a14671096bd43715bb0b73de3bdabb63125be2f80a8fd53cdd'
        self.FOLDER = 'concung_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*xlsx'
        self.method = {
            'TIỀN MẶT': 'CASH'
        }

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

        # print(self.DATA)

    def get_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_error, submit_order, submit_payment
        files = self.scan_file()
        # print(DATA)
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            count = None
            try:
                ws = xlrd.open_workbook(DATA)
                raw = list(ws.sheets())[0]
                for i in range(1, raw.nrows):
                    code = raw.row(i)[0].value
                    if not code: continue
                    code = str(code)
                    pur_date = xlrd.xldate_as_datetime(raw.row(i)[3].value, ws.datemode)
                    # print(pur_date)
                    # if self.DATE.strftime("%d.%m.%Y") != pur_date.strftime('%d.%m.%Y'):
                    #     continue
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    # print(pur_date)
                    total = get_value(raw.row(i)[6].value)
                    cash = get_value(raw.row(i)[8].value)
                    cash -= get_value(raw.row(i)[7].value)
                    voucher = get_value(raw.row(i)[7].value)
                    credit = get_value(raw.row(i)[9].value)
                    pms = []
                    if cash:
                        pms.append({'Name': 'CASH', 'Value': cash})
                    if voucher:
                        pms.append({'Name': 'VOUCHER', 'Value': voucher})
                    if credit:
                        pms.append({'Name': 'CREDIT', 'Value': credit})
                    if not len(pms):
                        pms.append({'Name': 'CASH', 'Value': 0})
                    send = {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': [{'ProductId': 0}],
                        'PaymentMethods': pms
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                    for _ in pms:
                        if _['Value'] <= 0:
                            pm = {
                                'Code': f'{code}-{_["Name"]}',
                                'OrderCode': code,
                                'Amount': _["Value"],
                                'TransDate': pur_date,
                                'AccountId': _["Name"]
                            }
                            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
                    if count is None:
                        count = 1
                    else:
                        count += 1
            except Exception as e:
                print(e)
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            self.backup(DATA)
        # if count == 0:
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
    #
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
