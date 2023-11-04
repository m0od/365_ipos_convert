import io
import os
import sys
from datetime import datetime, timedelta
from os.path import dirname, join

from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

DRIVE_CRED = {
    # "installed": {
    "project_id": "prefab-kit-382903",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "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",
    "client_id": "726905584100-0pihs37sasrvr7p1oai5rn3gq05qkhv7.apps.googleusercontent.com",

    "redirect_uris": ["http://localhost"]
    # }
}


class YangHaoAMHD(object):
    def __init__(self):
        PATH = dirname(dirname(__file__))
        sys.path.append(PATH)
        self.FULL_PATH = f'/home/drive'
        self.ORDERS = {}
        self.ADAPTER_RETAILER = 'yanghao_amhd'
        self.ADAPTER_TOKEN = '4a63189b3901f20ae2fecaa490d658be6b3d5c6228e116a545b07c45c7752f23'
        self.GS = None
        self.FOLDER = ''
        self.TOKEN_CRED = {
            'access_token': 'ya29.a0AfB_byBcx6XIG4p3hwoMSTtgMPcAMtR4Ze45SkzUhVP1jpSG2qm085Eh0MFIQ-swiSy3XHV5oARLp35IY65Hg7mFlj5esZnXaxiyJ2UOO1lAE30RyttBxw5nawaV6ZG18F9xbWi6avF8K_0k7X_LWnBLqfCQbNwcL8-YaCgYKAUkSARISFQGOcNnCTjW7QcvMTbR08aaDdWNqtQ0171',
            'refresh_token': '1//0ed8qZoHhHbtyCgYIARAAGA4SNwF-L9IrgxjN4cjezzbKW99VruQ-G9P5itECyl_BeHDEJORpjReqQU58Pe5gUP6FpI-rBMXZ5aY',
            'scope': SCOPE,
            'token_type': 'Bearer'
        }
        self.DRIVE = None
        self.SHEETS = None
        self.DRIVE_FOLDER = 'YANGHAO_AMHD'
        self.field = 'nextPageToken, files(id, name)'
        self.FOLDER_ID = '1oqTTtH4CUEA6ZFqonhPKEAzzlhLFGpR0'
    def google_auth(self):
        self.TOKEN_CRED.update({
            'client_secret': DRIVE_CRED['client_secret'],
            'client_id': DRIVE_CRED['client_id']
        })
        creds = Credentials.from_authorized_user_info(self.TOKEN_CRED, SCOPE)
        # creds = None
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                CRED = {'installed': DRIVE_CRED}
                flow = InstalledAppFlow.from_client_config(
                    CRED, SCOPE,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob')
                auth_url, _ = flow.authorization_url(prompt='consent')
                print('Please go to this URL: {}'.format(auth_url))
                code = input('Enter the authorization code: ')
                self.TOKEN_CRED = flow.fetch_token(code=code)
                self.TOKEN_CRED.update({
                    'client_secret': DRIVE_CRED['client_secret'],
                    'client_id': DRIVE_CRED['client_id']
                })
                print(self.TOKEN_CRED)
        self.DRIVE = build('drive', 'v3', credentials=creds)
        self.SHEETS = build('sheets', 'v4', credentials=creds)

    def create_sheet(self, file):
        request = self.DRIVE.files().get_media(fileId=file['id'])
        _ = io.BytesIO()
        downloader = MediaIoBaseDownload(_, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fp = join(self.FULL_PATH, file['name'])
        f = open(fp, 'wb')
        f.write(_.getvalue())
        f.close()

        file_metadata = {
            'name': f"convert_{file['name']}",
            'parents': [self.FOLDER_ID],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(
            fp,
            mimetype='application/vnd.ms-excel',
            resumable=True
        )
        _ = self.DRIVE.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        try:
            os.remove(fp)
        except:
            pass
        return _['id']
    def extract_data(self, SHEET_ID):
        from pos_api.adapter import submit_order
        ws = self.SHEETS.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range='1:1000'
        ).execute()
        for row, rec in enumerate(ws['values'][3:-3]):
            code = rec[7].replace('.00', '').replace(',', '')
            pur_date = f'{rec[4]} {rec[12]}'
            pur_date = datetime.strptime(pur_date, '%d/%m/%Y %H:%S')
            pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
            total = int(rec[18].replace('.00', '').replace(',', ''))
            discount = abs(int(rec[15].replace('.00', '').replace(',', '')))
            discount += int(rec[26].replace('.00', '').replace(',', ''))
            vat = int(rec[17].replace('.00', '').replace(',', ''))
            cash = int(rec[19].replace('.00', '').replace(',', ''))
            card = int(rec[20].replace('.00', '').replace(',', ''))
            momo = int(rec[21].replace('.00', '').replace(',', ''))
            vnpay = int(rec[22].replace('.00', '').replace(',', ''))
            zalopay = int(rec[23].replace('.00', '').replace(',', ''))
            clingme = int(rec[24].replace('.00', '').replace(',', ''))
            point = int(rec[25].replace('.00', '').replace(',', ''))
            voucher = int(rec[27].replace('.00', '').replace(',', ''))
            pms = [
                {'Name': 'CASH', 'Value': cash},
                {'Name': 'CARD', 'Value': card},
                {'Name': 'MOMO', 'Value': momo},
                {'Name': 'VNPAY', 'Value': vnpay},
                {'Name': 'ZALOPAY', 'Value': zalopay},
                {'Name': 'CLINGME', 'Value': clingme},
                {'Name': 'POINT', 'Value': point},
                {'Name': 'VOUCHER', 'Value': voucher},
            ]
            for pos, _ in enumerate(pms.copy()):
                if _['Value'] == 0:
                    pms.remove(_)
            order = {
                'Code': code,
                'Status': 2,
                'PurchaseDate': pur_date,
                'Total': total,
                'TotalPayment': total,
                'VAT': vat,
                'Discount': discount,
                'OrderDetails': [{'ProductId': 0}],
                'PaymentMethods': pms
            }
            submit_order(retailer=self.ADAPTER_RETAILER, token=self.ADAPTER_TOKEN, data=order)
        try:
            self.DRIVE.files().delete(fileId=SHEET_ID).execute()
        except Exception as e:
            print(e)

    def get_file(self):
        yesterday = datetime.utcnow() - timedelta(days=1)
        query = [
            f"'{self.FOLDER_ID}' in parents",
            f"createdTime >= '{yesterday.strftime('%Y-%m-%dT00:00:00')}'",
            f"createdTime < '{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}'",
            "trashed = false"
        ]
        query = ' and '.join(query).strip()
        results = self.DRIVE.files().list(
            q=query,
            fields=self.field
        ).execute()
        return results
    def get_data(self):
        from pos_api.adapter import submit_error
        try:
            for file in self.get_file().get('files', []):
                print(file)
                try:
                    SHEET_ID = self.create_sheet(file)
                    self.extract_data(SHEET_ID)
                except Exception as e:
                    submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))
        except Exception as e:
            submit_error(retailer=self.ADAPTER_RETAILER, reason=str(e))


x = YangHaoAMHD()
x.google_auth()
x.get_data()
