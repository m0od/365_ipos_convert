import json
import sys
import uuid
from datetime import datetime, timedelta

import requests

from schedule.pos_api.adapter import submit_order

u = 'https://am036.pos365.vn'
b = requests.session()
def fix():
    # print(game)
    # u = 'https://am149.pos365.vn'
    # b = requests.session()
    r = b.post(f'{u}/api/auth', json={'username': 'admin',
                                      'password': '123456'})
    # print(r.text)
    skip = 0
    b.headers.update({'content-type': 'application/json'})
    index = 0
    while True:
        try:
            # print(skip)
            t = datetime.strptime('2023-10-09', '%Y-%m-%d')
            f = (t- timedelta(days=1)).strftime('%Y-%m-%dT17:00:00Z')
            t = t.strftime('%Y-%m-%dT16:59:00Z')
            filter = []
            since = datetime.now() - timedelta(days=21)
            since = since.strftime('%Y-%m-%dT17:00:00Z')
            before = datetime.now() - timedelta(days=1)
            before = before.strftime('%Y-%m-%dT16:59:00Z')
            # filter += ['Status', 'eq', '2']
            # filter += ['and']
            filter += ['Total', 'gt', '0', 'and']
            filter += ["substringof('OFF',Code)"]
            # filter += ['and']
            # filter += ['PurchaseDate', 'ge']
            # filter += [f"'datetime''{since}'''"]
            # filter += ['and']
            # filter += ['PurchaseDate', 'lt']
            # filter += [f"'datetime''{before}'''"]
            # filter = str(*filter)
            # print(' '.join(filter))
            # r = b.get(f'{u}/api/orders', params={
            r = b.get(f'{u}/api/pricebooks/items', params={
                # 'inventorycount'
                'Top': '50',
                # 'Skip': str(skip),
                # 'Filter': ' '.join(filter)
                # 'Filter': "(Status eq 2 or Status eq 0) and PurchaseDate eq 'yesterday'"
                # 'Filter': f"(Status eq 2 and PurchaseDate ge 'datetime''{f}''' and PurchaseDate lt 'datetime''{t}''')"
                # 'Filter': "(PurchaseDate ge 'datetime''2023-10-01T17:00:00Z''' and PurchaseDate lt 'datetime''2023-10-02T16:59:00Z''')"
            })
            # print(r.text)
            if len(r.json()['results']) == 0: break

            for _ in r.json()['results']:
                print(_)
                id = _["Id"]
                # if 'VOID' not in _["Code"]:
                #     code = f'VOID{_["Code"]}'
                # else:
                # code = _["Code"]
                # # if code != 'CHB110100000670': continue
                # # print(code)
                # pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                # pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                # # attr = _['MoreAttributes']
                # # # attr = attr.replace('PaymentMethods:', '"PaymentMethods":')
                # # # attr = attr.replace('{AccountId', '{"AccountId"')
                # # attr = attr.replace('Null', 'null')
                # # # print(attr)
                # # attr = json.loads(attr)
                # # print(attr)
                # # attr = {'PaymentMethods':[attr['PaymentMethods']]}
                # # _['MoreAttributes'] = _['MoreAttributes'].replace('PaymentMethods:', '"PaymentMethods":{')
                # # _['MoreAttributes'] = json.loads(_['MoreAttributes'])
                # # _['MoreAttributes'] = json.dumps(_['MoreAttributes'])
                # js = {'Order': {
                #     'Id': id,
                #     'Status': 2,
                #     'Code': str(uuid.uuid4()),
                #     'PurchaseDate': pur_date,
                #     'Discount': 0,
                #     'VAT': 0,
                #     'Total': 0,
                #     'TotalPayment': 0,
                #     'AccountId': None,
                #     'OrderDetails': [
                #         {
                #             'ProductId': 0
                #         }
                #     ],
                # }}

                # r = b.post(f'{u}/api/orders', json=js).json()
                # print(r)
                # if r.get('Errors') is not None: continue
                # sys.exit(0)
                # b.delete(f'{u}/api/orders/{id}/void').json()
                # print(b.delete(f'{u}/api/inventorycount/{id}/void').json())
                print(103,b.delete(f'{u}/api/pricebooks/deleteitem', params={
                    'PriceBookDetailId': id
                }).json())
                sys.exit(0)
                # submit_order(retailer, token, js)
            skip += 50
        except Exception as e:
            print(e)
            pass
    # print(r.text)

fix()
