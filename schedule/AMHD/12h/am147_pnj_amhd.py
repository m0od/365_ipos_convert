import glob
import os
import shutil
import smtplib
import sys
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from os.path import dirname
import xlrd


class AM147(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'pnj{}_amhd'
        self.ADAPTER_TOKEN = '22e07b3b942190b5b91eaf88b8c7937741fcbbf9932def888c1aad9aa72fcba5'
        self.FOLDER = 'pnj_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.DATE = datetime.now() - timedelta(days=1)
        self.EXT = f'*{self.DATE.strftime("%Y%m%d")}*xlsx'
        self.ORDERS = {}
        self.PMS = {}
        self.ODS = {}

    def scan_file(self):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{self.EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_data(self):
        from pos_api.adapter import submit_error, submit_order
        DATA = self.scan_file()
        if not DATA:
            self.report_not_recv()
            submit_error(self.ADAPTER_RETAILER, 'FILE NOT FOUND')
            return
        ws = xlrd.open_workbook(DATA)
        raw = ws.sheet_by_name('Danh sách đơn hàng')
        orders = {}
        for i in range(1, raw.nrows):
            code = raw.row(i)[0].value
            if code is None: break
            code = str(code)
            branch = str(int(raw.row(i)[6].value))
            status = str(raw.row(i)[1].value).strip()
            pur_date = str(raw.row(i)[2].value).strip()
            pur_date = datetime.strptime(pur_date, '%d%m%Y%H%M')
            now = datetime.now() - timedelta(days=1)
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            discount = str(raw.row(i)[3].value)
            total = str(raw.row(i)[4].value)
            vat = str(raw.row(i)[5].value)
            if orders.get(code) is None:
                orders[code] = {
                    'Code': code,
                    'Branch': branch,
                    'Status': int(status),
                    'PurchaseDate': pur_date,
                    'Total': float(total),
                    'TotalPayment': float(total),
                    'VAT': float(vat),
                    'Discount': abs(float(discount))
                }
        raw = ws.sheet_by_name('Phương thức thanh toán')
        pms = {}
        for i in range(1, raw.nrows):
            code = raw.row(i)[0].value
            if code is None: break
            code = str(code)
            name = str(raw.row(i)[1].value)
            value = str(raw.row(i)[2].value)
            if pms.get(code) is None:
                pms[code] = {
                    'PaymentMethods': [
                        {
                            'Name': name,
                            'Value': float(value)
                        }
                    ]
                }
            else:
                pms[code]['PaymentMethods'].append(
                    {
                        'Name': name,
                        'Value': float(value)
                    }
                )
        for k, v in pms.items():
            if orders.get(k) is not None:
                orders[k].update(v)
        raw = ws.sheet_by_name('Chi tiết đơn hàng')
        ods = {}
        for i in range(2, raw.nrows):
            code = raw.row(i)[0].value
            if code is None: continue
            code = str(code).strip()
            p_code = str(raw.row(i)[1].value)
            name = str(raw.row(i)[2].value)
            qty = str(raw.row(i)[3].value)
            price = str(raw.row(i)[4].value)
            if ods.get(code) is None:
                ods[code] = {
                    'OrderDetails': [{
                        'Code': p_code,
                        'Name': name,
                        'Price': float(price),
                        'Quantity': float(qty)
                    }],
                }
            else:
                ods[code]['OrderDetails'].append(
                    {
                        'Code': p_code,
                        'Name': name,
                        'Price': float(price),
                        'Quantity': float(qty)
                    }
                )
        for k, v in ods.items():
            if orders.get(k) is not None:
                orders[k].update(v)
        for k, v in orders.items():
            if v.get('PaymentMethods') is None:
                v['PaymentMethods'] = [{'Name': 'CASH', 'Value': v['Total']}]
            if v.get('OrderDetails') is None:
                v['OrderDetails'] = [{'ProductId': 0}]
            retailer = self.ADAPTER_RETAILER.format(str(int(v['Branch'])))
            v.pop('Branch')
            if v['Status'] == 2:
                submit_order(retailer, self.ADAPTER_TOKEN, v)
            elif v['Status'] == 1:
                send = v.copy()
                send.update({
                    'ReturnDate': send['PurchaseDate'],
                    'Total': abs(send['Total']),
                    'TotalPayment': abs(send['TotalPayment']),
                    'Status': 0,
                    'ReturnDetails': send['OrderDetails'],
                    'PaymentMethods': send['PaymentMethods']
                })
                send.pop('PurchaseDate')
                send.pop('OrderDetails')
                submit_order(retailer=retailer, token=self.ADAPTER_TOKEN, data=send)
        self.backup(DATA)

    def backup(self, DATA):
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        if os.path.exists(f'{self.FULL_PATH}/bak/{name}'):
            os.remove(f'{self.FULL_PATH}/bak/{name}')
        try:
            os.mkdir(f'{self.FULL_PATH}/bak')
        except:
            pass
        try:
            shutil.move(DATA, f'{self.FULL_PATH}/bak')
        except:
            pass

    def report_not_recv(self):
        now = datetime.now() - timedelta(days=1)
        port = 465  # For SSL
        password = 'abqqzkkrgftlodny'
        smtp_server = "smtp.gmail.com"
        sender_email = "tungpt@pos365.vn"  # Enter your address
        to_email = 'vuong.tt01@pnj.com.vn'  # Enter receiver address
        cc_email = 'tungpt@pos365.vn'
        message = MIMEMultipart("alternative")
        message["Subject"] = f'Report 0 orders PNJ-AMHD {now.strftime("%Y-%m-%d")}'
        message["From"] = 'tungpt@pos365.vn'
        message["To"] = to_email
        toAddr = [to_email]
        while True:
            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
                server.login(sender_email, password)
                server.sendmail(sender_email, toAddr, message.as_string())
                break
            except:
                pass

