import sys
from datetime import datetime, timedelta
from os.path import dirname

import requests


class AM181(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'inochi_amhd'
        self.ADAPTER_TOKEN = 'c6f17c9fd72c4350c70f29737e8bd3023c6c2a52a04f2a9ba8c174a9dfd62e66'
        self.API = 'https://inochishop.mysapogo.com'

        self.ORDERS = {}
        self.DETAILS = {}
        self.TENANT = None
        self.ACCOUNT = 'trungn@aeonmall-vn.com'
        self.PASSWORD = 'Trung!123aeon'
        self.DATE = datetime.now() - timedelta(days=1)
        # self.DATE = date

    def login(self):
        from pos_api.adapter import submit_order, submit_error
        try:
            self.browser = requests.session()
            r = self.browser.get(f'{self.API}/admin/authorization/login')
            csrf = r.text.split('__RequestVerificationToken" type="hidden" value="')[1].split('"')[0]
            data = {
                '__RequestVerificationToken': csrf,
                'Password': self.PASSWORD,
                'Email': self.ACCOUNT
            }
            self.browser.post(f'{self.API}/admin/authorization/login', data=data)
            self.TENANT = self.browser.get(f'{self.API}/admin/tenant.json').json()['tenant']['id']
            return True
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, reason=str(e))
            return False

    def get_orders(self):
        from pos_api.adapter import submit_order, submit_error
        page = 1
        while True:
            params = {
                'start_date': (self.DATE - timedelta(days=1)).strftime('%Y-%m-%dT17:00:00Z'),
                'end_date': self.DATE.strftime('%Y-%m-%dT16:59:59Z'),
                'order_status': 'completed',
                'return_status': 'unreturned',
                'type': 'by_completed',
                'page': str(page),
                'limit': '100',

            }
            # print(params)
            try:
                r = self.browser.get(f'{self.API}/admin/reports/fact_order.json', params=params, timeout=10)
            except:
                continue
            items = r.json()['items']
            if not len(items): break
            for _ in r.json()['items']:
                cash = _['cash_payments']
                transfer = _['transfer_payments']
                card = _['mpos_payments']
                cod = _['cod_payments']
                other = _['unknown_payments']
                point = _['point_payments']
                online = _['online_payments']
                gateway = _['gateway_payments']
                pms = [
                    {'Name': 'CASH', 'Value': _['cash_payments']},
                    {'Name': 'CARD', 'Value': _['mpos_payments']},
                    {'Name': 'CHUYỂN KHOẢN', 'Value': _['transfer_payments']},
                    {'Name': 'COD', 'Value': _['cod_payments']},
                    {'Name': 'ĐIỂM', 'Value': _['point_payments']},
                    {'Name': 'KHÁC', 'Value': _['unknown_payments']},
                    {'Name': 'ONLINE', 'Value': _['online_payments']},
                    {'Name': 'GATEWAY', 'Value': _['gateway_payments']},
                ]
                for pm in pms.copy():
                    if not pm['Value']:
                        pms.remove(pm)
                # print(pms)
                # print(self.DETAILS)
                if self.DETAILS.get(_['order_code']):
                    ods = self.DETAILS.get(_['order_code'])
                else:
                    ods = [{'ProductId': 0}]
                pur_date = datetime.strptime(str(_['date_key']), '%Y%m%d%H')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                orders = {
                    'Code': _['order_code'],
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': _['payments'],
                    'TotalPayment': _['payments'],
                    'VAT': 0,
                    'Discount': _['total_discount_amount'],
                    'OrderDetails': ods,
                    'PaymentMethods': pms
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
            page += 1

    def get_details(self):
        from pos_api.adapter import submit_order, submit_error
        try:
            r = self.browser.get(f'{self.API}/admin/analytics/sale_orders/statistical_order')
            token = r.text.split('token&quot;:&quot;')[1].split('&quot;')[0]
            time = self.DATE.strftime('%Y-%m-%d')
            query = ['SHOW', 'quantity,', 'price', 'BY', 'variant_name,', 'variant_sku,', 'order_code']
            query += ['FROM', 'orders']
            query += ['WHERE', 'return_status', '==', '"Chưa trả hàng"']
            query += ['SINCE', time, 'UNTIL', time]
            query += ['LIMIT', '10000']

            params = {
                'token': token,
                'q': ' '.join(query),
                'beta': 'true',
                'options': 'time:"completed_at"',
                'timezone': 'Asia/Ho_Chi_Minh'
            }
            # print(params['q'])
            self.browser.headers.update({
                'x-sapo-tenantid': str(self.TENANT)
            })
            r = self.browser.get('https://analytics.sapo.vn/query', params=params)
            # print(r.text)
            headers = []
            for _ in r.json()['result']['columns']:
                headers.append(_['field'])
            for _ in r.json()['result']['data']:
                data = dict(zip(headers, _))
                if not self.DETAILS.get(data['order_code']):
                    self.DETAILS.update({
                        data['order_code']: [{
                            'Code': data['variant_sku'].strip(),
                            'Name': data['variant_name'].strip(),
                            'Price': data['price'],
                            'Quantity': data['quantity']
                        }]
                    })
                else:
                    self.DETAILS[data['order_code']].append({
                        'Code': data['variant_sku'].strip(),
                        'Name': data['variant_name'].strip(),
                        'Price': data['price'],
                        'Quantity': data['quantity']
                    })
            # print(self.DETAILS)
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, reason=f'get_details {str(e)}')

    def get_returns(self):
        from pos_api.adapter import submit_order, submit_error, submit_payment
        r = self.browser.get(f'{self.API}/admin/analytics/sale_orders/return_by_order')
        token = r.text.split('token&quot;:&quot;')[1].split('&quot;')[0]
        time = self.DATE.strftime('%Y-%m-%d')
        query = ['SHOW', 'returns,', 'returned_item_quantity']
        query += ['BY', 'hour,', 'order_code,', 'sale_kind,', 'product_name,', 'variant_sku,', 'product_price']
        query += ['FROM', 'sales', 'WHERE', 'sale_kind', '==', '"Trả hàng"']
        query += ['AND', 'order_status', '==', '"Hoàn thành"']
        query += ['SINCE', time, 'UNTIL', time, 'ORDER', 'BY', 'hour', 'ASC']
        query += ['LIMIT', '10000']
        params = {
            'token': token,
            'q': ' '.join(query),
            'beta': 'true',
            'o': '',
            'timezone': 'Asia/Ho_Chi_Minh'
        }
        # print(params)
        self.browser.headers.update({
            'x-sapo-tenantid': str(self.TENANT)
        })
        # print(str(self.TENANT))
        r = self.browser.get('https://analytics.sapo.vn/query', params=params)
        # print(r.text)
        headers = []
        for _ in r.json()['result']['columns']:
            headers.append(_['field'])
        orders = {}
        for _ in r.json()['result']['data']:
            data = dict(zip(headers, _))
            # print(data)
            code = f'R_{data["order_code"]}'
            pur_date = data['hour'].split('+')[0]
            pur_date = datetime.strptime(pur_date, '%Y-%m-%dT%H:%M:%S')
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            total = data['returns']
            if total == 0: continue
            # discount = data['discounts']
            # if len(data['variant_sku'].strip()):
            ods = [{
                'Code': data['variant_sku'].strip(),
                'Name': data['product_name'].strip(),
                'Price': data['product_price'],
                'Quantity': data['returned_item_quantity'] * -1
            }]
            # else:
            #     ods = [{'ProductId': 0}]
            if orders.get(code) is None:
                orders.update({
                    code:{
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date,
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': 0,
                        'Discount': 0,
                        'OrderDetails': ods,
                        'PaymentMethods': [{'Name': 'CASH', 'Value': total}]
                    }
                })
            else:
                orders[code]['Total'] += total
                orders[code]['TotalPayment'] += total
                # orders[code]['Discount'] += discount
                orders[code]['PaymentMethods'] = [{
                    'Name': 'CASH',
                    'Value': orders[code]['Total']
                }]
                orders[code]['OrderDetails'].extend(ods)
        for _, order in orders.items():
            # print(order)
            submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
            pm = {
                'Code': f'{order["Code"]}-CASH',
                'OrderCode': order["Code"],
                'Amount': order["Total"],
                'TransDate': order["PurchaseDate"],
                'AccountId': 'CASH'
            }
            submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)

    def get_data(self):
        self.login()
        self.get_details()
        self.get_orders()
        self.get_returns()
        return

# x = 29
# while x < 60:
#     INOCHI_AMHD(datetime.now() - timedelta(days=x)).get_data()
#     x += 1
