import glob
import os
import shutil
import sys
from datetime import datetime, timedelta
from os.path import dirname


class AM111(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from drive import Google
        self.ADAPTER_RETAILER = 'life4cuts_amhd'
        self.ADAPTER_TOKEN = '78ba2854e04f8cc2d4d83a55ddb8711f243142028ac8b3731561f4abc8e02e80'
        self.DATE = datetime.now() - timedelta(days=1)
        from pos import POS365
        self.ORDERS = {}
        self.TRANS = []
        self.DATE = datetime.now() - timedelta(days=1)
        self.POS = POS365()
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'
        self.POS.DOMAIN = self.__class__.__name__


    def get_data(self):
        from pos_api.adapter import submit_order
        self.POS.login()
        data = self.POS.get_order()
        if not data: return
        # print(data['Code'])
        pur_date = data['PurchaseDate'].split('.')[0]
        pur_date = datetime.strptime(pur_date, '%Y-%m-%dT%H:%M:%S')
        pur_date = pur_date + timedelta(hours=7)
        pur_date = pur_date.replace(hour=10, minute=0, second=0)
        print(pur_date)
        tq = 0
        for _ in data['OrderDetails']:
            print(_['Code'], abs(_['Quantity']))
            tq += abs(_['Quantity'])
        print(tq)
        for idx in range(1, tq):
            p_date = pur_date + timedelta(seconds=idx * int(43200/tq))
            order = {
                'Code': f"{data['Code']}_{idx}",
                'Status': 2,
                'PurchaseDate': p_date.strftime('%Y-%m-%d %H:%M:%S'),
                'Total': 0,
                'TotalPayment': 0,
                'VAT': 0,
                'Discount': 0,
                'OrderDetails': [{'ProductId': 0}],
                'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
            }
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
