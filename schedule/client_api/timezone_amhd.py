import glob
import os
import shutil
from datetime import datetime
from os.path import dirname




class TimeZoneAMHD(object):
    def __init__(self):
        import sys
        PATH = dirname(dirname(__file__))
        sys.path.append(PATH)

        self.ADAPTER_RETAILER = 'timezone_amhd'
        self.ADAPTER_TOKEN = 'fb7226b8d3033064611519b2683d15fa9ce2ce80b4a44c6a40dcf28d55a42af3'
        self.FOLDER = 'timezone_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/TEEG_Test/'
        self.EXT = '*txt'
        self.DATA = None
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT)
        # print(files)
        self.DATA = max(files, key=os.path.getmtime)

        print(self.DATA)


    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        try:
            self.scan_file()
            try:
                f = open(self.DATA, 'rb')
                s = f.read().decode('utf-8')
                f.close()
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
                return
            lines = s.strip().split('\n')
            for line in lines:
                try:
                    _ = line.strip().split('|')
                    code = _[0].strip()
                    pur_date = datetime.strptime(_[1], '%H%M%d%m%Y')
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    total = float(_[2].strip())
                    discount = float(_[3].strip())
                    vat = round(float(_[4].strip()), 0)
                    cash = float(_[6].strip())
                    payoo = float(_[7].strip())
                    cheque = float(_[8].strip())
                    momo = float(_[9].strip())
                    pms = []
                    if cash != 0:
                        pms.append({'Name': 'CASH', 'Value': cash})
                    if payoo != 0:
                        pms.append({'Name': 'PAYOO', 'Value': payoo})
                    if cheque != 0:
                        pms.append({'Name': 'CHEQUE', 'Value': cheque})
                    if momo != 0:
                        pms.append({'Name': 'MOMO', 'Value': momo})
                    ods = [{'ProductId': 0}]
                    send = {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': [{'ProductId': 0}],
                        'PaymentMethods': pms
                    }
                    submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            idx = self.DATA.rindex('/')
            name = self.DATA[idx + 1:]
            if os.path.exists(f'{self.FULL_PATH}bak/{name}'):
                os.remove(f'{self.FULL_PATH}bak/{name}')
            try:
                shutil.move(self.DATA, f'{self.FULL_PATH}bak')
            except:
                pass
        except:
            pass


if __name__:
    # import sys
    print(__name__)
    # # PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # sys.path.append(PATH)
    # from schedule.pos_api.adapter import submit_error, submit_order
    # TimeZoneAMHD().get_data()
