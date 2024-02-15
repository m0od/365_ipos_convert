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
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os.path import dirname
from pathlib import Path
import xlrd


class AM115(object):
    def __init__(self):
        PATH = dirname(dirname(dirname(__file__)))
        sys.path.append(PATH)
        self.sender_email = 'cntt@tocotocotea.com'
        self.smtp_host = 'smtp.gmail.com'
        self.imap_host = 'imap.gmail.com'
        self.gmail_user = 'tungpt@pos365.vn'
        self.gmail_pass = 'abqqzkkrgftlodny'
        self.recv_email = 'trungn@aeonmall-vn.com'
        self.ADAPTER_RETAILER = 'tocotoco_amhd'
        self.ADAPTER_TOKEN = 'd49f2de0062a35cff78550df114dc27b2ad33d6fece1e8f9509350fc64d7b31b'
        self.FOLDER = 'tocotoco_amhd'
        self.FULL_PATH = f'/home/{self.FOLDER}'
        self.NOW = datetime.now() - timedelta(days=1)
        self.xlsx_path = None

    # def get_float(self, d):
    #     try:
    #         return float(d.value)
    #     except:
    #         return 0

    def extract_data(self):
        def get_value(value):
            try:
                return float(value)
            except:
                return 0
        def get_date(value):
            try:
                value = (value - 25569) * 86400.0
                value = datetime.utcfromtimestamp(value)
                return value.strftime('%Y-%m-%d')
            except:
                return 0
        from pos_api.adapter import submit_error, submit_order
        ws = xlrd.open_workbook(self.xlsx_path)
        raw = list(ws.sheets())[0]
        orders = {}
        for i in range(4, raw.nrows):
            code = raw.row(i)[4].value
            if not code: continue
            code = str(code).strip()
            if not len(code): continue
            pur_date = f'{get_date(raw.row(i)[7].value)} {str(raw.row(i)[8].value)}'
            # print(pur_date)
            try:
                pur_date = datetime.strptime(pur_date, '%Y-%m-%d %H:%M')
                pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                continue
            # print(code)
            discount = get_value(raw.row(i)[11].value)
            total = get_value(raw.row(i)[18].value)
            vat = get_value(raw.row(i)[15].value)
            cash = get_value(raw.row(i)[24].value)
            cash += get_value(raw.row(i)[25].value)
            cash += get_value(raw.row(i)[27].value)
            cash += get_value(raw.row(i)[28].value)
            voucher = get_value(raw.row(i)[29].value)
            voucher += get_value(raw.row(i)[30].value)
            voucher += get_value(raw.row(i)[31].value)
            voucher += get_value(raw.row(i)[32].value)
            voucher += get_value(raw.row(i)[41].value)
            voucher += get_value(raw.row(i)[42].value)
            voucher += get_value(raw.row(i)[43].value)
            voucher += get_value(raw.row(i)[44].value)
            voucher += get_value(raw.row(i)[45].value)
            voucher += get_value(raw.row(i)[46].value)
            voucher += get_value(raw.row(i)[48].value)
            voucher += get_value(raw.row(i)[49].value)
            vani = get_value(raw.row(i)[33].value)
            vnpay = get_value(raw.row(i)[34].value)
            vnpay += get_value(raw.row(i)[47].value)
            zalopay = get_value(raw.row(i)[35].value)
            momo = get_value(raw.row(i)[36].value)
            jamja = get_value(raw.row(i)[37].value)
            metee = get_value(raw.row(i)[38])
            mediaone = get_value(raw.row(i)[39].value)
            sodexo = get_value(raw.row(i)[40].value)
            pms = [
                {'Name': 'CASH', 'Value': cash},
                {'Name': 'VOUCHER', 'Value': voucher},
                {'Name': 'VNPAY-POS', 'Value': vnpay},
                {'Name': 'ZALO-PAY', 'Value': zalopay},
                {'Name': 'MOMO', 'Value': momo},
                {'Name': 'JAMJA', 'Value': jamja},
                {'Name': 'METEE', 'Value': metee},
                {'Name': 'MEDIAONE', 'Value': mediaone},
                {'Name': 'SODEXO', 'Value': sodexo},
                {
                    'Name': str(raw.row(i)[5].value).upper().strip(),
                    'Value': get_value(raw.row(i)[26].value)
                },

            ]
            for _ in pms.copy():
                if not _['Value']: pms.remove(_)
            orders.update({code: {
                'Code': code,
                'Status': 2,
                'PurchaseDate': pur_date,
                'Total': total,
                'TotalPayment': total,
                'VAT': vat,
                'Discount': discount,
                'OrderDetails': [{'ProductId': 0}],
                'PaymentMethods': pms
            }})
        for k, v in orders.items():
            if not len(v['PaymentMethods']):
                v['PaymentMethods'] = [{'Name': 'CASH', 'Value': 0}]
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=v)
        subprocess.Popen(['rm', '-rf', self.xlsx_path], shell=False)

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
        before = datetime.utcnow() + timedelta(days=1)
        since = before - timedelta(days=2)
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
            subject = decode_header(msg["Subject"])[0][0].decode('utf-8')

            if 'Bảng kê chi tiết' in subject:
                print(subject)
                attachment = msg.get_payload()
                for item in attachment:
                    print(item.get_content_type())
                    if item.get_content_type() == 'application/octet-stream':
                        name = decode_header(item.get_filename())[0][0].decode('utf-8')
                        self.xlsx_path = f'{self.FULL_PATH}/{name}'
                        f = open(self.xlsx_path, 'wb')
                        f.write(item.get_payload(decode=True))
                        f.close()
                        self.extract_data()
                    if item.get_content_type() == 'multipart/mixed':
                        for part in item.walk():
                            if part.get_content_type() == 'application/octet-stream':
                                name = decode_header(part.get_filename())[0][0].decode('utf-8')
                                self.xlsx_path = f'{self.FULL_PATH}/{name}'
                                f = open(self.xlsx_path, 'wb')
                                f.write(part.get_payload(decode=True))
                                f.close()
                                self.extract_data()
