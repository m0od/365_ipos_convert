from datetime import datetime

import requests
import json
from openpyxl import Workbook

def get_orders(browser, domain):
    skip = 0
    orders = []
    while True:
        try:
            p = {
                'format': 'json',
                'Top': '50',
                'Skip': str(skip),
                'Filter': "PurchaseDate eq 'yesterday' and Status eq 2",
                'Includes': 'OrderDetails'
            }
            r = browser.get(f'https://{domain}.pos365.vn/api/orders', params=p)
            if r.status_code != 200: continue
            js = r.json()
            if len(js['results']) == 0: break
            orders.extend(js['results'])
            skip += 50
        except:
            continue
    return orders

def get_products(browser, domain, details, products):
    skip = 0
    print(products)
    for id in details:
        while True:
            try:
                p = {
                    'format': 'json',
                    # 'Top': '50',
                    # 'Skip': str(skip),
                    'Filter': f'Id eq {id}'
                }
                # print(domain, p)
                r = browser.get(f'https://{domain}.pos365.vn/api/products', params=p)
                if r.status_code != 200: continue
                js = r.json()
                # print(len(js['results']))
                if len(js['results']) == 0: break
                for _ in js['results']:
                    try:
                        # print(48, _)
                        print(_['Name'], '|', products[str(_['Id'])]['qty'])
                    except Exception as e:
                        print(50, e)
                skip += 50
                break
            except Exception as ex:
                print(563, ex)
                continue
    return details

wb = Workbook()
bill = wb.create_sheet('Đơn hàng')
d = ['am063']
for domain in d:
    b = requests.session()
    b.headers.update({'content-type': 'application/json'})
    r = b.post(f'https://{domain}.pos365.vn/api/auth', json={
        'Username': 'report',
        'Password': '123123123'
    })
    if r.status_code == 200 and r.json().get('SessionId') is not None:
        try:
            vendor = b.get(f'https://{domain}.pos365.vn/Config/VendorSession').text
            # print(vendor)
            retailer = json.loads(vendor.split('retailer:')[1].split('},')[0] + '}')
            # print(retailer)
            branchs = json.loads(vendor.split('branchs:')[1].split('],')[0] + ']')
            branch = {}
            for _ in branchs:
                branch.update({
                    _['Id']: _['Name']
                })
            orders = get_orders(b, domain)
            details = set()
            products = {}
            total = 0
            pm = 0
            vat = 0
            discount = 0
            for _ in orders:
                total += _['Total']
                pm += _['TotalPayment']
                vat += _['VAT']
                discount += _['Discount']
                pur_date = datetime.strptime(_["PurchaseDate"].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                for __ in _["OrderDetails"]:
                    if __['Price'] == 0: continue
                    details.add(__['ProductId'])
                    if products.get(str(__['ProductId'])) is None:
                        products.update({
                            str(__['ProductId']): {
                                'qty': __['Quantity']
                            }
                        })
                    else:
                        products[str(__['ProductId'])].update({
                            'qty': products[str(__['ProductId'])]['qty'] + __['Quantity']
                        })
            print(
                f'{retailer["Name"]}|{discount}|{total}|{vat}')
            # print(''.join(f'Id eq {str(i)} or ' for i in details)[:-4])
            print(len(details))
            get_products(b, domain, details, products)
        except Exception as e:
            print(e)
