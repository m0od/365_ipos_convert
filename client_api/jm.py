import sys
sys.path.append('/home/blackwings/365ipos')
import requests
import json
from requests_toolbelt import MultipartEncoder
from pos_api.adapter import submit_order, submit_error


class JM(object):
    def __init__(self):
        self.ACCESS_TOKEN = None
        self.ADAPTER_RETAILER = 'jm_aeonhd'
        # self.ADAPTER_RETAILER = 'retry'
        self.ADAPTER_TOKEN = '9691940f7835e84077bc89d548fa86dc7c70e6268ada508cee2cd033e025cb37'
        # self.ADAPTER_TOKEN = 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
        self.MAIN = 'https://nhanh.vn'
        self.VERSION = '2.0'
        self.APPID = '73116'
        self.USERNAME = 'cht_hn10'
        self.PASSWORD = 'jm246810'
        self.SECRET_KEY = '1N9GyG9askOH1fGpxGu5sLKlOStK4DJLNyJxNp0gZpRxAiFwyR6rt92MLZDqVDFl' \
                          'GAEeERDKNLQAC50nYnnwURXoZUOjmtnrLm09SHVcJjqjv7IRu24edOHYb6YfPbXR'
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
        if not self.oauth():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='Request Oauth Fail')
            return False
        if not self.access_code():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='Get ACCESS_CODE Fail')
            return False
        if not self.access_token():
            submit_error(retailer=self.ADAPTER_RETAILER, reason='Get ACCESS_TOKEN Fail')
            return False
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

    def get_data(self, from_date):
        if not self.auth(): return False
        for did in self.DEPOT_ID:
            page = 1
            while True:
                try:
                    data = {
                        'version': self.VERSION,
                        'appId': self.APPID,
                        'businessId': self.BUSINESS_ID,
                        'accessToken': self.ACCESS_TOKEN,
                        'data': json.dumps({
                            'fromDate': from_date,
                            'toDate': from_date,
                            'depotId': str(did),
                            'icpp': '20',
                            'mode': '2',
                            'page': str(page)
                        })
                    }
                    m = MultipartEncoder(fields=data)
                    self.browser.headers.update({'content-type': m.content_type})
                    res = self.browser.post(f'{self.API}/api/bill/search', data=m)
                    js = res.json()
                    if (len(js) == 0): break
                    for raw_code, bill in js['data']['bill'].items():
                        if bill['type'] == '1':
                            minus = -1
                            code = f'VAT_{raw_code}'
                        else:
                            minus = 1
                            code = raw_code
                        pm = []
                        if int(bill['creditMoney']) > 0:
                            pm.append({'Name': 'THẺ', 'Value': bill['creditMoney'] * minus})
                        if int(bill['moneyTransfer']) > 0:
                            pm.append({'Name': 'CHUYỂN KHOẢN', 'Value': bill['moneyTransfer'] * minus})
                        if int(bill['cash']) > 0:
                            pm.append({'Name': 'CASH', 'Value': bill['cash'] * minus})
                        od = []
                        for pc, pv in bill['products'].items():
                            od.append({
                                'Code': pv['code'].strip(),
                                'Name': pv['name'].strip(),
                                'Price': pv['money'],
                                'Quantity': int(pv['quantity'])
                            })

                        data = {
                            'Code': raw_code,
                            'Total': bill['money'],
                            'TotalPayment': bill['money'],
                            'PaymentMethods': pm,
                            'VAT': 0,
                            'Discount': int(bill['discount']),
                        }
                        if minus == 1:
                            data.update({
                                'Status': 2,
                                'OrderDetails': od,
                                'PurchaseDate': bill['createdDateTime'],
                            })
                            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                        else:
                            data.update({
                                'Status': 0,
                                'ReturnDetails': od,
                                'ReturnDate': bill['createdDateTime'],
                            })
                            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                            data = {
                                'Code': code,
                                'Total': 0,
                                'TotalPayment': 0,
                                'PaymentMethods': pm,
                                'Discount': 0,
                                'Status': 2,
                                'VAT': 0,
                                'AdditionalServices': [{'Name': 'Hoàn VAT', 'Value': bill['money']*minus}],
                                'PurchaseDate': bill['createdDateTime'],
                                'OrderDetails': []
                            }
                            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=data)
                    if page == js['data']['totalPages']:
                        break
                    page += 1
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=f'[Fetch Data] {str(e)}')
                    pass

# JM().get_data('2023-05-08')