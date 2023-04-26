import sys
sys.path.append('/home/blackwings/pos365')
from pos_api.adapter import submit_order, submit_error
import requests
from datetime import datetime


class ATO(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'lock_n_lock_aeonhd'
        self.ADAPTER_TOKEN = 'e7f63e6620e4d146c8b6c5e9862677f7fd92ef0056d3225844decbbe2beb8850'

        # self.ADAPTER_RETAILER = 'retry'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.API = 'lockandlock.ddns.net:3333'
        self.USER = 'DungLinh'
        self.PASSWORD = 'ato@12345'
        self.browser = requests.session()
        self.METHOD = {
            'TIỀN MẶT': 'CASH',
            'CARD': 'THẺ'
        }

    def get_data(self, d_from, d_to):
        params = {
            'TuNgay': d_from.strftime('%Y-%m-%d'),
            'DenNgay': d_to.strftime('%Y-%m-%d')
        }
        headers = {
            'TaiKhoan': self.USER,
            'MatKhau': self.PASSWORD
        }
        # data = None
        try:
            r = self.browser.get(f'http://{self.API}/api/dunglinh/getdoanhthu', params=params, headers=headers)
            res = r.json()
            if res['success'] is False: return
            data = res['data']
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Data] {str(e)}')
            return
        ods = {}
        for d in data:
            try:
                if int(d['Tổng Đơn']) >= 0:
                    minus = 1
                else:
                    minus = -1
                code = d['Mã Đơn Hàng']
                pur_date = datetime.strptime(d['Ngày Tạo'], '%Y/%m/%d %H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                discount = d.get('Chiết Khấu') is not None and int(d['Chiết Khấu']) or 0
                method = self.METHOD.get(str(d['Tên PTTT']).strip().upper())
                if method is None:
                    method = str(d['Tên PTTT']).strip().upper()
                if minus == 1:
                    if ods.get(code) is None:
                        od = [{
                            'Code': d['Mã Hàng Hóa'].strip(),
                            'Name': d['Tên Hàng'].strip(),
                            'Price': int(d['Đơn Giá']),
                            'Quantity': int(d['Số Lượng'])
                        }]
                        o = {
                            'Code': d['Mã Đơn Hàng'],
                            'PurchaseDate': pur_date,
                            'Status': 2,
                            'Total': int(d['Tổng Đơn']),
                            'TotalPayment': int(d['Tổng Đơn']),
                            'VAT': 0,
                            'Discount': discount,
                            'OrderDetails': od,
                            'PaymentMethods': [{'Name': method, 'Value': int(d['Tổng Đơn'])}]
                        }
                        ods.update({code: o})
                    else:
                        od = ods[code]['OrderDetails']
                        od.append({
                            'Code': d['Mã Hàng Hóa'].strip(),
                            'Name': d['Tên Hàng'].strip(),
                            'Price': int(d['Đơn Giá']),
                            'Quantity': int(d['Số Lượng'])
                        })
                        ods[code].update({'OrderDetails': od})
                else:
                    vat_code = f"VAT_{d['Mã Đơn Hàng']}"
                    if ods.get(vat_code) is None:
                        o = {
                            'Code': vat_code,
                            'PurchaseDate': pur_date,
                            'Total': 0,
                            'Status': 2,
                            'TotalPayment': 0,
                            'VAT': 0,
                            'Discount': 0,
                            'OrderDetails': [],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': 0}],
                            'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': int(d['Tổng Đơn'])}],
                        }
                        ods.update({vat_code: o})
                    if ods.get(code) is None:
                        od = [{
                            'Code': d['Mã Hàng Hóa'].strip(),
                            'Name': d['Tên Hàng'].strip(),
                            'Price': int(d['Đơn Giá']),
                            'Quantity': int(d['Số Lượng'])
                        }]
                        r = {
                            'Code': code,
                            'ReturnDate': pur_date,
                            'Discount': d.get('Chiết Khấu') is not None and int(d['Chiết Khấu']) or 0,
                            'Total': int(d['Tổng Đơn']) * minus,
                            'TotalPayment': int(d['Tổng Đơn']) * minus,
                            'Status': 0,
                            'ReturnDetails': od,
                            'PaymentMethods': [{'Name': method,'Value': int(d['Tổng Đơn'] * minus)}]
                        }
                        ods.update({code: r})
                    else:
                        od = ods[code]['ReturnDetails']
                        od.append({
                            'Code': d['Mã Hàng Hóa'].strip(),
                            'Name': d['Tên Hàng'].strip(),
                            'Price': int(d['Đơn Giá']),
                            'Quantity': int(d['Số Lượng'])
                        })
                        ods[code].update({'ReturnDetails': od})
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Order] {str(e)} {d}')
        for _, js in ods.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)

# ATO().get_data(datetime.strptime('2023-04-23','%Y-%m-%d'), datetime.strptime('2023-04-23','%Y-%m-%d'))