from datetime import datetime
from os.path import dirname

import requests
import json

from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder


class JM(object):
    def __init__(self):
        self.ACCESS_TOKEN = None
        self.ADAPTER_RETAILER = 'jm_aeonhd'
        # self.ADAPTER_RETAILER = 'retry'
        self.ADAPTER_TOKEN = '9691940f7835e84077bc89d548fa86dc7c70e6268ada508cee2cd033e025cb37'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.MAIN = 'https://nhanh.vn'
        self.VERSION = '2.0'
        self.APPID = '73543'
        self.USERNAME = 'cht_hn10'
        self.PASSWORD = 'jm246810'
        self.SECRET_KEY = 'fobDBuxWyFrfKyjZEIy2FSJYVftb0uXEVGcS83ywEfHwS8p6VaKgMNkZqlnEsG6M' \
                          'iV4ZaxFTGGBo4XD2jQSSrBx8WR3vFyCuaqriOnX1AnokQ0W3qhUTbXseWjejiWFt'
        self.API = 'https://open.nhanh.vn'
        self.browser = requests.session()
        self.RETURN_LINK = 'https://pos365.vn'
        self.NUC_TK = None
        self.STORE_ID = None
        self.ACCESS_CODE = None
        self.BUSINESS_ID = None
        self.DEPOT_ID = None
        self.CSRF = None
        # self.ROUTE = 'jm'
        self.METHOD = {
            'Quẹt thẻ': 'THẺ',
            'Tiền khách đưa': 'CASH',
            'Chuyển khoản': 'CHUYỂN KHOẢN',
            'Tiền chuyển khoản trả khách': 'CHUYỂN KHOẢN',
            'Tiền mặt trả khách': 'CASH'
        }

    def get_login_page(self):
        try:
            res = self.browser.get(f'{self.MAIN}/signin')
            if res.status_code != 200: return False
            self.CSRF = res.text.split('name="csrf" value="')[1].split('"')[0].strip()
            if len(self.CSRF) > 0: return True
            return False
        except:
            return False

    def login(self):
        try:
            data = {
                'csrf': self.CSRF,
                'username': self.USERNAME,
                'password': self.PASSWORD
            }
            m = MultipartEncoder(fields=data)
            self.browser.headers.update({'content-type': m.content_type})
            res = self.browser.post(f'{self.MAIN}/signin', data=m)
            if res.status_code != 200: return False
            if not res.url.endswith('/admin'): return False
            # print(res.text)
            self.STORE_ID = res.text.split('id="storeId" value="')[1].split('"')[0]
            if len(self.STORE_ID) > 0: return True
            return False
        except:
            return False

    def auth(self):
        if not self.get_login_page():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='Get Login Page Fail')
            return False
        if not self.login():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='Login Fail')
            return False
        # if not self.oauth():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='Request Oauth Fail')
        #     return False
        # if not self.access_code():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='Get ACCESS_CODE Fail')
        #     return False
        # if not self.access_token():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='Get ACCESS_TOKEN Fail')
        #     return False
        return True

    def oauth(self):
        try:
            data = {
                'version': self.VERSION,
                'appId': self.APPID,
                'returnLink': self.RETURN_LINK,
            }
            res = self.browser.get(f'{self.MAIN}/oauth', params=data)
            if res.status_code != 200: return False
            self.NUC_TK = res.text.split('data-nuctk="')[1].split('"')[0]
            if len(self.NUC_TK) > 0: return True
            return False
        except:
            return False

    def access_code(self):
        try:
            data = {
                'appId': self.APPID,
                'returnLink': self.RETURN_LINK,
                'permissions[]': [
                    'pos.orderList', 'pos.orderHistory',
                    'pos.billList', 'pos.billmex', 'pos.billRequirement',
                ],
                'storeId': self.STORE_ID,
                'nuctk': self.NUC_TK
            }
            self.browser.headers.update({'content-type': 'application/x-www-form-urlencoded'})
            res = self.browser.post(f'{self.MAIN}/openapi/addaccesscode', data=data)
            print(res.text)
            if res.status_code != 200: return False
            self.ACCESS_CODE = res.json()['redirect'].split('accessCode=')[1]
            if len(self.ACCESS_CODE) > 0: return True
            return False
        except:
            return False

    def access_token(self):
        try:
            data = {
                'version': self.VERSION,
                'appId': self.APPID,
                'accessCode': self.ACCESS_CODE,
                'secretKey': self.SECRET_KEY,
            }
            m = MultipartEncoder(fields=data)
            self.browser.headers.update({'content-type': m.content_type})
            res = self.browser.post(f'{self.MAIN}/oauth/access_token', data=m)
            if res.status_code != 200: return False
            self.ACCESS_TOKEN = res.json()['accessToken']
            self.BUSINESS_ID = str(res.json()['businessId'])
            self.DEPOT_ID = res.json()['depotIds']
            if len(self.ACCESS_TOKEN) > 0: return True
            return False
        except:
            return False

    def get_returns(self, from_date):
        page = 1
        returns = {}
        while page > 0:
            p = {
                'storeId': self.STORE_ID,
                'fromDate': from_date,
                'toDate': from_date,
                'page': str(page)
            }
            r = self.browser.get(f'{self.MAIN}/pos/return/index', params=p)
            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            if len(tbody) == 0: break
            code = None
            for _ in tbody[:-1]:
                try:
                    code = _.find('td', {'class': 'dgColId'}).a.text.strip()
                    if returns.get(code) is not None:
                        page = -1
                        break
                    r_date = _.find('td', {'class': 'dgColDate'})['title']
                    r_date = r_date[r_date.index(':') + 1:].strip()
                    r_date = datetime.strptime(r_date, '%d/%m/%Y %H:%M:%S')
                    returns.update(
                        {code: {'Code': code, 'ReturnDetails': [], 'ReturnDate': r_date.strftime('%Y-%m-%d %H:%M:%S')}})
                except:
                    pass
                try:
                    rds = returns[code]['ReturnDetails']
                    rd = _.find('td', {'class': 'dgColProduct'})
                    p_code = rd.span.text.strip()
                    rds.append({
                        'Code': p_code[1:-1],
                        'Name': rd.text.strip().replace(p_code, '').strip(),
                        'Price': _.find('td', {'class': 'dgColProductPrice'}).text.strip(),
                        'Quantity': _.find('td', {'class': 'dgColQuantity'}).text.strip()
                    })
                    returns[code].update({'ReturnDetails': rds})
                except:
                    pass
                raw = _.findAll('td', {'class': 'text-right'})
                try:
                    discount = raw[3].text.strip().split('(')[0].strip().replace('.', '')
                    if len(discount) == 0: discount = 0
                    pms = [{'Name': self.METHOD.get(raw[4].i['title'].strip()),
                            'Value': int(raw[4].text.strip().replace('.', ''))}]
                    total = raw[6].text.strip().replace('.', '').strip()
                    if len(total) == 0: total = 0
                    returns[code].update({
                        'Discount': int(discount),
                        'PaymentMethods': pms,
                        'Total': int(total),
                        'TotalPayment': int(total),
                        'VAT': 0,
                        'Status': 0
                    })
                except:
                    pass
            page += 1
        for k, v in returns.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
            data = {
                'Code': f'VAT_{v["Code"]}',
                'Total': 0,
                'TotalPayment': 0,
                'PaymentMethods': [],
                'Discount': 0,
                'Status': 2,
                'VAT': 0,
                'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': v['Total'] * -1}],
                'PurchaseDate': v['ReturnDate'],
                'OrderDetails': []
            }
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)

    def get_orders(self, from_date):
        page = 1
        code = None
        orders = {}
        while page > 0:
            p = {
                'storeId': self.STORE_ID,
                'fromDate': from_date,
                'toDate': from_date,
                'page': str(page)
            }
            r = self.browser.get(f'{self.MAIN}/pos/bill/index', params=p)
            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            for _ in tbody[:-1]:
                pms = []
                try:
                    code = _['data-id']
                    if orders.get(code) is not None:
                        page = -1
                        break
                    else:
                        orders.update({code: {'OrderDetails': []}})
                except:
                    pass
                try:
                    ods = orders[code]['OrderDetails']
                    product = _.find('td', {'class': 'dgColProduct dgColProduct'})
                    pn = product.text.split('(')[0].strip()
                    product.unwrap()
                    pc = _.find('span', {'class': 'dgColCode'}).text.strip()[1:-1].strip()
                    price_qty = _.findAll('td', {'class': 'text-right dgColProduct'})
                    price = price_qty[0].text.strip().replace('.', '').split(' ')[0].strip()
                    if len(price) == 0:
                        price = 0
                    else:
                        price = int(price)
                    ods.append({
                        'Code': pc,
                        'Name': pn,
                        'Price': price,
                        'Quantity': int(price_qty[1].text.strip())
                    })
                    orders[code].update({
                        'Code': code,
                        'OrderDetails': ods
                    })
                    for i in price_qty:
                        i.unwrap()
                except:
                    pass
                try:
                    _.find('td', {'class': 'dgColVat'}).unwrap()
                    x = _.find('td', {'class': 'dgColPayment'})
                    dup = []
                    for pm in x.findAll('label'):
                        pn = pm['title'].split(':')[0]
                        pn = self.METHOD.get(pn)
                        if pn not in dup:
                            dup.append(pn)
                            pms.append({'Name': self.METHOD.get(pn), 'Value': int(pm.text.strip().replace('.', ''))})
                    x.unwrap()
                    dis_total = _.findAll('td', {'class': 'text-right'})
                    discount = dis_total[0].text.strip().split('(')[0].strip().replace('.', '')
                    if len(discount) == 0: discount = '0'
                    total = dis_total[1].text.strip().split('(')[0].strip().replace('.', '')
                    orders[code].update({
                        'Discount': int(discount),
                        'Total': int(total),
                        'TotalPayment': int(total),
                        'PaymentMethods': pms,
                        'Status': 2,
                        'VAT': 0,
                        'PurchaseDate': _.find('td', {'class': 'dgColDate'}).find('span')['title']
                    })
                except:
                    pass
            page += 1
            # break
        for k, v in orders.items():
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)

    def get_data(self, from_date):
        if not self.auth(): return False
        from_date = from_date.strftime('%d/%m/%Y')
        self.get_orders(from_date)
        self.get_returns(from_date)

    # def get_data(self, from_date):
    #     if not self.auth(): return False
    #     for did in self.DEPOT_ID:
    #         page = 1
    #         while True:
    #             try:
    #                 data = {
    #                     'version': self.VERSION,
    #                     'appId': self.APPID,
    #                     'businessId': self.BUSINESS_ID,
    #                     'accessToken': self.ACCESS_TOKEN,
    #                     'data': json.dumps({
    #                         'fromDate': from_date,
    #                         'toDate': from_date,
    #                         'depotId': str(did),
    #                         'icpp': '20',
    #                         'mode': '2',
    #                         'page': str(page)
    #                     })
    #                 }
    #                 m = MultipartEncoder(fields=data)
    #                 self.browser.headers.update({'content-type': m.content_type})
    #                 res = self.browser.post(f'{self.API}/api/bill/search', data=m)
    #                 js = res.json()
    #                 if (len(js) == 0): break
    #                 for raw_code, bill in js['data']['bill'].items():
    #                     if bill['type'] == '1':
    #                         minus = -1
    #                         code = f'VAT_{raw_code}'
    #                     else:
    #                         minus = 1
    #                         code = raw_code
    #                     pm = []
    #                     if int(bill['creditMoney']) > 0:
    #                         pm.append({'Name': 'THẺ', 'Value': bill['creditMoney'] * minus})
    #                     if int(bill['moneyTransfer']) > 0:
    #                         pm.append({'Name': 'CHUYỂN KHOẢN', 'Value': bill['moneyTransfer'] * minus})
    #                     if int(bill['cash']) > 0:
    #                         pm.append({'Name': 'CASH', 'Value': bill['cash'] * minus})
    #                     od = []
    #                     for pc, pv in bill['products'].items():
    #                         od.append({
    #                             'Code': pv['code'].strip(),
    #                             'Name': pv['name'].strip(),
    #                             'Price': pv['money'],
    #                             'Quantity': int(pv['quantity'])
    #                         })
    #
    #                     data = {
    #                         'Code': raw_code,
    #                         'Total': bill['money'],
    #                         'TotalPayment': bill['money'],
    #                         'PaymentMethods': pm,
    #                         'VAT': 0,
    #                         'Discount': int(bill['discount']),
    #                     }
    #                     if minus == 1:
    #                         data.update({
    #                             'Status': 2,
    #                             'OrderDetails': od,
    #                             'PurchaseDate': bill['createdDateTime'],
    #                         })
    #                         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
    #                     else:
    #                         data.update({
    #                             'Status': 0,
    #                             'ReturnDetails': od,
    #                             'ReturnDate': bill['createdDateTime'],
    #                         })
    #                         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
    #                         data = {
    #                             'Code': code,
    #                             'Total': 0,
    #                             'TotalPayment': 0,
    #                             'PaymentMethods': pm,
    #                             'Discount': 0,
    #                             'Status': 2,
    #                             'VAT': 0,
    #                             'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': bill['money'] * minus}],
    #                             'PurchaseDate': bill['createdDateTime'],
    #                             'OrderDetails': []
    #                         }
    #                         submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
    #                 if page == js['data']['totalPages']:
    #                     break
    #                 page += 1
    #             except Exception as e:
    #                 submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Data] {str(e)}')
    #                 pass



if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    # JM().get_orders('')
