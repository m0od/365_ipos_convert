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
from email.utils import parsedate_to_datetime
from os.path import dirname
from pathlib import Path
import requests
import xlrd


class AM194(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        from pos import POS365
        self.ADAPTER_RETAILER = 'jollibee_amhd'
        self.ADAPTER_TOKEN = '7c56878bf662384ae91e6f97fed59b1ccccc51eab36bebce55b5166b8543c5b1'
        self.browser = requests.session()
        self.ORDERS = []
        self.ORDERS_COUNT = []
        self.TRANS = []
        self.DATE = None
        self.VAT = 0
        self.FOLDER = 'jollibee_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.z_path = None
        self.extract_path = None
        self.POS = POS365()
        self.POS.DOMAIN = self.__class__.__name__
        self.POS.ACCOUNT = 'admin'
        self.POS.PASSWORD = 'aeonhd'
        self.breadtalk_email = 'jbvn158@gmail.com'
        self.smtp_host = 'smtp.gmail.com'
        self.imap_host = 'imap.gmail.com'
        self.gmail_user = 'tungpt@pos365.vn'
        self.gmail_pass = 'abqqzkkrgftlodny'
        self.recv_email = 'trungn@aeonmall-vn.com'
        self.ATTACHMENTS = []

    def get_attachments(self):
        try:
            imap = imaplib.IMAP4_SSL(self.imap_host)
            imap.login(self.gmail_user, self.gmail_pass)
            imap.select('Inbox')
            before = datetime.now() - timedelta(days=6)
            since = before - timedelta(days=7)
            before = before.strftime('%d-%b-%Y')
            since = since.strftime('%d-%b-%Y')
            search = []
            search += ['FROM', self.breadtalk_email]
            search += ['SINCE', f"{since}"]
            tmp, data = imap.search(None, *search)
            for num in data[0].split():
                tmp, data = imap.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                # print(msg.get('Date'), type(msg.get('Date')))
                # print(parsedate_to_datetime(msg.get('Date')))
                attachment = msg.get_payload()
                for item in attachment:
                    if item.get_content_type() == 'application/vnd.ms-excel':
                        self.ATTACHMENTS.append(item)
        except Exception as e:
            print(e)
            pass

    def scan_file(self, EXT):
        try:
            files = glob.glob(f'{self.FULL_PATH}/{EXT}')
            return max(files, key=os.path.getmtime)
        except:
            return None

    def get_time_data(self):
        from pos_api.adapter import submit_order, submit_error, submit_payment
        ws = self.scan_file('*time.xls')
        if not ws:
            submit_error(self.ADAPTER_RETAILER, 'TIME_NOT_FOUND')
            return
        ws = xlrd.open_workbook(ws)
        raw = ws[0]
        nRows = raw.nrows
        sales = 0
        get = False
        date = None
        hour = None
        for row in range(1, nRows):
            data = raw[row][0].value
            if 'Business Date' in data:
                date = data.strip().split('From')[1].split('to')[0].strip()
                date = datetime.strptime(date, '%A, %B %d, %Y')
            elif '-' in data and '05:59' not in data:
                get = True
                hour = data.strip().split('-')[1]
                hour = datetime.strptime(hour, '%H:%M')
            elif 'Net Sales' in data and get:
                sales = float(data.strip().split()[-1].replace(',', ''))
            elif 'Average Check' in data and get:
                count = int(data.strip().split()[2].replace(',', ''))
                # print(x)
                get = False
                d = date.strftime("%Y%m%d")
                code = f'TIME_{d}{hour.strftime("%H")}'
                d = date.strftime("%Y-%m-%d")
                h = hour.strftime("%H:00:00")
                order = {
                    'Code': f'{code}_{count}',
                    'Status': 2,
                    'PurchaseDate': f'{d} {h}',
                    'Discount': 0,
                    'Total': sales,
                    'TotalPayment': 0,
                    'VAT': 0,
                    'OrderDetails': [{'ProductId': 0}],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                }
                pm = {
                    'Code': f'{code}_{count}-CASH',
                    "OrderCode": f'{code}_{count}',
                    "Amount": 0,
                    "TransDate": f'{d} {h}',
                    "AccountId": 'CASH'
                }
                submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)
                submit_payment(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, pm)
                for i in range(1, count):
                    order = {
                        'Code': f'{code}_{i}',
                        'Status': 2,
                        'PurchaseDate': f'{d} {h}',
                        'Discount': 0,
                        'Total': 0,
                        'TotalPayment': 0,
                        'VAT': 0,
                        'OrderDetails': [],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': 0}]
                    }
                    submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)

    def get_sys_data(self):
        from pos_api.adapter import submit_order, submit_error, submit_payment
        ws = self.scan_file('*report.xls')
        if not ws:
            submit_error(self.ADAPTER_RETAILER, 'TIME_NOT_FOUND')
            return
        ws = xlrd.open_workbook(ws)
        raw = ws[0]
        nRows = raw.nrows
        vat = 0
        total = 0
        delivery = 0
        keyword = [
            'BUSINESS DATE', '+DELIVERY CHARGE','+ TAX', 'NET SALES W/ TAX', 'CASH REPORT',
            'GC', 'ZALO', 'USED OIL', 'GRAB', 'BAEMIN', 'NOW', 'GOT IT',
            'UTOP', 'BE', 'GOJEK', 'MOMO', 'QR CODE', 'SODEXO'
        ]
        pm = {}
        row = 0
        date = None
        while row < nRows:
            # for row in range(0, nRows):
            data = str(raw[row][0].value).upper().strip()
            # print(data)
            for k in keyword:
                if data.startswith(k):
                    data = data.replace(k, '')
                    if k == 'BUSINESS DATE':
                        data = str(raw[row][0].value)
                        date = data.strip().split('From')[1].split('to')[0].strip()
                        date = datetime.strptime(date, '%A, %B %d, %Y')
                    elif k == '+DELIVERY CHARGE':
                        delivery = float(data.strip().split()[1].replace(',', ''))
                    elif k == '+ TAX':
                        vat += float(data.strip().split()[1].replace(',', ''))
                    elif k == 'NET SALES W/ TAX' and not total:
                        total = float(data.strip().split()[0].replace(',', ''))
                    elif k == 'CASH REPORT':
                        for _ in range(row, nRows):
                            data = str(raw[row][0].value).upper()
                            # print(data)
                            if not data.startswith('OTHERS'):
                                row += 1

                            else:
                                # print(row)
                                break
                    else:
                        # print(row, str(raw[row][0].value).upper())
                        try:
                            value = float(data.strip().split()[-1].replace(',', ''))
                            if not pm.get(k):
                                pm.update({k: value})
                            else:
                                pm[k] += value
                        except:
                            pass
            row += 1
        print('*' * 5)
        pms = []
        # print(pm)
        pm.pop('NET SALES W/ TAX')
        other = 0
        print(total, type(total))
        for k, v in pm.items():
            print(v, type(v))
            if v:
                other += v
                pms.append({'Name': k, 'Value': v})
        pms.append({'Name': 'CASH', 'Value': total-other})
        order = {
            'Code': f'FINAL_{date.strftime("%Y%m%d")}',
            'Status': 2,
            'PurchaseDate': f'{date.strftime("%Y-%m-%d 07:00:00")}',
            'Discount': 0,
            'Total': vat + delivery,
            'TotalPayment': 0,
            'VAT': vat,
            'OrderDetails': [{'ProductId': 0}],
            'PaymentMethods': pms,
            'ShippingCost': delivery
        }
        print(order)
        submit_order(self.ADAPTER_RETAILER, self.ADAPTER_TOKEN, order)

    def get_data(self):
        self.get_attachments()
        for item in self.ATTACHMENTS:
            print(item.get_filename().lower())
            self.z_path = f'{self.FULL_PATH}/{item.get_filename().lower()}'
            # self.extract_path = f'{self.FULL_PATH}/{since}_{num.decode("utf-8")}'
            f = open(self.z_path, 'wb')
            f.write(item.get_payload(decode=True))
            f.close()
        self.get_time_data()
        self.get_sys_data()
