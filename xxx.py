import requests
import json

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
# r = b.post('https://cuockid.pos365.vn/api/auth', json={
#     'Username': 'quantri@pos365.vn',
#     'Password': 'IT@P0s365kmS'
# })
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

data = {'name': 'Alice', 'age': [{'a':None}], 'ákdjasld':{}}
json_str = json.dumps(ignore_null(data))
print(json_str)