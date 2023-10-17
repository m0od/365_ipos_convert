import uuid
from datetime import datetime

import requests


def fix():
    ___ = '''VE_8403282400
VE_1640480321
VE_1210081974
VE_1016331106
VE_3116029000
VE_1827974050
VE_5796748200
VE_4278570010
VE_1831710642
VE_1161861861
VE_2074875055
VE_1961001190
VE_1046802363
VE_1284706730
VE_1246301200
VE_1300637712
VE_1261937394
VE_1723302762
VE_6835573220
VE_1746190259
VE_2099503898
VE_1988806771
VE_1931893306
VE_1000329386
VE_1396341111
VE_3907130190
VE_3688443580
VE_6282673770
VE_9746172000
VE_7436834730
VE_1625187742
VE_3579781160
VE_1779591332'''.split('\n')
    game = {}
    for _ in ___:
        game.update({_[3:]: _})
    # print(game)
    u = 'https://am169.pos365.vn'
    b = requests.session()
    r = b.post(f'{u}/api/auth', json={'username': 'admin', 'password': 'aeonhd'})

    skip = 0
    b.headers.update({'content-type': 'application/json'})
    index = 0
    while True:
        try:
            print(skip)
            r = b.get(f'{u}/api/orders', params={
                'Top': '50', 'Skip': str(skip), 'Filter': 'Status eq 2'
            })
            if len(r.json()['results']) == 0: break

            for _ in r.json()['results']:
                # print(_)
                id = _["Id"]
                # if 'VOID' not in _["Code"]:
                #     code = f'VOID{_["Code"]}'
                # else:
                code = _["Code"]
                if game.get(code) is not None:
                    code = f'VE_{code}'
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
                # print(b.delete(f'{u}/api/orders/{id}/void', json=js).json())
            skip += 50
        except Exception as e:
            print(e)
            pass
    # print(r.text)

fix()