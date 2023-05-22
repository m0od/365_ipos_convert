from os.path import dirname
import requests
import json
import xmltodict
from datetime import datetime


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
        self.ORDERS = {}

    def prepare_data(self, content):
        try:
            ts = datetime.fromtimestamp(int(content['tran_date'].strip()[6:-5]))
            ts = f'{ts.strftime("%Y-%m-%d")} {content["tran_time"].strip()}:00'
            tmp = content['trans_num'].strip()
            if len(tmp) == 0:
                return
            method = content['httt'].strip().upper()
            d_pm = {}
            for i in range(0, len(method), 2):
                method_code = method[i:i + 2]
                if method_code == 'TM':
                    value = content['end_amt']
                elif method_code == 'TH':
                    value = content['begin_amt']
                elif method_code == 'CK':
                    value = content.get('kit_qty')
                else:
                    value = content['pay_amt']
                if value is None: value = 0
                d_pm.update({
                    method_code: value
                })
            if self.ORDERS.get(tmp) is None:
                self.ORDERS[tmp] = {
                    'exp_id': content['exp_id'],
                    'Code': tmp,
                    'PurchaseDate': ts,
                    'Status': 2,
                    'Discount': content['dis_amt'],
                    'VAT': content['vat_amt'],
                    'Total': content['pay_amt'],
                    'TotalPayment': content['pay_amt'],
                    'OrderDetails': [
                        {
                            'Code': content['goods_id'].strip(),
                            'Name': content['goods_id'].strip(),
                            'Price': int(content['amount'] / int(content['qty'])),
                            'Quantity': int(content['qty'])
                        }
                    ]
                }
                self.ORDERS[tmp].update(d_pm)
            else:
                # print('is not None')
                od = self.ORDERS[tmp]['OrderDetails']
                od.append({
                    'Code': content['goods_id'].strip(),
                    'Name': content['goods_id'].strip(),
                    'Price': int(content['amount'] / int(content['qty'])),
                    'Quantity': int(content['qty'])
                })
                self.ORDERS[tmp].update({
                    'Discount': self.ORDERS[tmp]['Discount'] + content['dis_amt'],
                    'VAT': self.ORDERS[tmp]['VAT'] + content['vat_amt'],
                    'Total': self.ORDERS[tmp]['Total'] + content['pay_amt'],
                    'TotalPayment': self.ORDERS[tmp]['TotalPayment'] + content['pay_amt'],
                    'OrderDetails': od
                })
                for k, v in d_pm.items():
                    self.ORDERS[tmp].update({k: self.ORDERS[tmp][k] + v})
                    # for i in dic[tmp]['PaymentMethods']:
                #     # print(i)
                #     if i['Value'] < d_pm[i['Name']]['Value']:
                #         i['Value'] = d_pm[i['Name']]['Value']
                # if dic[tmp]['PaymentMethods'] != pm:
                #     dic[tmp].update({'PaymentMethods': pm})
        except Exception as e:
            if content['exp_id'] == 'S00001':
                submit_error(retailer=self.ADAPTER_RETAILER_BLOOM, reason=f'[Prepare Data] {str(e)}')
            else:
                submit_error(retailer=self.ADAPTER_RETAILER_TGC, reason=f'[Prepare Data] {str(e)}')
            pass

    def get_data(self, date_from):
        p = {
            'tenonline': self.TEN_ONLINE,
            'tendn': self.TEN_DN, 'pass': self.PASS,
            'tungay': date_from.strftime('%d-%m-%Y'),
            'denngay': date_from.strftime('%d-%m-%Y')
        }
        try:
            res = requests.get(self.CLIENT_API, params=p).text
            xml = xmltodict.parse(res)
            js = json.dumps(xml['string'])
            js = json.loads(js)['#text']
            js = json.loads(js)
            js = json.loads(js[2]['Data'])
            for i in js:
                # if i['exp_id'] == 'S00001':
                self.prepare_data(i)
                # elif i['exp_id'] == 'S00002':
                #     prepare_data(self.TRANS_TGC, i, self.ADAPTER_RETAILER_TGC)
            for _, js in self.ORDERS.items():
                pms = []
                if js.get('TM') is not None:
                    pms.append({'Name': 'CASH', 'Value': js.get('TM')})
                    js.pop('TM')
                if js.get('CK') is not None:
                    pms.append({'Name': 'CHUYỂN KHOẢN', 'Value': js.get('CK')})
                    js.pop('CK')
                if js.get('TH') is not None:
                    pms.append({'Name': 'THẺ', 'Value': js.get('TH')})
                    js.pop('TH')
                js.update({'PaymentMethods': pms})
                if js['exp_id'] == 'S00001':
                    js.pop('exp_id')
                    submit_order(retailer=self.ADAPTER_RETAILER_BLOOM, token=self.ADAPTER_TOKEN_BLOOM, data=js)
                else:
                    js.pop('exp_id')
                    submit_order(retailer=self.ADAPTER_RETAILER_TGC, token=self.ADAPTER_TOKEN_TGC, data=js)
                # print(js)
            # for _, js in self.TRANS_TGC.items():
            #     # print(js)
            #     submit_order(retailer=self.ADAPTER_RETAILER_TGC, token=self.ADAPTER_TOKEN_TGC, data=js)
        except Exception as e:
            submit_error(retailer='TGC_BLOOM', reason=f'[Fetch Data] {str(e)}')


if __name__.__contains__('schedule.client_api'):
    import sys

    PATH = dirname(dirname(__file__))
    sys.path.append(PATH)
    from schedule.pos_api.adapter import submit_error, submit_order
