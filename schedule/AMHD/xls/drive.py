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

class Google(object):
    def __init__(self):
        self.DRIVE = None
        self.SHEETS = None
        self.FOLDER_ID = '1wtoQQn505535Uy8ihNz8AiLvQalwE9pB'
        self.TOKEN_CRED = {
            'access_token': 'ya29.a0AfB_byBcx6XIG4p3hwoMSTtgMPcAMtR4Ze45SkzUhVP1jpSG2qm085Eh0MFIQ-swiSy3XHV5oARLp35IY65Hg7mFlj5esZnXaxiyJ2UOO1lAE30RyttBxw5nawaV6ZG18F9xbWi6avF8K_0k7X_LWnBLqfCQbNwcL8-YaCgYKAUkSARISFQGOcNnCTjW7QcvMTbR08aaDdWNqtQ0171',
            'refresh_token': '1//0ed8qZoHhHbtyCgYIARAAGA4SNwF-L9IrgxjN4cjezzbKW99VruQ-G9P5itECyl_BeHDEJORpjReqQU58Pe5gUP6FpI-rBMXZ5aY',
            'scope': SCOPE,
            'token_type': 'Bearer'
        }

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

    def create_sheet(self, DATA):
        idx = DATA.rindex('/')
        name = DATA[idx + 1:]
        file_metadata = {
            'name': name,
            'parents': [self.FOLDER_ID],
            'mimeType': 'application/vnd.google-apps.spreadsheet'
        }
        media = MediaFileUpload(
            DATA,
            # mimetype='application/vnd.ms-excel',
            resumable=True
        )
        _ = self.DRIVE.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return _['id']

    def delete(self, ID):
        try:
            self.DRIVE.files().delete(fileId=ID).execute()
        except:
            pass