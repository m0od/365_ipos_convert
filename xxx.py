import requests
import json

url = "https://testkt365.pos365.vn/api/products"

payload = json.dumps({
    "Product": {
        "Id": 0,
        "Code": "HH-0541",
        "Name": "Noel Pine Cake",

    },
}, separators=(',', ':'))
headers = {
  'Content-Type': 'application/json',
  'Cookie': 'ss-id=mjJ8WriFSBHnOuPHq2Ob;'
}
from concurrent import futures

with futures.ThreadPoolExecutor(max_workers=4) as mt:
  thread = [
    mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
    mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
    mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
    mt.submit(requests.request, 'POST', url, headers=headers, data=payload),
    # mt.submit(ao.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
    # mt.submit(bl.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
    # mt.submit(at.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
    # mt.submit(atk.get_data, (now - timedelta(days=1)).strftime('%y%m%d')),
  ]
  futures.as_completed(thread)


