from datetime import datetime, timedelta

import requests
import json

from schedule.pos_api.adapter import submit_order

url = "https://cuockid.pos365.vn/api/products"

# payload = json.dumps({
#     "Product": {
#         "Id": 0,
#         "Code": "HH-0541",
#         "Name": "Noel Pine Cake",
#
#     },
# }, separators=(',', ':'))
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'ss-id=GpFbtwoauyjUaYKtHWYA'
}
b = requests.session()
b.headers.update({
'Content-Type': 'application/json',
  # 'Cookie': 'ss-id=GpFbtwoauyjUaYKtHWYA'
})
# from concurrent import futures
#
# with futures.ThreadPoolExecutor(max_workers=4) as mt:
#   thread = [
#     mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
#     mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
#     mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
#     mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
#     # mt.submit(ao.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
#     # mt.submit(bl.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
#     # mt.submit(at.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
#     # mt.submit(atk.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
#   ]
#   futures.as_completed(thread)
#
#
r_date = '03/06/2023 21:28:50'
print(datetime.strptime(r_date, '%d/%m/%Y %H:%M:%S'))
# r = b.post('https://am062.pos365.vn/api/auth', json={
#     'Username': 'admin',
#     'Password': '123456'
# })
# retail = 'lyn_aeonhd'
# token = '7d5545b898b1a57468ed47d1944e18b7d19cc43b76ef6d271226df64f25e407d'
# skip = 0
# while True:
#     r = b.get('https://am062.pos365.vn/api/orders', params = {
#         '$top': '50',
#         '$skip': str(skip),
#         '$filter': f"(PurchaseDate ge 'datetime''2023-05-31T17:00:00Z''' and PurchaseDate lt 'datetime''2023-06-01T17:00:00Z''')",
#         'format': 'json'
#     })
#     if len(r.json()['results']) == 0: break
#     for _ in r.json()['results']:
#         if _.get('AccountId') == 978:
#             p_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')+ timedelta(hours=7)
#             send = {
#                 'Code': _['Code'],
#                 'Total': _['Total'],
#                 'TotalPayment': _['TotalPayment'],
#                 'PaymentMethods': [{'Name': 'VNPAY', 'Value': _['Total']}],
#                 'Discount': _.get('Discount') is not None and _.get('Discount') or 0,
#                 'Status': 2,
#                 'VAT': _['VAT'],
#                 'PurchaseDate': p_date.strftime('%Y-%m-%d %H:%M:%S'),
#                 'OrderDetails': []
#
#             }
#             submit_order(retailer=retail, token=token, data=send)
#         print(_['Code'], _.get('AccountId'))
#     skip += 50
# print(r.text)
# for i in range(1,31):
#     js = {
#         'Room': {'Name':f'Bàn {i}'}
#     }
#     b.post('https://cuockid.pos365.vn/api/rooms', json=js)

# mport json

def ignore_null(_):
    """recursively remove empty lists, empty dicts, or None elements from a dictionary"""

    def empty(x):
        return x is None or x == {} or x == []

    if not isinstance(_, (dict, list)):
        return _
    elif isinstance(_, list):
        return [v for v in (ignore_null(v) for v in _) if not empty(v)]
    else:
        return {k: v for k, v in ((k, ignore_null(v)) for k, v in _.items()) if not empty(v)}

