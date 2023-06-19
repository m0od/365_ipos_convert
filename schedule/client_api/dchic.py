from datetime import datetime, timedelta
from os.path import dirname

import requests


class Dchic(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'dchic_aeonhd'
        self.ADAPTER_TOKEN = '41ad34825bfa260bc53863d146b8579de118c4df599ba44dcf70e46ab2b9e45f'
        self.URL = 'https://dc08.dchic.vn/api/Dc08Rpt'
        self.orders = {}
        self.browser = requests.session()
        self.METHOD = {
            't_tt_the': 'THẺ',
            'tien_kh_tt': 'CASH',
            'tien_km_ttvoucher': 'VOUCHER',
            'tien_qrcode': 'QRCODE'
        }

    def get_data(self, fromdate):
        try:
            p = {
                'fromdate': fromdate.strftime('%Y%m%d'),
                'todate': fromdate.strftime('%Y%m%d')
            }
            # print(p)
            res = self.browser.get(self.URL, params=p)
            if res.status_code != 200:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=str(res.status_code))
            # print(res.text)
            js = res.json()
            for _ in js:
                code = _['so_ct']
                pur_date = datetime.strptime(_['ngay_ct'], '%d/%m/%Y %H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                if self.orders.get(code) is None:
                    # pms = []
                    # if _['t_tt_the'] != 0:
                    #     pms.append({'Name': 'THẺ', 'Value': _['t_tt_the']})
                    # if _['tien_kh_tt'] != 0:
                    #     pms.append({'Name': 'CASH', 'Value': _['tien_kh_tt']})
                    # if _['tien_km_ttvoucher'] != 0:
                    #     pms.append({'Name': 'VOUCHER', 'Value': _['tien_km_ttvoucher']})
                    # if _['tien_qrcode'] != 0:
                    #     pms.append({'Name': 'QRCODE', 'Value': _['tien_qrcode']})
                    self.orders[code] = {
                        'Code': code,
                        'PurchaseDate': pur_date,
                        'Status': 2,
                        'Total': _['t_tt'],
                        'TotalPayment': _['t_tt'],
                        'VAT': _['dt_vat'],
                        'Discount': _['ck'],
                        'OrderDetails': [],
                        't_tt_the': _['t_tt_the'],
                        'tien_kh_tt': _['tien_kh_tt'],
                        'tien_km_ttvoucher': _['tien_km_ttvoucher'],
                        'tien_qrcode': _['tien_qrcode'],
                        'tien_the_qt': _['tien_the_qt'],
                        'tien_tra_truoc': _['tien_tra_truoc']
                    }
                else:
                    self.orders[code].update({
                        't_tt_the': self.orders[code]['t_tt_the'] + _['t_tt_the'],
                        'tien_kh_tt': self.orders[code]['tien_kh_tt'] + _['tien_kh_tt'],
                        'tien_km_ttvoucher': self.orders[code]['tien_km_ttvoucher'] + _['tien_km_ttvoucher'],
                        'tien_qrcode': self.orders[code]['tien_qrcode'] +  _['tien_qrcode'],
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
                if v['t_tt_the'] != 0:
                    pms.append({'Name': 'THẺ', 'Value': v['t_tt_the']})
                if v['tien_km_ttvoucher'] != 0:
                    pms.append({'Name': 'VOUCHER', 'Value': v['tien_km_ttvoucher']})
                if v['tien_qrcode'] != 0:
                    pms.append({'Name': 'QRCODE', 'Value': v['tien_qrcode']})
                if v['tien_the_qt'] != 0:
                    pms.append({'Name': 'GIFT CARD', 'Value': v['tien_the_qt']})
                if v['tien_tra_truoc'] != 0:
                    pms.append({'Name': 'THẺ TRẢ TRƯỚC', 'Value': v['tien_tra_truoc']})
                if len(pms) == 0:
                    pms.append({'Name': 'CASH', 'Value': 0})
                v.pop('t_tt_the')
                v.pop('tien_kh_tt')
                v.pop('tien_km_ttvoucher')
                v.pop('tien_qrcode')
                v.update({'PaymentMethods': pms})
                # print(v)
                submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)

            return True
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
            return False


if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    now = datetime.now()
    # print(now-timedelta(15+12))
    Dchic().get_data(now - timedelta(days=1))
