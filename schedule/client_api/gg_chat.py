import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CHAT_CRED = {
    "project_id": "prefab-kit-382903",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "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",
    "client_id": "726905584100-0pihs37sasrvr7p1oai5rn3gq05qkhv7.apps.googleusercontent.com",

    "redirect_uris": ["http://localhost"]
}
SCOPE = [
    "https://www.googleapis.com/auth/chat.messages.create"
]
TOKEN_CRED = {
    'access_token': 'ya29.a0AfB_byBGsEw7eszhd1lrKL653eU_NKLbFaEQPFBKkkiJVRoTeVV-pn_saSJBxJiRUWO4WPx58VtagPsP2W32zTdc0K-QXGTHnXNcuE_mIwPbMi0D7ibvtCjPitDHtMYbM0p4NOdIhSUlAI9IgnkgTty9OuuHTaaHtPBuaCgYKASgSARISFQHGX2MioiWtThAa2SvwB5ygPTtI1A0171',
    'expires_in': 3599,
    'refresh_token': '1//0fOuyLs_Xns1dCgYIARAAGA8SNwF-L9IrowOniSLMElnP7LZRCRQwxjTF1DwW3DS7rSW0R7I8vKVPTG73P2qDuH_FOZkY5hhcV1U',
    'scope': ['https://www.googleapis.com/auth/chat.messages.create'], 'token_type': 'Bearer',
    'expires_at': 1700686764.231711, 'client_secret': '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'}
# CRED = {'installed': CHAT_CRED}
# flow = InstalledAppFlow.from_client_config(
#     CRED, SCOPE,
#     redirect_uri='urn:ietf:wg:oauth:2.0:oob')
# auth_url, _ = flow.authorization_url(prompt='consent')
# print('Please go to this URL: {}'.format(auth_url))
# code = input('Enter the authorization code: ')
# TOKEN_CRED = flow.fetch_token(code=code)
TOKEN_CRED.update({
    'client_secret': CHAT_CRED['client_secret'],
    'client_id': CHAT_CRED['client_id']
})
print(TOKEN_CRED)
creds = Credentials.from_authorized_user_info(TOKEN_CRED, SCOPE)

chat = build('chat', 'v1', credentials=creds)
result = chat.spaces().messages().create(
    parent='space/AAAATDjnhNQ', body={'text': f'5404044986822954|03|25|507'}
).execute()
print(result)
