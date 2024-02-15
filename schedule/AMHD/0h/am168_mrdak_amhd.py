import sys
from datetime import datetime, timedelta
from os.path import dirname

import requests


class AM168(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'mrdak_amhd'
        self.ADAPTER_TOKEN = '70f8a0a869f2ca7b25f9b68bdc86f374a2f541dc4e872a55118734c0c89bd112'
        self.API = 'https://fnb.mysapo.vn'

        self.ORDERS = {}
        self.DETAILS = {}
        self.TENANT = None
        self.ACCOUNT = 'ketoan123'
        self.PASSWORD = 'Aeonhd@123'
        self.PHONE = '0379462994'
        self.DATE = datetime.now() - timedelta(days=1)
        self.TOKEN = None

    def login(self):
        from pos_api.adapter import submit_order, submit_error
        try:
            self.browser = requests.session()
            js = {
                'phone': self.PHONE,
                'username': self.ACCOUNT,
                'password': self.PASSWORD
            }
            r = self.browser.post(f'{self.API}/admin/staffs/xauth.json', json=js)

            store = r.json()['stores'][0]
            self.browser.headers.update({
                'x-fnb-token': store['token'],
                'x-store-id': str(store['store']['server_id']),
                'x-merchant-id': str(store['merchant']['server_id'])
            })
            return True
        except Exception as e:
            submit_error(self.ADAPTER_RETAILER, reason=str(e))
            return False

    def get_orders(self):
        from pos_api.adapter import submit_order, submit_error
        page = 1
        while True:
            since = self.DATE.replace(hour=0, minute=0, second=0, microsecond=0)
            until = self.DATE.replace(hour=23, minute=59, second=59, microsecond=0)
            params = {
                'from': str(int(since.timestamp())),
                'to': str(int(until.timestamp())),
                # 'order_status': 'completed',
                # 'from': 'unreturned',
                # 'to': 'by_completed',
                'page': str(page),
                'limit': '50',

            }
            # print(params)
            try:
                r = self.browser.get(f'{self.API}/admin/orders.json', params=params, timeout=10)
                # print(65, r.text)
            except:
                continue
            orders = r.json()['orders']
            if not len(orders): break
            for _ in orders:
                if _['status'] != 'completed': continue
                print(_['name'], _['status'])
                pur_date = datetime.fromtimestamp(_['order_time'])
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                # print(pur_date)
                total = _['total_price']
                discount = _['total_discount']
                vat = _['taxes'][0]['taxed_value']
                ods = []
                for item in _['items']:
                    ods.append({
                        'Code': item['item_id'].strip(),
                        'Name': item['item_name'].strip(),
                        'Price': item['quantity'],
                        'Quantity': item['variant']['unit_price']
                    })
                pms = []
                for item in _['payments']:
                    name = item['payment_method_name'].upper()
                    if name == 'TIỀN MẶT': name = 'CASH'
                    pms.append({
                        'Name': name,
                        'Value': item['money_collected']
                    })
                orders = {
                    'Code': _['name'],
                    'Status': 2,
                    'PurchaseDate': pur_date,
                    'Total': total,
                    'TotalPayment': total,
                    'VAT': vat,
                    'Discount': discount,
                    'OrderDetails': ods,
                    'PaymentMethods': pms
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, orders)
            page += 1

    # def get_details(self):
    #     from pos_api.adapter import submit_order, submit_error
    #     try:
    #         r = self.browser.get(f'{self.API}/admin/analytics/sale_orders/statistical_order')
    #         token = r.text.split('token&quot;:&quot;')[1].split('&quot;')[0]
    #         time = self.DATE.strftime('%Y-%m-%d')
    #         query = ['SHOW', 'quantity,', 'price', 'BY', 'variant_name,', 'variant_sku,', 'order_code']
    #         query += ['FROM', 'orders']
    #         query += ['WHERE', 'return_status', '==', '"Chưa trả hàng"']
    #         query += ['SINCE', time, 'UNTIL', time]
    #         query += ['LIMIT', '10000']
    #
    #         params = {
    #             'token': token,
    #             'q': ' '.join(query),
    #             'beta': 'true',
    #             'options': 'time:"completed_at"',
    #             'timezone': 'Asia/Ho_Chi_Minh'
    #         }
    #         # print(params['q'])
    #         self.browser.headers.update({
    #             'x-sapo-tenantid': str(self.TENANT)
    #         })
    #         r = self.browser.get('https://analytics.sapo.vn/query', params=params)
    #         # print(r.text)
    #         headers = []
    #         for _ in r.json()['result']['columns']:
    #             headers.append(_['field'])
    #         for _ in r.json()['result']['data']:
    #             data = dict(zip(headers, _))
    #             if not self.DETAILS.get(data['order_code']):
    #                 self.DETAILS.update({
    #                     data['order_code']: [{
    #                         'Code': data['variant_sku'].strip(),
    #                         'Name': data['variant_name'].strip(),
    #                         'Price': data['price'],
    #                         'Quantity': data['quantity']
    #                     }]
    #                 })
    #             else:
    #                 self.DETAILS[data['order_code']].append({
    #                     'Code': data['variant_sku'].strip(),
    #                     'Name': data['variant_name'].strip(),
    #                     'Price': data['price'],
    #                     'Quantity': data['quantity']
    #                 })
    #         # print(self.DETAILS)
    #     except Exception as e:
    #         submit_error(self.ADAPTER_RETAILER, reason=f'get_details {str(e)}')
    #
    # def get_returns(self):
    #     r = self.browser.get(f'{self.API}/admin/analytics/sale_orders/return_by_order')
    #     token = r.text.split('token&quot;:&quot;')[1].split('&quot;')[0]
    #     time = self.DATE.strftime('%y-%m-%d')
    #     query = ['SHOW', 'returns', 'BY', 'order_code,', 'sale_kind']
    #     query += ['FROM', 'sales', 'WHERE', 'sale_kind', '==', '"Trả hàng"']
    #     query += ['SINCE', time, 'UNTIL', time, 'ORDER', 'BY', 'returns', 'DESC']
    #     query += ['LIMIT', '10000']
    #     params = {
    #         'token': token,
    #         'q': ' '.join(query),
    #         'beta': 'true',
    #         'o': 'time:"completed_at"',
    #         'timezone': 'Asia/Ho_Chi_Minh'
    #     }
    #     'https://inochishop.mysapogo.com/admin/analytics/sale_orders/return_by_order'

    def get_data(self):
        self.login()
        # self.get_details()
        self.get_orders()
        # return

# x = 29
# while x < 60:
#     INOCHI_AMHD(datetime.now() - timedelta(days=x)).get_data()
#     x += 1
