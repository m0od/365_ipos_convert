import requests
import json

def auth(d, u, p):
    url = f'https://{d}.pos365.vn/api/auth'
    try:
        b = requests.session()
        b.headers.update({'Content-Type': 'application/json'})
        b.timeout = 10
        account = json.dumps({'UserName': u, 'PassWord': p})
        res = b.post(url, data=account)
        # print(res.status_code)
        if res.status_code == 200:
            return b
        elif res.status_code in [400, 401]:
            return None
        # print(res.text)
        return b
    except: return None