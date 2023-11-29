import json
import subprocess
import time
import uuid
from concurrent import futures
from datetime import datetime, timedelta

import requests
from celery import Celery
# from celery import Celery
from pytz import timezone

from pos365api import API

LOCAL_URL = 'https://adapter.pos365.vn'
CELERY_BROKER_URL = 'redis://localhost:6379'
RESULT_BACKEND = 'redis://localhost:6379'
background = Celery('Backend converter', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)


@background.task(bind=True)
def convert(self, domain, cfgId, ck, content, user, password, vat):
    log(self.request.id, None)
    content['Id'] = 0
    content['Code'] = content['Code'].replace('_DEL', '')
    content['Total'] = content['Total']
    content['TotalPayment'] = content['TotalPayment']
    count = 0
    while count < 5:
        api = API(domain, ck, user, password)
        al = api.account_list()
        if al['status'] is False:
            session = api.auth()
            if session is not None:
                ck = session
                try:
                    requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': session})
                except:
                    pass
        try:
            if content.get('Branch') is not None:
                branch = api.branch_list()
                # print(branch)
                if len(branch) > 0:
                    for _ in branch:
                        if _['Name'] == content.get('Branch').upper():
                            if not api.switch_branch(_['Id']):
                                return {'status': False}
                            break

            # vat = 0
            try:
                pd = datetime.strptime(content['PurchaseDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)
                pd = pd.astimezone(timezone('Etc/Gmt+0'))
                content.update({'PurchaseDate': str(pd)})
            except:
                pass
            try:
                pd = datetime.strptime(content['ReturnDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)
                pd = pd.astimezone(timezone('Etc/Gmt+0'))
                content.update({'ReturnDate': str(pd)})
            except:
                pass
            if content.get('PaymentMethods') is not None or type(content.get('PaymentMethods')) == list:
                pm = content.get('PaymentMethods')
                if pm is not None and type(pm) == list:
                    pms = []
                    for i in pm:
                        p_name = i.get('Name')
                        if p_name is not None and type(p_name) == str:
                            p_name = p_name.upper().strip()
                            if i.get('Value') is not None:
                                v = int(i.get('Value'))
                            else:
                                v = 0
                            if p_name in ['CASH', 'COD']:
                                pms.append({'AccountId': None, 'Value': v})
                            else:
                                res = requests.get(f'{LOCAL_URL}/payment',
                                                   params={'cfgId': cfgId, 'name': p_name}).json()
                                if res.get('status') is True:
                                    pms.append({'AccountId': res.get('AccountId'), 'Value': v})
                                else:
                                    res = api.account_save(p_name)
                                    if res.get('status') is True:
                                        pms.append({'AccountId': res.get('Id'), 'Value': v})
                                        requests.post(f'{LOCAL_URL}/payment',
                                                      params={'cfgId': cfgId, 'name': p_name, 'accId': res.get('Id')})
                                    else:
                                        ret = {'status': False, 'result': res.get('err')}
                                        log(self.request.id, ret)
                                        return ret
                    content['MoreAttributes'] = json.dumps({'PaymentMethods': pms})
            if content.get('AdditionalServices') is not None:
                try:
                    att = json.loads(content.get('MoreAttributes'))
                except:
                    att = {}
                service = content['AdditionalServices']
                att.update({'AdditionalServices': service})
                content['MoreAttributes'] = json.dumps(att)
                add = 0
                for i in service:
                    add += i['Value']
                content.update({
                    'TotalAdditionalServices': add,
                    'TotalAdditionalServicesVAT': int(round(abs(add) / ((1 + vat) / vat), 0))
                })
            if content.get('OrderDetails') is not None or type(content.get('OrderDetails')) == list:
                ods = content.get('OrderDetails')
                if len(ods) == 0: ods = [{'ProductId': 0}]
                for i in range(len(ods)):
                    if type(ods[i]) == dict:
                        if ods[i].get('ProductId') == 0: continue
                        p_code = ods[i].get('Code')
                        p_name = ods[i].get('Name') is None and ods[i].get('Code') or ods[i].get('Name')
                        p_price = ods[i].get('Price')
                        res = requests.get(f'{LOCAL_URL}/product',
                                           params={'cfgId': cfgId, 'code': p_code})
                        if res.status_code != 200:
                            ret = {'status': False, 'result': f'[{res.status_code}] /LOCAL/product'}
                            log(self.request.id, ret)
                            return ret
                        elif res.json().get('status') is True:
                            ods[i].update({'ProductId': res.json()['Id']})
                        else:
                            ps = api.product_save(p_code, p_name, p_price)
                            if ps.get('status'):
                                ods[i].update({'ProductId': ps.get('Id')})
                                requests.post(f'{LOCAL_URL}/product',
                                              params={'cfgId': cfgId, 'code': p_code, 'pid': ps['Id']}).json()
                            else:
                                ret = {'status': False, 'result': ps.get('err')}
                                log(self.request.id, ret)
                                return ret
                content['OrderDetails'] = ods
            if content.get('ReturnDetails') is not None or type(content.get('ReturnDetails')) == list:
                rds = content.get('ReturnDetails')
                if len(rds) == 0: rds = [{'ProductId': 0}]
                for i in range(len(rds)):
                    if type(rds[i]) == dict:
                        if rds[i].get('ProductId') == 0: continue
                        p_code = rds[i].get('Code')
                        p_price = rds[i].get('Price')
                        p_name = rds[i].get('Name') is None and rds[i].get('Code') or rds[i].get('Name')
                        res = requests.get(f'{LOCAL_URL}/product',
                                           params={'cfgId': cfgId, 'code': p_code})
                        if res.status_code != 200:
                            ret = {'status': False, 'result': f'[{res.status_code}] /LOCAL/product'}
                            log(self.request.id, ret)
                            return ret
                        elif res.json().get('status') is True:
                            rds[i].update({'ProductId': res.json()['Id']})
                        else:
                            ps = api.product_save(p_code, p_name, p_price)
                            if ps.get('status'):
                                rds[i].update({'ProductId': ps.get('Id')})
                                requests.post(f'{LOCAL_URL}/product',
                                              params={'cfgId': cfgId, 'code': p_code, 'pid': ps['Id']}).json()
                            else:
                                ret = {'status': False, 'result': ps.get('err')}
                                log(self.request.id, ret)
                                return ret
                content['ReturnDetails'] = rds
        except Exception as e:
            ret = {'status': False, 'result': str(e)}
            log(self.request.id, ret)
            return ret
        content.update({
            'AccountId': None,
            'OrderDetailBuilder': True
        })
        '''
        New Order = 2
        '''
        if int(content.get('Status')) == 2:
            bill = {
                'Order': content.copy()
            }
            try:
                del bill['Order']['PaymentMethods']
            except:
                pass
            try:
                del bill['Order']['AdditionalServices']
            except:
                pass
            try:
                del bill['Order']['VoucherCode']
            except:
                pass
            try:
                bill['Order']['Total'] = bill['Order']['Total'] - bill['Order']['Voucher']
            except:
                pass

            if bill['Order'].get('TotalAdditionalServicesVAT') is not None:
                bill['Order']['VAT'] -= bill['Order']['TotalAdditionalServicesVAT']
                try:
                    del bill['Order']['TotalAdditionalServicesVAT']
                except:
                    pass
            if bill['Order']['VAT'] == 0:
                try:
                    bill['Order']['VAT'] = int(round(bill['Order']['Total'] / ((1 + vat) / vat), 0))
                except:
                    pass
            res = api.order_save(bill)
            if res['status'] == 0:
                requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
                ck = res.get('ck')
            elif res['status'] == 1:
                ret = {'status': False, 'result': str(res['message'])}
                log(self.request.id, ret)
                return ret
            elif res['status'] == 3:
                id = api.order_get(content['Code'])

                if id['status'] is True:
                    if id.get('id') is not None:
                        content.update({'Id': id['id']})
                    else:
                        ret = {'status': False, 'result': id['err']}
                        log(self.request.id, ret)
                        return ret
                    if id.get('dup'):
                        bill = {
                            'Order': {
                                'Id': id['id'], 'Status': 2,
                                'PurchaseDate': content['PurchaseDate'],
                                'Code': f"DUP_{content['Code']}",
                                'Total': 0, 'Discount': 0,
                                'VAT': 0, 'OrderDetails': [{}],
                                'AccountId': None
                            }
                        }
                        res = api.order_save(bill)
                        # f = open('log.txt', 'a')
                        # f.write(str(res) + '\n')
                        # f.close()
                        if res['status'] == 2:
                            api.order_void(content['Id'])
                else:
                    ret = {'status': False, 'result': id['err']}
                    log(self.request.id, ret)
                    return ret
            else:  # if int(content.get('Status')) == 2:
                ret = {'status': True, 'result': res['message']}
                log(self.request.id, ret)
                return ret
        '''
        Cancel Order
        '''
        if int(content.get('Status')) == 3:
            id = api.order_get(content['Code'])
            if id['status']:
                if id.get('id') is not None:
                    content.update({'Id': id['id']})
                else:
                    ret = {'status': False, 'result': id['err']}
                    log(self.request.id, ret)
                    return ret
            else:
                ret = {'status': False, 'result': id['err']}
                log(self.request.id, ret)
                return ret
            res = api.order_void(id['id'])
            if res['status'] == 0:
                requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
                ck = res.get('ck')
            elif res['status'] == 1:
                ret = {'status': False, 'result': str(res['message'])}
                log(self.request.id, ret)
                return ret
            else:
                ret = {'status': True, 'result': res['message']}
                log(self.request.id, ret)
                return ret
        '''
        Return Order
        '''
        if int(content.get('Status')) == 0:
            bill = {
                'Return': content.copy()
            }
            res = api.return_save(bill)
            if res['status'] == 0:
                requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
                ck = res.get('ck')
            elif res['status'] == 1:
                ret = {'status': False, 'result': str(res['message'])}
                log(self.request.id, ret)
                return ret
            elif res['status'] == 3:
                id = api.return_get(content['Code'])
                if id['status']:
                    content.update({'Id': id['id']})
                else:
                    ret = {'status': False, 'result': str(id['err'])}
                    log(self.request.id, ret)
                    return ret
            else:
                ret = {'status': True, 'result': res['message']}
                log(self.request.id, ret)
                return ret
        count += 1
    ret = {'status': False, 'result': 'Over 5 times'}
    log(self.request.id, ret)
    return ret


@background.task(bind=True)
def add_payment(self, domain, cfgId, ck, content, user, password):
    content['OrderCode'] = content['OrderCode'].replace('_DEL', '')
    content['Id'] = 0
    count = 0
    while count < 5:
        api = API(domain, ck, user, password)
        al = api.account_list()
        if al['status'] is False:
            session = api.auth()
            if session is not None:
                ck = session
                try:
                    requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': session})
                except:
                    pass
        try:
            pd = datetime.strptime(content['TransDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)
            pd = pd.astimezone(timezone('Etc/Gmt+0'))
            content.update({'TransDate': str(pd)})
        except:
            pass
        data = content.copy()
        if data.get('AccountId') is not None:
            pm = data.get('AccountId').upper().strip()
            if pm in ['CASH', 'COD']:
                data.update({'AccountId': None})
            else:
                res = requests.get(f'{LOCAL_URL}/payment', params={'cfgId': cfgId, 'name': pm}).json()
                if res.get('status') is True:
                    data.update({'AccountId': res.get('AccountId')})
                else:
                    res = api.account_save(pm)
                    if res.get('status') is True:
                        data.update({'AccountId': res.get('AccountId')})
                        requests.post(f'{LOCAL_URL}/payment',
                                      params={'cfgId': cfgId, 'name': pm, 'accId': res.get('Id')})
                    else:
                        ret = {'status': False, 'result': res.get('err')}
                        log(self.request.id, ret)
                        return ret
        id = api.order_get(content['OrderCode'])
        if id['status'] is True:
            if id.get('id') is not None:
                data.update({'OrderId': id['id']})
            else:
                ret = {'status': False, 'result': id['err']}
                log(self.request.id, ret)
                return ret
        else:  # if int(content.get('Status')) == 2:
            ret = {'status': False, 'result': id['err']}
            log(self.request.id, ret)
            return ret
        id = api.accounting_transaction_get(content['Code'])
        if id['status'] is True:
            if id.get('id') is not None:
                data.update({'Id': id['id']})
            else:
                ret = {'status': False, 'result': id['err']}
                log(self.request.id, ret)
                return ret
            if id.get('dup'):
                trans = {
                    'Id': id['id'], 'Status': 2,
                    'TransDate': content['TransDate'],
                    'Code': f"DUP_{content['Code']}",
                    'AccountId': None,
                    'Amount': 0
                }
                api.accounting_transaction_save(trans)
                count += 1
                continue
        # else:  # if int(content.get('Status')) == 2:
        #     ret = {'status': False, 'result': id['err']}
        #     log(self.request.id, ret)
        #     return ret
        res = api.accounting_transaction_save(data)
        if res['status'] == 0:
            session = api.auth()
            if session is not None:
                ck = session
                try:
                    requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': session})
                except:
                    pass
            count += 1
            continue
        elif res['status'] == 1:
            ret = {'status': False, 'result': res['message']}
            log(self.request.id, ret)
            return ret
        elif res['status'] == 2:
            ret = {'status': True, 'result': res['message']}
            log(self.request.id, ret)
            return ret
        count += 1
    ret = {'status': False, 'result': 'Over 5 times'}
    log(self.request.id, ret)
    return ret


@background.task(bind=True)
def delData(self, domain, user, password, since, before):
    try:
        url = f'https://{domain}.pos365.vn'
        since = since - timedelta(days=1)
        since = since.strftime('%Y-%m-%dT17:00:00Z')
        before = before.strftime('%Y-%m-%dT16:59:00Z')
        b = None
        while True:
            if not b:
                while True:
                    try:
                        b = requests.session()
                        b.headers.update({'content-type': 'application/json'})
                        r = b.post(url + '/api/auth', json={'username': user, 'password': password}).json()
                        if r.get('SessionId'): break
                    except:
                        b = None
            skip = 0
            try:
                filter = []
                filter += ['(Status', 'eq', '2', 'or', 'Total', 'gt','0)']
                # filter += ['Status', 'eq', '0', ')']
                filter += ['and']
                filter += ['PurchaseDate', 'ge']
                filter += [f"'datetime''{since}'''"]
                filter += ['and']
                filter += ['PurchaseDate', 'lt']
                filter += [f"'datetime''{before}'''"]
                print(' '.join(filter))
                r = b.get(f'{url}/api/orders', params={
                    'Top': '50',
                    'Skip': str(skip),
                    'Filter': ' '.join(filter)
                })
                if len(r.json()['results']) == 0: break
                for _ in r.json()['results']:
                    print(_['Code'])
                    id = _["Id"]
                    code = _["Code"]
                    pur_date = datetime.strptime(_['PurchaseDate'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    pur_date = pur_date.strftime('%Y-%m-%d %H:%M:%S')
                    js = {'Order': {
                        'Id': id,
                        'Status': 2,
                        'Code': str(uuid.uuid4()),
                        'PurchaseDate': pur_date,
                        'Discount': 0,
                        'VAT': 0,
                        'Total': 0,
                        'TotalPayment': 0,
                        'AccountId': None,
                        'OrderDetails': [{'ProductId': 0}]
                    }}
                    r = b.post(f'{url}/api/orders', json=js).json()
                    if r.get('Errors') is not None: continue
                    print(b.delete(f'{url}/api/orders/{id}/void', json=js).json())
                skip += 50
            except Exception as e:
                print(e)
                b = None
    except:
        pass
    print('DONE')

@background.task(bind=True)
def addUser(self, user, password, user_type):
    try:
        p = subprocess.Popen(f'/usr/sbin/userdel -r {user}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'userdel {p.communicate()}')
        f = open('/etc/proftpd.conf', 'r')
        content = f.read()
        content = content.replace(f'''<IfUser {user}>\n\tTLSRequired off\n</IfUser>''','')
        f.close()
        f = open('/etc/proftpd.conf', 'w')
        f.write(content.strip())
        f.close()
        # p = subprocess.Popen('systemctl restart proftpd', shell=True)
        p = subprocess.Popen(f'/usr/sbin/useradd -m {user}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'useradd {p.communicate()}')
        # time.sleep(1)
        p = subprocess.Popen(f'echo {user}:{password} | /usr/sbin/chpasswd', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f'chpasswd {p.communicate()}')
        if user_type == 'FTP':
            f = open('/etc/proftpd.conf', 'a')
            f.write(f'''\r\n<IfUser {user}>\r\n\tTLSRequired off\r\n</IfUser>\r\n''')
            f.close()
        # time.sleep(1)
        while True:
            p = subprocess.Popen('/usr/bin/systemctl restart proftpd', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            print(f'proftpd {err}')
            if not len(err.decode('utf-8')): break
    except Exception as e:
        print(e)

def log(id, result):
    try:
        while True:
            r = requests.post(f'http://127.0.0.1:6060/log', json={'rid': id, 'result': str(result)})
            if r.status_code == 200:
                break
        # requests.post(f'http://adapter.pos365.vn:6000/log', json={'rid': id, 'result': str(result)})
        # print(time.perf_counter())
    except:
        pass
