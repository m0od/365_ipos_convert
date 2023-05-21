from datetime import datetime

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

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
FOLDER = '1o37ZfJQFrGhvE1pYIg7yz8mJonLiJem-'


class Sheet(object):
    def __init__(self):
        self.cred = ServiceAccountCredentials.from_json_keyfile_dict(JSON_CRED, SCOPE)
        self.wb = None
        self.sheet_id = None
        self.sheet_url = None

    def create_sheet(self, domain=None, title=None):
        client = gspread.authorize(self.cred)
        print('LOGGED')
        title = f"{domain}_{title}_{datetime.now().strftime('%d-%m-%y %H:%M')}"
        self.wb = client.create(title, folder_id=FOLDER)
        print('CREATED')

        self.sheet_id = self.wb.id
        self.sheet_url = self.wb.url
        print(self.sheet_url)

    def insert(self, data=None):
        ws = self.wb.get_worksheet(0)
        values = [
            ['Mã hàng hóa', 'Tên hàng hóa', 'Tên nhóm', 'ĐVT', 'ĐVT Lớn', 'Mã ĐVT Lớn', 'Giá trị quy đổi', 'Giá bán',
             'Giá bán ĐVT Lớn', 'Giá vốn', 'Tồn kho', 'Thuộc tính', 'Hình ảnh', 'Ghi chú nhanh khi bán hàng',
             'Định mức tồn nhỏ nhất', 'Định mức tồn lớn nhất', 'Loại hàng', 'Không cho phép bán',
             'Tách thành nhiều dòng khi bán hàng', 'Tên máy in', 'Mã nhà cung cấp', 'VAT', 'Thành phần',
             'Quản lý theo Lô Hạn', 'Không in ra tem nhãn', 'Mở Extra/Topping khi chọn', 'In nhiều vị trí', 'Hoa hồng',
             'Id']]
        values.extend(data)
        ws.insert_rows(values)
        set_frozen(ws, 1)
        fmt = CellFormat(
            backgroundColor=Color(147 / 255, 204 / 255, 234 / 255),  # set it to yellow
            textFormat=TextFormat(bold=True),
        )
        format_cell_range(ws, '1:1', fmt)
# Sheet().auth(None)
