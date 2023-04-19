import json
from datetime import datetime

import requests
from celery import Celery
# from celery import Celery
from pytz import timezone

from pos365api import API

LOCAL_URL = 'https://adapter.pos365.vn'
CELERY_BROKER_URL = 'redis://localhost:6379'
RESULT_BACKEND = 'redis://localhost:6379'
background = Celery('Background converter', backend=RESULT_BACKEND, broker=CELERY_BROKER_URL)


@background.task(bind=True)
def convert(self, domain, cfgId, ck, content, user, password):
    content['Id'] = 0
    content['Code'] = content['Code'].replace('_DEL', '')
    content['Total'] = abs(content['Total'])
    content['TotalPayment'] = abs(content['TotalPayment'])
    while True:
        api = API(domain, ck, user, password)
        al = api.account_list()
        if al['status'] is False:
            res = api.auth()
            try:
                requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
            except:
                pass
        try:
            try:
                pd = datetime.strptime(content['PurchaseDate'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=None)
                pd = pd.astimezone(timezone('Etc/Gmt+0'))
                content.update({'PurchaseDate': str(pd)})
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
                                v = abs(int(i.get('Value')))
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
                                    pms.append({'AccountId': res.get('Id'), 'Value': v})
                                    requests.post(f'{LOCAL_URL}/payment',
                                                  params={'cfgId': cfgId, 'name': p_name, 'accId': res.get('Id')})
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
                content.update({'TotalAdditionalServices': add})
            if content.get('OrderDetails') is not None or type(content.get('OrderDetails')) == list:
                ods = content.get('OrderDetails')
                for i in range(len(ods)):
                    if type(ods[i]) == dict:
                        p_code = ods[i].get('Code')
                        p_name = ods[i].get('Name') is None and ods[i].get('Code') or ods[i].get('Name')
                        res = requests.get(f'{LOCAL_URL}/product',
                                           params={'cfgId': cfgId, 'code': p_code}).json()
                        if res.get('status') is True:
                            ods[i].update({'ProductId': res.get('Id')})
                        else:
                            ps = api.product_save(p_code, p_name)
                            ods[i].update({'ProductId': ps.get('Id')})
                            requests.post(f'{LOCAL_URL}/product',
                                          params={'cfgId': cfgId, 'code': p_code, 'pid': ps['Id']}).json()
                content['OrderDetails'] = ods
        except Exception as e:
            ret = {'status': False, 'result': str(e)}
            log(self.request.id, ret)
            return ret
        content.update({
            'AccountId': None,
            'OrderDetailBuilder': True
        })
        order = {
            'Order': content.copy()
        }
        res = api.order_save(order)
        if res['status'] == 0:
            requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
            ck = res.get('ck')
        elif res['status'] == 1:
            ret = {'status': False, 'result': str(res['message'])}
            log(self.request.id, ret)
            return ret
        elif res['status'] == 3:
            id = api.order_get(content['Code'])
            if id is not None:
                content.update({'Id': id})
        elif int(content.get('Status')) == 2:
            ret = {'status': True, 'result': res['message']}
            log(self.request.id, ret)
            return ret
        if int(content.get('Status')) == 3:
            while True:
                id = api.order_get(content['Code'])
                if id is not None: break
            content.update({'Id': id})
            res = api.order_void(id)
            if res['status'] == 0:
                requests.patch(f'{LOCAL_URL}/cfg', data={'cfgId': cfgId, 'cookie': res.get('ck')})
                ck = res.get('ck')
            elif res['status'] == 1:
                ret = {'status': False, 'result': str(res['message'])}
                log(self.request.id, ret)
                return ret
            else:
                ret = {'status': True, 'result': str(res['message'])}
                log(self.request.id, ret)
                return ret


def log(id, result):
    try:
        requests.post(f'{LOCAL_URL}/log', json={'rid': id, 'result': str(result)})
    except:
        pass