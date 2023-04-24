from datetime import datetime
from html import escape
import requests

URl = 'https://adapter.pos365.vn'
TOKEN = {'token': 'kt365aA@123'}

def submit_error(retailer=None, reason=None):
    try:
        TELE_TOKEN = '6094052614:AAHhC8l1GKHXwBlLCHxWXySLxOSjFnvteB4'
        TELE_URL = f'https://api.telegram.org/bot{TELE_TOKEN}/sendMessage'
        HTML = f'<b>[{retailer}]</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n=> {escape(reason)}'
        DATA = {
            'chat_id': '-855515377',
            'text': HTML,
            'parse_mode': 'HTML'
        }
        requests.post(TELE_URL, data=DATA)
    except:
        pass

def submit_job(headers=None, data=None):
    if headers['retailer'].endswith('_aeonhd'):
        url_path = 'aeon_orders'
    else:
        url_path = 'orders'
    while True:
        try:
            res = requests.post(f'{URl}/{url_path}', headers=headers, json=data, timeout=10)
            if res.json()['result_id'] is not None:
                break
        except Exception as e:
            submit_error(retailer=headers['retailer'], reason=f'{str(e)} {data}')
while True:
    try:
        jobs = requests.get(f'{URl}/fetch_log', params=TOKEN).json()
        print(jobs)
        for job in jobs:
            headers = {
                'content-type': 'application/json',
                'retailer': job['retailer'],
                'authorization': job['token']
            }
            submit_job(headers=headers, data=job['content'])
        break
    except:
        pass