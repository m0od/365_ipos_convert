import requests
#
js = {'Code': '133714', 'Status': 2, 'PurchaseDate': '2023-01-05 21:31:42', 'Total': 791600, 'TotalPayment': 791600, 'VAT': 71964, 'Discount': 1187400, 'OrderDetails': [{'Code': '221113225842', 'Name': 'Giày da nam hiệu KANGLONG hàng mới 100%. Size 42', 'Price': 1979000, 'Quantity': 1}, {'Code': '1229190003', 'Name': 'Túi giấy hiệu Aokang hàng mới 100%', 'Price': 0, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'THẺ', 'Value': 791600}]}
h = {
    'content-type': 'application/json',
    'retailer': 'aokang_aeonhd',
    'authorization': '407f86411bd52a7ed956f07579109ce42638d7c6acee0336bfd839745e1bde37'
}
requests.post('https://adapter.pos365.vn/aeon_orders', headers=h, json=js)
# import json
# f = open('bak', 'r')
# s = f.read().strip()
# f.close()
# s = s.split('\n')
# x = []
# for line in s:
#     l = line.split('	')[6].replace("'",'"')
#     # print(l)
#     js = json.loads(l)
#     # print(js['Code'], js['PurchaseDate'])
#     if js['Code'] not in x:
#         x.append(js['Code'])
#         requests.post('https://adapter.pos365.vn/orders', headers=h, json=js)
#     else:
#         print(js)
# print(len(x))