from datetime import datetime
from html import escape

import requests


def submit_order(retailer=None, token=None, data=None):
    while True:
        try:
            # print(retailer, token)
            URL = 'https://adapter.pos365.vn/orders'
            headers = {
                'content-type': 'application/json',
                'retailer': retailer,
                'authorization': token,
                'debug': 'kt365aA@123'
            }
            res = requests.post(URL, headers=headers, json=data, timeout=10)
            # print(res.text)
            if res.json()['result_id'] is not None: return True
            return False
        except ConnectionError as ce:
            submit_error(retailer, f'{str(ce).split(":")[-1].strip()[:-3]} {data}')
        except Exception as e:
            submit_error(retailer, f'{str(e)} {data}')

def submit_payment(retailer=None, token=None, data=None):
    while True:
        try:
            # print(retailer, token)
            URL = 'https://adapter.pos365.vn/add_methods'
            headers = {
                'content-type': 'application/json',
                'retailer': retailer,
                'authorization': token
            }
            res = requests.post(URL, headers=headers, json=data, timeout=10)
            # print(res.text)
            if res.json()['result_id'] is not None: return True
            return False
        except ConnectionError as ce:
            submit_error(retailer, f'{str(ce).split(":")[-1].strip()[:-3]} {data}')
        except Exception as e:
            # submit_error(retailer, f'{str(e)} {data}')
            pass
def submit_error(retailer=None, reason=None):
    try:
        TOKEN = '6094052614:AAHhC8l1GKHXwBlLCHxWXySLxOSjFnvteB4'
        URL = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
        HTML = f'<b>[{retailer}]</b> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n=> {escape(reason)}'
        DATA = {
            'chat_id': '-855515377',
            'text': HTML,
            'parse_mode': 'HTML'
        }
        requests.post(URL, data=DATA)
    except Exception as e:
        print(56, e)
        pass

# if __name__ == '__main__':
#     print('XXX')