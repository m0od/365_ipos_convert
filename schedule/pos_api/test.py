import gspread
from oauth2client.service_account import ServiceAccountCredentials
# from gspread_dataframe import set_with_dataframe

json_path = '###' # Please set the file for using service account.

scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('../webgui/ggsheet/cred.json', scope)
client = gspread.authorize(creds)

spreadsheetTitle = 'new spreadsheet title'
folderId = '1o37ZfJQFrGhvE1pYIg7yz8mJonLiJem-' # Please set the folder ID of the folder in your Google Drive.

workbook = client.create(spreadsheetTitle, folder_id=folderId)
