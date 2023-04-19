import json
import math
import requests
f = open('ipos.log.bak', 'rb')
x = []
import time
c = 0
total = 0
while True:
    line = f.readline()
    if len(line) == 0:
        f.close()
        break
    s = line.decode('utf-8')
    # # if '2023-04-09' not in s: continue
    # if s.startswith('{'):
    #     # print(s.strip())
    s = s.strip().replace('[[','[').replace(']]',']').replace("'", '"')
    # print(s)
    s = s.split('	')
    rid = s[2]
    js = json.loads(s[6])
    code = js['Code']
    # print(code)
    if code not in x:
        x.append(code)
    else:
        print(code)
    # if 'DEL' in code: continue
    # print(code, js['PaymentMethods'])
    #
    # for i in js['AdditionalServices']:
    #     total += int(i['Value'])
    # #     # print(js)
    # # print(js.get('Code'))
    # # if js.get('Code') not in x:
    # #     x.append(js.get('Code'))
    # # else:
    # #     print(js)
    # headers = {
    #     'retailer': 'demo',
    #     'authorization': 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d',
    #     'content-type': 'application/json'
    # }
    # r = requests.post('http://adapter.pos365.vn:6000/orders', headers=headers, json=js)
    res = requests.get(f'https://adapter.pos365.vn/result/{rid}').json()
    res['state'] = True
    print(rid, res.get('result'))
    js = {'rid': rid, 'result': code}
    requests.post('http://adapter.pos365.vn:6000/log', json=js)
    # print(r.text)
    # c += 1
    # time.sleep()
    # print(r.text)
        # break
    # print(requests.get(f'https://adapter.pos365.vn/result/{r.json()["result_id"]}').text)
# print(len(x))
# print(total)
#
# js = {'Code': '1sdfsdf23123', 'PurchaseDate': '2023-04-18 20:25:00', 'Status': 2, 'Discount': 20400, 'VAT': 0, 'Total': 115600, 'TotalPayment': 115600, 'OrderDetails': [{'Code': 'MT14L', 'Name': 'Mango Milk L', 'Price': 56000, 'Quantity': 1}, {'Code': '50I', 'Name': '50% I', 'Price': 0, 'Quantity': 1}, {'Code': 'TOP8L', 'Name': 'White Pearls*', 'Price': 10000, 'Quantity': 1}, {'Code': '70S', 'Name': '70% S', 'Price': 0, 'Quantity': 1}, {'Code': 'MT9L', 'Name': 'Hazelnut Milk Tea L', 'Price': 56000, 'Quantity': 1}, {'Code': 'TOP5L', 'Name': 'Pearls*', 'Price': 7000, 'Quantity': 1}, {'Code': 'TOP4L', 'Name': 'Grass Jelly*', 'Price': 7000, 'Quantity': 1}], 'AdditionalServices': [{'Name': 'Phí dịch vụ', 'Value': 0}, {'Name': 'Phí hoa hồng', 'Value': 0}, {'Name': 'Phí marketing', 'Value': 0}], 'PaymentMethods': [{'Name': 'ATM', 'Value': 115600}]}
# headers = {
#     'retailer': 'retry',
#     'authorization': 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d',
#     'content-type': 'application/json'
# }
# r = requests.post('http://adapter.pos365.vn:6000/orders', headers=headers, json=js)