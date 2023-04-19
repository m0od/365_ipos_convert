import requests
import json
from model import db, TenAntConfig


class API(object):
    def __init__(self, domain, cookie=None, user=None, password=None):
        self.browser = requests.session()
        # self.browser.verify = False
        self.browser.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.cookie = cookie
        if self.cookie is not None:
            self.browser.cookies.update({'ss-id': self.cookie})
        self.domain = domain
        self.user = user
        self.password = password
        self.base_url = f'https://{self.domain}.pos365.vn'


    def check_login(self):
        try:
            res = self.browser.get(self.base_url + '/Config/VendorSession')
            if len(res.text) == 0:
                return True
        except Exception as e:
            pass
        return False


    def auth(self):
        try:
            data = json.dumps({
                'Username': self.user,
                'Password': self.password
            })
            res = self.browser.post(self.base_url + '/api/auth', data=data).json()
            if res.get('SessionId') is not None:
                return res.get('SessionId')
        except Exception as e:
            pass
        return None

    def order_void(self, id):
        try:
            res = self.browser.delete(self.base_url + f'/api/orders/{str(id)}/void')
            if res.status_code == 401:
                session = self.auth()
                return {'status': 0, 'ck': session}
            elif res.status_code == 400:
                return {'status': 1, 'message': str(res.json())}
            elif res.status_code == 200:
                return {'status': 2, 'message': res.json()}
            else:
                return {'status': 1, 'message': 'Unknown'}
        except Exception as e:
            return {'status': 1, 'message': str(e)}

    def order_save(self, order):
        try:
            try:
                del order['Order']['PaymentMethods']
            except:
                pass
            try:
                del order['Order']['AdditionalServices']
            except:
                pass
            data = json.dumps(order)
            res = self.browser.post(self.base_url + '/api/orders', data=data)
            if res.status_code == 401:
                session = self.auth()
                return {'status': 0, 'ck': session}
            elif res.status_code == 500:
                return {'status': 1, 'message': res.json()}
            elif res.status_code == 400:
                if order['Order']['Code'] in res.json().get('ResponseStatus').get('Message'):
                    return {'status': 3}
                else:
                    return {'status': 1, 'message': res.json()}
            elif res.status_code == 200:
                return {'status': 2, 'message': res.json()}
            else:
                return {'status': 1, 'message': 'Unknown'}

        except Exception as e:
            return {'status': 1, 'message': str(e)}


    def order_get(self, code):
        try:
            params = {
                'format': 'json',
                '$top': '50',
                '$filter': f"substringof('{code}',Code)"
            }
            res = self.browser.get(self.base_url + '/api/orders', params=params).json()
            for i in res['results']:
                if i['Code'] == code:
                    return i['Id']
        except:
            return None

    def product_save(self, code, name):
        while True:
            try:
                data = json.dumps({
                    'Product': {
                        'Id': 0,
                        'Code': code,
                        'Name': name
                    }
                })
                res = self.browser.post(self.base_url + '/api/products', data=data)
                if res.status_code == 401:
                    session = self.auth()
                    return {'status': False, 'ck': session}
                elif res.status_code == 400:
                    gpc = self.get_product_by_code(code)
                    if gpc['status'] is True:
                        return {'status': True, 'Id': gpc['pid']}
                elif res.status_code == 200:
                    return {'status': True, 'Id': res.json()['Id']}
            except: pass

    def account_save(self, name):
        try:
            data = json.dumps({
                'Account': {
                    "Id": 0,
                    "Name": name
                }
            })
            res = self.browser.post(self.base_url + '/api/accounts', data=data)
            if res.status_code == 401:
                session = self.auth()
                return {'status': False, 'ck': session}

            else:
                response = res.json()
                if response.get('Id') is None:
                    response = {}
                    response['Id'] = self.account_list()['accounts'][name]
                response['status'] = True
                return response
        except Exception as e:
            return {'status': False, 'message': str(e)}

    def get_product_by_code(self, code):
        try:
            p = {
                'code': code
            }
            res = self.browser.get(self.base_url + '/api/products/getbycode', params=p)
            if res.status_code == 401:
                session = self.auth()
                return {'status': False, 'ck': session}
            elif res.status_code == 204:
                return {'status': True, 'pid': 0}
            elif res.status_code == 200:
                return {'status': True, 'pid': int(res.json()['Id'])}
            return {'status': False, 'message': res.status_code}

        except Exception as e:
            return {'status': False, 'message': str(e)}

    def account_list(self):
        try:
            res = self.browser.get(self.base_url + '/api/accounts', params={'format': 'json'})
            if res.status_code == 401:
                session = self.auth()
                return {'status': False, 'ck': session}
            else:
                accounts = {}
                for i in res.json():
                    accounts[i['Name'].upper()] = i['Id']
                return {'status': True, 'accounts': accounts}
        except Exception as e:
            return {'status': False, 'message': str(e)}