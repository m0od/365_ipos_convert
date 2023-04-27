import sys
sys.path.append('/home/blackwings/365ipos')
from pos_api.adapter import submit_order, submit_error
import requests
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")


class Boo(object):

    def __init__(self):
        self.ADAPTER_RETAILER = 'boo_aeonhd'
        self.ADAPTER_TOKEN = '1066c597a758f4b4ba92d6ba46ec207a53a0fc471e23566f4c00f0c40d98d422'
        self.API = 'https://odoo.boo.vn'
        self.TOKEN = 'b75d4ddd-65b2-4841-80a5-f8269ad26078'
        self.STORE = '1.1.3.OPS.077'
        self.orders = {}
        self.returns = {}
        self.browser = requests.session()

    def get_data(self, d_to=None):
        self.fetch_orders(d_to)
        self.filter_cancel(d_to)
        self.fetch_details(d_to)

    def fetch_orders(self, d_to=None):
        offset = 0
        while True:
            try:
                p = {
                    # 'time_start': dFrom.strftime('%d/%m/%Y'),
                    'time_end': (datetime.now() - timedelta(days=1)).date().strftime('%d/%m/%Y'),
                    'access_token': self.TOKEN,
                    'store': self.STORE,
                    'offset': str(offset),
                    'limit': '100'
                }
                self.browser.headers.update({'Content-Type': 'application/json'})
                res = self.browser.get(f'{self.API}/order-data-warehouse', params=p, json={}).json()
                # print(res)
                orders = res['result']['order']
                if len(orders) == 0: break
                for order in orders:
                    type = order['type']
                    code = order['order_num']
                    if type == 'Cancel': continue
                    pd = datetime.strptime(order['order_time'], '%Y-%m-%d %H:%M:%S')
                    if pd.date() > d_to.date():
                        continue
                    if pd.date() < d_to.date():
                        return

                    total = int(order['total_amount'])
                    self.orders.update({
                        code: {
                            # 'type': type,
                            'Code': code,
                            'Status': 2,
                            'PurchaseDate': pd.strftime('%Y-%m-%d %H:%M:%S'),
                            'Total': total,
                            'TotalPayment': total,
                            'VAT': 0,
                            'Discount': 0,
                            'OrderDetails': [],
                            'PaymentMethods': [{'Name': 'CASH', 'Value': total}]
                        }
                    })
                offset += 100
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Order] {str(e)}')
                pass

    def filter_cancel(self, d_to=None):
        offset = 0
        while True:
            # print(88, offset)
            try:
                p = {
                    # 'time_start': dFrom.strftime('%d/%m/%Y'),
                    'time_end': (datetime.now() - timedelta(days=1)).date().strftime('%d/%m/%Y'),
                    'access_token': self.TOKEN,
                    'store': self.STORE,
                    'offset': str(offset),
                    'limit': '100'
                }
                self.browser.headers.update({'Content-Type': 'application/json'})
                res = self.browser.get(f'{self.API}/order-data-warehouse', params=p, json={}).json()
                # print(res)
                orders = res['result']['order']
                if len(orders) == 0: break
                for order in orders:
                    type = order['type']
                    pd = datetime.strptime(order['order_time'], '%Y-%m-%d %H:%M:%S')
                    # print(pd.date(), dTo.date(), pd.date() < dTo.date())
                    if pd.date() > d_to.date():
                        continue
                    if pd.date() < d_to.date():
                        return
                    if type != 'Cancel': continue
                    code = order['reference_order_id']
                    if code is not None:
                        try:
                            self.orders.pop(code)
                        except:
                            pass
                offset += 100
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Filter Cancel] {str(e)}')
            # self.LOCAL.put_order(js)

    def fetch_details(self, d_to=None):
        self.filter_cancel(d_to)
        offset = 0
        while True:
            # print(offset)
            try:
                p = {
                    'time_start': d_to.strftime('%d/%m/%Y'),
                    'time_end': d_to.strftime('%d/%m/%Y'),
                    'access_token': self.TOKEN,
                    'store': self.STORE,
                    'offset': str(offset),
                    'limit': '100'
                }
                self.browser.headers.update({'Content-Type': 'application/json'})
                res = self.browser.get(f'{self.API}/order-detail-data-warehouse', params=p, json={}).json()
                orders = res['result']['order']
                if len(orders) == 0: break
                for detail in orders:
                    code = detail['order_num']
                    qty = int(detail['quantity'])
                    item = {
                        'Code': detail['sku'].strip(),
                        'Name': detail['item_code'].strip(),
                        'Price': int(int(detail['amount']) / qty),
                        'Quantity': qty
                    }
                    if self.orders.get(code) is not None:
                        od = self.orders[code]['OrderDetails']
                        od.append(item)
                        self.orders[code]['Discount'] = self.orders[code]['Discount'] + int(detail['discount_amount'])
                        self.orders[code]['OrderDetails'] = od
                    # if self.returns.get(code) is not None:
                    #     od = json.loads(self.returns[code]['od'])
                    #     od.append(item)
                    #     self.returns[code]['od'] = json.dumps(od)
                offset += 100
            except Exception as e:
                submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Order Detail] {str(e)}')
        # self.print_o_r()
        for _, js in self.orders.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=js)
            # print(json.dumps(js))
            # break
