import json
from datetime import datetime
from html import escape

import requests

URl = 'https://adapter.pos365.vn'
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
            if res.json()['result_id'] is not None:
                break
        except Exception as e:
            submit_error(retailer=headers['retailer'], reason=f'{str(e)} {data}')

f = open('xxxx.json', 'r')
s = f.read().strip()
f.close()
js = json.loads(s)
f = open('token.json', 'r')
s = f.read().strip()
f.close()
token = json.loads(s)
author = {}
for _ in token['data']:
    author.update({_['branch']: _['token']})
for _ in js['data']:
    try:

        # print(_['branch'], author[_['branch']])
        headers = {
            'content-type': 'application/json',
            'retailer': _['branch'],
            'authorization': author[_['branch']],
            'debug': 'kt365aA@123'
        }
        if _.get('store') is not None:
            headers.update({'store': str(_['store'])})
        submit_job(headers=headers, data=json.loads(_['content']))
        # break
    except:
        print(_)