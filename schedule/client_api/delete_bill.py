import uuid
from datetime import datetime

import requests


def fix(self):
    u = 'https://am170.pos365.vn'
    b = requests.session()
    r = b.post(f'{u}/api/auth', json={'username': 'admin', 'password': 'aeonhd'})

    skip = 0
    b.headers.update({'content-type': 'application/json'})
    index = 0
    while True:
        try:
            r = b.get(f'{u}/api/orders', params={
                'Top': '50', 'Skip': '0', 'Filter': 'Status eq 2'
            })
            if len(r.json()['results']) == 0: break

            for _ in r.json()['results']:
                # print(_)
                id = _["Id"]
                # if 'VOID' not in _["Code"]:
                #     code = f'VOID{_["Code"]}'
                # else:
                code = str(uuid.uuid4())
                pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                js = {'Order': {
                    'Id': id,
                    'Status': 2,
                    'Code': code,
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
                print(b.post(f'{u}/api/orders', json=js).json())
                print(b.delete(f'{u}/api/orders/{id}/void', json=js).json())
            # skip += 1
        except Exception as e:
            print(e)
            pass
    print(r.text)