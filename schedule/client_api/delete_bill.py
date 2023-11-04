import uuid
from datetime import datetime, timedelta

import requests


def fix():
    # print(game)
    u = 'https://am147.pos365.vn'
    b = requests.session()
    r = b.post(f'{u}/api/auth', json={'username': 'admin', 'password': 'aeonhd'})

    skip = 0
    b.headers.update({'content-type': 'application/json'})
    index = 0
    while True:
        try:
            # print(skip)
            t = datetime.strptime('2023-10-09', '%Y-%m-%d')
            f = (t- timedelta(days=1)).strftime('%Y-%m-%dT17:00:00Z')
            t = t.strftime('%Y-%m-%dT16:59:00Z')
            r = b.get(f'{u}/api/orders', params={
                'Top': '50',
                # 'Skip': str(skip),
                # 'Filter': 'Status eq 3 or Status eq 0'
                'Filter': f"(Status eq 2 and PurchaseDate ge 'datetime''{f}''' and PurchaseDate lt 'datetime''{t}''')"
                # 'Filter': "(PurchaseDate ge 'datetime''2023-10-01T17:00:00Z''' and PurchaseDate lt 'datetime''2023-10-02T16:59:00Z''')"
            })
            print(len(r.json()['results']))
            if len(r.json()['results']) == 0: break

            for _ in r.json()['results']:
                # print(_)
                id = _["Id"]
                # if 'VOID' not in _["Code"]:
                #     code = f'VOID{_["Code"]}'
                # else:
                code = _["Code"]
                # if code != 'CHB110100000670': continue
                # print(code)
                pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                js = {'Order': {
                    'Id': id,
                    'Status': 2,
                    'Code': str(uuid.uuid4()),
                    'PurchaseDate': pur_date,
                    'Discount': 0,
                    'VAT': 0,
                    'Total': 0,
                    'TotalPayment': 0,
                    'AccountId': None,
                    'OrderDetails': [
                        {
                            'ProductId': 0
                        }
                    ]
                }}
                r = b.post(f'{u}/api/orders', json=js).json()
                if r.get('Errors') is not None: continue
                print(b.delete(f'{u}/api/orders/{id}/void', json=js).json())
            skip += 50
        except Exception as e:
            print(e)
            pass
    # print(r.text)

fix()