from datetime import datetime, timedelta

import requests
import json
from os.path import dirname
from requests_toolbelt import MultipartEncoder
from bs4 import BeautifulSoup

class ATZ(object):
    def __init__(self):
        self.ACCESS_TOKEN = None
        self.ADAPTER_RETAILER = 'atz_aeonhd'
        self.ADAPTER_TOKEN = 'bf7d42474649167185485a1ffabb1e2fc5f02ed7f55a19ee19e18a3411c5959c'
        self.MAIN = 'https://nhanh.vn'
        self.VERSION = '2.0'
        self.APPID = '73156'
        self.USERNAME = 'adminamhd'
        self.PASSWORD = '123456'
        self.SECRET_KEY = 'CUHr6fNfDcSHTUFiyvKwZB1xVJE5N6gUGJlON0liBH8SVaj53sfZIzaQxMM5hSpk' \
                          'qTazhEaN4xR5GvzDcapQRVDwlqggKsdnDDwzgApsgPu5SmszAWHSllEJUSNLlJZ2'
        self.API = 'https://open.nhanh.vn'
        self.browser = requests.session()
        self.RETURN_LINK = 'https://pos365.vn'
        self.NUC_TK = None
        self.STORE_ID = None
        self.ACCESS_CODE = None
        self.BUSINESS_ID = None
        self.DEPOT_ID = None
        self.CSRF = None
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
            submit_error(retailer=self.ADAPTER_RETAILER, reason='[Get Login Page Fail]')
            return False
        if not self.login():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='[Login Fail]')
            return False
        # if not self.oauth():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='[Request Oauth Fail]')
        #     return False
        # if not self.access_code():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='[Get ACCESS_CODE Fail]')
        #     return False
        # if not self.access_token():
        #     submit_error(retailer=self.ADAPTER_RETAILER, reason='[Get ACCESS_TOKEN Fail]')
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
            # print(page)
            p = {
                'storeId': self.STORE_ID,
                'fromDate': from_date,
                'toDate': from_date,
                'page': str(page)
            }
            # print(p)
            r = self.browser.get(f'{self.MAIN}/pos/return/index', params=p)

            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            if len(tbody) == 0: break
            # print(tbody)
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
            # print(page)
            p = {
                'storeId': self.STORE_ID,
                'fromDate': from_date,
                'toDate': from_date,
                'page': str(page)
            }
            r = self.browser.get(f'{self.MAIN}/pos/bill/index', params=p)
            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            if len(tbody) == 0: break
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
                    try:
                        for pm in x.findAll('label'):
                            pn = pm['title'].split(':')[0]
                            pn = self.METHOD.get(pn)
                            if pn not in dup:
                                dup.append(pn)
                                pms.append({'Name': pn, 'Value': int(pm.text.strip().replace('.', ''))})
                        x.unwrap()
                    except:
                        pass
                    if len(pms) == 0:
                        pms.append({'Name': 'CASH', 'Value': 0})
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
                except Exception as e:
                    # print(e)
                    pass
            page += 1
            # break
        for k, v in orders.items():
            # print(v)
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)

    def get_data(self, from_date):
        if not self.auth(): return False
        from_date = from_date.strftime('%d/%m/%Y')
        self.get_orders(from_date)
        self.get_returns(from_date)



if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
    # ATZ().get_data(datetime.now() - timedelta(days=1))
