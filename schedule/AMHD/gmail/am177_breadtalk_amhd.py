import email
import glob
import imaplib
import os
import smtplib
import subprocess
import sys
import time
import zipfile
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os.path import dirname
from pathlib import Path

import requests
import xlrd


class AM177(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.ADAPTER_RETAILER = 'breadtalk_amhd'
        self.ADAPTER_TOKEN = '25b73845815ffae2bd4a0fa32a7743a5da2aaf0a6f3a7d59c9a37f7d8b707c3a'
        self.browser = requests.session()
        self.ORDERS = []
        self.ORDERS_COUNT = []
        self.TRANS = []
        self.DATE = None
        self.VAT = 0
        self.FOLDER = 'breadtalk_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}/*'
        self.z_path = None
        self.extract_path = None
        self.POS = 'https://am177.pos365.vn'
        self.ACC = 'admin'
        self.PW = 'aeonhd'
        self.breadtalk_email = 'autoreport2023@gmail.com'
        self.smtp_host = 'smtp.gmail.com'
        self.imap_host = 'imap.gmail.com'
        self.gmail_user = 'tungpt@pos365.vn'
        self.gmail_pass = 'abqqzkkrgftlodny'
        self.recv_email = 'trungn@aeonmall-vn.com'

    def scan_file(self, EXT):
        files = glob.glob(f'{self.extract_path}/{EXT}')
        # print(files)
        return max(files, key=os.path.getmtime)

    def get_sys_report(self):
        # from pos_api.adapter import submit_order, submit_payment
        sys_report = self.scan_file('System*.xls')
        excel = xlrd.open_workbook(sys_report)
        raw = excel[0]
        nRows = raw.nrows
        card = 0
        extract = {}
        for row in range(1, nRows):
            data = raw[row][2].value
            if not len(data.strip()): continue
            for keyword in [
                'Rounding Total', 'Non $ Col Diff',
                'Total Revenue', 'Tax Collected', 'Total Discounts',
                'CASH', 'MASTER', 'VISA', 'AMEX', 'STAFF MEAL',
                'SAMPLING', 'BREADTALK', 'BT', 'GRAB',
                'SODEXO', 'ESTEEM', 'GOTIT', 'VNpay', 'Now', 'VI MOMO',
                'BAEMIN', 'VinID', 'URBOX', 'SHOPEE PAY', 'Shopee Merchant',
                'Mobile Gift', 'Giftpop', 'ZaloPay',
                # Product
                'BREAD', 'CAKE', 'BEVERAGE', 'OTHERS'

            ]:
                if data.strip().startswith(keyword):
                    if keyword in ['BREAD', 'CAKE', 'BEVERAGE', 'OTHERS']:
                        _ = data.replace(keyword, '').strip().split()
                        # print(keyword, _)
                        qty = int(_[-2].replace(',', ''))
                        total = int(_[-1].replace(',', ''))
                        extract.update({
                            keyword.upper(): {
                                'Code': keyword.upper(),
                                'Name': keyword.upper(),
                                'Price': round(total / qty, 0),
                                'Quantity': qty
                            }
                        })
                    else:
                        _ = data.replace(keyword, '').strip().split()[-1]  # print(keyword, _)
                        _ = int(_.replace(',', ''))
                        if extract.get(keyword.upper()) and keyword.upper() != 'ROUNDING TOTAL':
                            extract.update({
                                keyword.upper(): int(_) + extract[keyword.upper()]
                            })
                        else:
                            extract.update({
                                keyword.upper(): int(_)
                            })
                    break
            if data.strip().startswith('System Sales Report'):
                for _ in data.strip().split('\n'):
                    if _.strip().startswith('Date Range'):
                        self.DATE = _.replace('Date Range', '').strip().split()
                        self.DATE = '-'.join(self.DATE[:3])
        self.DATE = datetime.strptime(self.DATE, '%d-%m-%y')
        total = extract['TOTAL REVENUE']
        discount = abs(extract['TOTAL DISCOUNTS'])
        self.VAT = extract['TAX COLLECTED']
        cash = extract['CASH']
        card = extract['MASTER']
        card += extract['VISA']
        card += extract['AMEX']
        voucher = extract['BREADTALK']
        voucher += extract['BT']
        voucher += extract['GRAB']
        voucher += extract['SODEXO']
        voucher += extract['ESTEEM']
        voucher += extract['GOTIT']
        voucher += extract['URBOX']
        voucher += extract['MOBILE GIFT']
        voucher += extract['GIFTPOP']
        vnpay = extract['VNPAY']
        now = extract['NOW']
        momo = extract['VI MOMO']
        baemin = extract['BAEMIN']
        vinid = extract['VINID']
        shopee = extract['SHOPEE PAY']
        shopee += extract['SHOPEE MERCHANT']
        zalo = extract['ZALOPAY']
        pms = [
            {'Name': 'CASH', 'Value': cash},
            {'Name': 'CARD', 'Value': card},
            {'Name': 'VOUCHER', 'Value': voucher},
            {'Name': 'VNPAY', 'Value': vnpay},
            {'Name': 'NOW', 'Value': now},
            {'Name': 'MOMO', 'Value': momo},
            {'Name': 'BAEMIN', 'Value': baemin},
            {'Name': 'VINID', 'Value': vinid},
            {'Name': 'SHOPEE', 'Value': shopee},
            {'Name': 'ZALOPAY', 'Value': zalo},
        ]
        ods = []
        ods.append(extract['BREAD'])
        ods.append(extract['CAKE'])
        ods.append(extract['BEVERAGE'])
        ods.append(extract['OTHERS'])
        for _ in pms.copy():
            if _['Value'] == 0:
                pms.remove(_)
        self.ORDERS.append({
            'Code': f'FINAL_{self.DATE.strftime("%Y%m%d")}',
            'Status': 2,
            'PurchaseDate': self.DATE.strftime('%Y-%m-%d 23:00:00'),
            'Discount': discount,
            'Total': self.VAT,
            'TotalPayment': total,
            'VAT': self.VAT,
            'OrderDetails': ods,
            'PaymentMethods': pms
        })
        cash = -extract['NON $ COL DIFF']
        cash -= extract['ROUNDING TOTAL']
        self.TRANS.append({
            'Code': f'{self.DATE.strftime("%y%m%d")}-CASH',
            'OrderCode': f'FINAL_{self.DATE.strftime("%Y%m%d")}',
            'Amount': cash,
            'TransDate': self.DATE.strftime('%Y-%m-%d 23:00:00'),
            'AccountId': 'CASH'
        })

    def get_time_report(self):
        # from pos_api.adapter import submit_order, submit_payment
        time_report = self.scan_file('Time*.xls')
        time = xlrd.open_workbook(time_report)
        raw = time[0]
        nRows = raw.nrows
        next = False
        ord = {
            'Total': None,
            'Count': None,
            'Hour': None
        }
        sales = []
        for row in range(14, nRows):
            # if next:

            code = raw[row][2].value
            if not len(code.strip()):
                continue
            elif 'Net Sales Total' in code:
                total = code.replace('Net Sales Total', '').strip()
                total = float(total.replace(',', ''))
                # print('==> total', total)
                ord.update({'Total': total})
            elif 'Average $/Check' in code:
                count = code.replace('Average $/Check', '').strip().split()[0]
                # print('==> count', count)
                ord.update({'Count': int(count)})
                if ord.get('Hour'):
                    sales.append(ord)
                ord = {
                    'Total': None,
                    'Count': None,
                    'Hour': None
                }
            elif 'Average $/Cover' in code:
                continue
            else:
                try:
                    _ = code.strip().split()
                    hour = int(_[0])
                    ord.update({'Hour': hour})
                except:
                    pass

        for pos, _ in enumerate(sales):
            self.ORDERS.append({
                'Code': f'TIME_{self.DATE.strftime("%Y%m%d")}_{_["Hour"]}_{_["Count"]}',
                'Status': 2,
                'PurchaseDate': f'{self.DATE.strftime("%Y-%m-%d")} {_["Hour"]}:00:00',
                'Discount': 0,
                'Total': _['Total'],
                'TotalPayment': -0,
                'VAT': 0,
                'OrderDetails': [],
                'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
            })
            # submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=order)
            for i in range(1,_['Count']):
                self.ORDERS_COUNT.append({
                    'Code': f'TIME_{self.DATE.strftime("%Y%m%d")}_{_["Hour"]}_{i}',
                    'Status': 2,
                    'PurchaseDate': f'{self.DATE.strftime("%Y-%m-%d")} {_["Hour"]}:00:00',
                    'Discount': 0,
                    'Total': 0,
                    'TotalPayment': 0,
                    'VAT': 0,
                    'OrderDetails': [],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                })
                # submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=order)
        for pos, _ in enumerate(sales):
            self.TRANS.append({
                'Code': f'{self.DATE.strftime("%y%m%d")}-{_["Hour"]}-CASH',
                "OrderCode": f'TIME_{self.DATE.strftime("%Y%m%d")}_{_["Hour"]}_{_["Count"]}',
                "Amount": 0,
                "TransDate": f'{self.DATE.strftime("%Y-%m-%d")} {_["Hour"]}:00:00',
                "AccountId": 'CASH'
            })

    def login(self):
        js = {
            'username': self.ACC,
            'password': self.PW
        }
        while True:
            try:
                r = self.browser.post(f'{self.POS}/api/auth', json=js, timeout=5).json()
                if r.get('SessionId'): break
            except:
                pass

    def check_total(self):
        since = self.DATE - timedelta(hours=7)
        since = since.strftime('%Y-%m-%dT17:00:00Z')
        before = self.DATE.strftime('%Y-%m-%dT16:59:00Z')
        self.browser.headers.update({'content-type': 'application/json'})
        while True:
            if self.TOTAL == 0: break
            try:
                filter = []
                filter += ['Status', 'eq', '2']
                filter += ['and']
                filter += ['PurchaseDate', 'ge']
                filter += [f"'datetime''{since}'''"]
                filter += ['and']
                filter += ['PurchaseDate', 'lt']
                filter += [f"'datetime''{before}'''"]
                # filter = str(*filter)
                print(' '.join(filter))
                params = {
                    'Top': '1',
                    'IncludeSummary': 'true',
                    'Filter': ' '.join(filter)
                }
                r = self.browser.get(f'{self.POS}/api/orders',
                                     params=params,
                                     timeout=5).json()
                print(self.TOTAL, r['results'][0]['Total'])
                if self.TOTAL == r['results'][0]['Total']:
                    return
                time.sleep(30)
            except Exception as e:
                print(e.__class__.__name__)
                time.sleep(5)

    def submit_data(self):
        from pos_api.adapter import submit_order, submit_payment
        self.login()
        self.TOTAL = 0
        for _ in self.ORDERS:
            self.TOTAL += _['Total']
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
        self.check_total()
        for _ in self.TRANS:
            # print(_)
            submit_payment(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
    def submit_count(self):
        from pos_api.adapter import submit_order, submit_payment
        for _ in self.ORDERS_COUNT:
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
    def forward_amhd(self):
          # Enter receiver address
        message = MIMEMultipart()
        message['Subject'] = f'Breadtalk Backup {self.DATE.strftime("%d-%m-%Y")}'
        message['From'] = self.gmail_user
        message['To'] = self.recv_email
        # toAddr = [to_email]
        toAddr = [self.recv_email]
        part = MIMEBase('application', 'octet-stream')
        with open(self.z_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(self.z_path).name))
        message.attach(part)
        while True:
            try:
                server = smtplib.SMTP_SSL(self.smtp_host, 465)
                server.login(self.gmail_user, self.gmail_pass)
                server.sendmail(self.gmail_user, toAddr, message.as_string())
                break
            except Exception as e:
                print(e)
                pass

    def get_data(self):
        imap = imaplib.IMAP4_SSL(self.imap_host)
        imap.login(self.gmail_user, self.gmail_pass)
        imap.select('Inbox')
        before = datetime.now()
        since = before - timedelta(days=1)
        before = before.strftime('%d-%b-%Y')
        since = since.strftime('%d-%b-%Y')
        search = []
        search += ['FROM', self.breadtalk_email]
        search += ['SINCE', f"{since}"]
        tmp, data = imap.search(None, *search)
        for num in data[0].split():
            tmp, data = imap.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            attachment = msg.get_payload()
            for item in attachment:
                if item.get_content_type() == 'application/octet-stream':
                    self.z_path = f'{self.FULL_PATH}/{item.get_filename()}'
                    self.extract_path = f'{self.FULL_PATH}/{since}_{num.decode("utf-8")}'
                    f = open(self.z_path, 'wb')
                    f.write(item.get_payload(decode=True))
                    f.close()
                    zipfile.ZipFile(self.z_path).extractall(self.extract_path)
                    self.TRANS = []
                    self.ORDERS = []
                    self.ORDERS_COUNT = []
                    self.get_sys_report()
                    if self.DATE.strftime('%d-%b-%Y') == since:
                        self.get_time_report()
                        self.submit_data()
                        self.forward_amhd()
                        self.submit_count()
            subprocess.Popen(['rm', '-rf', self.FULL_PATH], shell=False)
        # if self.DATE.strftime('%d-%b-%Y') == since:
        #     self.submit_count()

# x = BreadTalkAMHD()
# x.get_data()
# x.get_sys()
# x.get_time()
