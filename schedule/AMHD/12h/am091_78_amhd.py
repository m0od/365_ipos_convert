import glob
import os
import random
import shutil
import sys
from concurrent import futures
from datetime import datetime, timedelta
from os.path import dirname
import xlrd
from unidecode import unidecode


class AM091(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'lotte_amhd'
        self.ADAPTER_TOKEN = '24eea78755b6ce8560bb95ea9096e6a2022a36d6bcc8b33ca673f85a137843e6'
        self.FOLDER = '78_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.DATE = self.DATE.strftime('%d%m%Y')
        self.EXT = f'*.xlsx'
        self.ORDERS = None
        # self.PAYMENT= {
        #     'TIEN MAT': 'CASH',
        #     'THE TIN DUNG': 'CARD'
        # }

    def scan_file(self):
        try:
            return glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            # return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        def get_value(value):
            try:
                # print(value, type(value))
                return float(value)
            except:
                return 0

        from pos_api.adapter import submit_order, submit_payment, submit_error
        files = self.scan_file()
        if not len(files):
            submit_error(self.ADAPTER_RETAILER, 'FILE_NOT_FOUND')
            return
        for DATA in files:
            # print(DATA)
            idx = DATA.rindex('/')
            name = DATA[idx + 1:].split('.')[0]
            try:
                pur_date = datetime.strptime(name, '%d%m%Y')
                print(pur_date)
            except:
                continue
            orders = []
            sheet = xlrd.open_workbook(DATA)
            raw = list(sheet.sheets())[0]
            nRows = raw.nrows
            # headers = []
            # for _ in raw.row(0):
            #     headers.append(unidecode(str(_.value).upper()))
            # print(headers)
            # current = None
            cash = 0
            money = 0
            for i in range(0, nRows):
                rec = raw.row(i)
                # print(rec)
                try:
                    hour = int(rec[0].value)
                except:
                    if rec[0].value.strip().upper() == 'CASH':
                        cash = get_value(rec[2].value)
                    continue
                rc = int(get_value(rec[1].value))
                if rc <= 0: continue
                money += get_value(rec[2].value)
                p_date = pur_date + timedelta(hours=hour)
                code = f'HD_{p_date.strftime("%d%m%Y-%H")}'
                total = get_value(rec[2].value)
                orders.append({
                    'Code': f'{code}_{rc}',
                    'Status': 2,
                    'PurchaseDate': p_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': 0,
                    'Discount': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    # 'PaymentMethods': pms
                })
                for i in range(1, rc):
                    _code = f'{code}_{i}'
                    _date = p_date + timedelta(seconds=i*int(3600/rc))
                    o = {
                        'Code': _code,
                        'Status': 2,
                        'PurchaseDate': _date.strftime('%Y-%m-%d %H:%M:%S'),
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': [{'ProductId': 0}],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    }
                    submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, o)
            other = money - cash
            # print(money, cash, other)
            for _ in orders:
                # print(_)
                if cash > 0:
                    if _['Total'] > cash:
                        print(_['Total'])
                        pms = [
                                {'Name': 'CASH', 'Value': cash},
                                {'Name': 'OTHER', 'Value': _['Total'] - cash}
                            ]
                        _.update({'PaymentMethods':pms})
                        other -= (_['Total'] - cash)
                        cash = 0
                    elif _['Total'] < cash:
                        pms = [{'Name': 'CASH', 'Value': _['Total']}]
                        _.update({'PaymentMethods': pms})
                        cash -= _['Total']
                elif other > 0:
                    pms = [{'Name': 'OTHER', 'Value': _['Total']}]
                    _.update({'PaymentMethods': pms})
                    other -= _['Total']
                print(_, other, cash)
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, _)
            # break
            #     else:
            #         orders[code]['Total'] += total
            #         orders[code]['TotalPayment'] += total
            #         orders[code]['Discount'] += discount
            #         orders[code]['PaymentMethods'].extend(pms)
            #         # orders[code]['VOUCHER'] += voucher
            # #
            # # # print(self.ORDERS)
            # for _, order in orders.items():
            #     # print(order)
            #     submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            #     for _ in order['PaymentMethods']:
            #         if _['Value'] <= 0:
            #             pm = {
            #                 'Code': f'{order["Code"]}-{_["Name"]}',
            #                 'OrderCode': order["Code"],
            #                 'Amount': _["Value"],
            #                 'TransDate': order["PurchaseDate"],
            #                 'AccountId': _['Name']
            #             }
            #             submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
            self.backup(DATA)
            # # break

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
