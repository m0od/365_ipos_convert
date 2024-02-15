import sys
from datetime import datetime, timedelta
from os.path import dirname
import requests


class AM140(object):

    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'aristino_amhd'
        self.ADAPTER_TOKEN = 'f9c538ed4381881731a92b24b7362c0918d31c07de4e2ab37ca7822f0d22a176'
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
        self.DATE = datetime.now() - timedelta(days=1)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        try:
            params = {
                'ngay_bd': self.DATE.strftime('%Y-%m-%d'),
                # 'ngay_bd': '2023-05-01',
                'ngay_kt': self.DATE.strftime('%Y-%m-%d'),
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
                        discount = r['ck_them']
                        total = r['tt_truoc_ck'] - discount - r['doi_tra']
                        pm = []
                        if r['voucher'] != 0:
                            pm.append({'Name': 'VOUCHER', 'Value': r['voucher']})
                        if r['tien_mat'] != 0:
                            pm.append({'Name': 'CASH', 'Value': r['tien_mat']})
                        if r['tt_the'] != 0:
                            pm.append({'Name': 'THẺ', 'Value': r['tt_the']})
                        if r['tt_khac'] != 0:
                            pm.append({'Name': 'KHÁC', 'Value': r['tt_khac']})
                        if r['pay_qr'] != 0:
                            pm.append({'Name': 'QR', 'Value': r['pay_qr']})
                        if r['diem_the'] != 0:
                            pm.append({'Name': 'POINT', 'Value': r['diem_the']})
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
