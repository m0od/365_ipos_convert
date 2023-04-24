import requests
#
error = [
{'Code': 'HD006495', 'Status': 2, 'PurchaseDate': '2023-01-08 17:15:52', 'Total': 179200, 'TotalPayment': 179200, 'VAT': 16291, 'Discount': 0, 'OrderDetails': [{'Code': '8809713405179', 'Name': 'Áo ba lỗ (Ryan)', 'Price': 304000, 'Quantity': 1}, {'Code': '8809713404790', 'Name': 'Set Áo cộc tay quần đùi (Ryan)', 'Price': 592000, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'THẺ', 'Value': 179200}]},
{'Code': 'HD006628', 'Status': 2, 'PurchaseDate': '2023-01-18 14:33:55', 'Total': 169200, 'TotalPayment': 169200, 'VAT': 15382, 'Discount': 0, 'OrderDetails': [{'Code': '8809721503379', 'Name': 'Set 3 bút bi cầu vồng (Lovely Apeach)', 'Price': 132000, 'Quantity': 1}, {'Code': '8809645610078', 'Name': 'Sổ tay B6 - April Shower (Apeach)', 'Price': 56000, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'THẺ', 'Value': 169200}]},
{'Code': 'HD007004', 'Status': 2, 'PurchaseDate': '2023-02-02 17:21:31', 'Total': 52000, 'TotalPayment': 52000, 'VAT': 4727, 'Discount': 0, 'OrderDetails': [{'Code': '8809534489235', 'Name': 'File tài liệu A4 - 3 lớp (Little Apeach)', 'Price': 52000, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'CASH', 'Value': 52000}]},
{'Code': 'HD007154', 'Status': 2, 'PurchaseDate': '2023-02-11 14:58:11', 'Total': 297000, 'TotalPayment': 297000, 'VAT': 27000, 'Discount': 0, 'OrderDetails': [{'Code': '8809814925446', 'Name': 'Gối ôm nhỏ (Little Jordy)', 'Price': 330000, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'CASH', 'Value': 297000}]}
]
# js = {'Code': '133714', 'Status': 2, 'PurchaseDate': '2023-01-05 21:31:42', 'Total': 791600, 'TotalPayment': 791600, 'VAT': 71964, 'Discount': 1187400, 'OrderDetails': [{'Code': '221113225842', 'Name': 'Giày da nam hiệu KANGLONG hàng mới 100%. Size 42', 'Price': 1979000, 'Quantity': 1}, {'Code': '1229190003', 'Name': 'Túi giấy hiệu Aokang hàng mới 100%', 'Price': 0, 'Quantity': 1}], 'PaymentMethods': [{'Name': 'THẺ', 'Value': 791600}]}
for content in error:
    h = {
        'content-type': 'application/json',
        'retailer': 'kakao_aeonhd',
        'authorization': '8add972c8f30406354872d3272f755fff035661f9ddd590e6e71c267b756a546'
    }
    requests.post('https://adapter.pos365.vn/aeon_orders', headers=h, json=content)
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