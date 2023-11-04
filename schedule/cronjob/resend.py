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
    while True:
        try:
            res = requests.post(f'{URl}/orders', headers=headers, json=data, timeout=10)
            print(res.text)
            if res.json()['result_id'] is not None:
                break
        except Exception as e:
            pass
            # submit_error(retailer=headers['retailer'], reason=f'{str(e)} {data}')


while True:
    try:
        jobs = requests.get(f'{URl}/fetch_log', params=TOKEN)
        # print(jobs.text)
        for job in jobs.json():
            if job['type'] == 1:
                print(job['content']['Code'])
                headers = {
                    'content-type': 'application/json',
                    'retailer': job['retailer'],
                    'authorization': job['token'],
                    'debug': 'kt365aA@123'
                }
                if job.get('store') is not None:
                    headers.update({'store': str(job['store'])})
                submit_job(headers=headers, data=job['content'])
        break
    except Exception as e:
        print(e)
        pass
