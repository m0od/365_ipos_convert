import requests

url = 'https://am167.pos365.vn'

b = requests.session()
# b.proxies.update({
#     'http': 'socks5://adapter.pos365.vn:13337'
# })
b.headers.update({'content-type': 'application/json'})
r = b.post(url + '/api/auth', json={
    'username': 'admin',
    'password':'aeonhd'
})
skip = 0
while True:
    r = b.get(url + '/api/orders', params={
        'Top': '50', 'Skip': str(skip),
        # 'Type':'2',
        'Filter': f"substringof('202401',Code)"
    })
    if r.status_code != 200: continue
    # print(r.text)
    js = r.json()['results']
    if len(js) == 0: break
    for _ in js:
        # print(_['Id'])
        b.delete(url + f'/api/partners/{_["Id"]}')
        # b.delete(url + f'/api/orderstock/{_["Id"]}')
    skip += 50

