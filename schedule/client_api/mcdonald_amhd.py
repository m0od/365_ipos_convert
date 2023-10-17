import glob
import os
import shutil
from os.path import dirname
from datetime import datetime, timedelta


class McDonaldAMHD(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'mcdonald_amhd'
        self.ADAPTER_TOKEN = '59be732c9d48d58772011f30f74c447cbfee32a9b82c4cebe1e0d8b1a35aac9a'
        # self.ADAPTER_RETAILER = '695'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'

        self.FOLDER = 'mcd_amhd'
        self.FULL_PATH = f'../home/{self.FOLDER}/'
        self.EXT = '*txt'
        self.DATA = None
        self.ORDERS = []
        # self.PMS = {}
        # self.ODS = {}

    def scan_file(self):
        # print(os.getcwd())
        # print(os.path.getmtime(self.FULL_PATH))
        # print(for name in glob.glob('/home/geeks/Desktop/gfg/data.txt'):)
        files = glob.glob(self.FULL_PATH + self.EXT)
        # print(files)
        self.DATA = max(files, key=os.path.getmtime)

        print(self.DATA)

    def get_data(self):
        self.scan_file()
        f = open(self.DATA, 'rb')
        lines = f.read().decode('utf-8').strip().split('\n')
        f.close()
        for line in lines[1:]:
            # '''[MachineID]|[BatchID]|[DDMMYYYY]|[HH]|[RC]|
            # [GTOSales]|[VAT]|[Discount]|[ServiceCharge]|[NoPax]|[CashAmount]|[CashlessAmount]|[Visa]|[MasterCard]|[Amex]|[VoucherAmount]|[RefundGross]|[VATRegister]
            #                             8               9       10          11
            # [MachineID]|[BatchID]|10092023|09|11|
            # 862036.00|68964.00|0|0.00|0|714000.00|0.00|0.00|0.00|0.00|0.00|217000.00|R'''
            raw = line.strip().split('|')
            # print(raw[2], raw[3])
            pur_date = datetime.strptime(f'{raw[2]}{raw[3]}', '%d%m%Y%H')
            rc = int(raw[4])
            total = float(raw[5]) + float(raw[6])
            vat = float(raw[6])
            discount = float(raw[7])
            cash = float(raw[10])
            card = float(raw[11])
            card += float(raw[12])
            card += float(raw[13])
            card += float(raw[14])
            voucher = float(raw[15])
            point = float(raw[16])
            if total != 0 or cash != 0 or card != 0 and point != 0 or voucher != 0:
                pms = []
                if cash != 0:
                    pms.append({'Name': 'CASH', 'Value': cash})
                if card != 0:
                    pms.append({'Name': 'CARD', 'Value': card})
                if voucher != 0:
                    pms.append({'Name': 'VOUCHER', 'Value': voucher})
                if point != 0:
                    pms.append({'Name': 'POINT', 'Value': point})
                self.ORDERS.append({
                    'Code': f'{pur_date.strftime("%Y%m%d_%H")}_{rc}',
                    'Status': 2,
                    'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': int(total),
                    'TotalPayment': int(total),
                    'VAT': 0,
                    'Discount': int(discount),
                    'OrderDetails': [],
                    'PaymentMethods': pms
                })
                for _ in range(1, rc):
                    self.ORDERS.append({
                        'Code': f'{pur_date.strftime("%Y%m%d_%H")}_{_}',
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': [],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    })
        for _ in self.ORDERS:
            print(_.get('Code'))
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
        try:
            shutil.move(self.DATA, f'{self.FULL_PATH}bak')
        except:
            pass


if __name__:
    import sys

    # PATH = dirname(dirname(__file__))
    PATH = dirname(dirname(dirname(__file__)))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order, submit_payment

    # McDonaldAMHD().get_data()