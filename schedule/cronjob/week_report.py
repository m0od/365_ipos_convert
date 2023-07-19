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
                'Filter': "PurchaseDate eq 'yesterday' and Status eq 2"
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

wb = Workbook()
bill = wb.create_sheet('Đơn hàng')
d = ['am124', 'am063']
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
            # print(r.json())
            for _ in orders:
                pur_date = datetime.strptime(_["PurchaseDate"].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                print(
                    f'{retailer["Name"]}|{branch[_["BranchId"]]}|{_["Code"]}|{pur_date}|{_["Discount"]}|{_["Total"]}|{_["VAT"]}')
        except Exception as e:
            print(e)
