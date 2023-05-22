import requests
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs

from requests_toolbelt import MultipartEncoder


def auth(USER, PASSWORD, DOMAIN):
    try:
        login = 'https://accounts.sapo.vn/login'
        url = f'https://{DOMAIN}.mysapogo.com'
        # p = {
        #     'clientId': CLIENT_ID,
        #     'domain': DOMAIN,
        # }
        b =  requests.session()
        res = b.get(f'{url}/admin/login')
        # print(res.url)
        parsed_url = urlparse(res.url)
        params = parse_qs(parsed_url.query)
        csrf = res.text.split('name="_csrf" content="')[1].split('"')[0]
        CLIENT_ID = params['clientId'][0]

        p = {
            '_csrf': csrf,
            # 'clientId': CLIENT_ID,
            # 'domain': DOMAIN,
            'phoneNumber': USER,
            'password': PASSWORD,
            # 'isFixedDomain': str(False),
            # 'loginToken': '',
            # 'relativeContextPath': '/status-error/404',
            'countryCode': '84'
        }
        m = MultipartEncoder(fields=p)
        b.headers.update({'content-type': m.content_type})
        res = b.post(login, data=m)
        print(res.text)
        res = b.get(f'{url}/status-error/404')
        print(res.text)
        # print(list(b.cookies))
        b.headers.update({
            'content-type': 'application/json',
            # 'X-Sapo-Client': 'sapo-frontend-v3',
            # 'X-Sapo-Serviceid': 'sapo-frontend-v3',
            'authorization': '',
            # 'referer': f'{url}/admin'
        })
        res = b.get(f'{url}/admin/authorization/login')
        # print(res.text)
        # b.headers.update({
        #     'accept': 'application/json',
        #     'X-Sapo-Client': 'sapo-frontend-v3',
        #     'X-Sapo-Serviceid': 'sapo-frontend-v3',
        #     'authorization': ''
        # })
        res = b.get(f'{url}/admin/orders.json?page=1&limit=1')
        for i in res.json()['orders']:
            print(i)
    except Exception as e:
        print(e)
        pass

auth('0981339456', '123456', 'ttpos')