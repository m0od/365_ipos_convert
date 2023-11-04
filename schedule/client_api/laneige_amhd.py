from datetime import datetime
from os.path import dirname

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
SHEET_ID = '1-VOAOgCVfHARl2riwwIBCr1eYXGKNb54O8SePm2DDgY'
SHEET_ID = '1cp-6FTZsIwnolY5DlzkMb6O_TcS84ddfnHep2oVpL6I'
class LaneigeAMHD(object):
    def __init__(self):
        self.ADAPTER_RETAILER = 'laneige_amhd'
        self.ADAPTER_TOKEN = '847d18ced3ad93f957199727f626e22e14ffd9a9a8a0a41a7ab911a862184176'
        self.GS = None

    def get_data(self):
        ord = []
        try:
            cred = ServiceAccountCredentials.from_json_keyfile_dict(JSON_CRED, SCOPE)
            self.GS = gspread.authorize(cred)
            # print(39)
            ws = self.GS.open_by_key(SHEET_ID).get_worksheet(0)
            # print(ws)
                # .worksheet('date3110')
            # print(41)
            # print(ws.get_values())
            for row, rec in enumerate(ws.get_values()):
                print(rec)
                # pms = []
                # date = rec['Ngày'].strip()
                # if not date: continue
                # if rec['Done'].strip(): continue
                #
                # pur_date = datetime.strptime(date, '%d-%m-%Y')
                # code = pur_date.strftime("%Y%m%d")
                # total = int(rec['Tổng doanh số'].split()[0].replace(',',''))
                # vat = int(rec['Thuế'].split()[0].replace(',', ''))
                # cash = int(rec['Doanh số tiền mặt'].split()[0].replace(',', ''))
                # card = int(rec['Doanh số thẻ'].split()[0].replace(',', ''))
                # other = int(rec['Doanh số khác'].split()[0].replace(',', ''))
                # if cash != 0:
                #     pms.append({'Name': 'CASH', 'Value': cash})
                # if card != 0:
                #     pms.append({'Name': 'CARD', 'Value': card})
                # if other != 0:
                #     pms.append({'Name': 'OTHER', 'Value': other})
                # count = rec["Số đơn hàng"]
                # for i in range(1, count):
                #     ord.append({
                #         'Code': f'{code}_{i}',
                #         'Status': 2,
                #         'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
                #         'Total': 0,
                #         'TotalPayment': 0,
                #         'VAT': 0,
                #         'Discount': 0,
                #         'PaymentMethods': [{'Name': 'CASH', 'Value': total}],
                #         'OrderDetails': []
                #     })
                # ord.append({
                #     'Code': f'{code}_{count}',
                #     'Status': 2,
                #     'PurchaseDate': f"{pur_date.strftime('%Y-%m-%d')} 14:00:00",
                #     'Total': total,
                #     'TotalPayment': total,
                #     'VAT': vat,
                #     'Discount': 0,
                #     'PaymentMethods': pms,
                #     'OrderDetails': []
                # })
                # if len(ord) > 0:
                #     ws.update_cell(row=row+2, col=9, value=datetime.now().strftime('%y-%m-%d %H:%M:%S'))
        except Exception as e:
            print(e)
            # submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        # for _ in ord:
        #     submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=_)
if __name__:
    import sys

    PATH = dirname(dirname(__file__))
    # PATH = dirname(dirname(dirname(__file__)))
    # print(PATH)
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order

    LaneigeAMHD().get_data()
