import json
import smtplib
import sys
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os.path import dirname
from pathlib import Path
# import xlsxwriter
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
import requests
import pandas as pd
JSON_CRED = {
    "type": "service_account",
    "project_id": "kt365-387014",
    "private_key_id": "9eb19ad641f9d39c1088f931f3c43954e68b2367",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCUMuYltO1xyWoW\nNfXavlO02Ch3PSbAseVuUhcnzRPhVTkXqU8UiQYStUuhgcwY0KIypbftw3qRUYrd\nvgub++VqKiEHp2S2/1MYt9SYXVbmTEYmoVO5S7yWQFfXAvrDOPkAwyG3UQtUG2Ve\nF7P+jcUGU6WWLOZih7/WtNklEFi4BmVKaO564NubGtC5qRLlaFVP7DVHCcoghCqK\n4cnX5NHN3F854la3gyZDsm7j8fe/p9RAW4Xv1Hia4AjASJ9BiStkYgmyC7OBCxQM\nOcgI+SVtCiKyH/qnPB+y7v4QcxxvroRNHumCG30bdySHVqUvjpFH46TFQFkZCm2+\nv4hJylYrAgMBAAECggEAKR1t6Gwnq/fbLMpPqR5Ajt2hbGNUywUPx+mSbwJgT5Wb\nP0tDm0jgnHQbxXUDMKdBOJftTVN8P7DFu/srsVzTKv8BJuRz9qkjXqoxmwvaPg5P\nMAx18+RlL7IuLIKxG1RFEMcSJY+gevcWymH9F9QxIy41tFJEoHVU7bZCwBum4XbI\nnJkEr40SF7CoN+8VJvvccZc+BF3ak00SJkxmXMsmvE3PMbOsfdlMNo9mP9f2FpJP\nV2OIOJKBFSJ+9Va++yNZHdl/l+B5Rcfw40AUuY7OJMxRwHVMoNf/PSnZtuGanGzK\nzpC/avLHPA7HbxetFtfbUp64mukPQI5Qas98lNj0sQKBgQDK3FvIhCUZ5j/7A3A8\nKruUKJH7xh/+8OuFIzwnE7URaF9BwdJqnGJ8AvSVJ0Xv3XTTkbyLjeWX9rcJ876o\nbFVkdzRdfZtDM8Ro9tNJAs3unM5jEYuaAKipIGpLjq8aIR8B2zOsz8ZNM57NLKTr\n7ftygxPFmo2TYSlfj6biANrE7QKBgQC7BPbphmhheVfAqw1t6vRYNc2EGqrJghv2\nbeQHR51iS1lNkprGb1s1Tr4QfXqG55J3IEocM25jutWrXTMWQr0qLDDycahRzSHa\nqCCFBvbBuxtp14EhEGQ1wq8tjffqHgWJqbWmPlcSPd9x04MPeVFO/+srX0b5gmjw\nxPayjs58dwKBgQCKHkCLpJVSLfeP40ZuYLX4aSsD3mB4hvYEXvocrQlSQdrhfaLT\nHYjcYHLAfs3aQ9DAH/Dcn48byUnUh9Ve/OujDJplsRieR8fJo4w1oKgvdyn6P77p\n6trq0/wrV4mW48glzmY/mfOtKqFLlsLvM8hIrkAvAUy1dKjjvH3mUKii/QKBgDvk\nbx6CSNNOhOfS384fvHizYkm4MJGv9TyKHMioCqL79nF9TcvWxaLgwMWPKboiVymH\nUbSOU//kSaFDi6TJYsMqu9Ioy/rGct0PkrqHbGbGgRT4SwZHtY/x9R/lo0t6qdNY\nYjAHLuNMpU5Sqlo+Q+fE1Y9iR9yIAwt4SHkOetopAoGAJ+zARDsoxKdBNH3nMmU6\nsF/I9ItT82Liun8beId5+AMqbFlEOmwWChtATPsa42c5rKnvtBpNDwavgD+0FCNW\nq8aZ2KhbN1Z0Fjp0aLMhxbOLTtwk0DDpNDqqRwp3D3BZHX/BbpAScJWVmmtEHG+r\n2NKVg7C/T4EkMflIf8AEUlA=\n-----END PRIVATE KEY-----\n",
    "client_email": "kt365service@kt365-387014.iam.gserviceaccount.com",
    "client_id": "109188131360468428010",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/kt365service%40kt365-387014.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}
SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
FOLDER = '1B0ZaHo3h2MLpX7HSRZjtZ3Fux59AHUzH'

map_pm = {
    'LANDLORD-CASH': None, 'CASH TTTM': None,

    'CÀ THẺ': 'CREDIT CARD', 'PAYOO-POS': 'CREDIT CARD', 'PAYOO': 'CREDIT CARD',
    'POS': 'CREDIT CARD', 'CREDIT CARD': 'CREDIT CARD', 'STORE CREDIT': 'CREDIT CARD',
    'DEBIT CARD': 'CREDIT CARD', 'THẺ NGÂN HÀNG': 'CREDIT CARD', 'LANDLORD-CR.CARD': 'CREDIT CARD',
    'NAPAS': 'CREDIT CARD', 'VISA': 'CREDIT CARD', 'THẺ ATM': 'CREDIT CARD',
    'QUẸT THẺ': 'CREDIT CARD', 'DEBIT VN': 'CREDIT CARD', 'CONNECT24': 'CREDIT CARD',
    'MASTER': 'CREDIT CARD', 'TIỀN THẺ': 'CREDIT CARD', 'VIETIN BANK': 'CREDIT CARD',
    'CREDIT': 'CREDIT CARD', 'TK THẺ': 'CREDIT CARD', 'THANH TOÁN QUA THẺ': 'CREDIT CARD',
    'AMERICAN EXPRESS': 'CREDIT CARD', 'MASTER CARD': 'CREDIT CARD', 'THẺ NGÂN HÀNG + QR': 'CREDIT CARD',
    'TK NGÂN HÀNG': 'CREDIT CARD', 'THẺ': 'CREDIT CARD', 'BANK CARD': 'CREDIT CARD',
    'PAYOO POS': 'CREDIT CARD', 'CREDIT/ CÀ THẺ': 'CREDIT CARD', 'PAYOO QR': 'CREDIT CARD',
    'THANH TOÁN THẺ': 'CREDIT CARD', 'QUÉT QR PAYOO': 'CREDIT CARD', 'CARD': 'CREDIT CARD',
    'ATM': 'CREDIT CARD', 'NAPAS_ONLINE': 'CREDIT CARD', 'DEBIT': 'CREDIT CARD',
    'QRVCB': 'CREDIT CARD', 'VIETCOMBANK': 'CREDIT CARD', 'TECHCOMBANK': 'CREDIT CARD',
    'AGRIBANK': 'CREDIT CARD', 'FABI_DEBT': 'CREDIT CARD', 'MASTERCARD': 'CREDIT CARD',
    'VISA DEBIT': 'CREDIT CARD', 'MASTER DEBIT': 'CREDIT CARD', 'AMERICAN EXPRESS DEBIT': 'CREDIT CARD',
    'JCB': 'CREDIT CARD', 'UNIONPAY': 'CREDIT CARD', 'DISCOVER NETWORK': 'CREDIT CARD',
    'DINNERS CLUB INTERNATIONAL': 'CREDIT CARD', 'THE TIN DUNG': 'CREDIT CARD', 'POSAEON': 'CREDIT CARD',
    'CKAEON': 'CREDIT CARD', 'QR PAY': 'CREDIT CARD', 'PQT': 'CREDIT CARD',
    'VTB': 'CREDIT CARD', 'BIDV': 'CREDIT CARD', 'BANK': 'CREDIT CARD',
    'PAYOOATM': 'CREDIT CARD', 'BANK TTTM': 'CREDIT CARD', 'TM_TNHA(VE.CTY)': 'CREDIT CARD',

    'CHUYỂN KHOẢN': 'BANK TRANSFER', 'VIETQR': 'BANK TRANSFER', 'MOBILE BANKING (QR)': 'BANK TRANSFER',
    'THANH TOÁN LIVESTREAM': 'BANK TRANSFER', 'E-PAYMENT': 'BANK TRANSFER', 'IPAY': 'BANK TRANSFER',
    'QR': 'BANK TRANSFER', 'BÁN ONLINE': 'BANK TRANSFER', 'MOBILE BANKKING': 'BANK TRANSFER',
    'BANK TRANSFER': 'BANK TRANSFER', 'BACKWORKQR4': 'BANK TRANSFER', 'COD': 'BANK TRANSFER',
    'LOSHIP_PAY': 'BANK TRANSFER', 'ONLINE': 'BANK TRANSFER', 'PAYMENT_ON_DELIVERY': 'BANK TRANSFER',
    'PLATFORM': 'BANK TRANSFER', 'SKYBANK': 'BANK TRANSFER', 'SKYLINE': 'BANK TRANSFER',
    'SKYPOINT': 'BANK TRANSFER', 'WEBSITE_PAYMENT': 'BANK TRANSFER', 'HS.COD_ONLINE_AO': 'BANK TRANSFER',
    'VHS.COD_ONLINE_A': 'BANK TRANSFER', 'E-WALLET': 'BANK TRANSFER', 'CK': 'BANK TRANSFER',

    'ZALO-PAY': 'ZALOPAY', 'ZALO PAY': 'BANK TRANSFER', 'ZALO_ONLINE': 'BANK TRANSFER',
    'ZALOPAYQR4': 'ZALOPAY',

    'VNPAY-QR': 'VNPAY', 'VNPAY-POS': 'VNPAY', 'VNPAY': 'VNPAY', ' VN PAY': 'VNPAY',
    'VNPAY_APP': 'VNPAY', 'VNPAY_OD_ONLINE': 'VNPAY', 'VNPAY_ONLINE': 'VNPAY',
    'VNPAYOFFLINE': 'VNPAY', 'VNPAYQR4': 'VNPAY', 'VNPAY - TĨNH': 'VNPAY',

    'ĐẶT HÀNG': 'DATHANG', 'ĐẶT CỌC': 'DATHANG',

    'VOUCHER': 'VOUCHER', 'CHECK': 'VOUCHER', 'GIFT CERTIFICATE': 'VOUCHER',
    'GIFT CARD': 'VOUCHER', 'CENTRAL GIFT CARD': 'VOUCHER', 'CENTRAL GIFT CERTIFICATE': 'VOUCHER',
    'CENTRAL CREDIT': 'VOUCHER', 'ESTEM VOUCHER': 'VOUCHER', 'MERCHANDISE EXCHANGE VOUCHER': 'VOUCHER',
    'CPMD': 'VOUCHER', 'AER7HRWJ': 'VOUCHER', 'AEC12C9L': 'VOUCHER',
    'AER4CR84': 'VOUCHER', 'AER4HR2N': 'VOUCHER', 'FBAE': 'VOUCHER',
    'CPNE': 'VOUCHER', 'DEALTODAY': 'VOUCHER', 'CHEQUE': 'VOUCHER',
    'ROUND OFF': 'VOUCHER', 'ĐỔI TRẢ HÀNG': 'VOUCHER', 'CLINGME': 'VOUCHER',
    'GIFTCARD': 'VOUCHER', 'URBOX': 'VOUCHER', 'VC': 'VOUCHER',
    'VOU_GOTIT': 'VOUCHER', 'UTOP PAYMENT': 'VOUCHER', 'ESSTEEM GIFT': 'VOUCHER',
    'PHIẾU QUÀ TẶNG': 'VOUCHER', 'GOTIT': 'VOUCHER', ' GOT IT': 'VOUCHER',

    'CUSTOMER LOYALTY': 'POINT', 'PARAFAIT CARD': 'POINT', 'KHTT': 'POINT',

    'MOCA': 'MOCA', 'GRAB MOCA': 'MOCA', 'GRAP FOOD': 'MOCA',

    'MOMOOFFLINE': 'MOMO', 'MOMO': 'MOMO', 'MOMO_APP': 'MOMO',
    'MOMO_OD_ONLINE': 'MOMO', 'MOMO_ONLINE': 'MOMO', 'MOMO_P2SU': 'MOMO',
    'MOMO_SCANNER_V2': 'MOMO', 'MOMO1': 'MOMO', 'MOMOQR4': 'MOMO',
    'MOMO PAYMENT': 'MOMO',

    'GRAB': 'GRAB', 'GRABPAY': 'GRAB', 'GRAB_ONLINE': 'GRAB',
    'MOCA1': 'GRAB', 'MOCAQR4': 'GRAB', 'GRAB WALLET': 'GRAB',

    'SHOPEEPAY': 'SHOPEE', 'SHOPEEFOOD': 'SHOPEE', 'NOW': 'SHOPEE',
    'AIRPAY': 'SHOPEE', 'AIRPAY_APP': 'SHOPEE', 'AIRPAYQR4': 'SHOPEE',
    'NOWPAY': 'SHOPEE', 'QRSHOPEE': 'SHOPEE', 'SHOPEE PAY': 'SHOPEE',
    'VINOW': 'SHOPEE', 'SHOPEE FOOD': 'SHOPEE',

    'BAEMIN': 'BAEMIN', 'GOJEK': 'BAEMIN', 'BEAMIN': 'BAEMIN',

    'GOVIET': 'GOJEK',

    'VIETTEL-PAY': 'VIETTELPAY',

    'TCH_PAYMENT': 'OTHER', 'TGFOOD': 'OTHER', 'TOHOAQR4': 'OTHER',
    'VINID_APP': 'OTHER', 'VINIDPAY_ONLINE': 'OTHER', 'VINIDPAYQR4': 'OTHER',
    'LALA_PAYMENT': 'OTHER', 'RDEPOSIT': 'OTHER', 'SO': 'OTHER',
    'TGPOINT': 'OTHER', 'TGTOKENQR4': 'OTHER', 'VIN': 'OTHER',
    'VINIDPAY': 'OTHER', 'BE FOOD': 'OTHER', 'BE': 'OTHER',
    'ĐỔI HÀNG': 'OTHER', 'KHÁC': 'OTHER', 'VINID': 'OTHER', 'BANK ACCOUNT': 'OTHER',
}


def auth(domain):
    while True:
        try:
            b = requests.session()
            b.headers.update({'content-type': 'application/json'})
            r = b.post(f'https://{domain}.pos365.vn/api/auth', json={
                # 'Username': 'quantri@pos365.vn',
                # 'Password': 'IT@P0s365kmS'
                'Username': 'report',
                'Password': '123123123'
            })
            if r.status_code == 200:
                return b
            else:
                print(domain, r.json())
                return None
        except:
            pass


def get_accounts(browser, domain):
    accs = {}
    while True:
        try:
            r = browser.get(f'https://{domain}.pos365.vn/api/accounts')
            if r.status_code != 200: continue
            js = r.json()
            for _ in js:
                # print(map_pm.get(_['Name'].upper()), _['Name'])
                accs.update({
                    _['Id']: map_pm.get(_['Name'].upper())
                })
            break
        except:
            continue

    return accs


def get_orders(browser, domain):
    skip = 0
    orders = []
    while True:
        try:
            p = {
                'format': 'json',
                'Top': '50',
                'Skip': str(skip),
                # 'Filter': "PurchaseDate eq 'yesterday' and Status eq 2",
                'Filter': "PurchaseDate eq 'lastmonth' and Status eq 2",
                'Includes': 'OrderDetails',
                'Orderby': 'PurchaseDate'
            }
            r = browser.get(f'https://{domain}.pos365.vn/api/orders', params=p)
            if r.status_code != 200: continue
            js = r.json()
            if len(js['results']) == 0: break
            orders.extend(js['results'])
            skip += 50
        except:
            continue
    return orders


def get_returns(browser, domain):
    skip = 0
    orders = []
    while True:
        try:
            p = {
                'format': 'json',
                'Top': '50',
                'Skip': str(skip),
                # 'Filter': "ReturnDate eq 'yesterday' and Status eq 2",
                'Filter': "ReturnDate eq 'lastmonth' and Status eq 2",
                'Orderby': 'ReturnDate'
            }
            r = browser.get(f'https://{domain}.pos365.vn/api/returns', params=p)
            if r.status_code != 200: continue
            js = r.json()
            if len(js['results']) == 0: break
            orders.extend(js['results'])
            skip += 50
        except:
            continue
    return orders


def get_product_name(browser, domain, pid):
    while True:
        try:
            r = b.get(f'https://{domain}.pos365.vn/api/products', params={
                'Filter': f'Id eq {_}'
            })
            if r.status_code != 200: continue
            if len(r.json()['results']) > 0:
                return r.json()['results'][0]['Name'].strip()
            return None
        except:
            pass


def get_branch(browser, domain):
    while True:
        try:
            vendor = b.get(f'https://{domain}.pos365.vn/Config/VendorSession').text
            branchs = json.loads(vendor.split('branchs:')[1].split('],')[0] + ']')
            branch = {}
            for _ in branchs:
                branch.update({
                    _['Id']: _['Name']
                })
            return branch
        except:
            pass

if __name__ == '__main__':
    PATH = dirname(__file__)
    print(PATH)
    sys.path.append(PATH)
    pm = []
    data_order = {'Tenant': [], 'Mã hoá đơn': [], 'Ngày GD': [], 'Chiết khấu': [],
                  'Tổng hoá đơn': [], 'Khách thanh toán': [], 'VAT': [],
                  'CASH': [], 'CREDIT CARD': [], 'BANK TRANSFER': [], 'ZALOPAY': [], 'VNPAY': [], 'VIETTELPAY': [],
                  'DATHANG': [], 'VOUCHER': [], 'POINT': [], 'MOCA': [], 'MOMO': [], 'GRAB': [], 'SHOPEE': [], 'BAEMIN': [],
                  'GOJEK': [], 'OTHER': []}
    data_return = {'Tenant': [], 'Mã hoá đơn': [], 'Ngày GD': [], 'Chiết khấu': [], 'Tổng hoá đơn': [],
                   'Tổng chi': []}
    data_product = {'Tenant': [], 'Mã hoá đơn': [], 'Ngày GD': [], 'Tên sản phẩm': [], 'Số lương': [], 'Đơn giá': []}
    for am_num in range(1, 200):
        domain = 'am{:03d}'.format(am_num)
        print(domain)
        b = auth(domain)
        if b is None: continue
        branch = get_branch(b, domain)
        pm_name = get_accounts(b, domain)
        # print(pm_name)
        orders = get_orders(b, domain)
        # print(orders[0])
        products = []
        pid = []
        for _ in orders:
            # print(_)
            pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            pur_date = pur_date + timedelta(hours=7)
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            try:
                # print(_.get('MoreAttributes'))
                attr = json.loads(str(_.get('MoreAttributes')).strip())
                if attr is None: attr = {}
            except Exception as exxx:
                # print(exxx)
                attr = {}
                # print(attr is None)
            pm = {
                'CASH': 0,
                'CREDIT CARD': 0,
                'BANK TRANSFER': 0,
                'ZALOPAY': 0,
                'VNPAY': 0,
                'VIETTELPAY': 0,
                'DATHANG': 0,
                'VOUCHER': 0,
                'POINT': 0,
                'MOCA': 0,
                'MOMO': 0,
                'GRAB': 0,
                'SHOPEE': 0,
                'BAEMIN': 0,
                'GOJEK': 0,
                'OTHER': 0,
            }
            # print(attr)
            if attr.get('PaymentMethods') is not None:
                # print(_['MoreAttributes'])
                for __ in attr['PaymentMethods']:
                    if __.get('AccountId') is None or pm_name.get(__['AccountId']) is None:
                        pm.update({'CASH': __['Value']})
                    else:
                        pm.update({pm_name[__['AccountId']]: __['Value']})
            pm_str = '\t'.join(str(i) for i in list(pm.values()))
            # print(pm.values())
            discount = _.get('Discount') is not None and _['Discount'] or 0
            row = [branch.get(_['BranchId']), _['Code'], pur_date, discount, _['Total'], _['TotalPayment'], _['VAT']]
            row.extend(list(pm.values()))
            index = 0
            for k in data_order.keys():
                data_order[k].append(row[index])
                index += 1
            # data_order.append(row)
            for __ in _['OrderDetails']:
                products.append({
                    'id': __['ProductId'],
                    'qty': __['Quantity'],
                    'price': __['Price'],
                    'order': _['Code'],
                    'date': pur_date,
                    'branch': _['BranchId']
                })
                if __['ProductId'] not in pid:
                    pid.append(__['ProductId'])

            # print(f"{domain}\t{branch.get(_['BranchId'])}\t{_['Code']}\t{pur_date}\t"
            #       f"{discount}\t{_['Total']}\t{_['TotalPayment']}\t{_['VAT']}\t{pm_str}")
            # print(_['Code'], branch.get(_['BranchId']), pur_date,
            #       _['Discount'], _['Total'], _['TotalPayment'], _['VAT'], pm)
            # break
        p_name = {}
        for _ in pid:
            name = get_product_name(b, domain, _)
            p_name.update({_: name})
        for _ in products:
            # print(_)
            if p_name.get(_['id']) is not None:
                row = [branch.get(_['branch']), _['order'], _['date'], p_name.get(_['id']), _['qty'], _['price']]
                # row.extend(list(pm.values()))
                index = 0
                for k in data_product.keys():
                    data_product[k].append(row[index])
                    index += 1
                # data_product.append(row)
        returns = get_returns(b, domain)
        for _ in returns:
            pur_date = datetime.strptime(_['ReturnDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
            pur_date = pur_date + timedelta(hours=7)
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            discount = _.get('Discount') is not None and _['Discount'] or 0
            row = [branch.get(_['BranchId']), _['Code'], pur_date, discount, _['Total'], _['TotalPayment']]
            index = 0
            for k in data_return.keys():
                data_return[k].append(row[index])
                index += 1
        # break



    df1 = pd.DataFrame(data_order)
    df2 = pd.DataFrame(data_product)
    df3 = pd.DataFrame(data_return)
    now = datetime.now() - timedelta(days=1)
    f_path = f"{PATH}/dailyreport{now.strftime('%d%m%Y')}.xlsx"
    writer = pd.ExcelWriter(f_path, engine='xlsxwriter')

    df1.to_excel(writer, sheet_name='Order', index=False)
    df2.to_excel(writer, sheet_name='Product', index=False)
    df3.to_excel(writer, sheet_name='Return', index=False)

    writer.close()

    port = 465  # For SSL
    password = 'abqqzkkrgftlodny'
    smtp_server = "smtp.gmail.com"
    sender_email = "tungpt@pos365.vn"  # Enter your address
    to_email = 'hadong.accounting@aeonmall-vn.com'  # Enter receiver address
    # to_email = 'marinmmo@gmail.com'
    cc_email = 'duongnguyen@pos365.vn'
    # cc_email = 'tungpt@pos365.vn'
    message = MIMEMultipart()
    message["Subject"] = f'dailyreport{now.strftime("%d%m%Y")}'
    message["From"] = 'tungpt@pos365.vn'
    message["To"] = to_email
    message["Cc"] = cc_email
    toAddr = [to_email, cc_email]
    part = MIMEBase('application', "octet-stream")
    with open(f_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename={}'.format(Path(f_path).name))
    message.attach(part)
    while True:
        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.login(sender_email, password)
            server.sendmail(sender_email, toAddr, message.as_string())
            break
        except Exception as e:
            print(e)
            pass