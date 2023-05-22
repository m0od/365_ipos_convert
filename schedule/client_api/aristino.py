import json
from datetime import datetime
from os.path import dirname
import requests


class Aristino(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'aristino_aeonhd'
        self.ADAPTER_TOKEN = 'f9c538ed4381881731a92b24b7362c0918d31c07de4e2ab37ca7822f0d22a176'
        # self.ADAPTER_RETAILER = 'retry'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.URL = 'https://crm.aristino.com:4436/KGAPI/api/SOAPI/GetTransHistoryBL_HTTT'
        self.KEY = 'd3d75fc6-e507-4e41-9108-3764a036aa5c-J7k1E4r4IRzA99vEmtbTyARH6bOrZK'
        self.LOCATION = '0119'
        self.browser = requests.session()
        self.RETURN = []
        self.METHOD = {
            'CARD': 'THẺ',
            'TRANSFER': 'CHUYỂN KHOẢN',
            'CASH': 'CASH',
            'VOUCHER': 'VOUCHER'
        }
        self.TOKEN = None

    def get_data(self, d_from):
        try:
            params = {
                'ngay_bd': d_from.strftime('%Y-%m-%d'),
                # 'ngay_bd': '2023-05-01',
                'ngay_kt': d_from.strftime('%Y-%m-%d'),
                'ma_dvcs': self.LOCATION
            }
            self.browser.headers.update({
                'Key': self.KEY
            })
            res = self.browser.get(self.URL, params=params)
            if res.status_code != 200:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[FETCH DATA] {res.status_code}')
            # f = open('aristino.json', 'r')
            # s = f.read().strip()
            # f.close()
            js = res.json()
            if js.get('Success'):
                result = js.get('Result')
                if len(result) > 1:
                    for r in js['Result'][1:]:
                        pur_date = r['ngay_ct'].replace('00:00:00', r['time0'].split('.')[0])
                        pur_date = datetime.strptime(pur_date.upper(), '%Y-%m-%dT%H:%M:%S')
                        discount = r['diem_the'] + r['ck_them'] + r['voucher']
                        total = r['tt_truoc_ck'] - discount - r['doi_tra']
                        pm = []
                        if r['tien_mat'] != 0:
                            pm.append({'Name': 'CASH', 'Value': r['tien_mat']})
                        if r['tt_the'] != 0:
                            pm.append({'Name': 'THẺ', 'Value': r['tt_the']})
                        if r['tt_khac'] != 0:
                            pm.append({'Name': 'KHÁC', 'Value': r['tt_khac']})
                        if r['pay_qr'] != 0:
                            pm.append({'Name': 'QR', 'Value': r['pay_qr']})
                        send = {
                            'Code': r['doi_tra'] == 0 and r['so_ct'] or f"DTH_{r['so_ct']}",
                            'Status': 2,
                            'PurchaseDate': pur_date.strftime('%Y-%m-%d %H:%M:%S'),
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': [],
                            'PaymentMethods': pm
                        }
                        submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
                return True
            return False
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[FETCH DATA] {str(e)}')
            return False


if __name__.__contains__('schedule.client_api'):
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

# if __name__ == '__main__':
#     import sys
#
#     PATH = dirname(dirname(__file__))
#     sys.path.append(PATH)
#     from schedule.pos_api.adapter import submit_error, submit_order
#
#     Aristino().get_data()
