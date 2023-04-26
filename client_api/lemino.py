import sys
sys.path.append('/home/blackwings/pos365')

from pos_api.adapter import submit_error, submit_order
import requests
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")


class Lemino(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'lemino_aeonhd'
        self.ADAPTER_TOKEN = '1bd59a048bc2680486b5d6fa24b10afc365591c25511e4170d6149c3e44eec78'
        # self.ADAPTER_RETAILER = 'retry'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.API = 'http://shop.lemino.vn/WebServices/GenReportDaily.ashx'

        self.orders = {}
        self.browser = requests.session()

    def get_data(self, dFrom=None):
        try:
            p = {
                'groupcode': 'AHD',
                'date': dFrom.strftime('%m/%d/%Y')
            }
            res = self.browser.get(f"{self.API}", params=p).json()
            for i in res:
                try:
                    code = i['OrderCode']
                    pd = datetime.strptime(i['OrderDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    total = int(i['Amount'])
                    pm_name = i['PaymentMethod'].upper() == 'BANK' and 'THẺ' or 'CASH'
                    if self.orders.get(code) is None:
                        self.orders.update({
                            code: {
                                'Code': code,
                                'Status': 2,
                                'PurchaseDate': pd.strftime('%Y-%m-%d %H:%M:%S'),
                                'Discount': 0,
                                'Total': total,
                                'TotalPayment': total,
                                'VAT': 0,
                                'OrderDetails': [{'ProductId': 0}],
                                'PaymentMethods': [{'Name': pm_name, 'Value': total}]
                            }
                        })
                    else:
                        new_total = self.orders[code]['Total'] + total
                        pm = json.loads(self.orders[code]['pm'])
                        pm.append({'Name': pm_name, 'Value': total})
                        self.orders[code].update({
                            'Total': new_total,
                            'TotalPayment': new_total,
                            'PurchaseDate': pd.strftime('%Y-%m-%d %H:%M:%S'),
                            'PaymentMethods': pm
                        })
                except Exception as ex:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(ex))
            for _, js in self.orders.items():
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))


Lemino().get_data(datetime.strptime('04/24/2023','%m/%d/%Y'))