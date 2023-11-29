import email
import glob
import imaplib
import os
import shutil
import smtplib
import subprocess
import sys
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os.path import dirname
from pathlib import Path
import openpyxl


class AM003(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.sender_email = 'sales-report@skechersvn.vn'
        self.smtp_host = 'smtp.gmail.com'
        self.imap_host = 'imap.gmail.com'
        self.gmail_user = 'tungpt@pos365.vn'
        self.gmail_pass = 'abqqzkkrgftlodny'
        self.recv_email = 'trungn@aeonmall-vn.com'
        self.ADAPTER_RETAILER = 'skechers_amhd'
        self.ADAPTER_TOKEN = '8160a62214f756fdd68e3da0be37541fd439b83ce9e49365bd6e9f5fa21bdb29'
        self.FOLDER = 'skechers_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.NOW = datetime.now() - timedelta(days=1)
        self.xlsx_path = None

    def extract_data(self):
        from pos_api.adapter import submit_error, submit_order
        dataframe = openpyxl.load_workbook(self.xlsx_path, data_only=True)
        data = dataframe.worksheets[0]
        orders = {}
        for row in range(2, data.max_row + 1):
            code = data[row][1].value
            if not code: continue
            code = str(code).strip()
            if not len(code): continue
            pur_date = data[row][2].value
            discount = abs(float(data[row][9].value))
            vat = abs(float(data[row][8].value))
            total = abs(float(data[row][7].value)) + vat
            ods = {
                'Name': data[row][4].value,
                'Code': data[row][3].value,
                'Price': float(data[row][5].value),
                'Quantity': abs(float(data[row][6].value)),
            }
            if not orders.get(code):
                orders.update({
                    code: {
                        'Code': code,
                        'Status': 2,
                        'PurchaseDate': pur_date.strftime('%Y-%m-%d 07:00:00'),
                        'Total': total,
                        'TotalPayment': total,
                        'VAT': vat,
                        'Discount': discount,
                        'OrderDetails': [ods],
                        'PaymentMethods': [{'Name': 'CASH', 'Value': total}]
                    }
                })
            else:
                orders[code]['OrderDetails'].append(ods)
                orders[code].update({
                    'Total': total + orders[code]['Total'],
                    'TotalPayment': total + orders[code]['TotalPayment'],
                    'VAT': vat + orders[code]['VAT'],
                    'Discount': discount + orders[code]['Discount'],
                    'PaymentMethods': [{'Name': 'CASH', 'Value': total + orders[code]['Total']}]
                })
        for k, v in orders.items():
            if not len(v['PaymentMethods']):
                v['PaymentMethods'] = [{'Name': 'CASH', 'Value': 0}]
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)

    def forward_amhd(self):
        message = MIMEMultipart()
        message['Subject'] = f'Skechers Backup {self.NOW.strftime("%d-%m-%Y")}'
        message['From'] = self.gmail_user
        message['To'] = self.recv_email
        toAddr = [self.recv_email]
        part = MIMEBase('application', 'octet-stream')
        with open(self.xlsx_path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(self.xlsx_path).name))
        message.attach(part)
        while True:
            try:
                server = smtplib.SMTP_SSL(self.smtp_host, 465)
                server.login(self.gmail_user, self.gmail_pass)
                server.sendmail(self.gmail_user, toAddr, message.as_string())
                break
            except:
                pass
        subprocess.Popen(['rm', '-rf', self.xlsx_path], shell=False)

    def get_data(self):
        imap = imaplib.IMAP4_SSL(self.imap_host)
        imap.login(self.gmail_user, self.gmail_pass)
        imap.select('Inbox')
        before = datetime.now() + timedelta(days=1)
        since = before - timedelta(days=1)
        before = before.strftime('%d-%b-%Y')
        since = since.strftime('%d-%b-%Y')
        search = []
        search += ['FROM', self.sender_email]
        search += ['SINCE', f"{since}"]
        search += ['BEFORE', f"{before}"]
        tmp, data = imap.search(None, *search)
        for num in data[0].split():
            tmp, data = imap.fetch(num, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            attachment = msg.get_payload()
            for item in attachment:
                if item.get_content_type() == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    self.xlsx_path = f'{self.FULL_PATH}/{item.get_filename()}'
                    f = open(self.xlsx_path, 'wb')
                    f.write(item.get_payload(decode=True))
                    f.close()
                    self.extract_data()
                    self.forward_amhd()
