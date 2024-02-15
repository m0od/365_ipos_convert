from datetime import datetime

import requests
from bs4 import BeautifulSoup
from requests_toolbelt import MultipartEncoder


class NHANH(object):
    def __init__(self):
        self.ACCOUNT = None
        self.PASSWORD = None
        self.DATE = None
        self.METHOD = None
        self.URL = 'https://nhanh.vn'
        self.browser = requests.session()
        self.CSRF = None
        self.ORDERS = {}
        self.RETURNS = {}
        self.MODE = None

    def get_login_page(self):
        try:
            res = self.browser.get(f'{self.URL}/signin')
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
                'username': self.ACCOUNT,
                'password': self.PASSWORD
            }
            m = MultipartEncoder(fields=data)
            self.browser.headers.update({'content-type': m.content_type})
            res = self.browser.post(f'{self.URL}/signin', data=m)
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
            return False, 'GET_LOGIN_FAILED'
        if not self.login():
            return False, 'INVALID_LOGIN'
        return True, None

    def get_returns(self):
        page = 1
        while page > 0:
            p = {
                'storeId': self.STORE_ID,
                'fromDate': self.DATE.strftime('%d/%m/%Y'),
                'toDate': self.DATE.strftime('%d/%m/%Y'),
                'page': str(page)
            }
            if self.MODE:
                p.update({'mode': self.MODE})
            r = self.browser.get(f'{self.URL}/pos/return/index', params=p)
            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            if len(tbody) == 0: break
            code = None
            for _ in tbody[:-1]:
                try:
                    code = _.find('td', {'class': 'dgColId'}).a.text.strip()
                    if self.RETURNS.get(code) is not None:
                        page = -1
                        break
                    r_date = _.find('td', {'class': 'dgColDate'})['title']
                    r_date = r_date[r_date.index(':') + 1:].strip()
                    r_date = datetime.strptime(r_date, '%d/%m/%Y %H:%M:%S')
                    self.RETURNS.update({
                        code: {
                            'Code': code,
                            'ReturnDetails': [],
                            'ReturnDate': r_date.strftime('%Y-%m-%d %H:%M:%S')
                        }
                    })
                except:
                    pass
                try:
                    rds = self.RETURNS[code]['ReturnDetails']
                    rd = _.find('td', {'class': 'dgColProduct'})
                    p_code = rd.span.text.strip()
                    rds.append({
                        'Code': p_code[1:-1],
                        'Name': rd.text.strip().replace(p_code, '').strip(),
                        'Price': _.find('td', {'class': 'dgColProductPrice'}).text.strip(),
                        'Quantity': _.find('td', {'class': 'dgColQuantity'}).text.strip()
                    })
                    self.RETURNS[code].update({'ReturnDetails': rds})
                except:
                    pass
                raw = _.findAll('td', {'class': 'text-right'})
                try:
                    discount = raw[3].text.strip().split('(')[0].strip().replace('.', '')
                    if len(discount) == 0: discount = 0
                except:
                    discount = 0
                try:
                    name = self.METHOD.get(raw[4].i['title'].strip())
                except:
                    name = 'CASH'
                try:
                    value = int(raw[4].text.strip().replace('.', ''))
                except:
                    value = 0
                pms = [{'Name': name, 'Value': value}]
                try:
                    total = raw[6].text.strip().replace('.', '').strip()
                    if len(total) == 0: total = 0
                    self.RETURNS[code].update({
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
        for k, v in self.RETURNS.items():
            self.ORDERS.update({
                f'VAT_{v["Code"]}': {
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
            })

    def get_orders(self):
        page = 1
        code = None
        while page > 0:
            p = {
                'storeId': self.STORE_ID,
                'fromDate': self.DATE.strftime('%d/%m/%Y'),
                'toDate': self.DATE.strftime('%d/%m/%Y'),
                'page': str(page)
            }
            r = self.browser.get(f'{self.URL}/pos/bill/index', params=p)
            html = BeautifulSoup(r.text, 'html.parser')
            tbody = html.find('tbody').findAll('tr')
            if len(tbody) == 0: break
            for _ in tbody[:-1]:
                pms = []
                try:
                    code = _['data-id']
                    if self.ORDERS.get(code) is not None:
                        page = -1
                        break
                    else:
                        self.ORDERS.update({code: {'OrderDetails': []}})
                except:
                    pass
                try:
                    ods = self.ORDERS[code]['OrderDetails']
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
                    self.ORDERS[code].update({
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
                    self.ORDERS[code].update({
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
        # for k, v in orders.items():
        #     # print(v)
        #     submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
