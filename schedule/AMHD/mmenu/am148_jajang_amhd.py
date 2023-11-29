import sys
from os.path import dirname
import requests
from datetime import datetime, timedelta


class AM148(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'jajang_amhd'
        self.ADAPTER_TOKEN = '9ae294ff8451d14f4ed517e93dfdc73356d305a3ee2b247dcc9cac048db16bad'
        self.API_URL = 'https://api.mmenu.io/v2/restaurants/64b4b9efeb99ac0ba80d156b/statistics-report/orderByCustomer'
        self.CLIENT_ID = 'sgDcucYvNvLojdr'
        self.TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NDQzNTBkY2IxYTIyMmNhZDI3NWZjZmYiLCJpYXQiOjE2OD' \
                     'k5NDkwMTQsImV4cCI6NDcxMzE5NDI2MTQsInR5cGUiOiJhY2Nlc3MifQ.cXXv7m2sBpkm696vdFcRa0xHQZjsRaEN1r7TBf2Uzls'
        self.APP_ID = 'mmenu-admin.web.1.29.18'
        self.RESTAURANT_ID = '64b4b9efeb99ac0ba80d156b'
        self.browser = requests.session()
        self.DATE = datetime.now() - timedelta(days=1)

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        self.browser.headers.update({
            'authorization': f'Bearer {self.TOKEN}',
            'clienid': self.CLIENT_ID,
            'appid': self.APP_ID
        })
        js = {
            'from': self.DATE.strftime('%Y-%m-%d'),
            'to': self.DATE.strftime('%Y-%m-%d'),
            'restaurantId': self.RESTAURANT_ID
        }
        res = self.browser.post(self.API_URL, json=js)
        if res.status_code != 200:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=res.text)
            return
        js = res.json()['saleByCustomerReport']['customerItems']
        for _ in js:
            code = _['billNo']
            total = _['revenue']
            discount = _['discountAmount'] + _['discountAmountOfAppliedPromotion']
            pm = [{'Name': _['paymentMethod'].strip().upper(), 'Value': total}]
            od = [{'ProductId': 0}]
            send = {
                'Code': code,
                'Status': 2,
                'PurchaseDate': self.DATE.strftime('%Y-%m-%d 07:00:00'),
                'Total': total,
                'TotalPayment': total,
                'VAT': 0,
                'Discount': discount,
                'OrderDetails': od,
                'PaymentMethods': pm
            }
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=send)
