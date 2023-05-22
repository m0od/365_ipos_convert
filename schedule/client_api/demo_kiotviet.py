import requests
import json
from datetime import datetime, timedelta
from pytz import timezone
SCOPES = 'PublicApi.Access'
GRANT_TYPE = 'client_credentials'
CLIENT_ID = 'b1209e87-720f-4e80-8cba-88fd2d219e59'
CLIENT_SECRET = 'C6CACEC058B44FE961EC6023936BE7004469D183'
DOMAIN = ''


def auth():
    url = 'https://id.kiotviet.vn/connect/token'
    js = {
        'scopes': SCOPES,
        'grant_type': GRANT_TYPE,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    while True:
        try:
            b = requests.session()
            proxies = {
                'http': 'http://127.0.0.1:8888',
                'https': 'http://127.0.0.1:8888',
            }
            b.proxies = proxies
            b.verify = False
            b.headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0'
            })
            res = b.post(url, data=js).json()
            print(res)
            b.headers.update({'authorization': f'Bearer {res["access_token"]}'})
            return b
        except:
            pass


def get_orders(b, branch, date):
    b.headers.pop('content-type')
    b.headers.update({
        'retailer': 'suabimtrangnhungpt',
        # 'branchid': str(branch),
        # 'fingerprintkey': 'b51a22b8ef10263dcc1f6c5e037aced2_Firefox_Desktop_Máy tính Windows',
        # 'x-retailer-code': 'suabimtrangnhungpt',
        # 'x-group-id': '14',
        # 'isusekvclient': '1',
        # 'accept': 'application/json',
        # 'referer': 'https://suabimtrangnhungpt.kiotviet.vn',
        # 'origin': 'https://suabimtrangnhungpt.kiotviet.vn'
    })
    # ({: 'application/json'})
    url = 'https://public.kiotapi.com/invoices'
    now = datetime.now(timezone('Etc/GMT+7'))
    print(now)

    p = {
        'branchIds': [branch],
        'status': [1],
        'includePayment': True,
        'pageSize' : 5,
        # 'currentItem': '0',
        'orderBy': 'id',
        # 'orderDirection': 'Desc',
        'fromPurchaseDate': str(now - timedelta(days=365)),
        'toPurchaseDate': str(now - timedelta(days=1))
    }
    # js = {
    #     'Includes':[
    #         'BranchName',
    #         'Branch',
    #         'DeliveryInfoes',
    #         'DeliveryPackages',
    #         'Customer',
    #         'Payments',
    #         'SoldBy',
    #         'User',
    #         'InvoiceOrderSurcharges',
    #         'Order',
    #         'SaleChannel',
    #         'Returns',
    #         'InvoiceMedicine',
    #         'PriceBook'
    #     ],
    #     'ForSummaryRow': 'true',
    #     'FiltersForOrm':json.dumps({"BranchIds":[1262010],
    #                                 "PriceBookIds":[],
    #                                 "FromDate":None,"ToDate":None,
    #                                 "TimeRange":"year","InvoiceStatus":["3","1"],"UsingCod":[],
    #                                 "TableIds":[],"SalechannelIds":[],
    #                                 "StartDeliveryDate":None,"EndDeliveryDate":None,"UsingPrescription":2}),
    #     'UsingTotalApi': 'true',
    #     'UsingStoreProcedure' : 'false',
    #     'format': 'json',
    #     '$top': '100',
    #     '$inlinecount': 'allpages',
    #     '$filter': "(PurchaseDate eq 'year' and (Status eq 3 or Status eq 1))"
    # }
    # print(js)
    res = b.get(url, params=p).json()
    for i in res['data']:
        print(i['code'], i['purchaseDate'], i['branchId'], i['total'], i['total'])
        print(i)

browser = auth()
print(browser.headers)
get_orders(browser, 1262010, datetime.strptime('2022-11-09', '%Y-%m-%d'))
# # “includePayment”: Boolean, // có lấy thông tin thanh toán
# #  “includeInvoiceDelivery”: Boolean, //hóa đơn có giao hàng hay không
# # “lastModifiedFrom”: datetime? // thời gian cập nhật
# # “pageSize”: int?, // số items trong 1 trang, mặc định 20 items, tối đa 100 items
# # “currentItem”: int,
# # “lastModifiedFrom”: datetime? // thời gian cập nhật
# # “toDate”: datetime? //Thời gian cập nhật cho đến thời điểm toDate
# # “orderBy”: string, //Sắp xếp dữ liệu theo trường orderBy (Ví dụ: orderBy=name)
# # “pageSize”: int?, // số items trong 1 trang, mặc định 20 items, tối đa 100 items
# # “orderDirection”: string, //Sắp xếp kết quả trả về theo: Tăng dần Asc (Mặc định), giảm dần Desc “orderId”: long?, // Lọc danh sách hóa đơn theo Id của đơn đặt hàng
# # “createdDate”: datetime? //Thời gian tạo
# # “fromPurchaseDate”: datetime? //Từ ngày giao dịch
# # “toPurchaseDate”: datetime? //Đến ngày giao dịch'
#     'https://api-man.kiotviet.vn/api/invoices/list?' \
#         "BranchIds":[1262010],
#      "PriceBookIds":[],
#      "FromDate":null,
#      "ToDate":null,
#      "TimeRange":"year",
#      "InvoiceStatus":["3","1"],
#      "UsingCod":[],"TableIds":[],
#      "SalechannelIds":[],"StartDeliveryDate":null,
#      "EndDeliveryDate":null,"UsingPrescription":2}
#     &$top=10&$filter=(PurchaseDate+eq+'year'+and+(Status+eq+3+or+Status+eq+1))'
