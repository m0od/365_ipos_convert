import time

import requests
from concurrent import futures
import random


def submit_order():
    # u = 'http://192.168.101.174:6000'
    u = 'https://365ipos.ddns.net'


    b = requests.session()
    b.headers.update({
        'retailer': '695',
        'authorization': '9db0b9fa-d0a1-41ef-84fc-d2f6f503102e'
    })
    # b.post(u + '/add', data={'OrderCode':str(random.randint(1000000000000000,9000000000000000))})
    res = b.post(u + '/orders', json={
            'Code': str(random.randint(1000000,9000000)),
            # "Code": 'aaaaa2a',
            "Status": 2,
            "Discount": 0, "TotalPayment": 1000, "Total": 1000,
            "OrderDetails": [{"ProductId": None}],
            "PaymentMethods": [{"Name":"PTTT1","Value":1000},{"Name":"PTTT2","Value":1000},{"Name":"PTTT3","Value":1000}],
            # "PaymentMethods": '',
            "VAT": 0,
            "PurchaseDate": "2023-03-09 12:01:01"
        })
    # time.sleep(1)
    print(res.text)
    print(b.get(u + f'/result/{res.json()["result_id"]}').text)
with futures.ThreadPoolExecutor(max_workers=1) as mt:
    thread = []
    # for i in range(10):
    thread.append(mt.submit(submit_order))
    futures.as_completed(thread)

