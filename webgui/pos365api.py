import requests
import json

from pymongo import MongoClient

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
        self.db = MongoClient('localhost').adapter

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
                return {'status': 1, 'message': f'[{res.status_code}] [DELETE]/api/orders/[id]/void'}
        except Exception as e:
            return {'status': 1, 'message': str(e)}

    def order_save(self, order):
        data = json.dumps(order)
        # while True:
        try:
            res = self.browser.post(self.base_url + '/api/orders', data=data)
            if res.status_code in [500, 403]:
                return {'status': 1, 'message': f'{res.status_code} [POST] /api/orders'}
            elif res.status_code == 401:
                session = self.auth()
                return {'status': 0, 'ck': session}
            elif res.status_code == 400:
                if order['Order']['Code'] in res.json().get('ResponseStatus').get('Message'):
                    return {'status': 3}
                else:
                    return {'status': 1, 'message': res.text}
            elif res.status_code == 200:
                return {'status': 2, 'message': res.json()}
            else:
                return {'status': 1, 'message': 'Unknown'}

        except Exception as e:
            return {'status': 1, 'message': str(e)}

    def return_save(self, bill_return):
        bill_return['Return']['Status'] = 2
        try:
            att = json.loads(bill_return['Return']['MoreAttributes']['PaymentMethods'])
            bill_return['Return']['AccountId'] = att[0]['AccountId']
        except:
            pass
        try:
            del bill_return['Return']['MoreAttributes']
        except:
            pass
        try:
            del bill_return['Return']['PaymentMethods']
        except:
            pass
        try:
            del bill_return['Return']['AdditionalServices']
        except:
            pass

        data = json.dumps(bill_return)
        res = self.browser.post(self.base_url + '/api/returns', data=data)
        if res.status_code == 401:
            session = self.auth()
            return {'status': 0, 'ck': session}
        elif res.status_code == 500:
            return {'status': 1, 'message': f'[{res.status_code}] [POST]/api/returns'}
        elif res.status_code == 400:
            if bill_return['Return']['Code'] in res.json().get('ResponseStatus').get('Message'):
                return {'status': 3}
            else:
                return {'status': 1, 'message': res.text}
        elif res.status_code == 200:
            return {'status': 2, 'message': res.json()}
        else:
            return {'status': 1, 'message': 'Unknown'}

    def accounting_transaction_get(self, code):
        try:
            params = {
                'format': 'json',
                'Top': '50',
                'Filter': f"Code eq '{code}'"
            }
            res = self.browser.get(self.base_url + '/api/accountingtransaction', params=params)
            if res.status_code != 200:
                return {'status': False, 'err': f'[{res.status_code}] [GET]/api/accountingtransaction'}
            if len(res.json()['results']) > 1:
                transaction = res.json()['results'][-1]
                return {'status': True, 'id': transaction['Id'], 'dup': True}
            for i in res.json()['results']:
                if i['Code'] == code:
                    return {'status': True, 'id': i['Id']}

            return {'status': False, 'err': 'Transaction Not Found'}
        except Exception as e:
            return {'status': False, 'err': str(e)}

    def mongo_oid(self, code):
        try:
            order = self.db.order
            filter = {
                'domain': self.domain,
                'code': code
            }
            q = order.find_one(filter)
            if not q:
                return None
            else:
                return q['id']
        except:
            return None
    def order_get(self, code):
        try:
            # id = self.mongo_oid(code)
            # if id:
            #     return {'status': True, 'id': id}
            params = {
                'format': 'json',
                'Top': '50',
                'Filter': f"Code eq '{code}'"
            }
            res = self.browser.get(self.base_url + '/api/orders', params=params)
            if res.status_code != 200:
                return {'status': False, 'err': f'[{res.status_code}] [GET]/api/orders'}
            if len(res.json()['results']) > 1:
                order = res.json()['results'][-1]
                return {'status': True, 'id': order['Id'], 'dup': True}
            for i in res.json()['results']:
                if i['Code'] == code:
                    return {'status': True, 'id': i['Id']}

            return {'status': False, 'err': 'Order Not Found'}
        except Exception as e:
            return {'status': False, 'err': str(e)}

    def return_get(self, code):
        try:
            params = {
                'format': 'json',
                'Top': '50',
                'Filter': f"substringof('{code}',Code)"
            }
            res = self.browser.get(self.base_url + '/api/returns', params=params)
            if res.status_code != 200:
                return {'status': False, 'err': f'[{res.status_code}] [GET]/api/returns'}
            for i in res.json()['results']:
                if i['Code'] == code:
                    return {'status': True, 'id': i['Id']}
            return {'status': False, 'err': 'Return Not Found'}
        except Exception as e:
            return {'status': False, 'err': str(e)}

    def product_save(self, code, name, price=0):
        try:
            data = json.dumps({
                'Product': {
                    'Id': 0,
                    'Code': code,
                    'Name': name,
                    'Price': price
                }
            })
            res = self.browser.post(self.base_url + '/api/products', data=data)
            if res.status_code == 401:
                return {'status': False, 'err': 'invalid session'}
            elif res.status_code == 400:
                gpc = self.get_product_by_code(code)
                if gpc['status'] is True:
                    return {'status': True, 'Id': gpc['pid']}
                else:
                    return {'status': False, 'err': gpc['err']}
            elif res.status_code == 200:
                return {'status': True, 'Id': res.json()['Id']}
            else:
                return {'status': False, 'err': f'[{res.status_code}] [POST]/api/products'}
        except Exception as e:
            return {'status': False, 'err': str(e)}

    def account_save(self, name):
        try:
            data = json.dumps({
                'Account': {
                    'Id': 0,
                    'Name': name
                }
            })
            res = self.browser.post(self.base_url + '/api/accounts', data=data)
            if res.status_code == 401:
                # session = self.auth()
                return {'status': False, 'err': 'invalid session'}

            else:
                response = res.json()
                if response.get('Id') is None:
                    response = {}
                    response['Id'] = self.account_list()['accounts'][name]
                response['status'] = True
                return response
        except Exception as e:
            return {'status': False, 'err': str(e)}

    def accounting_transaction_save(self, transation):
        transation.update({
            # 'Id': 0,
            'AccountingTransactionType': 1,
        })
        data = {
            'AccountingTransaction': transation
        }
        # while True:
        try:
            res = self.browser.post(self.base_url + '/api/accountingtransaction', json=data)
            if res.status_code in [500, 403]:
                return {'status': 1, 'message': f'{res.status_code} [POST] /api/orders'}
            elif res.status_code == 401:
                session = self.auth()
                return {'status': 0, 'ck': session}
            elif res.status_code == 400:
                return {'status': 1, 'message': res.text}
            elif res.status_code == 200:
                return {'status': 2, 'message': res.json()}
            else:
                return {'status': 1, 'message': res.text.strip()}
        except Exception as e:
            return {'status': 1, 'message': str(e)}

    def get_product_by_code(self, code):
        try:
            p = {
                'code': code
            }
            res = self.browser.get(self.base_url + '/api/products/getbycode', params=p)
            if res.status_code == 401:
                return {'status': False, 'err': 'invalid session'}
            elif res.status_code == 204:
                return {'status': True, 'pid': 0}
            elif res.status_code == 200:
                return {'status': True, 'pid': int(res.json()['Id'])}
            return {'status': False, 'err': f'[{res.status_code}] [GET]/api/products/getbycode'}

        except Exception as e:
            return {'status': False, 'err': str(e)}

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

    def product_list(self, skip, worker=5):
        data = []
        # print(f'order_list {skip}')
        try:
            params = {
                'Top': '50',
                'Skip': str(skip)
            }
            res = self.browser.get(self.base_url + '/api/products', params=params)
            if res.status_code != 200:
                return {'status': 0, 'result': {}}
            if len(res.json()['results']) == 0: return {'status': 1, 'result': {}}
            for product in res.json()['results']:
                priceConfig = {}
                try:
                    priceConfig = json.loads(product.get('PriceConfig'))
                except:
                    pass
                printer = []
                try:
                    if priceConfig.get('SecondPrinter') is not None and len(priceConfig['SecondPrinter'].strip()) > 0:
                        printer.append(priceConfig['SecondPrinter'].strip())
                    if priceConfig.get('Printer3') is not None and len(priceConfig['Printer3'].strip()) > 0:
                        printer.append(priceConfig['Printer3'].strip())
                    if priceConfig.get('Printer4') is not None and len(priceConfig['Printer4'].strip()) > 0:
                        printer.append(priceConfig['Printer4'].strip())
                    if priceConfig.get('Printer5') is not None and len(priceConfig['Printer5'].strip()) > 0:
                        printer.append(priceConfig['Printer5'].strip())
                except:
                    pass
                code = []
                try:
                    if product.get('Code') is not None and len(product['Code'].strip()) > 0:
                        code.append(product['Code'].strip().replace(',', '.'))
                    if product.get('Code2') is not None and len(product['Code2'].strip()) > 0:
                        code.append(product['Code2'].strip().replace(',', '.'))
                    if product.get('Code3') is not None and len(product['Code3'].strip()) > 0:
                        code.append(product['Code3'].strip().replace(',', '.'))
                    if product.get('Code4') is not None and len(product['Code4'].strip()) > 0:
                        code.append(product['Code4'].strip().replace(',', '.'))
                    if product.get('Code5') is not None and len(product['Code5'].strip()) > 0:
                        code.append(product['Code5'].strip().replace(',', '.'))
                except:
                    pass
                try:
                    category = ''
                    if product.get('Category') is not None:
                        category = product['Category'].get('Name') is not None and product['Category'][
                            'Name'].strip() or ''
                except:
                    category = ''
                bonus = [product.get('BonusPoint'), product.get('BonusPointForAssistant'),
                         product.get('BonusPointForAssistant2'), product.get('BonusPointForAssistant3')]
                sup = self.product_supplier(product['Id'])
                info = [
                    ', '.join(_ for _ in code).strip(),
                    product['Name'].strip(),
                    category,
                    product.get('Unit') is not None and product['Unit'].strip() or '',
                    product.get('LargeUnit') is not None and product['LargeUnit'].strip() or '',
                    product.get('LargeUnitCode') is not None and product['LargeUnitCode'].strip() or '',
                    float(product['ConversionValue']),
                    product['Price'],
                    product['PriceLargeUnit'],
                    product['Cost'],
                    product['TotalOnHand'],
                    product.get('AttributesName') is not None and product['AttributesName'].strip() or '',
                    ', '.join(f'{img.get("ImageURL")}' for img in product['ProductImages']).strip(),
                    product.get('OrderQuickNotes') is not None and product['OrderQuickNotes'].strip() or '',
                    product['MinQuantity'],
                    product['MaxQuantity'],
                    product['ProductType'],
                    product.get('Hidden') and 1 or 0,
                    product['SplitForSalesOrder'] and 1 or 0,
                    product.get('Printer') is not None and product['Printer'].strip() or '',
                    sup,
                    priceConfig.get('VAT') is not None and priceConfig['VAT'] or 0,
                    product.get('Formular') is not None and product['Formular'].strip() or '',
                    product.get('IsSerialNumberTracking') and 1 or 0,
                    priceConfig.get('DontPrintLabel') and 1 or 0,
                    priceConfig.get('OpenTopping') and 1 or 0,
                    ', '.join(_ for _ in printer).strip(),
                    ', '.join(str(_) for _ in bonus).strip(),
                    product['Id']
                ]
                data.append(info)
            return {'status': 2, 'result': data}
        except Exception as e:
            print(e)
            return {'status': 0, 'result': {}}

    def count_products(self):
        while True:
            try:
                params = {
                    'Top': '50',
                    'Skip': str(0)
                }
                res = self.browser.get(self.base_url + '/api/products', params=params)
                if res.status_code == 200:
                    return res.json()['__count']
            except Exception as e:
                print(e)
                pass

    def branch_list(self):
        try:
            res = self.browser.get(self.base_url + '/Config/VendorSession')
            # print(res.text.split('branchs:')[1].split('accounts')[0].strip()[:-1])
            return json.loads(res.text.split('branchs:')[1].split('accounts')[0].strip()[:-1])

        except Exception as e:
            pass
        return []

    def switch_branch(self, branch):
        p = {
            'branchId': branch
        }
        res = self.browser.get(self.base_url + '/Home/ChangeBranch', params=p)
        if res.status_code == 200: return True
        return False

    def product_supplier(self, product_id):
        while True:
            try:
                res = self.browser.get(self.base_url + f'/api/products/{product_id}/suppliers')
                if res.status_code == 200:
                    return ', '.join(f'{img.get("Supplier").get("Code")}' for img in res.json()).strip()
            except:
                pass
