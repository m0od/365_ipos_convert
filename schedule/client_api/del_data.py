import requests

url = 'https://applestorehp1.pos365.vn'

b = requests.session()
b.headers.update({'content-type': 'application/json'})
r = b.post(url + '/api/auth', json={'username': 'quantri@pos365.vn', 'password':'IT@P0s365kmS'})
skip = 0
while True:
    r = b.get(url + '/api/partners', params={'Top': '50', 'Skip': str(skip), 'Type':'2'})
    if r.status_code != 200: continue
    # print(r.text)
    js = r.json()['results']
    if len(js) == 0: break
    for _ in js:
        print(_['Id'])
        b.delete(url + f'/api/partners/{_["Id"]}')
        # b.delete(url + f'/api/orderstock/{_["Id"]}')
    skip += 50

