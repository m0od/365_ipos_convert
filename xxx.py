import requests
#
# js = {'Code': '1sdfsdf23123', 'PurchaseDate': '2023-04-18 20:25:00', 'Status': 2, 'Discount': 20400, 'VAT': 0, 'Total': 115600, 'TotalPayment': 115600, 'OrderDetails': [{'Code': 'MT14L', 'Name': 'Mango Milk L', 'Price': 56000, 'Quantity': 1}, {'Code': '50I', 'Name': '50% I', 'Price': 0, 'Quantity': 1}, {'Code': 'TOP8L', 'Name': 'White Pearls*', 'Price': 10000, 'Quantity': 1}, {'Code': '70S', 'Name': '70% S', 'Price': 0, 'Quantity': 1}, {'Code': 'MT9L', 'Name': 'Hazelnut Milk Tea L', 'Price': 56000, 'Quantity': 1}, {'Code': 'TOP5L', 'Name': 'Pearls*', 'Price': 7000, 'Quantity': 1}, {'Code': 'TOP4L', 'Name': 'Grass Jelly*', 'Price': 7000, 'Quantity': 1}], 'AdditionalServices': [{'Name': 'Phí dịch vụ', 'Value': 0}, {'Name': 'Phí hoa hồng', 'Value': 0}, {'Name': 'Phí marketing', 'Value': 0}], 'PaymentMethods': [{'Name': 'ATM', 'Value': 115600}]}
# h = {
#     'content-type': 'application/json',
#     'retailer': 'retry',
#     'authorization': 'cf0f760c3c11b65139beaecd6e0dd12f80bc34a177704ffc497d2bf816d1ac2d'
# }
# requests.post('http://adapter.pos365.vn:6000/orders', headers=h, json=js)
import json
f = open('bak', 'r')
s = f.read().strip()
f.close()
s = s.split('\n')
x = []
for line in s:
    l = line.split('	')[6].replace("'",'"')
    # print(l)
    js = json.loads(l)
    # print(js['Code'], js['PurchaseDate'])
    if js['Code'] not in x:
        x.append(js['Code'])
    else:
        print(js)
print(len(x))