import sys
from datetime import datetime, timedelta
from os.path import dirname

import requests


class AM141(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'dchic_amhd'
        self.ADAPTER_TOKEN = '41ad34825bfa260bc53863d146b8579de118c4df599ba44dcf70e46ab2b9e45f'
        self.URL = 'https://dc08.dchic.vn/api/Dc08Rpt'
        self.orders = {}
        self.browser = requests.session()
        self.DATE = datetime.now() - timedelta(days=1)
        self.METHOD = {
            't_tt_the': 'THẺ',
            'tien_kh_tt': 'CASH',
            'tien_km_ttvoucher': 'VOUCHER',
            'tien_qrcode': 'QRCODE'
        }

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        try:
            p = {
                'fromdate': self.DATE.strftime('%Y%m%d'),
                'todate': self.DATE.strftime('%Y%m%d')
            }
            res = self.browser.get(self.URL, params=p)
            if res.status_code != 200:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(res.status_code))
            # print(res.text)
            js = res.json()
            for _ in js:
                pur_date = datetime.strptime(_['ngay_ct'], '%d/%m/%Y %H:%M:%S')
                code = f"{_['so_ct']}_{pur_date.strftime('%y%m%d')}"
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                if self.orders.get(code) is None:
                    self.orders[code] = {
                        'Code': code,
                        'PurchaseDate': pur_date,
                        'Status': 2,
                        'Total': _['t_tt'],
                        'TotalPayment': _['t_tt'],
                        'VAT': _['dt_vat'],
                        'Discount': _['ck'],
                        'OrderDetails': [],
                        'tt_ck': _['tt_ck'],
                        'tien_kh_tt': _['tien_kh_tt'],
                        'tt_pos': _['tt_pos'],
                        'tien_qrcode': _['tien_qrcode'],
                        'tien_the_qt': _['tien_the_qt'],
                        'tien_tra_truoc': _['tien_tra_truoc']
                    }
                else:
                    self.orders[code].update({
                        'tt_ck': self.orders[code]['tt_ck'] + _['tt_ck'],
                        'tien_kh_tt': self.orders[code]['tien_kh_tt'] + _['tien_kh_tt'],
                        'tt_pos': self.orders[code]['tt_pos'] + _['tt_pos'],
                        'tien_qrcode': self.orders[code]['tien_qrcode'] + _['tien_qrcode'],
                        'tien_the_qt': self.orders[code]['tien_the_qt'] + _['tien_the_qt'],
                        'tien_tra_truoc': self.orders[code]['tien_tra_truoc'] + _['tien_tra_truoc'],
                        'Total': self.orders[code]['Total'] + _['t_tt'],
                        'TotalPayment': self.orders[code]['TotalPayment'] + _['t_tt'],
                        'VAT': self.orders[code]['VAT'] + _['dt_vat'],
                        'Discount': self.orders[code]['Discount'] + _['ck'],
                    })
            for k, v in self.orders.items():
                pms = []
                if v['tien_kh_tt'] != 0:
                    pms.append({'Name': 'CASH', 'Value': v['tien_kh_tt']})
                if v['tt_ck'] != 0:
                    pms.append({'Name': 'CHUYỂN KHOẢN', 'Value': v['tt_ck']})
                if v['tt_pos'] != 0:
                    pms.append({'Name': 'PAYOO', 'Value': v['tt_pos']})
                if v['tien_qrcode'] != 0:
                    pms.append({'Name': 'QRCODE', 'Value': v['tien_qrcode']})
                if v['tien_the_qt'] != 0:
                    pms.append({'Name': 'GIFT CARD', 'Value': v['tien_the_qt']})
                if v['tien_tra_truoc'] != 0:
                    pms.append({'Name': 'THẺ TRẢ TRƯỚC', 'Value': v['tien_tra_truoc']})
                if len(pms) == 0:
                    pms.append({'Name': 'CASH', 'Value': 0})
                v.pop('tien_kh_tt')
                v.pop('tt_ck')
                v.pop('tt_pos')
                v.pop('tien_qrcode')
                v.update({'PaymentMethods': pms})
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)

            return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            return False
