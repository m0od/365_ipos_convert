import requests
import json
import sys
import xmltodict
sys.path.append('/home/blackwings/365ipos')
from pos_api.adapter import submit_order, submit_error
from datetime import datetime


def prepare_data(dic, content, retailer):
    try:
        ts = datetime.fromtimestamp(int(content['tran_date'].strip()[6:-5]))
        ts = f'{ts.strftime("%Y-%m-%d")} {content["tran_time"].strip()}:00'
        # ts = datetime.strptime(ts, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %H:%M:%S')
        tmp = content['trans_num'].strip()
        # print(tmp, retailer)
        if len(tmp) == 0:
            return
        method = content['httt'].strip().upper()
        d_pm = {}
        for i in range(0, len(method), 2):
            method_code = method[i:i+2]
            if method_code == 'TM':
                method_code = 'CASH'
                d_pm.update({
                    method_code: {
                        'Name': method_code,
                        'Value': content['end_amt']
                    }
                })
            elif method_code == 'TH':
                method_code = 'THẺ'
                d_pm.update({
                    method_code: {
                        'Name': method_code,
                        'Value': content['begin_amt']
                    }
                })
                # pm.append({
                #     'Name': 'THẺ',
                #     'Value': content['begin_amt']
                # })
            elif method_code == 'CK':
                method_code = 'CHUYỂN KHOẢN'
                d_pm.update({
                    method_code: {
                        'Name': method_code,
                        'Value': content['begin_amt']
                    }
                })
                # pm.append({
                #     'Name': 'CHUYỂN KHOẢN',
                #     'Value': content['begin_amt']
                # })
            else:
                d_pm.update({
                    method_code: {
                        'Name': method_code,
                        'Value': content['pay_amt']
                    }
                })
                # pm.append({
                #     'Name': method_code,
                #     'Value': content['pay_amt']
                # })
        if dic.get(tmp) is None:
            # print(list(d_pm.values()))
            dic[tmp] = {
                'Code': tmp,
                'PurchaseDate': ts,
                'Status': 2,
                'Discount': content['dis_amt'],
                'VAT': content['vat_amt'],
                'Total': content['pay_amt'],
                'TotalPayment': content['pay_amt'],
                'PaymentMethods': list(d_pm.values()),
                # 'Id': 0,
                'OrderDetails': [
                    {
                        'Code': content['goods_id'].strip(),
                        'Name': content['goods_id'].strip(),
                        'Price': int(content['amount'] / int(content['qty'])),
                        'Quantity': int(content['qty'])
                    }
                ]
            }
        else:
            # print('is not None')
            od = dic[tmp]['OrderDetails']
            od.append({
                'Code': content['goods_id'].strip(),
                'Name': content['goods_id'].strip(),
                'Price': int(content['amount'] / int(content['qty'])),
                'Quantity': int(content['qty'])
            })
            dic[tmp].update({
                'Discount': dic[tmp]['Discount'] + content['dis_amt'],
                'VAT': dic[tmp]['VAT'] + content['vat_amt'],
                'Total': dic[tmp]['Total'] + content['pay_amt'],
                'TotalPayment': dic[tmp]['TotalPayment'] + content['pay_amt'],
                'OrderDetails': od
            })
            for i in dic[tmp]['PaymentMethods']:
                # print(i)
                if i['Value'] < d_pm[i['Name']]['Value']:
                    i['Value'] = d_pm[i['Name']]['Value']
            # if dic[tmp]['PaymentMethods'] != pm:
            #     dic[tmp].update({'PaymentMethods': pm})
    except Exception as e:
        # print(e)
        submit_error(retailer=retailer, reason=f'[Prepare Data] {str(e)}')
        pass


class TGC_BLOOM(object):
    def __init__(self):
        self.ADAPTER_RETAILER_TGC = 'tgc_aeonhd'
        self.ADAPTER_TOKEN_TGC = '4a8055f47627ee8bb719328d32664d176eb3558dfc27e0e438d5970cb0bde152'
        self.ADAPTER_RETAILER_BLOOM = 'bloom_aeonhd'
        self.ADAPTER_TOKEN_BLOOM = 'f4537c11815d1aab2aca3bfeb95da0f9015f750d20ed823f334b04b3ef3859b6'
        self.CLIENT_API = 'http://online.phanmembanhang.net.vn/Admin/EstelleService.asmx/GetInfoSaleOrder'
        self.TEN_ONLINE = 'estelle'
        self.TEN_DN = 'bcaeon'
        self.PASS = '123456789!'
        self.ROUTE_BLOOM = 'bloom'
        self.ROUTE_TGC = 'tgc'
        self.TRANS_BLOOM = {}
        self.TRANS_TGC = {}

    def get_data(self, date_from):
        p = {
            'tenonline': self.TEN_ONLINE,
            'tendn': self.TEN_DN, 'pass': self.PASS,
            'tungay': date_from, 'denngay': date_from
        }
        try:
            res = requests.get(self.CLIENT_API, params=p).text
            xml = xmltodict.parse(res)
            js = json.dumps(xml['string'])
            js = json.loads(js)['#text']
            js = json.loads(js)
            js = json.loads(js[2]['Data'])
            for i in js:
                if i['exp_id'] == 'S00001':
                    prepare_data(self.TRANS_BLOOM, i, self.ADAPTER_RETAILER_BLOOM)
                elif i['exp_id'] == 'S00002':
                    prepare_data(self.TRANS_TGC, i, self.ADAPTER_RETAILER_TGC)
            for _, js in self.TRANS_BLOOM.items():
                # print(js)
                submit_order(retailer=self.ADAPTER_RETAILER_BLOOM, token=self.ADAPTER_TOKEN_BLOOM, data=js)
            for _, js in self.TRANS_TGC.items():
                # print(js)
                submit_order(retailer=self.ADAPTER_RETAILER_TGC, token=self.ADAPTER_TOKEN_TGC, data=js)
        except Exception as e:
            submit_error(retailer='TGC_BLOOM', reason=f'[Fetch Data] {str(e)}')

# TGC_BLOOM().get_data('23-04-2023')